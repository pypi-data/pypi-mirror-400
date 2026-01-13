import pyro
import pyro.distributions as dist
from pyro.optim import ExponentialLR
from pyro.infer import SVI, JitTraceEnum_ELBO, TraceEnum_ELBO, config_enumerate

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.distributions.utils import logits_to_probs, probs_to_logits, clamp_probs
from torch.distributions import constraints
from torch.distributions.transforms import SoftmaxTransform

from .utils.custom_mlp import MLP, Exp, ZeroBiasMLP
from .utils.utils import CustomDataset, tensor_to_numpy, convert_to_tensor
from .atac import binarize

from .dist.negbinomial import NegativeBinomial as MyNB
from .dist.negbinomial import ZeroInflatedNegativeBinomial as MyZINB

from sklearn.preprocessing import StandardScaler

import os
import argparse
import random
import numpy as np
import datatable as dt
from tqdm import tqdm
from scipy import sparse
import scanpy as sc

from typing import Literal

import warnings
warnings.filterwarnings("ignore")

import dill as pickle
import gzip
from packaging.version import Version
torch_version = torch.__version__


def set_random_seed(seed):
    # Set seed for PyTorch
    torch.manual_seed(seed)
    
    # If using CUDA, set the seed for CUDA
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)  # For multi-GPU setups.
    
    # Set seed for NumPy
    np.random.seed(seed)
    
    # Set seed for Python's random module
    random.seed(seed)

    # Set seed for Pyro
    pyro.set_rng_seed(seed)

class scGCA(nn.Module):
    """Single-Cell Genome-wide Chromatin Accessibility

    Parameters
    ----------
    inpute_size
        Number of features (e.g., genes, peaks, proteins, etc.) per cell.
    covariate_size
        Number of undesired factors. It would be used to adjust for undesired variations like batch effect.
    codebook_size
        Number of metacells.
    latent_dim
        Dimensionality of latent states and metacells. 
    hidden_layers
        A list give the numbers of neurons for each hidden layer.
    loss_func
        The likelihood model for single-cell data generation. 
        
        One of the following: 
        * ``'negbinomial'`` -  negative binomial distribution (default)
        * ``'poisson'`` - poisson distribution
        * ``'multinomial'`` - multinomial distribution
    latent_dist
        The distribution model for latent states. 
        
        One of the following:
        * ``'normal'`` - normal distribution
        * ``'laplacian'`` - Laplacian distribution
        * ``'studentt'`` - Student-t distribution. 
    use_cuda
        A boolean option for switching on cuda device. 

    Examples
    --------
    >>>
    >>>
    >>>

    """
    def __init__(self,
                 input_dim: int,
                 covariate_size: int = 0,
                 codebook_size: int = 200,
                 use_cell_factor: bool = True,
                 use_gene_factor: bool = True,
                 gene_factor_size: int = 0,
                 z_dim: int = 50,
                 z_dist: Literal['normal','studentt','laplacian','cauchy'] = 'studentt',
                 loss_func: Literal['poisson','bernoulli','negbinomial'] = 'poisson',
                 dispersion: float = 10.0,
                 use_zeroinflate: bool = False,
                 hidden_layers: list = [300],
                 hidden_layer_activation: Literal['relu','softplus','leakyrelu','linear'] = 'relu',
                 nn_dropout: float = 0.1,
                 post_layer_fct: list = ['layernorm'],
                 post_act_fct: list = None,
                 config_enum: str = 'parallel',
                 use_cuda: bool = False,
                 seed: int = 0,
                 dtype = torch.float32, # type: ignore
                 ):
        super().__init__()

        self.input_dim = input_dim
        self.covariate_size = covariate_size
        self.latent_dim = z_dim
        self.latent_dist = z_dist
        self.hidden_layers = hidden_layers
        self.decoder_hidden_layers = hidden_layers[::-1]
        self.allow_broadcast = config_enum == 'parallel'
        self.use_cuda = use_cuda
        self.dispersion = dispersion
        self.use_zeroinflate = use_zeroinflate
        self.loss_func = loss_func
        self.options = None
        self.code_size=codebook_size
        self.use_cell_factor = use_cell_factor
        self.use_gene_factor = use_gene_factor
        self.gene_factor_size = gene_factor_size
        self.gene_factors = None

        self.dtype = dtype

        self.nn_dropout = nn_dropout
        self.post_layer_fct = post_layer_fct
        self.post_act_fct = post_act_fct
        self.hidden_layer_activation = hidden_layer_activation

        self.codebook_weights = None

        if seed is not None:
            set_random_seed(seed)
            
        self.setup_networks()

    def setup_networks(self):
        latent_dim = self.latent_dim
        hidden_sizes = self.hidden_layers

        nn_layer_norm, nn_batch_norm, nn_layer_dropout = False, False, False
        na_layer_norm, na_batch_norm, na_layer_dropout = False, False, False

        if self.post_layer_fct is not None:
            nn_layer_norm=True if ('layernorm' in self.post_layer_fct) or ('layer_norm' in self.post_layer_fct) else False
            nn_batch_norm=True if ('batchnorm' in self.post_layer_fct) or ('batch_norm' in self.post_layer_fct) else False
            nn_layer_dropout=True if 'dropout' in self.post_layer_fct else False

        if self.post_act_fct is not None:
            na_layer_norm=True if ('layernorm' in self.post_act_fct) or ('layer_norm' in self.post_act_fct) else False
            na_batch_norm=True if ('batchnorm' in self.post_act_fct) or ('batch_norm' in self.post_act_fct) else False
            na_layer_dropout=True if 'dropout' in self.post_act_fct else False

        if nn_layer_norm and nn_batch_norm and nn_layer_dropout:
            post_layer_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.Dropout(self.nn_dropout),nn.BatchNorm1d(layer.module.out_features), nn.LayerNorm(layer.module.out_features))
        elif nn_layer_norm and nn_layer_dropout:
            post_layer_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.Dropout(self.nn_dropout), nn.LayerNorm(layer.module.out_features))
        elif nn_batch_norm and nn_layer_dropout:
            post_layer_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.Dropout(self.nn_dropout), nn.BatchNorm1d(layer.module.out_features))
        elif nn_layer_norm and nn_batch_norm:
            post_layer_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.BatchNorm1d(layer.module.out_features), nn.LayerNorm(layer.module.out_features))
        elif nn_layer_norm:
            post_layer_fct = lambda layer_ix, total_layers, layer: nn.LayerNorm(layer.module.out_features)
        elif nn_batch_norm:
            post_layer_fct = lambda layer_ix, total_layers, layer:nn.BatchNorm1d(layer.module.out_features)
        elif nn_layer_dropout:
            post_layer_fct = lambda layer_ix, total_layers, layer: nn.Dropout(self.nn_dropout)
        else:
            post_layer_fct = lambda layer_ix, total_layers, layer: None

        if na_layer_norm and na_batch_norm and na_layer_dropout:
            post_act_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.Dropout(self.nn_dropout),nn.BatchNorm1d(layer.module.out_features), nn.LayerNorm(layer.module.out_features))
        elif na_layer_norm and na_layer_dropout:
            post_act_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.Dropout(self.nn_dropout), nn.LayerNorm(layer.module.out_features))
        elif na_batch_norm and na_layer_dropout:
            post_act_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.Dropout(self.nn_dropout), nn.BatchNorm1d(layer.module.out_features))
        elif na_layer_norm and na_batch_norm:
            post_act_fct = lambda layer_ix, total_layers, layer: nn.Sequential(nn.BatchNorm1d(layer.module.out_features), nn.LayerNorm(layer.module.out_features))
        elif na_layer_norm:
            post_act_fct = lambda layer_ix, total_layers, layer: nn.LayerNorm(layer.module.out_features)
        elif na_batch_norm:
            post_act_fct = lambda layer_ix, total_layers, layer:nn.BatchNorm1d(layer.module.out_features)
        elif na_layer_dropout:
            post_act_fct = lambda layer_ix, total_layers, layer: nn.Dropout(self.nn_dropout)
        else:
            post_act_fct = lambda layer_ix, total_layers, layer: None

        if self.hidden_layer_activation == 'relu':
            activate_fct = nn.ReLU
        elif self.hidden_layer_activation == 'softplus':
            activate_fct = nn.Softplus
        elif self.hidden_layer_activation == 'leakyrelu':
            activate_fct = nn.LeakyReLU
        elif self.hidden_layer_activation == 'linear':
            activate_fct = nn.Identity

        self.encoder_n = MLP(
            [self.latent_dim] + hidden_sizes + [self.code_size],
            activation=activate_fct,
            output_activation=None,
            post_layer_fct=post_layer_fct,
            post_act_fct=post_act_fct,
            allow_broadcast=self.allow_broadcast,
            use_cuda=self.use_cuda,
        )

        self.encoder_zn = MLP(
            [self.input_dim] + hidden_sizes + [[latent_dim, latent_dim]],
            activation=activate_fct,
            output_activation=[None, Exp],
            post_layer_fct=post_layer_fct,
            post_act_fct=post_act_fct,
            allow_broadcast=self.allow_broadcast,
            use_cuda=self.use_cuda,
        )
        
        if self.use_cell_factor:
            self.cell_factor_effect = MLP(
                [self.input_dim] + hidden_sizes + [1],
                activation=activate_fct,
                output_activation=None,
                post_layer_fct=post_layer_fct,
                post_act_fct=post_act_fct,
                allow_broadcast=self.allow_broadcast,
                use_cuda=self.use_cuda,
            )
        
        if self.use_gene_factor and self.gene_factor_size>0:
            self.gene_factor_effect = nn.ModuleList()
            for i in np.arange(self.gene_factor_size):
                self.gene_factor_effect.append(MLP(
                    [1] + hidden_sizes + [1],
                    activation=activate_fct,
                    output_activation=None,
                    post_layer_fct=post_layer_fct,
                    post_act_fct=post_act_fct,
                    allow_broadcast=self.allow_broadcast,
                    use_cuda=self.use_cuda,
                )
                )

        if self.covariate_size>0:
            self.decoder_log_mu = ZeroBiasMLP(
                [self.covariate_size + self.latent_dim] + self.decoder_hidden_layers + [self.input_dim],
                activation=activate_fct,
                output_activation=None,
                post_layer_fct=post_layer_fct,
                post_act_fct=post_act_fct,
                allow_broadcast=self.allow_broadcast,
                use_cuda=self.use_cuda,
            )
        else:
            self.decoder_log_mu = MLP(
                [self.latent_dim] + self.decoder_hidden_layers + [self.input_dim],
                activation=activate_fct,
                output_activation=None,
                post_layer_fct=post_layer_fct,
                post_act_fct=post_act_fct,
                allow_broadcast=self.allow_broadcast,
                use_cuda=self.use_cuda,
            )

        if self.latent_dist == 'studentt':
            self.codebook = MLP(
                [self.code_size] + hidden_sizes + [[latent_dim,latent_dim,latent_dim]],
                activation=activate_fct,
                output_activation=[Exp,None,Exp],
                post_layer_fct=post_layer_fct,
                post_act_fct=post_act_fct,
                allow_broadcast=self.allow_broadcast,
                use_cuda=self.use_cuda,
            )
        else:
            self.codebook = MLP(
                [self.code_size] + hidden_sizes + [[latent_dim,latent_dim]],
                activation=activate_fct,
                output_activation=[None,Exp],
                post_layer_fct=post_layer_fct,
                post_act_fct=post_act_fct,
                allow_broadcast=self.allow_broadcast,
                use_cuda=self.use_cuda,
            )

        if self.use_cuda:
            self.cuda()

    def get_device(self):
        return next(self.parameters()).device

    def cutoff(self, xs, thresh=None):
        eps = torch.finfo(xs.dtype).eps
        
        if not thresh is None:
            if eps < thresh:
                eps = thresh

        xs = xs.clamp(min=eps)

        if torch.any(torch.isnan(xs)):
            xs[torch.isnan(xs)] = eps

        return xs

    def softmax(self, xs):
        xs = SoftmaxTransform()(xs)
        return xs
    
    def sigmoid(self, xs):
        sigm_enc = nn.Sigmoid()
        xs = sigm_enc(xs)
        xs = clamp_probs(xs)
        return xs

    def softmax_logit(self, xs):
        eps = torch.finfo(xs.dtype).eps
        xs = self.softmax(xs)
        xs = torch.logit(xs, eps=eps)
        return xs

    def logit(self, xs):
        eps = torch.finfo(xs.dtype).eps
        xs = torch.logit(xs, eps=eps)
        return xs

    def dirimulti_param(self, xs):
        xs = self.dirimulti_mass * self.sigmoid(xs)
        return xs

    def multi_param(self, xs):
        xs = self.softmax(xs)
        return xs

    def model(self, xs, us=None):
        pyro.module('scgca', self)

        eps = torch.finfo(xs.dtype).eps
        batch_size = xs.size(0)
        self.options = dict(dtype=xs.dtype, device=xs.device)
        
        if self.loss_func=='negbinomial':
            dispersion = pyro.param("dispersion", self.dispersion *
                                            xs.new_ones(self.input_dim), constraint=constraints.positive)
            
        if self.use_zeroinflate:
            gate_logits = pyro.param("dropout_rate", xs.new_zeros(self.input_dim))
            
        if self.use_gene_factor:
            if self.gene_factor_size>0:
                gfe = []
                for i in np.arange(self.gene_factor_size):
                    gfe.append(self.gene_factor_effect[i](self.gene_factors[:,i].reshape(-1,1)).T)
            else:
                gf = pyro.param("gene_factor", xs.new_zeros(self.input_dim))
        
        I = torch.eye(self.code_size)
        if self.latent_dist == 'studentt':
            acs_dof,acs_loc,acs_scale = self.codebook(I)
        else:
            acs_loc,acs_scale = self.codebook(I)

        with pyro.plate('data'):
            prior = torch.zeros(batch_size, self.code_size, **self.options)
            ns = pyro.sample('n', dist.OneHotCategorical(logits=prior))

            prior_loc = torch.matmul(ns,acs_loc)
            prior_scale = torch.matmul(ns,acs_scale)

            if self.latent_dist == 'studentt':
                prior_dof = torch.matmul(ns,acs_dof)
                zns = pyro.sample('zn', dist.StudentT(df=prior_dof, loc=prior_loc, scale=prior_scale).to_event(1))
            elif self.latent_dist == 'laplacian':
                zns = pyro.sample('zn', dist.Laplace(prior_loc, prior_scale).to_event(1))
            elif self.latent_dist == 'cauchy':
                zns = pyro.sample('zn', dist.Cauchy(prior_loc, prior_scale).to_event(1))
            elif self.latent_dist == 'normal':
                zns = pyro.sample('zn', dist.Normal(prior_loc, prior_scale).to_event(1))

            if us is not None:
                zs = [us, zns]
            else:
                zs = zns

            log_mu = self.decoder_log_mu(zs)
                
            if self.use_cell_factor:
                cf = self.cell_factor_effect(xs)
                log_mu += cf 
            if self.use_gene_factor:
                if self.gene_factor_size>0:
                    for i in np.arange(self.gene_factor_size):
                        log_mu += gfe[i]
                else:
                    log_mu += gf

            if self.loss_func in ['bernoulli']:
                log_theta = log_mu
            elif self.loss_func == 'negbinomial':
                mu = log_mu.exp()
            else:
                rate = log_mu.exp()
                theta = dist.DirichletMultinomial(total_count=1, concentration=rate).mean
                rate = theta * torch.sum(xs, dim=1, keepdim=True)

            if self.loss_func == 'poisson':
                if self.use_zeroinflate:
                    pyro.sample('x', dist.ZeroInflatedDistribution(dist.Poisson(rate=rate),gate_logits=gate_logits).to_event(1), obs=xs.round())
                else:
                    pyro.sample('x', dist.Poisson(rate=rate).to_event(1), obs=xs.round())
            elif self.loss_func == 'bernoulli':
                if self.use_zeroinflate:
                    pyro.sample('x', dist.ZeroInflatedDistribution(dist.Bernoulli(logits=log_theta),gate_logits=gate_logits).to_event(1), obs=xs)
                else:
                    pyro.sample('x', dist.Bernoulli(logits=log_theta).to_event(1), obs=xs)
            elif self.loss_func == 'negbinomial':
                if self.use_zeroinflate:
                    pyro.sample("x", MyZINB(mu=mu, theta=dispersion, zi_logits=gate_logits).to_event(1), obs=xs)
                else:
                    pyro.sample("x", MyNB(mu=mu, theta=dispersion).to_event(1), obs=xs)

    def guide(self, xs, us=None):
        with pyro.plate('data'):
            zn_loc, zn_scale = self.encoder_zn(xs)
            zns = pyro.sample('zn', dist.Normal(zn_loc, zn_scale).to_event(1))

            alpha = self.encoder_n(zns)
            ns = pyro.sample('n', dist.OneHotCategorical(logits=alpha))

    def _get_codebook_identity(self):
        return torch.eye(self.code_dim, **self.options)
    
    def _get_codebook(self):
        I = torch.eye(self.code_size, **self.options)
        if self.latent_dist=='studentt':
            _,cb,_ = self.codebook(I)
        else:
            cb,_ = self.codebook(I)
        return cb
    
    def get_codebook(self):
        """
        Return the mean part of metacell codebook
        """
        cb = self._get_codebook()
        cb = tensor_to_numpy(cb)
        return cb

    def _get_cell_embedding(self, xs):           
        zns, _ = self.encoder_zn(xs)
        return zns 
    
    def get_cell_embedding(self, 
                             xs, 
                             batch_size: int = 1024, 
                             show_progress: bool = True 
                             ):
        """
        Return cells' latent representations

        Parameters
        ----------
        xs
            Single-cell expression matrix. It should be a Numpy array or a Pytorch Tensor.
        batch_size
            Size of batch processing.
        use_decoder
            If toggled on, the latent representations will be reconstructed from the metacell codebook
        soft_assign
            If toggled on, the assignments of cells will use probabilistic values.
        """
        xs = convert_to_tensor(xs, device='cpu')
        dataset = CustomDataset(xs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        Z = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                X_batch = X_batch.to(self.get_device())
                zns = self._get_cell_embedding(X_batch)
                Z.append(tensor_to_numpy(zns))
                pbar.update(1)

        Z = np.concatenate(Z)
        return Z
    
    def _code(self, xs):
        zns,_ = self.encoder_zn(xs)
        alpha = self.encoder_n(zns)
        return alpha
    
    def code(self, xs, batch_size=1024, show_progress=True):
        xs = convert_to_tensor(xs, device='cpu')
        dataset = CustomDataset(xs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        A = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                X_batch = X_batch.to(self.get_device())
                a = self._code(X_batch)
                A.append(tensor_to_numpy(a))
                pbar.update(1)

        A = np.concatenate(A)
        return A
    
    def _soft_assignments(self, xs):
        alpha = self._code(xs)
        alpha = self.softmax(alpha)
        return alpha
    
    def soft_assignments(self, xs, batch_size=1024, show_progress=True):
        """
        Map cells to metacells and return the probabilistic values of metacell assignments
        """
        xs = convert_to_tensor(xs, device='cpu')
        dataset = CustomDataset(xs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        A = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                X_batch = X_batch.to(self.get_device())
                a = self._soft_assignments(X_batch)
                A.append(tensor_to_numpy(a))
                pbar.update(1)

        A = np.concatenate(A)
        return A
    
    def _hard_assignments(self, xs):
        alpha = self._code(xs)
        res, ind = torch.topk(alpha, 1)
        ns = torch.zeros_like(alpha).scatter_(1, ind, 1.0)
        return ns
    
    def hard_assignments(self, xs, batch_size=1024, show_progress=True):
        """
        Map cells to metacells and return the assigned metacell identities.
        """
        xs = convert_to_tensor(xs, device='cpu')
        dataset = CustomDataset(xs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        A = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                X_batch = X_batch.to(self.get_device())
                a = self._hard_assignments(X_batch)
                A.append(tensor_to_numpy(a))
                pbar.update(1)

        A = np.concatenate(A)
        return A
    
    def _log_mu(self,zns,us=None):
        if us is None:
            zs = zns
        else:
            zs = [us,zns]
        log_mu = self.decoder_log_mu(zs)
        return log_mu
    
    def _count(self, log_mu, library_size=None):
        if self.loss_func == 'bernoulli':
            counts = dist.Bernoulli(logits=log_mu).to_event(1).mean
        elif self.loss_func == 'negbinomial':
            counts = log_mu.exp()
        else:
            rate = log_mu.exp()
            theta = dist.DirichletMultinomial(total_count=1, concentration=rate).mean
            if library_size is None:
                counts = theta
            else:
                counts = theta * library_size
        return counts
    
    def get_log_mu(self, zs, us = None,
                   batch_size: int = 1024, 
                   show_progress: bool = True):
        """
        Return the scaled expression data of input cells.

        Parameters
        ----------
        xs
            Single-cell expression matrix. It should be a Numpy array or a Pytorch Tensor. Rows are cells and columns are features.
        batch_size
            Size of batch processing
        """
        zs = convert_to_tensor(zs, device='cpu')
        if us is not None:
            us = convert_to_tensor(us, device='cpu')
        dataset = CustomDataset(zs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        E = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for Z_batch, idx in dataloader:
                Z_batch = Z_batch.to(self.get_device())
                if us is None:
                    log_mu = self._log_mu(Z_batch)
                else:
                    U_batch = us[idx].to(self.get_device())
                    log_mu = self._log_mu(Z_batch, U_batch)
                E.append(tensor_to_numpy(log_mu))
                pbar.update(1)
        
        E = np.concatenate(E)
        return E
    
    def get_counts(self, zs, library_sizes, us=None, 
                        batch_size: int = 1024, 
                        show_progress: bool = True):
        """
        Return the simulated count data of input cells.

        Parameters
        ----------
        xs
            Single-cell expression matrix. It should be a Numpy array or a Pytorch Tensor. Rows are cells and columns are features.
        total_count
            Paramter for negative binomial distribution.
        total_counts_per_cell
            Parameter for poisson distribution.
        batch_size
            Size of batch processing.
        """
        zs = convert_to_tensor(zs, device='cpu')
        
        if us is not None:
            us = convert_to_tensor(us, device='cpu')
        
        if type(library_sizes) == list:
            library_sizes = np.array(library_sizes).reshape(-1,1)
        elif len(library_sizes.shape)==1:
            library_sizes = library_sizes.reshape(-1,1)
        ls = convert_to_tensor(library_sizes, device='cpu')
        
        dataset = CustomDataset(zs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
        
        E = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for Z_batch, idx in dataloader:
                Z_batch = Z_batch.to(self.get_device())
                L_batch = ls[idx].to(self.get_device())
                
                if us is None:
                    log_mu = self._log_mu(Z_batch)
                else:
                    U_batch = us[idx].to(self.get_device())
                    log_mu = self._log_mu(Z_batch, U_batch)
                    
                counts = self._count(log_mu, L_batch)
                
                E.append(tensor_to_numpy(counts))
                pbar.update(1)
        
        E = np.concatenate(E)
        return E
    
    def get_cell_accessibility(self, zs, us=None,
                                 batch_size: int = 1024, 
                                 show_progress: bool = True):
        """
        Return the accessibiilty estimation of input cells.

        Parameters
        ----------
        xs
            Single-cell ATAC matrix. It should be a Numpy array or a Pytorch Tensor. Rows are cells and columns are features.
        batch_size
            Size of batch processing
        """
        zs = convert_to_tensor(zs, device='cpu')
        
        if us is not None:
            us = convert_to_tensor(us, device='cpu')
            
        dataset = CustomDataset(zs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        E = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for Z_batch, idx in dataloader:
                Z_batch = Z_batch.to(self.get_device())
                if us is None:
                    log_mu = self._log_mu(Z_batch)
                else:
                    U_batch = us[idx].to(self.get_device())
                    log_mu = self._log_mu(Z_batch, U_batch)
                    
                acc = self._count(log_mu)
                E.append(tensor_to_numpy(acc))
                pbar.update(1)
        
        E = np.concatenate(E)
        return E
    
    def get_gene_factor_effect(self, gf_id):
        gf_matrix = self.gene_factors[:,gf_id].reshape(-1,1)
        gf_effect = self.gene_factor_effect[gf_id](gf_matrix)
        return tensor_to_numpy(gf_effect)
    
    def preprocess(self, xs, threshold=0):
        if self.loss_func == 'bernoulli':
            ad = sc.AnnData(xs)
            binarize(ad, threshold=threshold)
            xs = ad.X.copy()
        else:
            xs = np.round(xs)
            
        if sparse.issparse(xs):
            xs = xs.toarray()
        return xs 
    
    def fit(self, xs, 
            us = None, 
            gene_factors = None,
            num_epochs: int = 200, 
            learning_rate: float = 0.0001, 
            batch_size: int = 256, 
            algo: Literal['adam','rmsprop','adamw'] = 'adam', 
            beta_1: float = 0.9, 
            weight_decay: float = 0.005, 
            decay_rate: float = 0.9,
            config_enum: str = 'parallel',
            threshold: int = 0,
            use_jax: bool = False,
            show_progress=True):
        """
        Train the scGCA model.

        Parameters
        ----------
        xs
            Single-cell experssion matrix. It should be a Numpy array or a Pytorch Tensor. Rows are cells and columns are features.
        us
            Undesired factor matrix. It should be a Numpy array or a Pytorch Tensor. Rows are cells and columns are undesired factors.
        ys
            Desired factor matrix. It should be a Numpy array or a Pytorch Tensor. Rows are cells and columns are desired factors.
        num_epochs
            Number of training epochs.
        learning_rate
            Parameter for training.
        batch_size
            Size of batch processing.
        algo
            Optimization algorithm.
        beta_1
            Parameter for optimization.
        weight_decay
            Parameter for optimization.
        decay_rate 
            Parameter for optimization.
        use_jax
            If toggled on, Jax will be used for speeding up. CAUTION: This will raise errors because of unknown reasons when it is called in
            the Python script or Jupyter notebook. It is OK if it is used when runing scGCA in the shell command.
        """
        xs = self.preprocess(xs, threshold=threshold)
        xs = convert_to_tensor(xs, dtype=self.dtype, device='cpu')
        if us is not None:
            us = convert_to_tensor(us, dtype=self.dtype, device='cpu')
        if gene_factors is not None:
            self.gene_factors = convert_to_tensor(gene_factors, dtype=self.dtype, device=self.get_device())
            
        self.options = dict(dtype=xs.dtype, device=xs.device)

        dataset = CustomDataset(xs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        # setup the optimizer
        optim_params = {'lr': learning_rate, 'betas': (beta_1, 0.999), 'weight_decay': weight_decay}

        if algo.lower()=='rmsprop':
            optimizer = torch.optim.RMSprop
        elif algo.lower()=='adam':
            optimizer = torch.optim.Adam
        elif algo.lower() == 'adamw':
            optimizer = torch.optim.AdamW
        else:
            raise ValueError("An optimization algorithm must be specified.")
        scheduler = ExponentialLR({'optimizer': optimizer, 'optim_args': optim_params, 'gamma': decay_rate})

        pyro.clear_param_store()

        # set up the loss(es) for inference, wrapping the guide in config_enumerate builds the loss as a sum
        # by enumerating each class label form the sampled discrete categorical distribution in the model
        Elbo = JitTraceEnum_ELBO if use_jax else TraceEnum_ELBO
        elbo = Elbo(max_plate_nesting=1, strict_enumeration_warning=False)
        guide = config_enumerate(self.guide, config_enum, expand=True)
        loss_basic = SVI(self.model, guide, scheduler, loss=elbo)

        # build a list of all losses considered
        losses = [loss_basic]
        num_losses = len(losses)

        with tqdm(total=num_epochs, disable=not show_progress, desc='Training', unit='epoch') as pbar:
            for epoch in range(num_epochs):
                epoch_losses = [0.0] * num_losses
                for batch_x, idx in dataloader:
                    batch_x = batch_x.to(self.get_device())
                    batch_u = None
                    if us is not None:
                        batch_u = us[idx].to(self.get_device())

                    for loss_id in range(num_losses):
                        new_loss = losses[loss_id].step(batch_x, us=batch_u)
                        epoch_losses[loss_id] += new_loss

                avg_epoch_losses_ = map(lambda v: v / len(dataloader), epoch_losses)
                avg_epoch_losses = map(lambda v: "{:.4f}".format(v), avg_epoch_losses_)

                # store the loss
                str_loss = " ".join(map(str, avg_epoch_losses))

                # Update progress bar
                pbar.set_postfix({'loss': str_loss})
                pbar.update(1)
        
        assigns = self.soft_assignments(xs)
        assigns = convert_to_tensor(assigns, dtype=self.dtype, device=self.get_device())
        self.codebook_weights = torch.sum(assigns, dim=0)
        self.codebook_weights = self.codebook_weights / torch.sum(self.codebook_weights)

    @classmethod
    def save_model(cls, model, file_path, compression=False):
        """Save the model to the specified file path."""
        file_path = os.path.abspath(file_path)

        model.eval()
        if compression:
            with gzip.open(file_path, 'wb') as pickle_file:
                pickle.dump(model, pickle_file)
        else:
            with open(file_path, 'wb') as pickle_file:
                pickle.dump(model, pickle_file)

        print(f'Model saved to {file_path}')

    @classmethod
    def load_model(cls, file_path):
        """Load the model from the specified file path and return an instance."""
        print(f'Model loaded from {file_path}')

        file_path = os.path.abspath(file_path)
        if file_path.endswith('gz'):
            with gzip.open(file_path, 'rb') as pickle_file:
                model = pickle.load(pickle_file)
        else:
            with open(file_path, 'rb') as pickle_file:
                model = pickle.load(pickle_file)
        
        return model

