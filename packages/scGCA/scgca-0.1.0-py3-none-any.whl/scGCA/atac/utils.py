from typing import Union, Optional
from warnings import warn

import numpy as np
from scipy.sparse import csr_matrix, dia_matrix, issparse
from sklearn.preprocessing import MinMaxScaler

from anndata import AnnData

import scanpy as sc
from scanpy._utils import view_to_actual

import re
import pyBigWig
from collections import Counter
import pandas as pd

# Computational methods for preprocessing


def tfidf(
    data: AnnData,
    log_tf: bool = True,
    log_idf: bool = True,
    log_tfidf: bool = False,
    scale_factor: Union[int, float] = 1e4,
    inplace: bool = True,
    copy: bool = False,
    from_layer: Optional[str] = None,
    to_layer: Optional[str] = None,
):
    """
    Transform peak counts with TF-IDF (Term Frequency - Inverse Document Frequency).

    TF: peak counts are normalised by total number of counts per cell
    DF: total number of counts for each peak
    IDF: number of cells divided by DF

    By default, log(TF) * log(IDF) is returned.

    Parameters
    ----------
    data
            AnnData object with peak counts.
    log_idf
            Log-transform IDF term (True by default).
    log_tf
            Log-transform TF term (True by default).
    log_tfidf
            Log-transform TF*IDF term (False by default).
            Can only be used when log_tf and log_idf are False.
    scale_factor
            Scale factor to multiply the TF-IDF matrix by (1e4 by default).
    inplace
            If to modify counts in the AnnData object (True by default).
    copy
            If to return a copy of the AnnData object or the 'atac' modality (False by default).
            Not compatible with inplace=False.
    from_layer
            Layer to use counts (AnnData.layers[from_layer])
            instead of AnnData.X used by default.
    to_layer
            Layer to save transformed counts to (AnnData.layers[to_layer])
            instead of AnnData.X used by default.
            Not compatible with inplace=False.
    """
    if isinstance(data, AnnData):
        adata = data
    else:
        raise TypeError("Expected AnnData object")

    if log_tfidf and (log_tf or log_idf):
        raise AttributeError(
            "When returning log(TF*IDF), \
            applying neither log(TF) nor log(IDF) is possible."
        )

    if copy and not inplace:
        raise ValueError("`copy=True` cannot be used with `inplace=False`.")

    if to_layer is not None and not inplace:
        raise ValueError(f"`to_layer='{str(to_layer)}'` cannot be used with `inplace=False`.")

    if copy:
        adata = adata.copy()

    view_to_actual(adata)

    counts = adata.X if from_layer is None else adata.layers[from_layer]

    # Check before the computation
    if to_layer is not None and to_layer in adata.layers:
        warn(f"Existing layer '{str(to_layer)}' will be overwritten")

    if issparse(counts):
        n_peaks = np.asarray(counts.sum(axis=1)).reshape(-1)
        n_peaks = dia_matrix((1.0 / n_peaks, 0), shape=(n_peaks.size, n_peaks.size))
        # This prevents making TF dense
        tf = np.dot(n_peaks, counts)
    else:
        n_peaks = np.asarray(counts.sum(axis=1)).reshape(-1, 1)
        tf = counts / n_peaks

    if scale_factor is not None and scale_factor != 0 and scale_factor != 1:
        tf = tf * scale_factor
    if log_tf:
        tf = np.log1p(tf)

    idf = np.asarray(adata.shape[0] / counts.sum(axis=0)).reshape(-1)
    if log_idf:
        idf = np.log1p(idf)

    if issparse(tf):
        idf = dia_matrix((idf, 0), shape=(idf.size, idf.size))
        tf_idf = np.dot(tf, idf)
    else:
        tf_idf = np.dot(csr_matrix(tf), csr_matrix(np.diag(idf)))

    if log_tfidf:
        tf_idf = np.log1p(tf_idf)

    res = np.nan_to_num(tf_idf, nan=0.0)
    if not inplace:
        return res

    if to_layer is not None:
        adata.layers[to_layer] = res
    else:
        adata.X = res

    if copy:
        return adata


def binarize(data: AnnData, threshold: np.float32=0):
    """
    Transform peak counts to the binary matrix (all the non-zero values become 1).

    Parameters
    ----------
    data
            AnnData object with peak counts.
    """
    if isinstance(data, AnnData):
        adata = data
    else:
        raise TypeError("Expected AnnData object")

    if issparse(adata.X):
        # Sparse matrix
        adata.X.data[adata.X.data > threshold] = 1
    else:
        adata.X[adata.X > threshold] = 1


    
    
def convert_adata_to_bigwig(data, output, minmax=True):
    if isinstance(data, AnnData):
        adata = data
    else:
        raise TypeError("Expected AnnData object")
    
    # 2. 提取peak信息
    # 假设peak信息存储在var中，格式为"chr:start-end"
    peaks = adata.var_names

    # 3. 解析peak位置
    chromosomes = []
    starts = []
    ends = []

    for peak in peaks:
        chrom, start, end = re.split(r"[:-]", peak)
        chromosomes.append(chrom)
        starts.append(int(start))
        ends.append(int(end))

    # 4. 计算全基因组信号
    # 这里我们简单计算每个peak在所有细胞中的平均信号
    mean_signal = np.array(adata.X.mean(axis=0)).flatten()
    if minmax:
        mean_signal = mean_signal / mean_signal.max()

    # 5. 按染色体组织数据
    chromosome_data = {}
    for chrom in set(chromosomes):
        idx = [i for i, c in enumerate(chromosomes) if c == chrom]
        chrom_starts = [starts[i] for i in idx]
        chrom_ends = [ends[i] for i in idx]
        chrom_signal = [mean_signal[i] for i in idx]
    
        # 按起始位置排序
        sorted_idx = np.argsort(chrom_starts)
        chromosome_data[chrom] = {
            'starts': np.array(chrom_starts)[sorted_idx],
            'ends': np.array(chrom_ends)[sorted_idx],
            'signal': np.array(chrom_signal)[sorted_idx]
        }

    # 创建bigwig文件
    bw = pyBigWig.open(output, "w")
    bw.addHeader([(chrom, max(data['ends'])) for chrom, data in chromosome_data.items()])

    for chrom, data in chromosome_data.items():
        bw.addEntries(
            [chrom] * len(data['starts']),
            data['starts'].astype(int),
            ends=data['ends'].astype(int),
            values=data['signal'].astype(float)
        )
    bw.close()
    #将上述生成的bigwig文件加载到IGV或UCSC Genome Browser中可以获得交互式可视化
    

def parse_region(region_str):
    chrom, start, end = re.split(r"[:-]", region_str)
    return chrom, int(start), int(end)


from pyfaidx import Fasta
try:
    from Bio.SeqUtils import gc_fraction
    def GC(sequence):
        return 100 * gc_fraction(sequence, ambiguous="ignore")
except ImportError:
    # Older versions have this:
    from Bio.SeqUtils import GC
    
def fetch_peak_sequences(adata, genome_file):
    genome = Fasta(genome_file)
    parsed_regions = [parse_region(r) for r in adata.var.index]
    sequences = [genome[chrom][start+1:end].seq for chrom,start,end in parsed_regions]
    adata.var['peak_sequence'] = sequences
    
def genome_GC_content(adata, genome_file):
    genome = Fasta(genome_file)
    parsed_regions = [parse_region(r) for r in adata.var.index]

    # 计算GC含量
    gc_contents = []
    for chrom, start, end in parsed_regions:
        try:
            # 关键：0-based (BED) 到 1-based (FASTA) 的转换
            sequence = genome[chrom][start+1: end].seq
            gc_contents.append(GC(sequence))
        except Exception as e:
            print(f"Error with {chrom}:{start}-{end}: {e}")
            gc_contents.append(np.nan)

    # 保存结果
    adata.var['gc_content'] = gc_contents
    
    
def genome_tn5_bias(adata, genome_file):
    genome = Fasta(genome_file)
    parsed_regions = [parse_region(r) for r in adata.var.index]

    RECOMMENDED_TN5_WEIGHTS = {
        'GG': 1.8, 'GC': 1.4, 'CG': 1.2, 'AG': 1.3,
        'GA': 1.2, 'TG': 1.3, 'GT': 1.1, 'CC': 1.1,
        'TC': 1.1, 'CT': 1.0, 'CA': 1.0, 'AC': 1.0,
        'AT': 0.9, 'TA': 1.0, 'TT': 0.9, 'AA': 0.9
        }
    
    def get_tn5_bias_score(sequence):
        """
        获取序列的Tn5偏好性得分
        """
        scores = []
        for i in range(len(sequence) - 1):
            dinuc = sequence[i:i+2]
            scores.append(RECOMMENDED_TN5_WEIGHTS.get(dinuc, 1.0))
    
        return np.mean(scores) if scores else 1.0
    
    bias_scores = []
    for chrom, start, end in parsed_regions:
        # 关键：0-based (BED) 到 1-based (FASTA) 的转换
        sequence = genome[chrom][start+1: end].seq
        bias_scores.append(get_tn5_bias_score(sequence))

    # 保存结果
    adata.var['tn5_bias'] = bias_scores
    
def genome_methylation(adata, methyl_file):
    bw_methyl = pyBigWig.open(methyl_file)

    # 初始化列表
    methyl_means = []

    # 遍历每个区域计算平均信号
    for region in adata.var.index:
        chrom, start, end = parse_region(region)
    
        # 计算甲基化
        try:
            methyl_values = bw_methyl.values(chrom, start, end)
            # 处理可能存在的NaN值
            methyl_mean = np.nanmean(methyl_values)
            methyl_means.append(methyl_mean)
        except:
            methyl_means.append(np.nan)

    # 关闭bigWig文件
    bw_methyl.close()

    # 将结果添加到anndata对象
    adata.var['methylation'] = methyl_means
    
def genome_h3k27ac(adata, h3k27ac_file):
    bw_h3k27ac = pyBigWig.open(h3k27ac_file)

    # 初始化列表
    h3k27ac_means = []

    # 遍历每个区域计算平均信号
    for region in adata.var.index:
        chrom, start, end = parse_region(region)
    
        # 计算乙酰化
        try:
            h3k27ac_values = bw_h3k27ac.values(chrom, start, end)
            h3k27ac_mean = np.nanmean(h3k27ac_values)
            h3k27ac_means.append(h3k27ac_mean)
        except:
            h3k27ac_means.append(np.nan)

    # 关闭bigWig文件
    bw_h3k27ac.close()

    # 将结果添加到anndata对象
    adata.var['h3k27ac'] = h3k27ac_means


def calculate_simple_repeat_content(sequence, min_repeat_length=2, max_repeat_length=6):
    """
    计算简单重复序列含量（如二核苷酸、三核苷酸重复）
    """
    sequence = str(sequence).upper()
    total_length = len(sequence)
    
    repeat_content = {}
    
    for repeat_length in range(min_repeat_length, max_repeat_length + 1):
        repeats = []
        for i in range(0, len(sequence) - repeat_length + 1):
            repeat_unit = sequence[i:i + repeat_length]
            repeats.append(repeat_unit)
        
        # 计算重复单元的频率
        repeat_counter = Counter(repeats)
        
        # 只考虑出现多次的重复单元
        significant_repeats = {k: v for k, v in repeat_counter.items() if v > 1}
        
        repeat_content[f'{repeat_length}mer'] = {
            'total_repeats': sum(significant_repeats.values()),
            'percentage': (sum(significant_repeats.values()) * repeat_length) / total_length * 100,
            'unique_repeats': len(significant_repeats)
        }
    
    return repeat_content

def find_tandem_repeats(sequence, min_repeats=3):
    """
    使用正则表达式检测串联重复
    """
    sequence = str(sequence).upper()
    results = []
    
    # 检测不同长度的重复单元
    for unit_length in range(1, 6):  # 检测1-5bp的重复单元
        pattern = r'(\w{' + str(unit_length) + r'})\1{' + str(min_repeats-1) + r',}'
        
        matches = re.finditer(pattern, sequence)
        for match in matches:
            repeat_unit = match.group(1)
            repeat_count = len(match.group(0)) // unit_length
            start_pos = match.start()
            end_pos = match.end()
            
            results.append({
                'unit': repeat_unit,
                'count': repeat_count,
                'length': len(match.group(0)),
                'start': start_pos,
                'end': end_pos,
                'sequence': match.group(0)
            })
    
    return results

def calculate_tandem_repeat_content(sequence, min_repeats=3):
    """
    计算串联重复序列含量
    """
    tandem_repeats = find_tandem_repeats(sequence, min_repeats)
    total_length = len(sequence)
    
    if not tandem_repeats:
        return 0.0, []
    
    total_repeat_length = sum(repeat['length'] for repeat in tandem_repeats)
    percentage = (total_repeat_length / total_length) * 100
    
    return percentage, tandem_repeats


def calculate_sequence_complexity(sequence, window_size=10):
    """
    计算序列复杂度（低复杂度区域通常富含重复序列）
    """   
    sequence = str(sequence).upper()
    complexities = []
    
    for i in range(0, len(sequence) - window_size + 1):
        window = sequence[i:i + window_size]
        unique_bases = len(set(window))
        complexity = unique_bases / window_size
        complexities.append(complexity)
        
        dinuc = []
        for i in range(len(window) - 1):
            dinuc.append(sequence[i:i+2])
        unique_dinuc = len(set(dinuc))
        complexity = unique_dinuc / window_size
        complexities.append(complexity)
    
    return np.mean(complexities) if complexities else 0
    
def comprehensive_repeat_analysis(sequence, methods=['simple', 'tandem', 'complexity']):
    """
    综合重复序列分析
    """
    results = {}
    sequence = str(sequence).upper()
    
    if 'simple' in methods:
        # 简单重复分析
        simple_repeats = calculate_simple_repeat_content(sequence)
        results['simple_repeats'] = simple_repeats
        results['total_simple_repeat_content'] = sum(
            info['percentage'] for info in simple_repeats.values()
        )
    
    if 'tandem' in methods:
        # 串联重复分析
        tandem_percentage, tandem_repeats = calculate_tandem_repeat_content(sequence)
        results['tandem_repeats'] = tandem_repeats
        results['tandem_repeat_percentage'] = tandem_percentage
    
    if 'complexity' in methods:
        # 序列复杂度分析
        complexity = calculate_sequence_complexity(sequence)
        results['complexity'] = complexity
    
    # 总重复含量估计
    total_repeat_estimate = results.get('total_simple_repeat_content', 0) + \
                           results.get('tandem_repeat_percentage', 0)
    results['total_repeat_estimate'] = total_repeat_estimate
    
    return total_repeat_estimate, complexity

def genome_repeats(adata, genome_file, methods=['simple', 'tandem', 'complexity']):
    genome = Fasta(genome_file)
    parsed_regions = [parse_region(r) for r in adata.var.index]

    # 计算repeat含量
    repeat_contents = [comprehensive_repeat_analysis(genome[chrom][start+1: end].seq, methods=methods) for chrom, start, end in parsed_regions]    
    repeat_contents = pd.DataFrame(repeat_contents, columns=['total_repeat_estimate','sequence_complexity'])
    
    # 保存结果
    adata.var['total_repeat_estimate'] = repeat_contents['total_repeat_estimate'].tolist()
    adata.var['sequence_complexity'] = repeat_contents['sequence_complexity'].tolist()
    
    
def genome_complexity(adata, genome_file, window_size=10):
    genome = Fasta(genome_file)
    parsed_regions = [parse_region(r) for r in adata.var.index]

    # 计算repeat含量
    complexity = [calculate_sequence_complexity(genome[chrom][start+1: end].seq, window_size=window_size) for chrom, start, end in parsed_regions]    
    
    # 保存结果
    adata.var['complexity'] = complexity


def calculate_snr(accessibility_matrix):
    """计算信噪比"""
    signal = np.percentile(accessibility_matrix, 75)
    noise = np.percentile(accessibility_matrix, 25)
    return signal / (noise + 1e-6)