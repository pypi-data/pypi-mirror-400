#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, Literal, List, Union
from .destinations import Destination


class ParseConfig:
    """Parse 配置，支持动态字段"""

    def __init__(self, provider: Literal["textin", "mineru", "paddle", "textin-lite"] = "textin", **kwargs):
        self.provider = provider
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        result = {'provider': self.provider}
        for key, value in self.__dict__.items():
            if not key.startswith('_') and key != 'provider':
                result[key] = value
        return result

    def __repr__(self) -> str:
        attrs = ', '.join(f'{k}={v!r}' for k, v in sorted(self.__dict__.items()) if not k.startswith('_'))
        return f'ParseConfig({attrs})'


@dataclass
class ChunkConfig:
    """Chunk 配置"""
    strategy: Literal["basic", "by_title", "by_page"] = "basic"
    include_orig_elements: bool = False
    new_after_n_chars: int = 512
    max_characters: int = 1024
    overlap: int = 0
    overlap_all: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EmbedConfig:
    """Embed 配置"""
    provider: Literal["qwen", "doubao"] = "qwen"
    model_name: Literal[
        "text-embedding-v3",
        "text-embedding-v4",
        "doubao-embedding-large-text-250515",
        "doubao-embedding-text-240715"
    ] = "text-embedding-v3"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def validate(self) -> None:
        provider_models = {
            "qwen": ["text-embedding-v3", "text-embedding-v4"],
            "doubao": ["doubao-embedding-large-text-250515", "doubao-embedding-text-240715"]
        }
        if self.provider not in provider_models:
            raise ValueError(f"不支持的 provider: {self.provider}, 支持的有: {list(provider_models.keys())}")
        if self.model_name not in provider_models[self.provider]:
            raise ValueError(
                f"provider '{self.provider}' 不支持模型 '{self.model_name}', 支持的模型: {provider_models[self.provider]}"
            )


@dataclass
class Stage:
    """Pipeline Stage 配置"""
    type: Literal["parse", "chunk", "embed"]
    config: Union[ParseConfig, ChunkConfig, EmbedConfig, Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于 API 请求"""
        if isinstance(self.config, (ParseConfig, ChunkConfig, EmbedConfig)):
            return {
                'type': self.type,
                'config': self.config.to_dict()
            }
        else:
            # 如果 config 已经是字典，直接使用
            return {
                'type': self.type,
                'config': self.config
            }

    def __repr__(self) -> str:
        return f"Stage(type={self.type!r}, config={self.config!r})"


@dataclass
class PipelineStats:
    """Pipeline 统计信息"""
    original_elements: int = 0
    chunked_elements: int = 0
    embedded_elements: int = 0
    stages: Optional[List[Stage]] = None  # 存储实际执行的 stages
    record_id: Optional[str] = None  # 记录 ID，用于标识需要写入 Milvus 的记录


@dataclass
class PipelineConfig:
    """Pipeline 配置"""
    include_intermediate_results: bool = False
    intermediate_results_destination: Optional[Destination] = None  # 支持 Destination 类型，如 LocalDestination、S3Destination 等

    def __post_init__(self):
        """验证配置"""
        if self.include_intermediate_results and not self.intermediate_results_destination:
            raise ValueError("当 include_intermediate_results 为 True 时，必须设置 intermediate_results_destination")

    def to_dict(self) -> Dict[str, Any]:
        return {
            'include_intermediate_results': self.include_intermediate_results,
        }


__all__ = [
    'ParseConfig',
    'ChunkConfig',
    'EmbedConfig',
    'Stage',
    'PipelineStats',
    'PipelineConfig',
]

