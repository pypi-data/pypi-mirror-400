#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json
import logging
import uuid
import boto3

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from botocore.config import Config
from pymilvus import MilvusClient
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, PayloadSchemaType

logger = logging.getLogger(__name__)


def _flatten_dict(data: Dict[str, Any], prefix: str = '', fixed_fields: set = None) -> Dict[str, Any]:
    """递归展平嵌套字典
    
    Args:
        data: 要展平的字典
        prefix: 键的前缀
        fixed_fields: 需要排除的字段集合
        
    Returns:
        展平后的字典
    """
    if fixed_fields is None:
        fixed_fields = set()
    
    result = {}
    for key, value in data.items():
        flat_key = f'{prefix}_{key}' if prefix else key
        
        if flat_key in fixed_fields:
            continue
        
        if isinstance(value, dict):
            # 递归展平嵌套字典
            nested = _flatten_dict(value, flat_key, fixed_fields)
            result.update(nested)
        elif isinstance(value, list):
            # 列表转换为 JSON 字符串
            result[flat_key] = json.dumps(value, ensure_ascii=False)
        else:
            # 其他类型直接使用
            result[flat_key] = value
    
    return result


class Destination(ABC):
    """数据目的地抽象基类"""

    @abstractmethod
    def write(self, data: List[Dict[str, Any]], metadata: Dict[str, Any]) -> bool:
        """写入数据"""
        raise NotImplementedError


class MilvusDestination(Destination):
    """Milvus/Zilliz 向量数据库目的地"""

    def __init__(self, db_path: str, collection_name: str, dimension: int, api_key: str = None, token: str = None):
        from pymilvus import DataType

        self.db_path = db_path
        self.collection_name = collection_name
        self.dimension = dimension

        client_kwargs = {'uri': db_path}
        if api_key:
            client_kwargs['token'] = api_key
        elif token:
            client_kwargs['token'] = token

        self.client = MilvusClient(**client_kwargs)

        if not self.client.has_collection(collection_name):
            schema = self.client.create_schema(
                auto_id=False,
                enable_dynamic_field=True
            )

            schema.add_field(field_name="element_id", datatype=DataType.VARCHAR, max_length=128, is_primary=True)
            schema.add_field(field_name="embeddings", datatype=DataType.FLOAT_VECTOR, dim=dimension)
            schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
            schema.add_field(field_name="record_id", datatype=DataType.VARCHAR, max_length=200)

            index_params = self.client.prepare_index_params()
            index_params.add_index(
                field_name="embeddings",
                index_type="AUTOINDEX",
                metric_type="COSINE"
            )

            self.client.create_collection(
                collection_name=collection_name,
                schema=schema,
                index_params=index_params
            )
            print(f"✓ Milvus/Zilliz 集合创建: {collection_name} (自定义 Schema)")
        else:
            print(f"✓ Milvus/Zilliz 集合存在: {collection_name}")

        logger.info(f"Milvus/Zilliz 连接成功: {db_path}")

    def write(self, data: List[Dict[str, Any]], metadata: Dict[str, Any]) -> bool:
        try:
            # 如果 metadata 中有 record_id，先删除相同 record_id 的现有记录
            record_id = metadata.get('record_id')
            if record_id:
                try:
                    # 删除相同 record_id 的所有记录
                    # MilvusClient.delete 返回删除的记录数（可能是 int 或 dict）
                    result = self.client.delete(
                        collection_name=self.collection_name,
                        filter=f'record_id == "{record_id}"'
                    )
                    # 处理返回值：可能是数字或字典
                    deleted_count = result if isinstance(result, int) else result.get('delete_count', 0) if isinstance(result, dict) else 0
                    if deleted_count > 0:
                        print(f"  ✓ 删除现有记录: record_id={record_id}, 删除 {deleted_count} 条")
                        logger.info(f"删除 Milvus 现有记录: record_id={record_id}, 删除 {deleted_count} 条")
                    else:
                        print(f"  → 准备写入记录: record_id={record_id}")
                except Exception as e:
                    print(f"  ! 删除现有记录失败: {str(e)}")
                    logger.warning(f"删除 Milvus 现有记录失败: record_id={record_id}, {str(e)}")
                    # 继续执行写入，不因为删除失败而中断
            else:
                print(f"  → 没有 record_id")
                logger.warning(f"没有 record_id")
                return
            
            insert_data = []
            for item in data:
                # 获取元素级别的 metadata
                element_metadata = item.get('metadata', {})
                
                if 'embeddings' in item and item['embeddings']:
                    element_id = item.get('element_id') or item.get('id') or str(uuid.uuid4())
                    
                    # 构建基础数据
                    insert_item = {
                        'embeddings': item['embeddings'],
                        'text': item.get('text', ''),
                        'element_id': element_id,
                        'record_id': record_id
                    }
                    
                    # 合并文件级别的 metadata 和元素级别的 metadata
                    # 文件级别的 metadata 优先级更高
                    merged_metadata = {**element_metadata, **metadata}
                    
                    # 将 metadata 中的字段展平到顶层作为动态字段
                    # 排除已存在的固定字段，避免冲突
                    fixed_fields = {'embeddings', 'text', 'element_id', 'record_id', 'created_at', 'metadata'}
                    for key, value in merged_metadata.items():
                        if key not in fixed_fields:
                            # 特殊处理 data_source 字段：如果是字典则递归展平
                            if key == 'data_source' and isinstance(value, dict):
                                # 递归展平 data_source 字典，包括嵌套的字典
                                flattened = _flatten_dict(value, 'data_source', fixed_fields)
                                insert_item.update(flattened)
                            elif key == 'coordinates' and isinstance(value, list):
                                insert_item[key] = value
                            elif isinstance(value, (dict, list)):
                                continue
                            else:
                                insert_item[key] = value
                    
                    insert_data.append(insert_item)

            if not insert_data:
                print(f"  ! 警告: 没有有效的向量数据")
                return False

            self.client.insert(
                collection_name=self.collection_name,
                data=insert_data
            )
            print(f"  ✓ 写入 Milvus: {len(insert_data)} 条")
            logger.info(f"写入 Milvus 成功: {len(insert_data)} 条")
            return True
        except Exception as e:
            print(f"  ✗ 写入 Milvus 失败: {str(e)}")
            logger.error(f"写入 Milvus 失败: {str(e)}")
            return False


class LocalDestination(Destination):
    """本地文件系统目的地"""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ 输出目录: {self.output_dir}")
        logger.info(f"输出目录: {self.output_dir}")

    def write(self, data: List[Dict[str, Any]], metadata: Dict[str, Any]) -> bool:
        try:
            filename = metadata.get('filename', 'output')
            base_name = Path(filename).stem
            stage = metadata.get('stage')  # 用于区分中间结果的阶段
            
            # 如果是中间结果，在文件名中添加阶段标识
            if stage:
                output_file = self.output_dir / f"{base_name}_{stage}.json"
            else:
                output_file = self.output_dir / f"{base_name}.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"  ✓ 写入本地: {output_file}")
            logger.info(f"写入本地成功: {output_file}")
            return True
        except Exception as e:
            print(f"  ✗ 写入本地失败: {str(e)}")
            logger.error(f"写入本地失败: {str(e)}")
            return False


class S3Destination(Destination):
    """S3/MinIO 数据目的地"""

    def __init__(self, endpoint: str, access_key: str, secret_key: str,
                 bucket: str, prefix: str = '', region: str = 'us-east-1'):
        self.endpoint = endpoint
        self.bucket = bucket
        self.prefix = prefix.strip('/') if prefix else ''

        if self.endpoint == 'https://textin-minio-api.ai.intsig.net':
            config = Config(signature_version='s3v4')
        elif self.endpoint.endswith('aliyuncs.com'):
            config = Config(signature_version='s3', s3={'addressing_style': 'virtual'})
        elif self.endpoint.endswith('myhuaweicloud.com'):
            config = Config(signature_version='s3', s3={'addressing_style': 'virtual'})
        else:
            config = Config(signature_version='s3v4', s3={'addressing_style': 'virtual'})

        self.client = boto3.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            config=config
        )

        try:
            self.client.head_bucket(Bucket=bucket)
            test_key = f"{self.prefix}/empty.tmp" if self.prefix else f"empty.tmp"
            self.client.put_object(
                Bucket=bucket,
                Key=test_key,
                Body=b''
            )
            try:
                self.client.delete_object(Bucket=bucket, Key=test_key)
            except Exception:
                pass

            print(f"✓ S3 连接成功且可写: {endpoint}/{bucket}")
            logger.info(f"S3 连接成功且可写: {endpoint}/{bucket}")
        except Exception as e:
            print(f"✗ S3 连接或写入测试失败: {str(e)}")
            logger.error(f"S3 连接或写入测试失败: {str(e)}")
            raise

    def write(self, data: List[Dict[str, Any]], metadata: Dict[str, Any]) -> bool:
        try:
            filename = metadata.get('filename', 'output')
            base_name = Path(filename).stem
            object_key = f"{self.prefix}/{base_name}.json" if self.prefix else f"{base_name}.json"

            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            json_bytes = json_data.encode('utf-8')

            self.client.put_object(
                Bucket=self.bucket,
                Key=object_key,
                Body=json_bytes,
                ContentType='application/json'
            )

            print(f"  ✓ 写入 S3: {self.endpoint}/{self.bucket}/{object_key}")
            logger.info(f"写入 S3 成功: {self.endpoint}/{self.bucket}/{object_key}")
            return True
        except Exception as e:
            print(f"  ✗ 写入 S3 失败: {str(e)}")
            logger.error(f"写入 S3 失败: {str(e)}")
            return False


class QdrantDestination(Destination):
    """Qdrant 向量数据库目的地"""

    def __init__(self, url: str, collection_name: str, dimension: int, api_key: str = None, prefer_grpc: bool = False):
        """初始化 Qdrant 目的地
        
        Args:
            url: Qdrant 服务地址（如 'http://localhost:6333' 或 'https://xxx.qdrant.io'）
            collection_name: Collection 名称
            dimension: 向量维度
            api_key: API Key（可选，用于 Qdrant Cloud）
            prefer_grpc: 是否优先使用 gRPC（默认 False，使用 HTTP）
        """
        
        self.url = url
        self.collection_name = collection_name
        self.dimension = dimension
        
        client_kwargs = {'url': url}
        if api_key:
            client_kwargs['api_key'] = api_key
        if prefer_grpc:
            client_kwargs['prefer_grpc'] = True
        
        self.client = QdrantClient(**client_kwargs)
        
        # 检查或创建 collection
        try:
            collections = self.client.get_collections()
            collection_exists = any(col.name == collection_name for col in collections.collections)
            
            if not collection_exists:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=dimension,
                        distance=Distance.COSINE
                    )
                )
                # 为 record_id 创建索引，用于过滤查询
                try:
                    self.client.create_payload_index(
                        collection_name=collection_name,
                        field_name="record_id",
                        field_schema=PayloadSchemaType.KEYWORD
                    )
                    print(f"✓ Qdrant Collection 创建: {collection_name} (维度: {dimension})")
                except Exception as e:
                    logger.warning(f"创建 record_id 索引失败（可能已存在）: {str(e)}")
                    print(f"✓ Qdrant Collection 创建: {collection_name} (维度: {dimension})")
            else:
                print(f"✓ Qdrant Collection 存在: {collection_name}")
                # 确保 record_id 索引存在（如果不存在则创建）
                try:
                    self.client.create_payload_index(
                        collection_name=collection_name,
                        field_name="record_id",
                        field_schema=PayloadSchemaType.KEYWORD
                    )
                except Exception as e:
                    # 索引可能已存在，忽略错误
                    logger.debug(f"record_id 索引可能已存在: {str(e)}")
            
            logger.info(f"Qdrant 连接成功: {url}/{collection_name}")
        except Exception as e:
            print(f"✗ Qdrant 连接失败: {str(e)}")
            logger.error(f"Qdrant 连接失败: {str(e)}")
            raise

    def write(self, data: List[Dict[str, Any]], metadata: Dict[str, Any]) -> bool:
        try:
            # 如果 metadata 中有 record_id，先删除相同 record_id 的现有记录
            record_id = metadata.get('record_id')
            if record_id:
                try:
                    # 查询并删除相同 record_id 的所有记录
                    # 使用字典格式的 filter（兼容性更好）
                    scroll_result = self.client.scroll(
                        collection_name=self.collection_name,
                        scroll_filter={
                            "must": [
                                {
                                    "key": "record_id",
                                    "match": {"value": record_id}
                                }
                            ]
                        },
                        limit=10000  # 假设单次最多删除 10000 条
                    )
                    
                    if scroll_result[0]:  # 有记录
                        point_ids = [point.id for point in scroll_result[0]]
                        self.client.delete(
                            collection_name=self.collection_name,
                            points_selector=point_ids
                        )
                        print(f"  ✓ 删除现有记录: record_id={record_id}, 删除 {len(point_ids)} 条")
                        logger.info(f"删除 Qdrant 现有记录: record_id={record_id}, 删除 {len(point_ids)} 条")
                    else:
                        print(f"  → 准备写入记录: record_id={record_id}")
                except Exception as e:
                    print(f"  ! 删除现有记录失败: {str(e)}")
                    logger.warning(f"删除 Qdrant 现有记录失败: record_id={record_id}, {str(e)}")
                    # 继续执行写入，不因为删除失败而中断
            else:
                print(f"  → 没有 record_id")
                logger.warning(f"没有 record_id")
                return False
            
            points = []
            for item in data:
                # 获取元素级别的 metadata
                element_metadata = item.get('metadata', {})
                
                if 'embeddings' in item and item['embeddings']:
                    element_id = item.get('element_id') or item.get('id') or str(uuid.uuid4())
                    
                    # 构建 payload（元数据）
                    payload = {
                        'text': item.get('text', ''),
                        'record_id': record_id,
                    }
                    
                    # 合并文件级别的 metadata 和元素级别的 metadata
                    # 文件级别的 metadata 优先级更高
                    merged_metadata = {**element_metadata, **metadata}
                    
                    # 将 metadata 中的字段添加到 payload
                    # 排除已存在的固定字段，避免冲突
                    fixed_fields = {'embeddings', 'text', 'element_id', 'record_id', 'created_at', 'metadata'}
                    for key, value in merged_metadata.items():
                        if key not in fixed_fields:
                            # 特殊处理 data_source 字段：如果是字典则递归展平
                            if key == 'data_source' and isinstance(value, dict):
                                # 递归展平 data_source 字典，包括嵌套的字典
                                flattened = _flatten_dict(value, 'data_source', fixed_fields)
                                payload.update(flattened)
                            elif key == 'coordinates' and isinstance(value, list):
                                payload[key] = value
                            elif isinstance(value, (dict, list)):
                                # Qdrant 支持 JSON 格式的 payload
                                payload[key] = value
                            else:
                                payload[key] = value
                    
                    # 创建 Point（id 是必需的）
                    # Qdrant 的 point id 可以是整数或 UUID 字符串
                    # 如果 element_id 是 UUID 格式，直接使用；否则转换为 UUID5（基于 element_id 生成稳定的 UUID）
                    try:
                        # 尝试将 element_id 解析为 UUID
                        point_id = str(uuid.UUID(element_id))
                    except (ValueError, TypeError):
                        # 如果不是有效的 UUID，使用 UUID5 基于 element_id 生成稳定的 UUID
                        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, str(element_id)))
                    
                    point = PointStruct(
                        id=point_id,
                        vector=item['embeddings'],
                        payload=payload
                    )
                    points.append(point)

            if not points:
                print(f"  ! 警告: 没有有效的向量数据")
                return False

            # 批量插入
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            print(f"  ✓ 写入 Qdrant: {len(points)} 条")
            logger.info(f"写入 Qdrant 成功: {len(points)} 条")
            return True
        except Exception as e:
            print(f"  ✗ 写入 Qdrant 失败: {str(e)}")
            logger.error(f"写入 Qdrant 失败: {str(e)}")
            return False


__all__ = [
    'Destination',
    'MilvusDestination',
    'QdrantDestination',
    'LocalDestination',
    'S3Destination',
]

