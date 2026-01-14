import logging
from pathlib import Path
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
    encoding='utf-8'
)

from .pipeline.config import ParseConfig, ChunkConfig, EmbedConfig, Stage, PipelineStats, PipelineConfig
from .pipeline.sources import Source, S3Source, LocalSource, FtpSource, SmbSource
from .pipeline.destinations import Destination, MilvusDestination, QdrantDestination, LocalDestination, S3Destination
from .pipeline.pipeline import Pipeline, create_pipeline_from_config

__all__ = [
    'ParseConfig',
    'ChunkConfig',
    'EmbedConfig',
    'Stage',
    'PipelineStats',
    'PipelineConfig',
    'Source',
    'S3Source',
    'LocalSource',
    'FtpSource',
    'SmbSource',
    'Destination',
    'MilvusDestination',
    'QdrantDestination',
    'LocalDestination',
    'S3Destination',
    'Pipeline',
    'create_pipeline_from_config',
]

# 自动从 pyproject.toml 读取版本号
def _get_version():
    """从 pyproject.toml 读取版本号"""
    try:
        # 优先尝试从已安装的包中读取版本
        from importlib.metadata import version
        return version('xparse-client')
    except Exception:
        # 如果包未安装，从 pyproject.toml 读取
        pyproject_path = Path(__file__).parent.parent / 'pyproject.toml'
        if pyproject_path.exists():
            content = pyproject_path.read_text(encoding='utf-8')
            # 使用正则表达式匹配 version = "x.x.x"
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
        return '0.0.0'

__version__ = _get_version()
