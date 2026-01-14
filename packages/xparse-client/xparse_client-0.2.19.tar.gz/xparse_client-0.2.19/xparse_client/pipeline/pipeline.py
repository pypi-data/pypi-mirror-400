#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List, Union

import requests

from .config import ParseConfig, ChunkConfig, EmbedConfig, Stage, PipelineStats, PipelineConfig
from .sources import Source, S3Source, LocalSource, FtpSource, SmbSource
from .destinations import Destination, MilvusDestination, QdrantDestination, LocalDestination, S3Destination


logger = logging.getLogger(__name__)


class Pipeline:
    """数据处理 Pipeline"""

    def __init__(
        self,
        source: Source,
        destination: Destination,
        api_base_url: str = 'http://localhost:8000/api/xparse',
        api_headers: Optional[Dict[str, str]] = None,
        stages: Optional[List[Stage]] = None,
        pipeline_config: Optional[PipelineConfig] = None,
        intermediate_results_destination: Optional[Destination] = None
    ):
        self.source = source
        self.destination = destination
        self.api_base_url = api_base_url.rstrip('/')
        self.api_headers = api_headers or {}
        self.pipeline_config = pipeline_config or PipelineConfig()

        # 处理 intermediate_results_destination 参数
        # 如果直接传入了 intermediate_results_destination，优先使用它并自动启用中间结果保存
        if intermediate_results_destination is not None:
            self.pipeline_config.include_intermediate_results = True
            self.pipeline_config.intermediate_results_destination = intermediate_results_destination
        # 如果 pipeline_config 中已设置，使用 pipeline_config 中的值
        elif self.pipeline_config.include_intermediate_results:
            if not self.pipeline_config.intermediate_results_destination:
                raise ValueError("当 include_intermediate_results 为 True 时，必须设置 intermediate_results_destination")

        # 处理 stages 配置
        if stages is None:
            raise ValueError("必须提供 stages 参数")
        
        self.stages = stages

        # 验证 stages
        if not self.stages or self.stages[0].type != 'parse':
            raise ValueError("stages 必须包含且第一个必须是 'parse' 类型")
        
        # 验证 embed config（如果存在）
        for stage in self.stages:
            if stage.type == 'embed' and isinstance(stage.config, EmbedConfig):
                stage.config.validate()
        
        # 验证 intermediate_results_destination
        if self.pipeline_config.include_intermediate_results:
            # 验证是否为支持的 Destination 类型
            from .destinations import Destination
            if not isinstance(self.pipeline_config.intermediate_results_destination, Destination):
                raise ValueError(f"intermediate_results_destination 必须是 Destination 类型")
            self.intermediate_results_destination = self.pipeline_config.intermediate_results_destination

        print("=" * 60)
        print("Pipeline 初始化完成")
        print(f"  Stages: {[s.type for s in self.stages]}")
        for stage in self.stages:
            print(f"    - {stage.type}: {stage.config}")
        if self.pipeline_config.include_intermediate_results:
            print(f"  Pipeline Config: 中间结果保存已启用")
        print("=" * 60)

    def get_config(self) -> Dict[str, Any]:
        """获取 Pipeline 的完整配置信息，返回字典格式（与 create_pipeline_from_config 的入参格式一致）"""
        config = {}
        
        # Source 配置
        source_type = type(self.source).__name__.replace('Source', '').lower()
        config['source'] = {'type': source_type}
        
        if isinstance(self.source, S3Source):
            config['source'].update({
                'endpoint': self.source.endpoint,
                'bucket': self.source.bucket,
                'prefix': self.source.prefix,
                'pattern': self.source.pattern,
                'recursive': self.source.recursive
            })
            # access_key 和 secret_key 不在对象中保存，无法恢复
            # region 也不在对象中保存，使用默认值
            config['source']['region'] = 'us-east-1'  # 默认值
        elif isinstance(self.source, LocalSource):
            config['source'].update({
                'directory': str(self.source.directory),
                'pattern': self.source.pattern,
                'recursive': self.source.recursive
            })
        elif isinstance(self.source, FtpSource):
            config['source'].update({
                'host': self.source.host,
                'port': self.source.port,
                'username': self.source.username,
                'pattern': self.source.pattern,
                'recursive': self.source.recursive
            })
            # password 不在对象中保存，无法恢复
        elif isinstance(self.source, SmbSource):
            config['source'].update({
                'host': self.source.host,
                'share_name': self.source.share_name,
                'username': self.source.username,
                'domain': self.source.domain,
                'port': self.source.port,
                'path': self.source.path,
                'pattern': self.source.pattern,
                'recursive': self.source.recursive
            })
            # password 不在对象中保存，无法恢复
        
        # Destination 配置
        dest_type = type(self.destination).__name__.replace('Destination', '').lower()
        # MilvusDestination 和 Zilliz 都使用 'milvus' 或 'zilliz' 类型
        if dest_type == 'milvus':
            # 判断是本地 Milvus 还是 Zilliz（通过 db_path 判断）
            if self.destination.db_path.startswith('http'):
                dest_type = 'zilliz'
            else:
                dest_type = 'milvus'
        
        config['destination'] = {'type': dest_type}
        
        if isinstance(self.destination, MilvusDestination):
            config['destination'].update({
                'db_path': self.destination.db_path,
                'collection_name': self.destination.collection_name,
                'dimension': self.destination.dimension
            })
            # api_key 和 token 不在对象中保存，无法恢复
        elif isinstance(self.destination, QdrantDestination):
            config['destination'].update({
                'url': self.destination.url,
                'collection_name': self.destination.collection_name,
                'dimension': self.destination.dimension,
                'prefer_grpc': getattr(self.destination, 'prefer_grpc', False)
            })
            # api_key 不在对象中保存，无法恢复
        elif isinstance(self.destination, LocalDestination):
            config['destination'].update({
                'output_dir': str(self.destination.output_dir)
            })
        elif isinstance(self.destination, S3Destination):
            config['destination'].update({
                'endpoint': self.destination.endpoint,
                'bucket': self.destination.bucket,
                'prefix': self.destination.prefix
            })
            # access_key, secret_key, region 不在对象中保存，无法恢复
            config['destination']['region'] = 'us-east-1'  # 默认值
        
        # API 配置
        config['api_base_url'] = self.api_base_url
        config['api_headers'] = {}
        for key, value in self.api_headers.items():
            config['api_headers'][key] = value
        
        # Stages 配置
        config['stages'] = []
        for stage in self.stages:
            stage_dict = {
                'type': stage.type,
                'config': {}
            }
            
            if isinstance(stage.config, ParseConfig):
                stage_dict['config'] = stage.config.to_dict()
            elif isinstance(stage.config, ChunkConfig):
                stage_dict['config'] = stage.config.to_dict()
            elif isinstance(stage.config, EmbedConfig):
                stage_dict['config'] = stage.config.to_dict()
            else:
                # 如果 config 是字典或其他类型，尝试转换
                if isinstance(stage.config, dict):
                    stage_dict['config'] = stage.config
                else:
                    stage_dict['config'] = str(stage.config)
            
            config['stages'].append(stage_dict)
        
        # Pipeline Config
        if self.pipeline_config.include_intermediate_results:
            config['pipeline_config'] = {
                'include_intermediate_results': True,
                'intermediate_results_destination': {}
            }
            
            inter_dest = self.pipeline_config.intermediate_results_destination
            if inter_dest:
                inter_dest_type = type(inter_dest).__name__.replace('Destination', '').lower()
                config['pipeline_config']['intermediate_results_destination']['type'] = inter_dest_type
                
                if isinstance(inter_dest, LocalDestination):
                    config['pipeline_config']['intermediate_results_destination']['output_dir'] = str(inter_dest.output_dir)
                elif isinstance(inter_dest, S3Destination):
                    config['pipeline_config']['intermediate_results_destination'].update({
                        'endpoint': inter_dest.endpoint,
                        'bucket': inter_dest.bucket,
                        'prefix': inter_dest.prefix
                    })
                    # access_key, secret_key, region 不在对象中保存，无法恢复
                    config['pipeline_config']['intermediate_results_destination']['region'] = 'us-east-1'  # 默认值
        
        return config

    def _extract_error_message(self, response: requests.Response) -> Tuple[str, str]:
        """
        从响应中提取规范化的错误信息
        
        Returns:
            Tuple[str, str]: (error_msg, x_request_id)
        """
        # 首先尝试从响应头中提取 x-request-id（requests的headers大小写不敏感）
        x_request_id = response.headers.get('x-request-id', '')
        error_msg = ''
        
        # 获取Content-Type
        content_type = response.headers.get('Content-Type', '').lower()
        
        # 尝试解析JSON响应
        if 'application/json' in content_type:
            try:
                result = response.json()
                # 如果响应头中没有x-request-id，尝试从响应体中获取
                if not x_request_id:
                    x_request_id = result.get('x_request_id', '')
                error_msg = result.get('message', result.get('msg', f'HTTP {response.status_code}'))
                return error_msg, x_request_id
            except:
                pass
        
        # 处理HTML响应
        if 'text/html' in content_type or response.text.strip().startswith('<'):
            try:
                # 从HTML中提取标题（通常包含状态码和状态文本）
                title_match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE)
                if title_match:
                    error_msg = title_match.group(1).strip()
                else:
                    # 如果没有title，尝试提取h1标签
                    h1_match = re.search(r'<h1>(.*?)</h1>', response.text, re.IGNORECASE)
                    if h1_match:
                        error_msg = h1_match.group(1).strip()
                    else:
                        error_msg = f'HTTP {response.status_code}'
            except:
                error_msg = f'HTTP {response.status_code}'
        
        # 处理纯文本响应
        elif 'text/plain' in content_type:
            error_msg = response.text[:200].strip() if response.text else f'HTTP {response.status_code}'
        
        # 其他情况
        else:
            if response.text:
                # 尝试截取前200字符，但去除换行和多余空格
                text = response.text[:200].strip()
                # 如果包含多行，只取第一行
                if '\n' in text:
                    text = text.split('\n')[0].strip()
                error_msg = text if text else f'HTTP {response.status_code}'
            else:
                error_msg = f'HTTP {response.status_code}'
        
        return error_msg, x_request_id

    def _call_pipeline_api(self, file_bytes: bytes, filename: str, data_source: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        url = f"{self.api_base_url}/pipeline"
        max_retries = 3

        for try_count in range(max_retries):
            try:
                files = {'file': (filename or 'file', file_bytes)}
                form_data = {}

                # 将 stages 转换为 API 格式
                stages_data = [stage.to_dict() for stage in self.stages]
                try:
                    form_data['stages'] = json.dumps(stages_data)
                    form_data['data_source'] = json.dumps(data_source, ensure_ascii=False)
                    
                    # 如果启用了中间结果保存，在请求中添加参数
                    if self.pipeline_config:
                        form_data['config'] = json.dumps(self.pipeline_config.to_dict(), ensure_ascii=False)
                except Exception as e:
                    print(f"  ✗ 入参处理失败，请检查配置: {e}")
                    logger.error(f"入参处理失败，请检查配置: {e}")
                    return None

                response = requests.post(
                    url,
                    files=files,
                    data=form_data,
                    headers=self.api_headers,
                    timeout=630
                )

                if response.status_code == 200:
                    result = response.json()
                    x_request_id = result.get('x_request_id', '')
                    print(f"  ✓ Pipeline 接口返回 x_request_id: {x_request_id}")
                    if result.get('code') == 200 and 'data' in result:
                        return result.get('data')
                    # 如果 code 不是 200，打印错误信息
                    error_msg = result.get('message', result.get('msg', '未知错误'))
                    print(f"  ✗ Pipeline 接口返回错误: code={result.get('code')}, message={error_msg}, x_request_id={x_request_id}")
                    logger.error(f"Pipeline 接口返回错误: code={result.get('code')}, message={error_msg}, x_request_id={x_request_id}")
                    return None
                else:
                    # 使用规范化函数提取错误信息
                    error_msg, x_request_id = self._extract_error_message(response)
                    
                    print(f"  ✗ API 错误 {response.status_code}: {error_msg}, x_request_id={x_request_id}, 重试 {try_count + 1}/{max_retries}")
                    logger.warning(f"API 错误 {response.status_code}: {error_msg}, x_request_id={x_request_id}, 重试 {try_count + 1}/{max_retries}")

            except Exception as e:
                # 如果是 requests 异常，尝试从响应中获取 x_request_id
                x_request_id = ''
                error_msg = str(e)
                try:
                    if hasattr(e, 'response') and e.response is not None:
                        try:
                            result = e.response.json()
                            x_request_id = result.get('x_request_id', '')
                            error_msg = result.get('message', result.get('msg', error_msg))
                        except:
                            pass
                except:
                    pass
                
                print(f"  ✗ 请求异常: {error_msg}, x_request_id={x_request_id}, 重试 {try_count + 1}/{max_retries}")
                logger.error(f"API 请求异常 pipeline: {error_msg}, x_request_id={x_request_id}")

            if try_count < max_retries - 1:
                time.sleep(2)

        return None

    def process_with_pipeline(self, file_bytes: bytes, filename: str, data_source: Dict[str, Any]) -> Optional[Tuple[List[Dict[str, Any]], PipelineStats]]:
        print(f"  → 调用 Pipeline 接口: {filename}")
        result = self._call_pipeline_api(file_bytes, filename, data_source)

        if result and 'elements' in result and 'stats' in result:
            elements = result['elements']
            stats_data = result['stats']

            stats = PipelineStats(
                original_elements=stats_data.get('original_elements', 0),
                chunked_elements=stats_data.get('chunked_elements', 0),
                embedded_elements=stats_data.get('embedded_elements', 0),
                stages=self.stages,  # 使用实际执行的 stages
                record_id=stats_data.get('record_id')  # 从 API 响应中获取 record_id
            )

            # 如果启用了中间结果保存，处理中间结果
            if self.pipeline_config.include_intermediate_results and 'intermediate_results' in result:
                self._save_intermediate_results(result['intermediate_results'], filename, data_source)

            print(f"  ✓ Pipeline 完成:")
            print(f"    - 原始元素: {stats.original_elements}")
            print(f"    - 分块后: {stats.chunked_elements}")
            print(f"    - 向量化: {stats.embedded_elements}")
            logger.info(f"Pipeline 完成: {filename}, {stats.embedded_elements} 个向量")

            return elements, stats
        else:
            print(f"  ✗ Pipeline 失败")
            logger.error(f"Pipeline 失败: {filename}")
            return None

    def _save_intermediate_results(self, intermediate_results: List[Dict[str, Any]], filename: str, data_source: Dict[str, Any]) -> None:
        """保存中间结果
        
        Args:
            intermediate_results: 中间结果数组，每个元素包含 stage 和 elements 字段
            filename: 文件名
            data_source: 数据源信息
        """
        try:
            # intermediate_results 是一个数组，每个元素是 {stage: str, elements: List}
            for result_item in intermediate_results:
                if 'stage' not in result_item or 'elements' not in result_item:
                    logger.warning(f"中间结果项缺少 stage 或 elements 字段: {result_item}")
                    continue
                
                stage = result_item['stage']
                elements = result_item['elements']
                
                metadata = {
                    'filename': filename,
                    'stage': stage,
                    'total_elements': len(elements),
                    'processed_at': datetime.now().isoformat(),
                    'data_source': data_source
                }
                
                self.pipeline_config.intermediate_results_destination.write(elements, metadata)
                print(f"  ✓ 保存 {stage.upper()} 中间结果: {len(elements)} 个元素")
                logger.info(f"保存 {stage.upper()} 中间结果成功: {filename}")

        except Exception as e:
            print(f"  ✗ 保存中间结果失败: {str(e)}")
            logger.error(f"保存中间结果失败: {filename}, {str(e)}")

    def process_file(self, file_path: str) -> bool:
        print(f"\n{'=' * 60}")
        print(f"处理文件: {file_path}")
        logger.info(f"开始处理文件: {file_path}")

        try:
            print(f"  → 读取文件...")
            file_bytes, data_source = self.source.read_file(file_path)
            data_source = data_source or {}
            
            # 检查文件大小，超过 100MB 则报错
            MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
            file_size = len(file_bytes)
            if file_size > MAX_FILE_SIZE:
                file_size_mb = file_size / (1024 * 1024)
                raise ValueError(f"文件大小过大: {file_size_mb:.2f}MB，超过100MB限制")
            
            # 转换为毫秒时间戳字符串
            timestamp_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
            data_source['date_processed'] = str(timestamp_ms)
            print(f"  ✓ 文件读取完成: {len(file_bytes)} bytes")

            result = self.process_with_pipeline(file_bytes, file_path, data_source)
            if not result:
                return False

            embedded_data, stats = result

            print(f"  → 写入目的地...")
            metadata = {
                'filename': file_path,
                'processed_at': str(timestamp_ms),
            }
            
            # 如果 stats 中有 record_id，添加到 metadata 中
            if stats.record_id:
                metadata['record_id'] = stats.record_id

            success = self.destination.write(embedded_data, metadata)

            if success:
                print(f"\n✓✓✓ 文件处理成功: {file_path}")
                logger.info(f"文件处理成功: {file_path}")
            else:
                print(f"\n✗✗✗ 文件处理失败: {file_path}")
                logger.error(f"文件处理失败: {file_path}")

            return success

        except Exception as e:
            print(f"\n✗✗✗ 处理异常: {str(e)}")
            logger.error(f"处理文件异常 {file_path}: {str(e)}")
            return False

    def run(self):
        start_time = time.time()

        print("\n" + "=" * 60)
        print("开始执行 Pipeline")
        print("=" * 60)
        logger.info("=" * 60)
        logger.info("开始执行 Pipeline")

        print("\n→ 列出文件...")
        files = self.source.list_files()

        if not files:
            print("\n✗ 没有找到文件")
            logger.info("没有找到文件")
            return

        total = len(files)
        success_count = 0
        fail_count = 0

        for idx, file_path in enumerate(files, 1):
            print(f"\n进度: [{idx}/{total}]")
            logger.info(f"进度: [{idx}/{total}] - {file_path}")

            try:
                if self.process_file(file_path):
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                print(f"\n✗✗✗ 文件处理异常: {str(e)}")
                logger.error(f"文件处理异常 {file_path}: {str(e)}")
                fail_count += 1

            if idx < total:
                time.sleep(1)

        elapsed = time.time() - start_time
        print("\n" + "=" * 60)
        print("Pipeline 执行完成！")
        print("=" * 60)
        print(f"总文件数: {total}")
        print(f"成功: {success_count}")
        print(f"失败: {fail_count}")
        print(f"总耗时: {elapsed:.2f} 秒")
        print("=" * 60)

        logger.info("=" * 60)
        logger.info(f"Pipeline 完成 - 总数:{total}, 成功:{success_count}, 失败:{fail_count}, 耗时:{elapsed:.2f}秒")
        logger.info("=" * 60)


def create_pipeline_from_config(config: Dict[str, Any]) -> Pipeline:
    source_config = config['source']
    if source_config['type'] == 's3':
        source = S3Source(
            endpoint=source_config['endpoint'],
            access_key=source_config['access_key'],
            secret_key=source_config['secret_key'],
            bucket=source_config['bucket'],
            prefix=source_config.get('prefix', ''),
            region=source_config.get('region', 'us-east-1'),
            pattern=source_config.get('pattern', None),
            recursive=source_config.get('recursive', False)
        )
    elif source_config['type'] == 'local':
        source = LocalSource(
            directory=source_config['directory'],
            pattern=source_config.get('pattern', None),
            recursive=source_config.get('recursive', False)
        )
    elif source_config['type'] == 'ftp':
        source = FtpSource(
            host=source_config['host'],
            port=source_config['port'],
            username=source_config['username'],
            password=source_config['password'],
            pattern=source_config.get('pattern', None),
            recursive=source_config.get('recursive', False)
        )
    elif source_config['type'] == 'smb':
        source = SmbSource(
            host=source_config['host'],
            share_name=source_config['share_name'],
            username=source_config['username'],
            password=source_config['password'],
            domain=source_config.get('domain', ''),
            port=source_config.get('port', 445),
            path=source_config.get('path', ''),
            pattern=source_config.get('pattern', None),
            recursive=source_config.get('recursive', False)
        )
    else:
        raise ValueError(f"未知的 source 类型: {source_config['type']}")

    dest_config = config['destination']
    if dest_config['type'] in ['milvus', 'zilliz']:
        destination = MilvusDestination(
            db_path=dest_config['db_path'],
            collection_name=dest_config['collection_name'],
            dimension=dest_config['dimension'],
            api_key=dest_config.get('api_key'),
            token=dest_config.get('token')
        )
    elif dest_config['type'] == 'qdrant':
        destination = QdrantDestination(
            url=dest_config['url'],
            collection_name=dest_config['collection_name'],
            dimension=dest_config['dimension'],
            api_key=dest_config.get('api_key'),
            prefer_grpc=dest_config.get('prefer_grpc', False)
        )
    elif dest_config['type'] == 'local':
        destination = LocalDestination(
            output_dir=dest_config['output_dir']
        )
    elif dest_config['type'] == 's3':
        destination = S3Destination(
            endpoint=dest_config['endpoint'],
            access_key=dest_config['access_key'],
            secret_key=dest_config['secret_key'],
            bucket=dest_config['bucket'],
            prefix=dest_config.get('prefix', ''),
            region=dest_config.get('region', 'us-east-1')
        )
    else:
        raise ValueError(f"未知的 destination 类型: {dest_config['type']}")

    # 处理 stages 配置
    if 'stages' not in config or not config['stages']:
        raise ValueError("配置中必须包含 'stages' 字段")
    
    stages = []
    for stage_cfg in config['stages']:
        stage_type = stage_cfg.get('type')
        stage_config_dict = stage_cfg.get('config', {})
        
        if stage_type == 'parse':
            parse_cfg_copy = dict(stage_config_dict)
            provider = parse_cfg_copy.pop('provider', 'textin')
            stage_config = ParseConfig(provider=provider, **parse_cfg_copy)
        elif stage_type == 'chunk':
            stage_config = ChunkConfig(
                strategy=stage_config_dict.get('strategy', 'basic'),
                include_orig_elements=stage_config_dict.get('include_orig_elements', False),
                new_after_n_chars=stage_config_dict.get('new_after_n_chars', 512),
                max_characters=stage_config_dict.get('max_characters', 1024),
                overlap=stage_config_dict.get('overlap', 0),
                overlap_all=stage_config_dict.get('overlap_all', False)
            )
        elif stage_type == 'embed':
            stage_config = EmbedConfig(
                provider=stage_config_dict.get('provider', 'qwen'),
                model_name=stage_config_dict.get('model_name', 'text-embedding-v3')
            )
        else:
            raise ValueError(f"未知的 stage 类型: {stage_type}")
        
        stages.append(Stage(type=stage_type, config=stage_config))

    # 创建 Pipeline 配置
    pipeline_config = None
    if 'pipeline_config' in config and config['pipeline_config']:
        pipeline_cfg = config['pipeline_config']
        include_intermediate_results = pipeline_cfg.get('include_intermediate_results', False)
        intermediate_results_destination = None
        
        if include_intermediate_results:
            if 'intermediate_results_destination' in pipeline_cfg:
                dest_cfg = pipeline_cfg['intermediate_results_destination']
                dest_type = dest_cfg.get('type')
                
                if dest_type == 'local':
                    intermediate_results_destination = LocalDestination(
                        output_dir=dest_cfg['output_dir']
                    )
                elif dest_type == 's3':
                    intermediate_results_destination = S3Destination(
                        endpoint=dest_cfg['endpoint'],
                        access_key=dest_cfg['access_key'],
                        secret_key=dest_cfg['secret_key'],
                        bucket=dest_cfg['bucket'],
                        prefix=dest_cfg.get('prefix', ''),
                        region=dest_cfg.get('region', 'us-east-1')
                    )
                else:
                    raise ValueError(f"不支持的 intermediate_results_destination 类型: '{dest_type}'，支持的类型: 'local', 's3'")
            else:
                raise ValueError("当 include_intermediate_results 为 True 时，必须设置 intermediate_results_destination")
        
        pipeline_config = PipelineConfig(
            include_intermediate_results=include_intermediate_results,
            intermediate_results_destination=intermediate_results_destination
        )

    # 创建 Pipeline
    pipeline = Pipeline(
        source=source,
        destination=destination,
        api_base_url=config.get('api_base_url', 'http://localhost:8000/api/xparse'),
        api_headers=config.get('api_headers', {}),
        stages=stages,
        pipeline_config=pipeline_config
    )

    return pipeline


__all__ = [
    'Pipeline',
    'create_pipeline_from_config',
]

