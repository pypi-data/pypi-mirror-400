"""
内容包含: 
1.基础使用
2.GEO数据获取
3.SRA数据获取
4.数据搜索功能
5.批量处理
6.缓存管理
7.高级功能
8.故障排除

多数据源支持：GEO, TCGA, SRA, ArrayExpress, ENCODE, 单细胞数据等
多种数据格式：表达矩阵、临床数据、突变数据、FASTQ文件等
智能缓存：自动缓存下载的数据，避免重复下载
并行下载：支持多线程并行下载大型文件
数据搜索：内置数据集搜索功能
批量处理：支持批量下载多个数据集
配置管理：支持YAML/JSON配置文件
历史记录：记录所有下载操作
向后兼容：保持与现有GEO函数的兼容性
错误处理：完善的错误处理和日志记录


# 1. 简单使用（自动优先fastq-dump）
fetcher = BioDataFetcher(dir_save="./my_cache", prefer_fastq_dump=True)
result = fetcher.fetch_data("SRR1635435", data_type='sra', data_format='fastq')

# 2. 使用配置文件
fetcher = BioDataFetcher(dir_save="./my_cache", config_file="./config.yaml")

# 3. 强制指定方法
result = fetcher.fetch_data(
    dataset_ids="SRR1635435",
    data_type='sra',
    data_format='fastq',
    download_method='fastq_dump'  # 或 'ftp'
)

# 4. 传递fastq-dump参数
result = fetcher.fetch_data(
    dataset_ids="SRR1635435",
    data_type='sra',
    data_format='fastq',
    split_files=True,
    gzip_output=True,
    threads=4
)

"""

import os
import re
import pandas as pd
import numpy as np
from typing import Union, Dict, List, Optional, Any, Tuple, Callable
import logging
from pathlib import Path
import warnings
from datetime import datetime
import json
import yaml
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import pickle
from tqdm import tqdm
import time
import requests 
from concurrent.futures import ThreadPoolExecutor, as_completed


logger = logging.getLogger(__name__)

# 导入现有的GEO函数
try:
    from . import bio as geo_utils
    GEO_UTILS_AVAILABLE = True
except ImportError:
    GEO_UTILS_AVAILABLE = False
    warnings.warn("GEO utils not available. Make sure bio.py is in the same directory")

# 可能需要的额外库（可选择安装）
try:
    import GEOparse
    GEOPARSE_AVAILABLE = True
except ImportError:
    GEOPARSE_AVAILABLE = False
    warnings.warn("GEOparse not available. Install with: pip install GEOparse")

try:
    from pysradb import SRAweb
    SRADB_AVAILABLE = True
except ImportError:
    SRADB_AVAILABLE = False
    warnings.warn("pysradb not available. Install with: pip install pysradb")

try:
    import gseapy as gp
    GSEAPY_AVAILABLE = True
except ImportError:
    GSEAPY_AVAILABLE = False

try:
    import mygene
    MYGENE_AVAILABLE = True
except ImportError:
    MYGENE_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    warnings.warn("requests not available. Install with: pip install requests")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据类型枚举
class DataSource(Enum):
    GEO = "geo"           # Gene Expression Omnibus
    SRA = "sra"           # Sequence Read Archive
    TCGA = "tcga"         # The Cancer Genome Atlas
    ENCODE = "encode"     # ENCODE Project
    ARRAY_EXPRESS = "arrayexpress"  # ArrayExpress
    DDBJ = "ddbj"         # DNA Data Bank of Japan
    EGA = "ega"           # European Genome-phenome Archive
    SINGLE_CELL = "single_cell"  # 单细胞数据
    PROTEIN_ATLAS = "protein_atlas"  # Human Protein Atlas
    STRINGDB = "stringdb"  # STRING数据库
    KEGG = "kegg"         # KEGG通路
    REACTOME = "reactome"  # Reactome通路
    CUSTOM = "custom"     # 自定义数据源
    
    @classmethod
    def from_accession(cls, accession: str) -> 'DataSource':
        """根据accession自动推断数据源"""
        accession = accession.upper()
        
        # GEO数据集
        if re.match(r'^GSE\d+$', accession) or re.match(r'^GDS\d+$', accession):
            return cls.GEO
        
        # SRA数据集
        elif re.match(r'^(SRR|ERR|DRR)\d+$', accession):
            return cls.SRA
        
        # TCGA项目
        elif re.match(r'^TCGA-[A-Z0-9]+$', accession) or accession.startswith('TCGA_'):
            return cls.TCGA
        
        # ENCODE数据集
        elif re.match(r'^ENC[SR]\d+$', accession):
            return cls.ENCODE
        
        # ArrayExpress
        elif re.match(r'^E-[A-Z]{4}-\d+$', accession):
            return cls.ARRAY_EXPRESS
        
        # DDBJ
        elif re.match(r'^(DRA|DRS|DRX|DRZ)\d+$', accession):
            return cls.DDBJ
        
        # 单细胞数据集（常见格式）
        elif re.match(r'^SC\d+$', accession) or 'SC' in accession:
            return cls.SINGLE_CELL
        
        # 默认返回GEO
        else:
            return cls.GEO

class DataFormat(Enum):
    EXPRESSION = "expression"    # 表达矩阵
    COUNTS = "counts"            # 原始计数
    FASTQ = "fastq"              # FASTQ文件
    BAM = "bam"                  # BAM文件
    METADATA = "metadata"        # 元数据
    CLINICAL = "clinical"        # 临床数据
    MUTATIONS = "mutations"      # 突变数据
    PROBE = "probe"              # 探针信息
    ANNOTATION = "annotation"    # 注释信息
    NETWORK = "network"          # 网络数据
    PATHWAY = "pathway"          # 通路数据
    
    @classmethod
    def infer_format(cls, data_type: DataSource, **kwargs) -> 'DataFormat':
        """根据数据源和其他参数推断数据格式"""
        platform = kwargs.get('platform', '').lower()
        data_format = kwargs.get('data_format', '').lower()
        
        # 如果有明确指定的格式，使用它
        if data_format:
            for fmt in cls:
                if fmt.value == data_format:
                    return fmt
        
        # 根据数据源推断
        if data_type == DataSource.GEO:
            return cls.EXPRESSION
        elif data_type == DataSource.SRA:
            return cls.FASTQ if kwargs.get('download_fastq', False) else cls.METADATA
        elif data_type == DataSource.TCGA:
            if platform == 'clinical':
                return cls.CLINICAL
            elif platform == 'mutations':
                return cls.MUTATIONS
            else:
                return cls.EXPRESSION
        elif data_type == DataSource.ENCODE:
            return cls.BAM if 'chip' in platform else cls.EXPRESSION
        else:
            return cls.METADATA
class FastqDumpDownloader:
    """
    使用fastq-dump下载SRA数据的下载器
    更可靠，支持更多功能
    """
    
    def __init__(self, cache_dir: str = "./sra_fastqdump", use_prefetch: bool = True):
        """
        Parameters:
        -----------
        cache_dir : str
            缓存目录
        use_prefetch : bool
            是否使用prefetch先下载.sra文件（推荐）
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.use_prefetch = use_prefetch
        
        # 查找工具
        self.fastq_dump_path = shutil.which("fastq-dump") or shutil.which("fastq-dump.exe")
        self.prefetch_path = shutil.which("prefetch") or shutil.which("prefetch.exe")
        self.fasterq_dump_path = shutil.which("fasterq-dump") or shutil.which("fasterq-dump.exe")
        
        print(f"工具状态:")
        print(f"  fastq-dump: {'✅ 可用' if self.fastq_dump_path else '❌ 未找到'}")
        print(f"  prefetch: {'✅ 可用' if self.prefetch_path else '❌ 未找到'}")
        print(f"  fasterq-dump: {'✅ 可用' if self.fasterq_dump_path else '❌ 未找到'}")
    
    def download_with_fastq_dump(self,
                               accession: str,
                               output_dir: Optional[Path] = None,
                               split_files: bool = True,
                               gzip_output: bool = True,
                               max_retries: int = 3) -> Dict[str, Any]:
        """
        使用fastq-dump下载数据
        
        Parameters:
        -----------
        accession : str
            SRA accession (SRR, ERR, DRR)
        output_dir : Path
            输出目录
        split_files : bool
            是否拆分文件（paired-end数据拆分为 _1.fastq 和 _2.fastq）
        gzip_output : bool
            是否gzip压缩输出
        max_retries : int
            最大重试次数
        
        Returns:
        --------
        Dict: 下载结果
        """
        import time
        
        if output_dir is None:
            output_dir = self.cache_dir / accession
        else:
            output_dir = Path(output_dir) / accession
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.fastq_dump_path:
            return {
                'accession': accession,
                'success': False,
                'error': 'fastq-dump not found. Please install SRA Toolkit.',
                'step': 'tool_check'
            }
        
        print(f"使用fastq-dump下载: {accession}")
        print(f"输出目录: {output_dir}")
        print(f"拆分文件: {split_files}")
        print(f"gzip压缩: {gzip_output}")
        print("-" * 50)
        
        results = {}
        
        # 方法1：使用prefetch + fastq-dump（推荐）
        if self.use_prefetch and self.prefetch_path:
            print("方法1: prefetch + fastq-dump")
            result = self._download_with_prefetch(
                accession=accession,
                output_dir=output_dir,
                split_files=split_files,
                gzip_output=gzip_output,
                max_retries=max_retries
            )
            results['prefetch_method'] = result
            
            if result.get('success', False):
                print("✅ prefetch方法成功")
                return self._format_result(accession, output_dir, result)
        
        # 方法2：直接使用fastq-dump
        print("\n方法2: 直接使用fastq-dump")
        result = self._download_direct(
            accession=accession,
            output_dir=output_dir,
            split_files=split_files,
            gzip_output=gzip_output,
            max_retries=max_retries
        )
        results['direct_method'] = result
        
        if result.get('success', False):
            print("✅ 直接方法成功")
            return self._format_result(accession, output_dir, result)
        
        # 方法3：使用fasterq-dump（如果可用）
        if self.fasterq_dump_path:
            print("\n方法3: 使用fasterq-dump（更快）")
            result = self._download_with_fasterq_dump(
                accession=accession,
                output_dir=output_dir,
                split_files=split_files,
                gzip_output=gzip_output,
                max_retries=max_retries
            )
            results['fasterq_method'] = result
            
            if result.get('success', False):
                print("✅ fasterq-dump方法成功")
                return self._format_result(accession, output_dir, result)
        
        # 所有方法都失败
        print("❌ 所有方法都失败")
        return {
            'accession': accession,
            'success': False,
            'error': 'All download methods failed',
            'results': results,
            'output_dir': str(output_dir)
        }
    
    def _download_with_prefetch(self, accession, output_dir, split_files, gzip_output, max_retries):
        """使用prefetch下载.sra文件，然后用fastq-dump转换"""
        import time
        
        sra_dir = output_dir / ".sra_cache"
        sra_dir.mkdir(exist_ok=True)
        
        # 步骤1: 使用prefetch下载.sra文件
        print("  步骤1: 使用prefetch下载.sra文件...")
        
        prefetch_cmd = [
            self.prefetch_path,
            accession,
            "-O", str(sra_dir),
            "--progress"  # 显示进度
        ]
        
        try:
            print(f"  运行: {' '.join(prefetch_cmd)}")
            result = subprocess.run(
                prefetch_cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10分钟超时
                check=True
            )
            
            print(f"  prefetch完成: {result.stdout[-200:] if result.stdout else '无输出'}")
            
            # 查找下载的.sra文件
            sra_files = list(sra_dir.glob(f"**/{accession}.sra"))
            if not sra_files:
                sra_files = list(sra_dir.glob(f"**/*.sra"))
            
            if not sra_files:
                return {'success': False, 'error': 'No .sra file found after prefetch'}
            
            sra_file = sra_files[0]
            print(f"  找到.sra文件: {sra_file} ({sra_file.stat().st_size/1024/1024:.1f} MB)")
            
            # 步骤2: 使用fastq-dump转换
            return self._run_fastq_dump(
                input_file=str(sra_file),
                output_dir=output_dir,
                split_files=split_files,
                gzip_output=gzip_output
            )
            
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'prefetch timed out after 10 minutes'}
        except subprocess.CalledProcessError as e:
            return {'success': False, 'error': f'prefetch failed: {e.stderr[:200]}'}
        except Exception as e:
            return {'success': False, 'error': f'prefetch error: {type(e).__name__}: {e}'}
    
    def _download_direct(self, accession, output_dir, split_files, gzip_output, max_retries):
        """直接使用fastq-dump下载（不先下载.sra文件）"""
        print("  直接下载并转换...")
        
        # 构建fastq-dump命令
        cmd = self._build_fastq_dump_command(
            accession=accession,
            output_dir=output_dir,
            split_files=split_files,
            gzip_output=gzip_output
        )
        
        try:
            print(f"  运行: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=900,  # 15分钟超时（可能较长）
                check=True
            )
            
            print(f"  fastq-dump输出: {result.stdout[-500:] if result.stdout else '无输出'}")
            
            # 检查生成的文件
            return self._check_output_files(output_dir, accession, split_files, gzip_output)
            
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'fastq-dump timed out after 15 minutes'}
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr[:500] if e.stderr else str(e)
            return {'success': False, 'error': f'fastq-dump failed: {error_msg}'}
        except Exception as e:
            return {'success': False, 'error': f'fastq-dump error: {type(e).__name__}: {e}'}
    
    def _download_with_fasterq_dump(self, accession, output_dir, split_files, gzip_output, max_retries):
        """使用fasterq-dump（更快版本）"""
        print("  使用fasterq-dump...")
        
        # 构建fasterq-dump命令
        cmd = [
            self.fasterq_dump_path,
            accession,
            "-O", str(output_dir),
            "-e", "4",  # 使用4个线程
            "-p"  # 显示进度
        ]
        
        if split_files:
            cmd.append("--split-files")
        
        try:
            print(f"  运行: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10分钟超时
                check=True
            )
            
            print(f"  fasterq-dump输出: {result.stdout[-500:] if result.stdout else '无输出'}")
            
            # 如果需要gzip，使用并行gzip
            if gzip_output:
                self._gzip_files(output_dir)
            
            return self._check_output_files(output_dir, accession, split_files, gzip_output)
            
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'fasterq-dump timed out'}
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr[:500] if e.stderr else str(e)
            return {'success': False, 'error': f'fasterq-dump failed: {error_msg}'}
        except Exception as e:
            return {'success': False, 'error': f'fasterq-dump error: {type(e).__name__}: {e}'}
    
    def _build_fastq_dump_command(self, accession, output_dir, split_files, gzip_output):
        """构建fastq-dump命令"""
        cmd = [
            self.fastq_dump_path,
            accession,
            "--outdir", str(output_dir),
            "--skip-technical",  # 跳过技术读取
            "--readids",  # 在读取ID中包含原始名称
            "--dumpbase",  # 以碱基形式格式化序列
            "--clip",  # 移除适配器和质量修剪
        ]
        
        if split_files:
            cmd.append("--split-files")
        
        if gzip_output:
            cmd.append("--gzip")
        
        # 添加其他有用选项
        cmd.extend([
            "--read-filter", "pass",  # 只保留通过的读取
            "--origfmt"  # 保持原始格式
        ])
        
        return cmd
    
    def _run_fastq_dump(self, input_file, output_dir, split_files, gzip_output):
        """运行fastq-dump转换.sra文件"""
        cmd = [
            self.fastq_dump_path,
            input_file,
            "--outdir", str(output_dir),
            "--skip-technical",
            "--readids",
            "--dumpbase",
            "--clip",
        ]
        
        if split_files:
            cmd.append("--split-files")
        
        if gzip_output:
            cmd.append("--gzip")
        
        try:
            print(f"  运行fastq-dump: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时（.sra文件已本地存在）
                check=True
            )
            
            print(f"  fastq-dump完成")
            return self._check_output_files(output_dir, Path(input_file).stem, split_files, gzip_output)
            
        except subprocess.CalledProcessError as e:
            return {'success': False, 'error': f'fastq-dump conversion failed: {e.stderr[:200]}'}
        except Exception as e:
            return {'success': False, 'error': f'fastq-dump error: {type(e).__name__}: {e}'}
    
    def _gzip_files(self, output_dir):
        """并行gzip文件（如果fastq-dump没有自动gzip）"""
        import gzip
        import shutil
        from concurrent.futures import ThreadPoolExecutor
        
        fastq_files = list(output_dir.glob("*.fastq"))
        
        if not fastq_files:
            return
        
        print(f"  压缩 {len(fastq_files)} 个fastq文件...")
        
        def compress_file(fastq_path):
            gzip_path = fastq_path.with_suffix('.fastq.gz')
            
            try:
                with open(fastq_path, 'rb') as f_in:
                    with gzip.open(gzip_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # 删除原始文件
                fastq_path.unlink()
                return True
            except Exception as e:
                print(f"    压缩失败 {fastq_path.name}: {e}")
                return False
        
        # 并行压缩
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(compress_file, fastq_files))
        
        success_count = sum(results)
        print(f"  压缩完成: {success_count}/{len(fastq_files)} 成功")
    
    def _check_output_files(self, output_dir, accession, split_files, gzip_output):
        """检查输出文件"""
        # 查找生成的文件
        patterns = []
        if gzip_output:
            patterns.extend([f"{accession}*.fastq.gz", f"{accession}*.fq.gz"])
        else:
            patterns.extend([f"{accession}*.fastq", f"{accession}*.fq"])
        
        files = []
        for pattern in patterns:
            files.extend(output_dir.glob(pattern))
        
        files = [str(f) for f in files if f.exists() and f.stat().st_size > 0]
        
        if files:
            total_size = sum(Path(f).stat().st_size for f in files)
            return {
                'success': True,
                'files': files,
                'file_count': len(files),
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024)
            }
        else:
            return {'success': False, 'error': 'No output files found'}
    
    def _format_result(self, accession, output_dir, result):
        """格式化结果"""
        return {
            'accession': accession,
            'success': True,
            'files': result.get('files', []),
            'file_count': result.get('file_count', 0),
            'total_size_mb': result.get('total_size_mb', 0),
            'output_dir': str(output_dir),
            'method': 'fastq-dump'
        }

# 测试使用
def test_fastq_dump_downloader():
    """测试fastq-dump下载器"""
    print("测试fastq-dump下载器")
    print("=" * 60)
    
    downloader = FastqDumpDownloader(cache_dir="./fastqdump_test")
    
    # 测试小文件
    result = downloader.download_with_fastq_dump(
        accession="SRR390728",  # 小文件，约1MB
        output_dir="./test_output",
        split_files=True,
        gzip_output=True,
        max_retries=2
    )
    
    print(f"\n结果:")
    print(f"  成功: {result['success']}")
    print(f"  文件数: {result.get('file_count', 0)}")
    print(f"  总大小: {result.get('total_size_mb', 0):.2f} MB")
    
    if result['success'] and result.get('files'):
        print(f"  文件列表:")
        for filepath in result['files']:
            size_mb = Path(filepath).stat().st_size / (1024 * 1024)
            print(f"    - {Path(filepath).name} ({size_mb:.2f} MB)")
    
    return result

# test_fastq_dump_downloader()

class SRADownloader:
    """
    独立的SRA数据下载器，不依赖pysradb
    直接使用ENA和NCBI API
    """
    
    def __init__(self, cache_dir: str = "./sra_data", max_workers: int = 4):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_metadata(self, accession: str) -> Dict[str, Any]:
        """
        从ENA获取SRA元数据
        参数可以是：SRR/ERR/DRR运行号，SRS样本号，SRX实验号
        """
        # 尝试不同API端点
        endpoints = [
            self._get_ena_metadata,
            self._get_ncbi_metadata,
        ]
        
        for endpoint in endpoints:
            try:
                metadata = endpoint(accession)
                if metadata:
                    return metadata
            except Exception as e:
                logger.debug(f"{endpoint.__name__} failed: {e}")
        
        return {'error': f'无法获取 {accession} 的元数据'}
    
    def _get_ena_metadata(self, accession: str) -> Dict[str, Any]:
        """使用ENA API获取元数据"""
        base_url = "https://www.ebi.ac.uk/ena/portal/api/search"
        
        # 根据accession类型确定结果类型
        if accession.startswith(('SRR', 'ERR', 'DRR')):
            result_type = 'read_run'
        elif accession.startswith(('SRS', 'ERS', 'DRS')):
            result_type = 'sample'
        elif accession.startswith(('SRX', 'ERX', 'DRX')):
            result_type = 'experiment'
        else:
            result_type = 'read_run'  # 默认
        
        fields = [
            'accession', 'secondary_sample_accession', 'run_accession',
            'experiment_accession', 'study_accession', 'submission_accession',
            'instrument_platform', 'instrument_model', 'library_layout',
            'library_selection', 'library_source', 'library_strategy',
            'read_count', 'base_count', 'sample_alias', 'sample_title',
            'experiment_title', 'study_title', 'fastq_ftp', 'submitted_ftp',
            'sra_ftp', 'first_public', 'last_updated'
        ]
        
        params = {
            'result': result_type,
            'query': f'accession="{accession}" OR run_accession="{accession}"',
            'fields': ','.join(fields),
            'format': 'json',
            'limit': 1
        }
        
        try:
            response = self.session.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0:
                return data[0]
        except Exception as e:
            logger.error(f"ENA metadata API error: {e}")
        
        return {}
    
    def _get_ncbi_metadata(self, accession: str) -> Dict[str, Any]:
        """使用NCBI API获取元数据（备用）"""
        # Entrez API
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        
        # 搜索
        search_params = {
            'db': 'sra',
            'term': f'{accession}[Accession]',
            'retmax': 1,
            'retmode': 'json'
        }
        
        try:
            search_response = self.session.get(base_url + "esearch.fcgi", params=search_params)
            search_data = search_response.json()
            
            ids = search_data.get('esearchresult', {}).get('idlist', [])
            if not ids:
                return {}
            
            # 获取摘要
            summary_params = {
                'db': 'sra',
                'id': ids[0],
                'retmode': 'json'
            }
            
            summary_response = self.session.get(base_url + "esummary.fcgi", params=summary_params)
            summary_data = summary_response.json()
            
            result = summary_data.get('result', {}).get(ids[0], {})
            
            # 转换为标准格式
            metadata = {
                'accession': accession,
                'title': result.get('title', ''),
                'organism': result.get('organism', ''),
                'platform': result.get('platform', ''),
                'library_strategy': result.get('librarystrategy', ''),
                'library_source': result.get('librarysource', ''),
                'library_selection': result.get('libraryselection', ''),
                'instrument': result.get('instrument', ''),
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"NCBI metadata API error: {e}")
            return {}
    
    def get_fastq_links(self, accession: str) -> List[str]:
        """获取FASTQ下载链接"""
        metadata = self.get_metadata(accession)
        
        links = []
        
        # 从元数据中提取FASTQ链接
        for field in ['fastq_ftp', 'submitted_ftp', 'sra_ftp']:
            if field in metadata and metadata[field]:
                ftp_links = str(metadata[field]).split(';')
                for link in ftp_links:
                    link = link.strip()
                    if link:
                        if not link.startswith(('http://', 'https://', 'ftp://')):
                            link = f"ftp://{link}"
                        links.append(link)
        
        # 如果没有找到链接，生成默认链接
        if not links:
            links = self._generate_default_links(accession)
        
        return list(set(links))  # 去重
    
    def _generate_default_links(self, accession: str) -> List[str]:
        """生成默认的ENA FTP链接"""
        links = []
        
        # ENA标准FTP路径模式
        # ftp://ftp.sra.ebi.ac.uk/vol1/fastq/XXXnnn/XXXnnnXXX/
        
        if accession.startswith(('SRR', 'ERR', 'DRR')):
            # 提取前6位
            prefix = accession[:6]
            # 尝试不同路径模式
            patterns = [
                f"ftp://ftp.sra.ebi.ac.uk/vol1/fastq/{prefix}/{accession}/{accession}.fastq.gz",
                f"ftp://ftp.sra.ebi.ac.uk/vol1/fastq/{prefix}/{accession}/{accession}_1.fastq.gz",
                f"ftp://ftp.sra.ebi.ac.uk/vol1/fastq/{prefix}/{accession}/{accession}_2.fastq.gz",
                f"ftp://ftp.sra.ebi.ac.uk/vol1/fastq/{prefix}/00{accession[-1]}/{accession}/{accession}.fastq.gz",
            ]
            links.extend(patterns)
        
        return links
    
    def download_fastq(self, 
                      accession: str, 
                      output_dir: Optional[Path] = None,
                      max_files: int = 10) -> Dict[str, Any]:
        """下载FASTQ文件"""
        if output_dir is None:
            output_dir = self.cache_dir / accession
        else:
            output_dir = Path(output_dir) / accession
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取下载链接
        links = self.get_fastq_links(accession)
        
        if not links:
            return {
                'accession': accession,
                'success': False,
                'error': 'No download links found',
                'files': []
            }
        
        logger.info(f"Found {len(links)} download links for {accession}")
        
        # 限制下载文件数量
        if len(links) > max_files:
            logger.info(f"Limiting to {max_files} files")
            links = links[:max_files]
        
        # 并行下载
        downloaded_files = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交下载任务
            future_to_url = {
                executor.submit(self._download_file, url, output_dir): url
                for url in links
            }
            
            # 使用进度条
            for future in tqdm(as_completed(future_to_url), 
                             total=len(links),
                             desc=f"Downloading {accession}"):
                url = future_to_url[future]
                try:
                    result = future.result(timeout=300)
                    if result['success']:
                        downloaded_files.append(result['filepath'])
                    else:
                        logger.error(f"Failed to download {url}: {result.get('error')}")
                except Exception as e:
                    logger.error(f"Download task failed for {url}: {e}")
        
        return {
            'accession': accession,
            'success': len(downloaded_files) > 0,
            'files': downloaded_files,
            'output_dir': str(output_dir),
            'metadata': self.get_metadata(accession)
        }
    
    def _download_file(self, url: str, output_dir: Path) -> Dict[str, Any]:
        """下载单个文件"""
        filename = self._extract_filename(url)
        filepath = output_dir / filename
        
        # 检查文件是否已存在
        if filepath.exists():
            file_size = filepath.stat().st_size
            if file_size > 1024:  # 大于1KB认为文件完整
                logger.debug(f"File already exists: {filepath}")
                return {
                    'success': True,
                    'filepath': str(filepath),
                    'size': file_size,
                    'cached': True
                }
        
        try:
            # 根据URL协议选择下载方法
            if url.startswith('ftp://'):
                result = self._download_ftp(url, filepath)
            elif url.startswith('http'):
                result = self._download_http(url, filepath)
            else:
                result = {'success': False, 'error': f'Unsupported protocol: {url}'}
            
            if result['success']:
                logger.info(f"Downloaded: {filename}")
            
            return result
            
        except Exception as e:
            logger.error(f"Download failed for {url}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_filename(self, url: str) -> str:
        """从URL提取文件名"""
        # 移除查询参数
        if '?' in url:
            url = url.split('?')[0]
        
        # 获取最后一部分作为文件名
        filename = url.split('/')[-1]
        
        # 如果文件名为空，使用默认名
        if not filename or filename.endswith('/'):
            return "unknown_file.fastq.gz"
        
        return filename
    
    def _download_http(self, url: str, filepath: Path) -> Dict[str, Any]:
        """下载HTTP/HTTPS文件"""
        try:
            response = self.session.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
            
            actual_size = filepath.stat().st_size
            
            return {
                'success': True,
                'filepath': str(filepath),
                'size': actual_size,
                'expected_size': total_size
            }
            
        except Exception as e:
            return {'success': False, 'error': f'HTTP download failed: {e}'}
    
    def _download_ftp(self, url: str, filepath: Path) -> Dict[str, Any]:
        """下载FTP文件"""
        import ftplib
        from urllib.parse import urlparse
        
        try:
            # 解析FTP URL
            parsed = urlparse(url)
            hostname = parsed.hostname
            path = parsed.path
            
            if not hostname:
                return {'success': False, 'error': 'Invalid FTP URL'}
            
            # 连接FTP服务器
            ftp = ftplib.FTP(hostname, timeout=30)
            ftp.login()  # 匿名登录
            
            # 提取目录和文件名
            if '/' in path:
                dir_path = '/'.join(path.split('/')[:-1]) or '/'
                filename = path.split('/')[-1]
            else:
                dir_path = '/'
                filename = path
            
            # 切换到目录
            if dir_path != '/':
                try:
                    ftp.cwd(dir_path)
                except:
                    # 如果目录不存在，尝试创建路径
                    pass
            
            # 获取文件大小
            try:
                ftp.sendcmd("TYPE I")  # 二进制模式
                file_size = ftp.size(filename)
            except:
                file_size = 0
            
            # 下载文件
            with open(filepath, 'wb') as f:
                ftp.retrbinary(f"RETR {filename}", f.write)
            
            ftp.quit()
            
            actual_size = filepath.stat().st_size
            
            return {
                'success': True,
                'filepath': str(filepath),
                'size': actual_size,
                'expected_size': file_size
            }
            
        except Exception as e:
            return {'success': False, 'error': f'FTP download failed: {e}'}
    
    def batch_download(self, 
                      accessions: List[str], 
                      output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """批量下载多个accession"""
        results = {}
        
        for accession in tqdm(accessions, desc="Processing accessions"):
            try:
                result = self.download_fastq(accession, output_dir)
                results[accession] = result
            except Exception as e:
                results[accession] = {
                    'accession': accession,
                    'success': False,
                    'error': str(e)
                }
        
        # 统计
        total = len(accessions)
        successful = sum(1 for r in results.values() if r.get('success', False))
        
        return {
            'total': total,
            'successful': successful,
            'failed': total - successful,
            'results': results
        }
@dataclass
class DatasetConfig:
    """数据集配置"""
    dataset_id: str
    data_type: DataSource
    data_format: DataFormat
    organism: Optional[str] = None
    platform: Optional[str] = None
    samples: Optional[List[str]] = None
    force_download: bool = False
    custom_params: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_accession(cls, accession: str, **kwargs) -> 'DatasetConfig':
        """从accession创建配置"""
        data_type = DataSource.from_accession(accession)
        data_format = DataFormat.infer_format(data_type, **kwargs)
        
        return cls(
            dataset_id=accession,
            data_type=data_type,
            data_format=data_format,
            organism=kwargs.get('organism'),
            platform=kwargs.get('platform'),
            samples=kwargs.get('samples'),
            force_download=kwargs.get('force_download', False),
            custom_params={k: v for k, v in kwargs.items() 
                         if k not in ['dataset_id', 'organism', 'platform', 
                                    'samples', 'force_download']}
        )

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = cache_dir / "cache_metadata.json"
        self._load_metadata()
    
    def _load_metadata(self):
        """加载缓存元数据"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
    
    def _save_metadata(self):
        """保存缓存元数据"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def get_cache_key(self, config: DatasetConfig) -> str:
        """生成缓存键"""
        key_parts = [
            config.dataset_id,
            config.data_type.value,
            config.data_format.value,
            config.organism or 'any',
            config.platform or 'any',
            str(sorted(config.samples)) if config.samples else 'all'
        ]
        key_string = '|'.join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_cache_path(self, config: DatasetConfig) -> Path:
        """获取缓存路径"""
        cache_key = self.get_cache_key(config)
        cache_dir = self.cache_dir / config.data_type.value
        cache_dir.mkdir(exist_ok=True)
        return cache_dir / f"{cache_key}.pkl"
    
    def exists(self, config: DatasetConfig) -> bool:
        """检查缓存是否存在"""
        cache_path = self.get_cache_path(config)
        return cache_path.exists()
    
    def load(self, config: DatasetConfig) -> Optional[Any]:
        """从缓存加载数据"""
        cache_path = self.get_cache_path(config)
        
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
                
                # 更新访问时间
                cache_key = self.get_cache_key(config)
                self.metadata[cache_key] = {
                    'last_accessed': datetime.now().isoformat(),
                    'dataset_id': config.dataset_id,
                    'data_type': config.data_type.value,
                    'data_format': config.data_format.value
                }
                self._save_metadata()
                
                logger.info(f"Loaded from cache: {cache_path}")
                return data
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        
        return None
    
    def save(self, config: DatasetConfig, data: Any):
        """保存数据到缓存"""
        cache_path = self.get_cache_path(config)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # 更新元数据
            cache_key = self.get_cache_key(config)
            self.metadata[cache_key] = {
                'created': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'dataset_id': config.dataset_id,
                'data_type': config.data_type.value,
                'data_format': config.data_format.value,
                'size': cache_path.stat().st_size if cache_path.exists() else 0
            }
            self._save_metadata()
            
            logger.info(f"Saved to cache: {cache_path}")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def clear_cache(self, data_type: Optional[str] = None, older_than_days: Optional[int] = None):
        """清理缓存"""
        cache_files = list(self.cache_dir.rglob("*.pkl"))
        
        for cache_file in cache_files:
            try:
                if data_type and data_type not in str(cache_file):
                    continue
                
                if older_than_days:
                    file_age = datetime.now().timestamp() - cache_file.stat().st_mtime
                    if file_age < older_than_days * 86400:
                        continue
                
                cache_file.unlink()
                logger.info(f"Removed cache: {cache_file}")
            except Exception as e:
                logger.error(f"Failed to remove cache {cache_file}: {e}")
        
        self._load_metadata()  # 重新加载元数据

class BioDataFetcher:
    """
    生物信息学数据获取器终极版
    支持多数据源、自动类型推断、智能缓存和并行下载
    """

    def __init__(self, dir_save: str = "./bio_data_cache", 
                config_file: Optional[str] = None,
                auto_infer: bool = True,
                prefer_fastq_dump: bool = True):
        """
        初始化数据获取器
        
        Parameters:
        -----------
        dir_save : str
            数据缓存目录
        config_file : str
            配置文件路径（YAML或JSON格式）
        auto_infer : bool
            是否启用自动类型推断
        prefer_fastq_dump : bool
            是否优先使用fastq-dump下载SRA数据
        """
        self.dir_save = Path(dir_save)
        self.auto_infer = auto_infer
        self.prefer_fastq_dump = prefer_fastq_dump
        # 初始化缓存管理器
        self.cache = CacheManager(self.dir_save)
        
        # 加载配置
        self.config = self._load_config(config_file)
        
        # 数据源API客户端
        self.sra_client = None
        self.mygene_client = None
        self._init_clients()
        # 检查fastq-dump是否可用
        self.fastq_dump_available = self._check_fastq_dump_available()
    
        # 数据源处理器映射 - 使用字符串键确保一致性
        self.data_processors = {
            'geo': self._process_geo,
            'sra': self._process_sra,
            'tcga': self._process_tcga,
            'encode': self._process_encode,
            'arrayexpress': self._process_array_express,
            'single_cell': self._process_single_cell,
            'custom': self._process_custom,
            # 同时支持枚举键的别名
            DataSource.GEO: self._process_geo,
            DataSource.SRA: self._process_sra,
            DataSource.TCGA: self._process_tcga,
            DataSource.ENCODE: self._process_encode,
            DataSource.ARRAY_EXPRESS: self._process_array_express,
            DataSource.SINGLE_CELL: self._process_single_cell,
            DataSource.CUSTOM: self._process_custom,
        }
        
        # 注册数据库API信息
        self.database_apis = {
            'ncbi': {
                'base_url': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/',
                'formats': ['xml', 'json'],
                'rate_limit': 3
            },
            'ena': {
                'base_url': 'https://www.ebi.ac.uk/ena/portal/api/',
                'formats': ['json'],
                'rate_limit': 10
            },
            'gdc': {
                'base_url': 'https://api.gdc.cancer.gov/',
                'formats': ['json'],
                'rate_limit': 5
            },
            'encode': {
                'base_url': 'https://www.encodeproject.org/',
                'formats': ['json'],
                'rate_limit': 5
            }
        }
        
        logger.info(f"BioDataFetcher initialized with cache dir: {self.dir_save}")
        if self.fastq_dump_available and self.prefer_fastq_dump:
            logger.info("fastq-dump available, will use it for SRA downloads")
    def _check_fastq_dump_available(self) -> bool:
        """检查fastq-dump是否可用"""
        import shutil
        
        # 检查主要工具
        tools_to_check = ['fastq-dump', 'prefetch']
        available_tools = []
        
        for tool in tools_to_check:
            path = shutil.which(tool)
            if path:
                available_tools.append((tool, path))
                logger.debug(f"{tool} found: {path}")
            else:
                logger.debug(f"{tool} not found in PATH")
        
        if len(available_tools) >= 1:  # 至少需要fastq-dump
            logger.info(f"fastq-dump tools available: {[t[0] for t in available_tools]}")
            return True
        else:
            install_fastq_dump_helper()
            logger.warning("fastq-dump not available. SRA downloads may use FTP fallback.")
            return False
    
    def _load_config(self, config_file: Optional[str]) -> Dict:
        """加载配置文件"""
        default_config = {
            'max_retries': 3,
            'timeout': 30,
            'batch_size': 10,
            'prefer_cached': True,
            'download_fastq': False,
            'parallel_downloads': 4,
            'ncbi_api_key': None,
            'ensembl_api_key': None,
            'max_cache_size_gb': 10,
            'auto_normalize': True,
            'gene_id_conversion': True,
            'quality_control': True,
            'prefer_fastq_dump': True,  # 是否优先使用fastq-dump
            'fastq_dump_split_files': True,  # 是否拆分文件
            'fastq_dump_gzip_output': True,  # 是否gzip压缩
            'fastq_dump_use_prefetch': True,  # 是否使用prefetch
            'fastq_dump_threads': 4,  # 线程数
            'fastq_dump_max_retries': 2,  # 最大重试次数
        }
        
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                        user_config = yaml.safe_load(f)
                    elif config_file.endswith('.json'):
                        user_config = json.load(f)
                    else:
                        logger.warning(f"Unsupported config file format: {config_file}")
                        return default_config
                
                # 合并配置
                default_config.update(user_config)
            except Exception as e:
                logger.error(f"Error loading config file: {e}")
        
        return default_config
    
    def _init_clients(self):
        """初始化API客户端"""
        if SRADB_AVAILABLE:
            try:
                self.sra_client = SRAweb()
                logger.info("SRAweb client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize SRAweb client: {e}")
        
        if MYGENE_AVAILABLE:
            try:
                self.mygene_client = mygene.MyGeneInfo()
                logger.info("MyGene client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize MyGene client: {e}")
    
    def fetch_data(self,
                   dataset_ids: Union[str, List[str]],
                   data_type: Optional[str] = None,
                   data_format: Optional[str] = None,
                   organism: Optional[str] = None,
                   platform: Optional[str] = None,
                   samples: Optional[List[str]] = None,
                   force_download: bool = False,
                   **kwargs) -> Dict[str, Any]:
        """
        通用数据获取函数（智能版）
        
        Parameters:
        -----------
        dataset_ids : Union[str, List[str]]
            数据集ID或ID列表
        data_type : Optional[str]
            数据类型，如未指定则自动推断
        data_format : Optional[str]
            数据格式，如未指定则自动推断
        organism : Optional[str]
            物种
        platform : Optional[str]
            平台类型
        samples : Optional[List[str]]
            指定样本ID列表
        force_download : bool
            强制重新下载，忽略缓存
        
        Returns:
        --------
        Dict[str, Any]: 包含数据和元数据的字典
        """
        if isinstance(dataset_ids, str):
            dataset_ids = [dataset_ids]
        
        results = {}
        
        for dataset_id in dataset_ids:
            try:
                # 自动推断数据类型
                inferred_type = data_type or self._infer_data_type(dataset_id)
                
                # 创建数据集配置
                config = DatasetConfig(
                    dataset_id=dataset_id,
                    data_type=DataSource(inferred_type),
                    data_format=DataFormat(data_format or 'expression'),
                    organism=organism,
                    platform=platform,
                    samples=samples,
                    force_download=force_download,
                    custom_params=kwargs
                )
                
                # 获取数据
                result = self._fetch_with_config(config)
                results[dataset_id] = result
                
            except Exception as e:
                logger.error(f"Failed to fetch data for {dataset_id}: {e}")
                results[dataset_id] = {
                    'error': str(e),
                    'traceback': self._format_exception(e)
                }
        
        # 记录下载历史
        self._record_download_history(dataset_ids)
        
        return results
    
    def _infer_data_type(self, dataset_id: str) -> str:
        """根据数据集ID推断数据类型"""
        if self.auto_infer:
            return DataSource.from_accession(dataset_id).value
        
        # 使用启发式规则
        dataset_id = dataset_id.upper()
        
        # GEO系列
        if dataset_id.startswith('GSE') or dataset_id.startswith('GDS'):
            return 'geo'
        
        # SRA运行
        elif dataset_id.startswith(('SRR', 'ERR', 'DRR')):
            return 'sra'
        
        # TCGA项目
        elif dataset_id.startswith('TCGA'):
            return 'tcga'
        
        # ENCODE实验
        elif dataset_id.startswith('ENC'):
            return 'encode'
        
        # ArrayExpress
        elif re.match(r'^E-[A-Z]{4}-\d+$', dataset_id):
            return 'arrayexpress'
        
        # 默认使用GEO
        else:
            return 'geo'
    
    def _fetch_with_config(self, config: DatasetConfig) -> Any:
        """使用配置获取数据"""
        dataset_id = config.dataset_id
        
        # 检查缓存
        if not config.force_download and self.config['prefer_cached']:
            cached_data = self.cache.load(config)
            if cached_data is not None:
                logger.info(f"Using cached data for {dataset_id}")
                return cached_data
        
        logger.info(f"Fetching data for {dataset_id} [{config.data_type.value}/{config.data_format.value}]")
        
        # 根据数据类型选择处理器
        # 将枚举类型转换为字符串键进行查找
        data_type_key = config.data_type.value if isinstance(config.data_type, DataSource) else config.data_type
        
        processor = self.data_processors.get(data_type_key)
        if not processor:
            # 如果直接查找失败，尝试使用枚举值查找
            if isinstance(config.data_type, DataSource):
                processor = self.data_processors.get(config.data_type)
            
            if not processor:
                # 最后尝试将字符串转换为枚举
                try:
                    enum_type = DataSource(data_type_key)
                    processor = self.data_processors.get(enum_type)
                except:
                    pass
            
            if not processor:
                raise ValueError(f"No processor for data type: {config.data_type} (key: {data_type_key})")
        processor = self.data_processors.get(config.data_type)
        if not processor:
            raise ValueError(f"No processor for data type: {config.data_type}")
        
        # 获取数据
        data = processor(config)
        
        # 后处理
        data = self._post_process(data, config)
        
        # 保存到缓存
        if not config.force_download:
            self.cache.save(config, data)
        
        return data
    
    def _process_geo(self, config: DatasetConfig) -> Any:
        """处理GEO数据"""
        if not GEO_UTILS_AVAILABLE:
            raise ImportError("GEO utilities not available")
        
        # 使用现有的GEO函数
        geo_data = geo_utils.load_geo(
            datasets=config.dataset_id,
            dir_save=str(self.dir_save / "geo"),
            verbose=config.custom_params.get('verbose', False)
        )
        
        # 根据格式提取数据
        if config.data_format == DataFormat.EXPRESSION:
            data = geo_utils.get_data(
                geo=geo_data,
                dataset=config.dataset_id,
                verbose=config.custom_params.get('verbose', False)
            )
        elif config.data_format == DataFormat.METADATA:
            data = geo_utils.get_meta(
                geo=geo_data,
                dataset=config.dataset_id,
                verbose=config.custom_params.get('verbose', False)
            )
        elif config.data_format == DataFormat.PROBE:
            data = geo_utils.get_probe(
                geo=geo_data,
                dataset=config.dataset_id,
                platform_id=config.platform,
                verbose=config.custom_params.get('verbose', False)
            )
        else:
            raise ValueError(f"Unsupported GEO format: {config.data_format}")
        
        # 过滤样本
        if config.samples:
            data = self._filter_samples(data, config.samples)
        
        return data
    def _process_sra(self, config: DatasetConfig) -> Any:
        """
        智能SRA处理器
        优先使用fastq-dump，失败时回退到FTP下载
        """
        dataset_id = config.dataset_id
        
        if config.data_format == DataFormat.METADATA:
            # 元数据仍然使用原来的方法
            return self._process_sra_original(config)
        
        elif config.data_format == DataFormat.FASTQ:
            # FASTQ下载：优先使用fastq-dump
            logger.info(f"Processing SRA FASTQ: {dataset_id}")
            
            # 检查是否强制使用某种方法
            force_method = config.custom_params.get('download_method')
            
            if force_method == 'fastq_dump' or (self.prefer_fastq_dump and self.fastq_dump_available and force_method != 'ftp'):
                # 尝试使用fastq-dump
                logger.info(f"Attempting fastq-dump for {dataset_id}")
                result = self._download_with_fastq_dump(config)
                
                if result.get('success', False):
                    logger.info(f"fastq-dump successful for {dataset_id}")
                    return result
                else:
                    logger.warning(f"fastq-dump failed for {dataset_id}: {result.get('error', 'unknown')}")
                    
                    # 如果用户没有明确要求fastq-dump，回退到FTP
                    if force_method != 'fastq_dump':
                        logger.info(f"Falling back to FTP for {dataset_id}")
                        return self._download_with_ftp(config)
                    else:
                        return result  # 用户明确要求fastq-dump，即使失败也返回
            
            else:
                # 使用FTP下载
                logger.info(f"Using FTP for {dataset_id}")
                return self._download_with_ftp(config)
        
        else:
            raise ValueError(f"Unsupported SRA format: {config.data_format}")
    def _download_with_ftp(self, config: DatasetConfig) -> Dict[str, Any]:
        """使用FTP下载（回退方法）"""
        dataset_id = config.dataset_id
        
        logger.info(f"Using FTP fallback for {dataset_id}")
        
        # 使用原来的SRADownloader
        downloader = SRADownloader(
            cache_dir=str(self.dir_save / "fastq"),
            max_workers=config.custom_params.get('parallel_downloads', 4)
        )
        
        result = downloader.download_fastq(
            dataset_id,
            output_dir=self.dir_save / "fastq",
            max_files=config.custom_params.get('max_files', 10)
        )
        
        # 添加方法标记
        if isinstance(result, dict):
            result['download_method'] = 'ftp'
        
        return result
    def _process_sra_original(self, config: DatasetConfig) -> Any:
        """处理SRA数据 - 使用独立的下载器"""
        dataset_id = config.dataset_id
        
        if config.data_format == DataFormat.METADATA:
            # 使用独立的下载器获取元数据
            downloader = SRADownloader(cache_dir=str(self.dir_save / "sra"))
            metadata = downloader.get_metadata(dataset_id)
            
            # 转换为DataFrame
            if isinstance(metadata, dict) and metadata:
                return pd.DataFrame([metadata])
            else:
                return pd.DataFrame()
        
        elif config.data_format == DataFormat.FASTQ:
            # 使用独立的下载器下载FASTQ
            downloader = SRADownloader(
                cache_dir=str(self.dir_save / "fastq"),
                max_workers=config.custom_params.get('parallel_downloads', 4)
            )
            
            result = downloader.download_fastq(
                dataset_id,
                output_dir=self.dir_save / "fastq",
                max_files=config.custom_params.get('max_files', 10)
            )
            
            return result
        
        else:
            raise ValueError(f"Unsupported SRA format: {config.data_format}")
 
    def _download_sra_fastq(self, config: DatasetConfig) -> Dict:
        """下载SRA FASTQ文件"""
        import requests
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        dataset_id = config.dataset_id
        output_dir = self.dir_save / "fastq" / dataset_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取下载链接
        download_links = self._get_sra_download_links(dataset_id)
        
        if not download_links:
            raise ValueError(f"No download links found for {dataset_id}")
        
        logger.info(f"Found {len(download_links)} download links for {dataset_id}")
        
        # 并行下载
        downloaded_files = []
        max_workers = config.custom_params.get('parallel_downloads', 
                                              self.config['parallel_downloads'])
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(self._download_file, url, output_dir, config): url
                for url in download_links[:10]  # 限制最多下载10个文件
            }
            
            for future in tqdm(as_completed(future_to_url), 
                             total=len(future_to_url),
                             desc=f"Downloading {dataset_id}"):
                url = future_to_url[future]
                try:
                    filepath = future.result(timeout=300)
                    if filepath:
                        downloaded_files.append(str(filepath))
                except Exception as e:
                    logger.error(f"Failed to download {url}: {e}")
        
        return {
            'metadata': self._get_sra_metadata(dataset_id),
            'fastq_files': downloaded_files,
            'output_dir': str(output_dir)
        }
    
    def _get_sra_download_links(self, accession: str) -> List[str]:
        """获取SRA下载链接"""
        try:
            # 尝试ENA API
            ena_links = self._get_ena_download_links(accession)
            if ena_links:
                return ena_links
            
            # 尝试NCBI
            ncbi_links = self._get_ncbi_download_links(accession)
            if ncbi_links:
                return ncbi_links
            
            # 生成默认链接
            return self._generate_default_links(accession)
            
        except Exception as e:
            logger.error(f"Failed to get download links for {accession}: {e}")
            return []
    
    def _get_ena_download_links(self, accession: str) -> List[str]:
        """从ENA获取下载链接"""
        if not REQUESTS_AVAILABLE:
            return []
        
        try:
            url = "https://www.ebi.ac.uk/ena/portal/api/filereport"
            params = {
                'accession': accession,
                'result': 'read_run',
                'fields': 'fastq_ftp',
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data and isinstance(data, list):
                links = []
                for item in data:
                    if 'fastq_ftp' in item and item['fastq_ftp']:
                        ftp_links = str(item['fastq_ftp']).split(';')
                        for link in ftp_links:
                            link = link.strip()
                            if link:
                                links.append(f"ftp://{link}")
                return links
        except Exception as e:
            logger.debug(f"ENA API failed: {e}")
        
        return []
    
    def _get_sra_metadata(self, accession: str) -> pd.DataFrame:
        """获取SRA元数据"""
        if self.sra_client:
            return self.sra_client.search_sra(run_accession =accession, detailed=True)
        return pd.DataFrame()

    def _download_with_fastq_dump(self, config: DatasetConfig) -> Dict[str, Any]:
        """使用fastq-dump下载SRA数据"""
        import subprocess
        import shutil
        import time
        
        dataset_id = config.dataset_id
        
        # 提取参数
        output_dir = self.dir_save / "fastq" / dataset_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        split_files = config.custom_params.get('split_files', True)
        gzip_output = config.custom_params.get('gzip_output', True)
        use_prefetch = config.custom_params.get('use_prefetch', True)
        max_retries = config.custom_params.get('max_retries', 2)
        threads = config.custom_params.get('threads', 4)
        
        # 查找工具
        fastq_dump_path = shutil.which("fastq-dump")
        prefetch_path = shutil.which("prefetch")
        fasterq_dump_path = shutil.which("fasterq-dump")
        if not fastq_dump_path and not fasterq_dump_path:
            return {
                'success': False,
                'error': 'Neither fastq-dump nor fasterq-dump found in PATH',
                'accession': dataset_id,
            } 
        
        logger.info(f"Downloading {dataset_id} with fastq-dump")
        logger.info(f"  Output dir: {output_dir}")
        logger.info(f"  Split files: {split_files}")
        logger.info(f"  Gzip output: {gzip_output}")
        
        results = {}
        
        # 方法1: 使用prefetch + fastq-dump（如果可用）
        if use_prefetch and prefetch_path:
            logger.info("Method 1: Using prefetch + fastq-dump")
            result = self._run_prefetch_fastq_dump(
                accession=dataset_id,
                fastq_dump_path=fastq_dump_path,
                prefetch_path=prefetch_path,
                output_dir=output_dir,
                split_files=split_files,
                gzip_output=gzip_output,
                threads=threads,
                max_retries=max_retries
            )
            results['prefetch_method'] = result
            
            if result.get('success', False):
                return self._format_fastq_dump_result(dataset_id, output_dir, result, 'prefetch+fastq-dump')
        
        # 方法2: 直接使用fastq-dump
        logger.info("Method 2: Using fastq-dump directly")
        result = self._run_fastq_dump_direct(
            accession=dataset_id,
            fastq_dump_path=fastq_dump_path,
            output_dir=output_dir,
            split_files=split_files,
            gzip_output=gzip_output,
            threads=threads,
            max_retries=max_retries
        )
        results['direct_method'] = result
        
        if result.get('success', False):
            return self._format_fastq_dump_result(dataset_id, output_dir, result, 'fastq-dump')
        
        # 方法3: 使用fasterq-dump（如果可用）
        if fasterq_dump_path:
            logger.info("Method 3: Using fasterq-dump")
            result = self._run_fasterq_dump(
                accession=dataset_id,
                fasterq_dump_path=fasterq_dump_path,
                output_dir=output_dir,
                split_files=split_files,
                gzip_output=gzip_output,
                threads=threads,
                max_retries=max_retries
            )
            results['fasterq_method'] = result
            
            if result.get('success', False):
                return self._format_fastq_dump_result(dataset_id, output_dir, result, 'fasterq-dump')
        
        # 所有方法都失败
        logger.error(f"All fastq-dump methods failed for {dataset_id}")
        return {
            'success': False,
            'error': 'All fastq-dump methods failed',
            'accession': dataset_id,
            'results': results,
            'method': 'fastq-dump'
        }

    def _run_prefetch_fastq_dump(self, accession, fastq_dump_path, prefetch_path, 
                            output_dir, split_files, gzip_output, threads, max_retries):
        """使用prefetch下载.sra文件，然后用fastq-dump转换"""

        sra_dir = output_dir / "sra"
        sra_dir.mkdir(exist_ok=True) 
        # 步骤1: 使用prefetch
        prefetch_cmd = [
            prefetch_path,
            accession,
            "-O", str(sra_dir),
            "--progress"
        ]
        
        try:
            logger.info(f"Running prefetch: {' '.join(prefetch_cmd)}")
            
            # 运行prefetch
            result = subprocess.run(
                prefetch_cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 10分钟超时
                check=False,# 不立即抛出异常
            )
        
            # 详细记录输出
            logger.debug(f"prefetch return code: {result.returncode}")
            if result.stdout:
                logger.debug(f"prefetch stdout (last 500 chars): {result.stdout[-500:]}")
            if result.stderr:
                logger.error(f"prefetch stderr: {result.stderr}")
            
            if result.returncode != 0:
                error_msg = f"prefetch failed with code {result.returncode}"
                if result.stderr:
                    error_msg += f": {result.stderr[:200]}"
                return {'success': False, 'error': error_msg}

            # 查找.sra文件
            sra_files = list(sra_dir.glob(f"**/{accession}.sra"))
            if not sra_files:
                sra_files = list(sra_dir.glob(f"**/*.sra"))
            
            if not sra_files:
                # 列出目录内容帮助调试
                all_files = list(sra_dir.rglob("*"))
                file_list = [f"{f.name} ({f.stat().st_size} bytes)" for f in all_files if f.is_file()]
                logger.warning(f"No .sra files found. Directory contents: {file_list}")
                return {'success': False, 'error': f'No .sra file found. Files: {file_list}'}

            
            sra_file = sra_files[0]
            logger.info(f"Found .sra file: {sra_file.name} ({sra_file.stat().st_size/1024/1024:.1f} MB)")

            # 步骤2: 使用fastq-dump转换
            return self._run_fastq_dump_on_file(
                sra_file=sra_file,
                fastq_dump_path=fastq_dump_path,
                output_dir=output_dir,
                split_files=split_files,
                gzip_output=gzip_output,
                threads=threads
            )
            
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'prefetch timed out'}
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()[:500]
            return {'success': False, 'error': f'prefetch error: {type(e).__name__}: {str(e)[:200]}\n{error_details}'}
            

    def _run_fastq_dump_direct(self, accession, fastq_dump_path, output_dir, 
                            split_files, gzip_output, threads, max_retries):
        """直接使用fastq-dump下载"""
        # 构建命令
        cmd = [
            fastq_dump_path,
            accession,
            "--outdir", str(output_dir),
            "--skip-technical",
            "--readids",
            "--dumpbase",
            "--clip",
            "--read-filter", "pass",
            "--origfmt"
        ]
        
        if split_files:
            cmd.append("--split-files")
        
        if gzip_output:
            cmd.append("--gzip")
        
        # 添加线程支持（如果版本支持）
        if threads > 1:
            cmd.extend(["--threads", str(threads)])
        
        try:
            logger.info(f"Running fastq-dump: {' '.join(cmd[:10])}...")  # 只显示前10个参数
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 15分钟超时
                check=False
            )
            
            logger.debug(f"fastq-dump stdout: {result.stdout[-500:] if result.stdout else ''}")
            logger.debug(f"fastq-dump stderr: {result.stderr[-500:] if result.stderr else ''}")
            
            # 检查输出文件
            return self._check_fastq_output(output_dir, accession, split_files, gzip_output)
            
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'fastq-dump timed out'}
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr[:500] if e.stderr else str(e)
            return {'success': False, 'error': f'fastq-dump failed: {error_msg}'}
        except Exception as e:
            return {'success': False, 'error': f'fastq-dump error: {type(e).__name__}: {str(e)[:200]}'}

    def _run_fasterq_dump(self, accession, fasterq_dump_path, output_dir, 
                        split_files, gzip_output, threads, max_retries):
        """使用fasterq-dump"""
        cmd = [
            fasterq_dump_path,
            accession,
            "-O", str(output_dir),
            "-e", str(threads),
            "-p",  # 显示进度
            "-t", str(output_dir / "temp")  # 临时目录
        ]
        
        if split_files:
            cmd.append("--split-files")
        
        try:
            logger.info(f"Running fasterq-dump: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10分钟超时
                check=True
            )
            
            logger.debug(f"fasterq-dump stdout: {result.stdout[-500:] if result.stdout else ''}")
            logger.debug(f"fasterq-dump stderr: {result.stderr[-500:] if result.stderr else ''}")
            
            # 如果需要gzip，压缩文件
            if gzip_output:
                self._compress_fastq_files(output_dir)
            
            return self._check_fastq_output(output_dir, accession, split_files, gzip_output)
            
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'fasterq-dump timed out'}
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr[:500] if e.stderr else str(e)
            return {'success': False, 'error': f'fasterq-dump failed: {error_msg}'}
        except Exception as e:
            return {'success': False, 'error': f'fasterq-dump error: {type(e).__name__}: {str(e)[:200]}'}

    def _run_fastq_dump_on_file(self, sra_file, fastq_dump_path, output_dir,
                            split_files, gzip_output, threads):
        """对已有的.sra文件运行fastq-dump"""
        cmd = [
            fastq_dump_path,
            str(sra_file),
            "--outdir", str(output_dir),
            "--skip-technical",
            "--readids",
            "--dumpbase",
            "--clip",
            "--read-filter", "pass",
            "--origfmt"
        ]
        
        if split_files:
            cmd.append("--split-files")
        
        if gzip_output:
            cmd.append("--gzip")
        
        if threads > 1:
            cmd.extend(["--threads", str(threads)])
        
        try:
            logger.info(f"Running fastq-dump on .sra file: {' '.join(cmd[:8])}...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时（文件已本地存在）
                check=True
            )
            
            return self._check_fastq_output(output_dir, sra_file.stem, split_files, gzip_output)
            
        except subprocess.CalledProcessError as e:
            return {'success': False, 'error': f'fastq-dump conversion failed: {e.stderr[:200] if e.stderr else str(e)}'}
        except Exception as e:
            return {'success': False, 'error': f'fastq-dump error: {type(e).__name__}: {str(e)[:200]}'}

    def _check_fastq_output(self, output_dir, accession, split_files, gzip_output):
        """检查fastq输出文件"""
        import glob
        
        # 查找文件模式
        if gzip_output:
            patterns = [f"{accession}*.fastq.gz", f"{accession}*.fq.gz"]
        else:
            patterns = [f"{accession}*.fastq", f"{accession}*.fq"]
        
        files = []
        for pattern in patterns:
            files.extend(output_dir.glob(pattern))
        
        # 过滤空文件
        files = [str(f) for f in files if f.exists() and f.stat().st_size > 0]
        
        if files:
            total_size = sum(Path(f).stat().st_size for f in files)
            return {
                'success': True,
                'files': files,
                'file_count': len(files),
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024)
            }
        else:
            # 尝试其他命名模式
            all_fastq_files = list(output_dir.glob("*.fastq*"))
            if all_fastq_files:
                files = [str(f) for f in all_fastq_files if f.stat().st_size > 0]
                if files:
                    total_size = sum(Path(f).stat().st_size for f in files)
                    return {
                        'success': True,
                        'files': files,
                        'file_count': len(files),
                        'total_size_bytes': total_size,
                        'total_size_mb': total_size / (1024 * 1024),
                        'note': 'Files found with different naming pattern'
                    }
            
            return {'success': False, 'error': 'No output files found'}

    def _compress_fastq_files(self, output_dir):
        """压缩fastq文件"""
        import gzip
        import shutil
        from concurrent.futures import ThreadPoolExecutor
        
        fastq_files = list(output_dir.glob("*.fastq"))
        
        if not fastq_files:
            return
        
        logger.info(f"Compressing {len(fastq_files)} fastq files...")
        
        def compress_file(fastq_path):
            gzip_path = fastq_path.with_suffix('.fastq.gz')
            
            try:
                with open(fastq_path, 'rb') as f_in:
                    with gzip.open(gzip_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # 删除原始文件
                fastq_path.unlink()
                return True
            except Exception as e:
                logger.warning(f"Failed to compress {fastq_path.name}: {e}")
                return False
        
        # 并行压缩
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(compress_file, fastq_files))
        
        success_count = sum(results)
        logger.info(f"Compression complete: {success_count}/{len(fastq_files)} successful")

    def _format_fastq_dump_result(self, accession, output_dir, result, method):
        """格式化fastq-dump结果"""
        formatted = {
            'accession': accession,
            'success': result['success'],
            'files': result.get('files', []),
            'file_count': result.get('file_count', 0),
            'total_size_mb': result.get('total_size_mb', 0),
            'output_dir': str(output_dir),
            'method': method,
            'download_method': 'fastq-dump'
        }
        
        if 'note' in result:
            formatted['note'] = result['note']
        
        return formatted


    def _download_file(self, url: str, output_dir: Path, config: DatasetConfig) -> Optional[Path]:
        """下载单个文件"""
        import requests
        
        filename = url.split('/')[-1].split('?')[0]
        filepath = output_dir / filename
        
        # 检查文件是否已存在
        if filepath.exists() and not config.force_download:
            file_size = filepath.stat().st_size
            if file_size > 1000:  # 文件大小合理
                logger.debug(f"File already exists: {filepath}")
                return filepath
        
        try:
            if url.startswith('ftp://'):
                return self._download_ftp_file(url, filepath)
            else:
                return self._download_http_file(url, filepath)
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return None
    
    def _download_http_file(self, url: str, filepath: Path) -> Path:
        """下载HTTP文件"""
        import requests
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, stream=True, headers=headers, timeout=60)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filepath, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
        
        logger.info(f"Downloaded: {filepath.name} ({downloaded/1024/1024:.1f} MB)")
        return filepath
    
    def _process_tcga(self, config: DatasetConfig) -> Any:
        """处理TCGA数据"""
        # 实现TCGA数据下载逻辑
        raise NotImplementedError("TCGA data fetching not yet implemented")
    
    def _process_encode(self, config: DatasetConfig) -> Any:
        """处理ENCODE数据"""
        # 实现ENCODE数据下载逻辑
        raise NotImplementedError("ENCODE data fetching not yet implemented")
    
    def _process_array_express(self, config: DatasetConfig) -> Any:
        """处理ArrayExpress数据"""
        # 实现ArrayExpress数据下载逻辑
        raise NotImplementedError("ArrayExpress data fetching not yet implemented")
    
    def _process_single_cell(self, config: DatasetConfig) -> Any:
        """处理单细胞数据"""
        # 实现单细胞数据下载逻辑
        raise NotImplementedError("Single-cell data fetching not yet implemented")
    
    def _process_custom(self, config: DatasetConfig) -> Any:
        """处理自定义数据"""
        # 用户自定义数据处理
        custom_func = config.custom_params.get('custom_function')
        if custom_func and callable(custom_func):
            return custom_func(config.dataset_id, **config.custom_params)
        
        raise ValueError("No custom function provided for custom data source")
    
    def _post_process(self, data: Any, config: DatasetConfig) -> Any:
        """数据后处理"""
        if isinstance(data, pd.DataFrame):
            # 自动归一化
            if self.config['auto_normalize'] and config.data_format == DataFormat.EXPRESSION:
                data = self._auto_normalize(data)
            
            # 基因ID转换
            if self.config['gene_id_conversion']:
                data = self._convert_gene_ids(data)
            
            # 质量控制
            if self.config['quality_control']:
                data = self._quality_control(data)
        
        return data
    
    def _auto_normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """自动归一化表达数据"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return df
        
        # 检测数据类型
        if self._is_raw_counts(df[numeric_cols]):
            logger.info("Detected raw counts, normalizing with TMM")
            try:
                return self._normalize_counts(df, numeric_cols)
            except Exception as e:
                logger.warning(f"TMM normalization failed: {e}")
        
        return df
    
    def _is_raw_counts(self, df_numeric: pd.DataFrame) -> bool:
        """检测是否为原始计数数据"""
        # 检查是否为整数
        if not df_numeric.applymap(lambda x: isinstance(x, (int, np.integer))).all().all():
            return False
        
        # 检查数值范围
        max_val = df_numeric.max().max()
        min_val = df_numeric.min().min()
        
        # 原始计数通常是正整数，且最大值较大
        return min_val >= 0 and max_val > 1000
    
    def _normalize_counts(self, df: pd.DataFrame, numeric_cols: pd.Index) -> pd.DataFrame:
        """使用TMM方法归一化计数数据"""
        from statsmodels import robust
        import numpy as np
        
        df_numeric = df[numeric_cols]
        
        # 简单的TMM-like归一化
        # 计算几何均值作为参考样本
        log_counts = np.log1p(df_numeric.values)
        ref_sample = np.exp(np.mean(log_counts, axis=1))
        
        # 计算缩放因子
        scaling_factors = []
        for col in df_numeric.columns:
            sample_counts = df_numeric[col].values
            log_ratio = np.log1p(sample_counts) - np.log1p(ref_sample)
            m_value = log_ratio - np.median(log_ratio)
            a_value = 0.5 * (np.log1p(sample_counts) + np.log1p(ref_sample))
            
            # 修剪极端值
            trim_frac = 0.3
            n = len(m_value)
            trim_n = int(n * trim_frac)
            indices = np.argsort(a_value)
            keep_indices = indices[trim_n:n-trim_n]
            
            # 计算缩放因子
            scaling_factor = np.exp(np.mean(m_value[keep_indices]))
            scaling_factors.append(scaling_factor)
        
        # 应用缩放因子
        scaling_factors = np.array(scaling_factors)
        df_normalized = df.copy()
        for i, col in enumerate(numeric_cols):
            df_normalized[col] = df_numeric[col] / scaling_factors[i]
        
        return df_normalized
    
    def _convert_gene_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        """转换基因ID"""
        if not MYGENE_AVAILABLE or self.mygene_client is None:
            return df
        
        # 检测可能的基因ID列
        gene_id_cols = [col for col in df.columns 
                       if col.lower() in ['gene_id', 'gene_symbol', 'entrez', 'ensembl']]
        
        if not gene_id_cols:
            return df
        
        # 使用mygene.info进行ID转换
        try:
            gene_ids = df[gene_id_cols[0]].dropna().tolist()
            results = self.mygene_client.querymany(gene_ids, scopes='symbol', fields='symbol,name')
            
            # 创建映射
            id_map = {}
            for result in results:
                if 'query' in result and 'symbol' in result:
                    id_map[result['query']] = result['symbol']
            
            # 应用映射
            df = df.copy()
            df[gene_id_cols[0]] = df[gene_id_cols[0]].map(id_map).fillna(df[gene_id_cols[0]])
            
        except Exception as e:
            logger.warning(f"Gene ID conversion failed: {e}")
        
        return df
    
    def _quality_control(self, df: pd.DataFrame) -> pd.DataFrame:
        """质量控制"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return df
        
        # 移除全为零的行
        df_numeric = df[numeric_cols]
        non_zero_rows = (df_numeric != 0).any(axis=1)
        
        if not non_zero_rows.all():
            logger.info(f"Removing {sum(~non_zero_rows)} rows with all zeros")
            df = df[non_zero_rows].copy()
        
        # 移除低表达基因
        mean_expression = df_numeric.mean(axis=1)
        if len(mean_expression) > 1000:  # 只在数据量较大时过滤
            threshold = mean_expression.quantile(0.1)
            keep_rows = mean_expression >= threshold
            
            if not keep_rows.all():
                logger.info(f"Removing {sum(~keep_rows)} low-expression rows")
                df = df[keep_rows].copy()
        
        return df
    
    def _filter_samples(self, data: Any, samples: List[str]) -> Any:
        """过滤样本"""
        if isinstance(data, pd.DataFrame):
            # 尝试按列名过滤
            if any(sample in data.columns for sample in samples):
                return data[samples]
            # 尝试按索引过滤
            elif any(sample in data.index for sample in samples):
                return data.loc[data.index.intersection(samples)]
        
        return data
    
    def _record_download_history(self, dataset_ids: List[str]):
        """记录下载历史"""
        history_file = self.dir_save / "download_history.json"
        
        history = []
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
                if isinstance(history, dict):
                    history = [history]
                elif not isinstance(history, list):
                    history = []
            except:
                history = []
        
        for dataset_id in dataset_ids:
            history.append({
                'dataset_id': dataset_id,
                'timestamp': datetime.now().isoformat(),
                'cache_dir': str(self.dir_save)
            })
        
        # 只保留最近100条记录
        history = history[-100:]
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def _format_exception(self, e: Exception) -> str:
        """格式化异常信息"""
        import traceback
        return traceback.format_exc()
    
    # 公共API方法
    def list_datasets(self, 
                     data_type: Optional[str] = None,
                     search_query: Optional[str] = None,
                     organism: Optional[str] = None,
                     limit: int = 50) -> pd.DataFrame:
        """列出或搜索数据集"""
        if search_query:
            return self._search_datasets(search_query, data_type, organism, limit)
        
        # 列出缓存的数据集
        return self.cache_list(data_type)
    
    def _search_datasets(self, 
                        query: str,
                        data_type: Optional[str],
                        organism: Optional[str],
                        limit: int) -> pd.DataFrame:
        """搜索数据集"""
        import requests
        
        # 根据数据类型选择API
        if data_type == 'geo' or data_type is None:
            return self._search_geo(query, organism, limit)
        elif data_type == 'sra':
            return self._search_sra(query, limit)
        else:
            logger.warning(f"Search not supported for data type: {data_type}")
            return pd.DataFrame()
    
    def _search_geo(self, query: str, organism: Optional[str], limit: int) -> pd.DataFrame:
        """搜索GEO数据集"""
        if not REQUESTS_AVAILABLE:
            return pd.DataFrame()
        
        try:
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
            
            search_term = query
            if organism:
                search_term += f" AND {organism}[Organism]"
            
            # 搜索
            search_params = {
                'db': 'gds',
                'term': search_term,
                'retmax': limit,
                'retmode': 'json'
            }
            
            response = requests.get(base_url + "esearch.fcgi", params=search_params)
            response.raise_for_status()
            
            result = response.json()
            ids = result.get('esearchresult', {}).get('idlist', [])
            
            if not ids:
                return pd.DataFrame()
            
            # 获取详细信息
            summary_params = {
                'db': 'gds',
                'id': ','.join(ids),
                'retmode': 'json'
            }
            
            summary_response = requests.get(base_url + "esummary.fcgi", params=summary_params)
            summary_result = summary_response.json()
            
            datasets = []
            for uid in ids:
                info = summary_result.get('result', {}).get(uid, {})
                datasets.append({
                    'accession': info.get('accession', ''),
                    'title': info.get('title', ''),
                    'summary': info.get('summary', '')[:200] + '...' if info.get('summary') else '',
                    'organism': info.get('organism', ''),
                    'platform': info.get('platform', ''),
                    'samples': info.get('samples', 0),
                    'type': info.get('entrytype', ''),
                    'gdstype': info.get('gdstype', ''),
                    'pubmed': info.get('pubmed', ''),
                })
            
            return pd.DataFrame(datasets)
            
        except Exception as e:
            logger.error(f"Failed to search GEO datasets: {e}")
            return pd.DataFrame()
    
    def _search_sra(self, query: str, limit: int) -> pd.DataFrame:
        """搜索SRA数据集"""
        if not self.sra_client:
            return pd.DataFrame()
        
        try:
            df = self.sra_client.search_sra(query, size=limit)
            return df
        except Exception as e:
            logger.error(f"Failed to search SRA datasets: {e}")
            return pd.DataFrame()
    
    def cache_list(self, data_type: Optional[str] = None) -> pd.DataFrame:
        """列出缓存的数据集"""
        cache_files = list(self.dir_save.rglob("*.pkl"))
        
        datasets = []
        for file_path in cache_files:
            try:
                rel_path = file_path.relative_to(self.dir_save)
                parts = rel_path.parts
                
                if len(parts) >= 2:
                    ds_type = parts[0]
                    
                    if data_type and ds_type != data_type:
                        continue
                    
                    # 尝试从缓存元数据获取信息
                    cache_key = file_path.stem
                    metadata = self.cache.metadata.get(cache_key, {})
                    
                    datasets.append({
                        'dataset_id': metadata.get('dataset_id', 'Unknown'),
                        'data_type': ds_type,
                        'data_format': metadata.get('data_format', 'Unknown'),
                        'file_path': str(file_path),
                        'size_mb': file_path.stat().st_size / (1024 * 1024),
                        'created': metadata.get('created', 'Unknown'),
                        'last_accessed': metadata.get('last_accessed', 'Unknown'),
                    })
            except:
                continue
        
        if datasets:
            df = pd.DataFrame(datasets)
            return df.sort_values('last_accessed', ascending=False)
        
        return pd.DataFrame()
    
    def batch_fetch(self,
                   configs: List[Dict[str, Any]],
                   max_workers: int = 4,
                   progress_bar: bool = True) -> Dict[str, Any]:
        """批量获取数据"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = {}
        
        def fetch_task(config_dict: Dict) -> Tuple[str, Any]:
            """单个获取任务"""
            try:
                dataset_id = config_dict.get('dataset_id', config_dict.get('id'))
                if not dataset_id:
                    return 'unknown', {'error': 'No dataset_id provided'}
                
                # 创建配置
                config = DatasetConfig.from_accession(dataset_id, **config_dict)
                
                # 获取数据
                data = self._fetch_with_config(config)
                return dataset_id, data
                
            except Exception as e:
                dataset_id = config_dict.get('dataset_id', config_dict.get('id', 'unknown'))
                return dataset_id, {'error': str(e)}
        
        # 使用进度条
        if progress_bar:
            configs_iter = tqdm(configs, desc="Batch fetching")
        else:
            configs_iter = configs
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_config = {
                executor.submit(fetch_task, config): config 
                for config in configs_iter
            }
            
            for future in as_completed(future_to_config):
                dataset_id, result = future.result()
                results[dataset_id] = result
        
        return results
    
    def get_dataset_info(self, dataset_id: str) -> Dict[str, Any]:
        """获取数据集信息"""
        # 自动推断数据类型
        data_type = self._infer_data_type(dataset_id)
        
        info = {
            'dataset_id': dataset_id,
            'inferred_type': data_type,
            'data_source': DataSource.from_accession(dataset_id).value,
            'cache_status': self._check_cache_status(dataset_id),
            'available_formats': self._get_available_formats(dataset_id, data_type),
        }
        
        # 尝试获取元数据
        try:
            if data_type == 'geo':
                info['metadata'] = self._get_geo_info(dataset_id)
            elif data_type == 'sra':
                info['metadata'] = self._get_sra_info(dataset_id)
        except Exception as e:
            info['metadata_error'] = str(e)
        
        return info
    
    def _check_cache_status(self, dataset_id: str) -> Dict[str, Any]:
        """检查缓存状态"""
        cache_files = list(self.dir_save.rglob(f"*{dataset_id}*.pkl"))
        
        status = {
            'cached': len(cache_files) > 0,
            'files': [],
            'total_size_mb': 0
        }
        
        for file_path in cache_files:
            status['files'].append({
                'path': str(file_path),
                'size_mb': file_path.stat().st_size / (1024 * 1024),
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
            })
            status['total_size_mb'] += file_path.stat().st_size / (1024 * 1024)
        
        return status
    
    def _get_available_formats(self, dataset_id: str, data_type: str) -> List[str]:
        """获取可用数据格式"""
        if data_type == 'geo':
            return ['expression', 'metadata', 'probe']
        elif data_type == 'sra':
            return ['metadata', 'fastq']
        elif data_type == 'tcga':
            return ['expression', 'clinical', 'mutations']
        else:
            return ['metadata']
    
    def _get_geo_info(self, dataset_id: str) -> Dict[str, Any]:
        """获取GEO数据集信息"""
        if not REQUESTS_AVAILABLE:
            return {}
        
        try:
            url = f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"
            params = {'acc': dataset_id, 'targ': 'self', 'form': 'xml', 'view': 'quick'}
            
            response = requests.get(url, params=params, timeout=10)
            if response.ok:
                # 解析HTML获取基本信息
                import re
                html = response.text
                
                info = {}
                
                # 提取标题
                title_match = re.search(r'<title>(.*?)</title>', html)
                if title_match:
                    info['title'] = title_match.group(1)
                
                # 提取样本数
                samples_match = re.search(r'Samples?:\s*(\d+)', html)
                if samples_match:
                    info['samples'] = int(samples_match.group(1))
                
                # 提取平台
                platform_match = re.search(r'Platform.*?GPL\d+', html)
                if platform_match:
                    info['platform'] = platform_match.group(0)
                
                return info
        except Exception as e:
            logger.debug(f"Failed to get GEO info: {e}")
        
        return {}
    
    def _get_sra_info(self, dataset_id: str) -> Dict[str, Any]:
        """获取SRA数据集信息"""
        if not self.sra_client:
            return {}
        
        try:
            df = self.sra_client.search_sra(run_accession =dataset_id, detailed=False)
            if not df.empty:
                return df.iloc[0].to_dict()
        except Exception as e:
            logger.debug(f"Failed to get SRA info: {e}")
        
        return {}
    
    def clear_cache(self, 
                   data_type: Optional[str] = None,
                   older_than_days: Optional[int] = None,
                   confirm: bool = False):
        """清理缓存"""
        if not confirm:
            logger.warning("Cache clearance requires confirmation. Use confirm=True")
            return
        
        self.cache.clear_cache(data_type, older_than_days)
    
    def export_data(self, 
                   dataset_id: str,
                   output_format: str = 'csv',
                   output_dir: Optional[str] = None) -> str:
        """导出数据"""
        # 获取数据
        data = self.fetch_data(dataset_id)
        
        if isinstance(data, dict) and 'error' in data:
            raise ValueError(f"Cannot export: {data['error']}")
        
        if output_dir is None:
            output_dir = self.dir_save / "exports"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(exist_ok=True)
        
        if output_format == 'csv':
            if isinstance(data, pd.DataFrame):
                output_path = output_dir / f"{dataset_id}.csv"
                data.to_csv(output_path)
                return str(output_path)
            else:
                raise ValueError("Data is not a DataFrame, cannot export as CSV")
        
        elif output_format == 'excel':
            if isinstance(data, pd.DataFrame):
                output_path = output_dir / f"{dataset_id}.xlsx"
                data.to_excel(output_path, engine='openpyxl')
                return str(output_path)
            else:
                raise ValueError("Data is not a DataFrame, cannot export as Excel")
        
        elif output_format == 'json':
            output_path = output_dir / f"{dataset_id}.json"
            with open(output_path, 'w') as f:
                if isinstance(data, pd.DataFrame):
                    json.dump(data.to_dict(orient='records'), f, indent=2)
                else:
                    json.dump(data, f, indent=2)
            return str(output_path)
        
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        cache_files = list(self.dir_save.rglob("*.pkl"))
        
        stats = {
            'total_datasets': len(set(f.stem for f in cache_files)),
            'total_files': len(cache_files),
            'total_size_gb': sum(f.stat().st_size for f in cache_files) / (1024**3),
            'by_data_type': {},
            'by_format': {},
            'recent_downloads': []
        }
        
        # 按数据类型统计
        for file_path in cache_files:
            try:
                rel_path = file_path.relative_to(self.dir_save)
                if len(rel_path.parts) >= 1:
                    data_type = rel_path.parts[0]
                    stats['by_data_type'][data_type] = stats['by_data_type'].get(data_type, 0) + 1
            except:
                pass
        
        # 读取下载历史
        history_file = self.dir_save / "download_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
                    stats['recent_downloads'] = history[-10:]  # 最近10次下载
            except:
                pass
        
        return stats


# 简化的使用函数（保持向后兼容）
def fetch_data(dataset_ids: Union[str, List[str]],
               data_type: Optional[str] = None,
               data_format: Optional[str] = None,
               organism: Optional[str] = None,
               platform: Optional[str] = None,
               samples: Optional[List[str]] = None,
               force_download: bool = False,
               dir_save: str = "./bio_data_cache",
               auto_infer: bool = True,
               **kwargs) -> Dict[str, Any]:
    """
    简化的数据获取函数（智能版）
    
    Parameters:
    -----------
    dataset_ids : Union[str, List[str]]
        数据集ID
    data_type : Optional[str]
        数据类型，如未指定则自动推断
    data_format : Optional[str]
        数据格式，如未指定则自动推断
    organism : Optional[str]
        物种
    platform : Optional[str]
        平台
    samples : Optional[List[str]]
        样本列表
    force_download : bool
        强制重新下载
    dir_save : str
        缓存目录
    auto_infer : bool
        是否启用自动类型推断
    
    Returns:
    --------
    Dict[str, Any]: 数据字典
    """
    fetcher = BioDataFetcher(dir_save=dir_save, auto_infer=auto_infer)
    
    return fetcher.fetch_data(
        dataset_ids=dataset_ids,
        data_type=data_type,
        data_format=data_format,
        organism=organism,
        platform=platform,
        samples=samples,
        force_download=force_download,
        **kwargs
    )


# 快速使用函数
def quick_fetch(dataset_id: str, 
               dir_save: str = "./bio_data_cache",
               **kwargs) -> Any:
    """
    快速获取数据（完全自动推断）
    
    Parameters:
    -----------
    dataset_id : str
        数据集ID
    dir_save : str
        缓存目录
    **kwargs : 其他参数传递给fetch_data
    
    Returns:
    --------
    Any: 获取的数据
    """
    return fetch_data(
        dataset_ids=dataset_id,
        dir_save=dir_save,
        auto_infer=True,
        **kwargs
    ).get(dataset_id)


# 示例配置文件
SAMPLE_CONFIG = """
# BioDataFetcher 配置文件
# 保存为 config.yaml 并使用 fetcher = BioDataFetcher(config_file='config.yaml')

# 下载设置
max_retries: 3
timeout: 30
parallel_downloads: 4
prefer_cached: true

# 数据处理
auto_normalize: true
gene_id_conversion: true
quality_control: true

# API密钥（可选）
ncbi_api_key: null
ensembl_api_key: null

# 缓存设置
max_cache_size_gb: 10

# 网络设置
proxy: null
user_agent: "BioDataFetcher/1.0"

# 日志设置
log_level: "INFO"
log_file: "bio_data_fetcher.log"
"""

import subprocess
import shutil
from pathlib import Path

def check_fastq_dump_available():
    """检查fastq-dump是否可用"""
    # 查找fastq-dump路径
    fastq_dump_path = shutil.which("fastq-dump")
    prefetch_path = shutil.which("prefetch")
    
    print("检查SRA Toolkit工具...")
    
    if fastq_dump_path:
        print(f"✅ fastq-dump 找到: {fastq_dump_path}")
        
        # 检查版本
        try:
            result = subprocess.run(
                [fastq_dump_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"   版本: {result.stdout.strip()}")
        except:
            print("   无法获取版本信息")
    else:
        print("❌ fastq-dump 未找到")
        print("   请安装 SRA Toolkit: https://github.com/ncbi/sra-tools")
    
    if prefetch_path:
        print(f"✅ prefetch 找到: {prefetch_path}")
    else:
        print("❌ prefetch 未找到")
    
    return fastq_dump_path is not None and prefetch_path is not None

# 检查工具
# check_fastq_dump_available()

def enhance_bio_data_fetcher_with_fastqdump():
    """增强BioDataFetcher，添加fastq-dump支持"""
    
    class EnhancedBioDataFetcher(BioDataFetcher):
        """增强版的BioDataFetcher，支持fastq-dump"""
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fastq_downloader = FastqDumpDownloader(
                cache_dir=str(self.dir_save / "fastqdump")
            )
            
            # 覆盖SRA处理器
            self.data_processors['sra'] = self._process_sra_enhanced
            if DataSource.SRA in self.data_processors:
                self.data_processors[DataSource.SRA] = self._process_sra_enhanced
        
        def _process_sra_enhanced(self, config: DatasetConfig) -> Any:
            """增强的SRA处理方法，优先使用fastq-dump"""
            dataset_id = config.dataset_id
            
            if config.data_format == DataFormat.METADATA:
                # 仍然使用原来的方法获取元数据
                return self._process_sra(config)
            
            elif config.data_format == DataFormat.FASTQ:
                print(f"使用fastq-dump下载FASTQ: {dataset_id}")
                
                # 提取参数
                split_files = config.custom_params.get('split_files', True)
                gzip_output = config.custom_params.get('gzip_output', True)
                use_prefetch = config.custom_params.get('use_prefetch', True)
                max_retries = config.custom_params.get('max_retries', 3)
                
                # 使用fastq-dump下载
                result = self.fastq_downloader.download_with_fastq_dump(
                    accession=dataset_id,
                    output_dir=self.dir_save / "fastq",
                    split_files=split_files,
                    gzip_output=gzip_output,
                    max_retries=max_retries
                )
                
                # 如果需要，也获取元数据
                if result.get('success', False) and config.custom_params.get('include_metadata', True):
                    metadata = self._get_sra_metadata(dataset_id)
                    result['metadata'] = metadata
                
                return result
            
            else:
                raise ValueError(f"Unsupported SRA format: {config.data_format}")
        
        def download_sra_with_fastqdump(self,
                                      accession: str,
                                      split_files: bool = True,
                                      gzip_output: bool = True,
                                      **kwargs) -> Dict[str, Any]:
            """
            专门使用fastq-dump下载SRA数据
            
            Parameters:
            -----------
            accession : str
                SRA accession
            split_files : bool
                是否拆分paired-end文件
            gzip_output : bool
                是否gzip压缩
            **kwargs : 
                其他参数传递给download_with_fastq_dump
            
            Returns:
            --------
            Dict: 下载结果
            """
            return self.fastq_downloader.download_with_fastq_dump(
                accession=accession,
                output_dir=self.dir_save / "fastq",
                split_files=split_files,
                gzip_output=gzip_output,
                **kwargs
            )
    
    return EnhancedBioDataFetcher

# 使用示例
def example_enhanced_fetcher():
    """使用增强版的BioDataFetcher"""
    print("使用增强版BioDataFetcher（支持fastq-dump）")
    print("=" * 60)
    
    # 创建增强版fetcher
    EnhancedFetcher = enhance_bio_data_fetcher_with_fastqdump()
    fetcher = EnhancedFetcher(dir_save="./enhanced_cache")
    
    # 方法1：使用统一接口（会自动选择fastq-dump）
    print("\n方法1：使用统一接口")
    result1 = fetcher.fetch_data(
        dataset_ids="SRR390728",  # 测试用小文件
        data_type='sra',
        data_format='fastq',
        split_files=True,
        gzip_output=True,
        force_download=True
    )
    
    print(f"结果1: {result1.get('SRR390728', {}).get('success', False)}")
    
    # 方法2：直接使用fastq-dump方法
    print("\n方法2：直接使用fastq-dump方法")
    result2 = fetcher.download_sra_with_fastqdump(
        accession="SRR390728",
        split_files=True,
        gzip_output=True
    )
    
    print(f"结果2: 成功={result2.get('success', False)}, 文件数={result2.get('file_count', 0)}")
    
    # 方法3：批量下载
    print("\n方法3：批量下载测试")
    batch_result = fetcher.batch_fetch([
        {
            'dataset_id': 'SRR390728',
            'type': 'sra',
            'format': 'fastq',
            'split_files': True,
            'gzip_output': True
        },
        {
            'dataset_id': 'SRR3473776',  # 另一个小文件
            'type': 'sra', 
            'format': 'fastq',
            'split_files': False  # 单端数据
        }
    ])
    
    for acc, res in batch_result.items():
        print(f"  {acc}: 成功={res.get('success', False)}, 文件={len(res.get('files', []))}")
    
    return fetcher, result1, result2, batch_result

# 运行示例
# fetcher, r1, r2, batch = example_enhanced_fetcher()

def setup_sra_toolkit():
    """帮助用户安装和配置SRA Toolkit"""
    import platform
    import sys
    
    print("SRA Toolkit 安装助手")
    print("=" * 60)
    
    system = platform.system()
    print(f"操作系统: {system}")
    print(f"Python版本: {sys.version}")
    
    # 检查是否已安装
    fastq_dump_path = shutil.which("fastq-dump")
    prefetch_path = shutil.which("prefetch")
    
    if fastq_dump_path and prefetch_path:
        print("✅ SRA Toolkit 已安装")
        print(f"   fastq-dump: {fastq_dump_path}")
        print(f"   prefetch: {prefetch_path}")
        return True
    
    print("❌ SRA Toolkit 未安装或不在PATH中")
    print("\n安装指南:")
    
    if system == "Darwin":  # macOS
        print("""
  方法1: 使用Homebrew (推荐)
    brew install sratoolkit
  
  方法2: 手动下载
    1. 访问: https://github.com/ncbi/sra-tools/wiki/Downloads
    2. 下载macOS版本
    3. 解压并添加到PATH:
        echo 'export PATH=$PATH:/path/to/sratoolkit/bin' >> ~/.zshrc
        source ~/.zshrc
        """)
    
    elif system == "Linux":
        print("""
  方法1: 使用包管理器
    # Ubuntu/Debian
    sudo apt-get install sra-toolkit
    
    # CentOS/RHEL/Fedora
    sudo yum install sra-toolkit
  
  方法2: 手动下载
    1. 访问: https://github.com/ncbi/sra-tools/wiki/Downloads
    2. 下载Linux版本
    3. 解压并添加到PATH:
        echo 'export PATH=$PATH:/path/to/sratoolkit/bin' >> ~/.bashrc
        source ~/.bashrc
        """)
    
    elif system == "Windows":
        print("""
  方法1: 使用Chocolatey
    choco install sratoolkit
  
  方法2: 手动下载
    1. 访问: https://github.com/ncbi/sra-tools/wiki/Downloads
    2. 下载Windows版本
    3. 解压并将bin目录添加到系统PATH
        """)
    
    else:
        print(f"  不支持的操作系统: {system}")
    
    print("\n配置建议:")
    print("  1. 运行 'vdb-config -i' 进行交互式配置")
    print("  2. 设置缓存目录: vdb-config --set /repository/user/main/public/root=./ncbi_cache")
    print("  3. 测试: prefetch SRR390728 && fastq-dump SRR390728")
    
    return False

def configure_sra_toolkit():
    """配置SRA Toolkit（如果已安装）"""
    import subprocess
    
    print("配置SRA Toolkit")
    print("=" * 50)
    
    # 检查是否安装
    if not shutil.which("vdb-config"):
        print("❌ vdb-config 未找到，请先安装SRA Toolkit")
        return False
    
    try:
        # 设置缓存目录
        cache_dir = Path.home() / ".ncbi" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"设置缓存目录: {cache_dir}")
        
        # 运行vdb-config进行配置
        print("\n建议运行以下命令进行配置:")
        print(f"  vdb-config -i")
        print("\n或者使用命令行配置:")
        print(f"  vdb-config --set /repository/user/main/public/root={cache_dir}")
        print("  vdb-config --set /repository/user/main/public/apps/http/read-only=true")
        
        # 尝试设置
        try:
            subprocess.run(
                ["vdb-config", "--set", f"/repository/user/main/public/root={cache_dir}"],
                check=True,
                capture_output=True,
                text=True
            )
            print("✅ 缓存目录设置成功")
        except:
            print("⚠️  无法自动设置，请手动运行vdb-config")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置失败: {e}")
        return False

# 运行安装助手
# setup_sra_toolkit()
# configure_sra_toolkit()

def install_fastq_dump_helper():
    """提供fastq-dump安装帮助"""
    import platform
    import sys
    import subprocess
    import shutil
    
    print("🔧 fastq-dump 安装助手")
    print("=" * 60)
    
    # 获取系统信息
    system = platform.system()
    machine = platform.machine()
    python_version = sys.version_info
    
    print(f"操作系统: {system} ({machine})")
    print(f"Python版本: {sys.version[:20]}")
    
    # 检查当前状态
    tools = ['fastq-dump', 'prefetch', 'fasterq-dump']
    available = {}
    
    for tool in tools:
        path = shutil.which(tool)
        available[tool] = path
        status = "✅ 已安装" if path else "❌ 未安装"
        print(f"{tool}: {status}")
        if path:
            print(f"    路径: {path}")
            
            # 尝试获取版本
            try:
                result = subprocess.run(
                    [tool, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    version_line = result.stdout.split('\n')[0] if result.stdout else "未知"
                    print(f"    版本: {version_line}")
            except:
                pass
    
    print("\n" + "=" * 60)
    print("安装指南:")
    
    if system == "Darwin":  # macOS
        print("""
方法1: 使用Homebrew (推荐)
  ---------------------------------
  1. 安装Homebrew (如果尚未安装):
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  
  2. 安装SRA Toolkit:
     brew install sratoolkit
  
  3. 验证安装:
     fastq-dump --version
     prefetch --version

方法2: 使用Conda
  ---------------------------------
  1. 安装Miniconda或Anaconda
  2. 创建环境并安装:
     conda create -n sra-tools -c bioconda sra-tools
     conda activate sra-tools
  3. 验证: fastq-dump --version

方法3: 手动下载
  ---------------------------------
  1. 访问: https://github.com/ncbi/sra-tools/wiki/Downloads
  2. 下载macOS版本 (.dmg或.tar.gz)
  3. 解压并添加到PATH:
     echo 'export PATH=$PATH:/path/to/sratoolkit/bin' >> ~/.zshrc
     source ~/.zshrc
        """)
        
    elif system == "Linux":
        print("""
方法1: 使用包管理器 (Ubuntu/Debian)
  ---------------------------------
  1. 更新包列表:
     sudo apt-get update
  
  2. 安装SRA Toolkit:
     sudo apt-get install sra-toolkit
  
  3. 验证安装:
     fastq-dump --version

方法2: 使用包管理器 (CentOS/RHEL/Fedora)
  ---------------------------------
  1. 安装EPEL仓库 (CentOS/RHEL):
     sudo yum install epel-release
  
  2. 安装SRA Toolkit:
     sudo yum install sra-toolkit
     或
     sudo dnf install sra-toolkit (Fedora)
  
  3. 验证安装

方法3: 使用Conda
  ---------------------------------
  1. 安装Miniconda:
     wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
     bash Miniconda3-latest-Linux-x86_64.sh
  
  2. 安装SRA Toolkit:
     conda install -c bioconda sra-tools

方法4: 手动下载
  ---------------------------------
  1. 访问: https://github.com/ncbi/sra-tools/wiki/Downloads
  2. 下载Linux版本 (.tar.gz)
  3. 解压并添加到PATH:
     tar -xzvf sratoolkit.*.tar.gz
     echo 'export PATH=$PATH:/path/to/sratoolkit/bin' >> ~/.bashrc
     source ~/.bashrc
        """)
        
    elif system == "Windows":
        print("""
方法1: 使用Chocolatey (推荐)
  ---------------------------------
  1. 安装Chocolatey (如果尚未安装):
     以管理员身份打开PowerShell，运行:
     Set-ExecutionPolicy Bypass -Scope Process -Force
     [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
     iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
  
  2. 安装SRA Toolkit:
     choco install sratoolkit
  
  3. 验证安装:
     fastq-dump --version

方法2: 使用Conda
  ---------------------------------
  1. 安装Miniconda: https://docs.conda.io/en/latest/miniconda.html
  2. 安装SRA Toolkit:
     conda install -c bioconda sra-tools

方法3: 手动下载
  ---------------------------------
  1. 访问: https://github.com/ncbi/sra-tools/wiki/Downloads
  2. 下载Windows版本 (.exe安装程序)
  3. 运行安装程序，确保勾选"Add to PATH"
        """)
        
    else:
        print(f"⚠️  不支持的操作系统: {system}")
        print("请手动访问: https://github.com/ncbi/sra-tools/wiki/Downloads")
    
    print("\n" + "=" * 60)
    print("配置建议:")
    
    if any(available.values()):
        print("运行以下命令进行配置:")
        print("  vdb-config -i  (交互式配置)")
        print("\n或使用命令行配置:")
        print("  vdb-config --set /repository/user/main/public/root=./ncbi_cache")
        print("  vdb-config --set /repository/user/main/public/apps/http/read-only=true")
    else:
        print("请先安装SRA Toolkit，然后运行上述配置命令")
    
    return available

# 运行安装助手
# install_fastq_dump_helper()




if __name__ == "__main__":
    # 演示如何使用
    print("BioDataFetcher 演示")
    print("=" * 50)
    
    # 创建fetcher实例
    fetcher = BioDataFetcher(dir_save="./test_cache")
    
    # 示例1: 自动推断并获取GEO数据
    print("\n1. 获取GEO数据 (自动推断):")
    geo_data = fetcher.fetch_data("GSE12345")
    print(f"  获取到数据: {type(geo_data)}")
    
    # 示例2: 获取SRA元数据
    print("\n2. 获取SRA元数据:")
    sra_meta = fetcher.fetch_data("SRR1635435", data_format="metadata")
    print(f"  获取到元数据: {type(sra_meta)}")
    
    # 示例3: 搜索数据集
    print("\n3. 搜索癌症相关数据集:")
    search_results = fetcher.list_datasets(search_query="cancer RNA-seq", limit=5)
    if not search_results.empty:
        print(f"  找到 {len(search_results)} 个数据集:")
        for _, row in search_results.iterrows():
            print(f"    {row['accession']}: {row['title'][:50]}...")
    
    # 示例4: 查看缓存
    print("\n4. 查看缓存数据:")
    cached = fetcher.cache_list()
    if not cached.empty:
        print(f"  有 {len(cached)} 个缓存数据集")
    
    # 示例5: 获取统计信息
    print("\n5. 统计信息:")
    stats = fetcher.get_statistics()
    print(f"  总数据集数: {stats['total_datasets']}")
    print(f"  缓存大小: {stats['total_size_gb']:.2f} GB")
