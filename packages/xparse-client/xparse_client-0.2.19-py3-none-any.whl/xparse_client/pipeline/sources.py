#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json
import logging
import boto3
import ftplib

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from smb.SMBConnection import SMBConnection
from botocore.config import Config


logger = logging.getLogger(__name__)


def _normalize_wildcard_patterns(pattern: Optional[List[str]]) -> Optional[List[str]]:
    """规范化通配符模式列表
    
    Args:
        pattern: 通配符模式列表，如果为 None 或空列表则返回 None（表示匹配所有文件）
        
    Returns:
        通配符模式列表，如果 pattern 是 None、空列表或包含 "*" 则返回 None（表示匹配所有文件）
    """
    if pattern is None or not pattern:
        return None  # None 表示匹配所有文件

    if not isinstance(pattern, list):
        raise ValueError(f"pattern 类型错误: {type(pattern)}")
    
    # 过滤空字符串并去除空格
    normalized = [p.strip() for p in pattern if p and p.strip()]
    
    if not normalized:
        return None
    
    # 如果包含 "*"，直接返回 None（匹配所有文件，减少后续开销）
    if '*' in normalized:
        return None
    
    return normalized


def _match_file_extension(file_path: str, wildcard_patterns: Optional[List[str]]) -> bool:
    """检查文件路径是否匹配通配符模式
    
    Args:
        file_path: 文件路径
        wildcard_patterns: 已规范化的通配符模式列表（如 ['*.pdf', '*.docx']）
        
    Returns:
        如果匹配返回 True，否则返回 False
    """
    # 如果 wildcard_patterns 是 None 或空列表，匹配所有文件
    if wildcard_patterns is None:
        return True
    
    # 检查是否匹配任何一个通配符模式
    for wildcard_pattern in wildcard_patterns:
        if fnmatch(file_path, wildcard_pattern):
            return True
    
    return False


def _to_millis_timestamp_string(timestamp):
    """将时间戳转换为毫秒时间戳字符串
    
    Args:
        timestamp: 时间戳（秒或毫秒），可以是 int、float 或 None
        
    Returns:
        str: 毫秒时间戳字符串，如果输入为 None 则返回空字符串
    """
    if timestamp is None:
        return ""
    
    # 如果已经是毫秒时间戳（大于 1e12），直接转换
    if isinstance(timestamp, (int, float)):
        if timestamp > 1e12:
            # 已经是毫秒时间戳
            return str(int(timestamp))
        else:
            # 秒级时间戳，转换为毫秒
            return str(int(timestamp * 1000))
    
    return str(timestamp)


class Source(ABC):
    """数据源抽象基类"""

    @abstractmethod
    def list_files(self) -> List[str]:
        """列出所有文件"""
        raise NotImplementedError

    @abstractmethod
    def read_file(self, file_path: str) -> Tuple[bytes, Dict[str, Any]]:
        """读取文件内容并返回数据来源信息"""
        raise NotImplementedError


class S3Source(Source):
    """S3/MinIO 数据源"""

    def __init__(self, endpoint: str, access_key: str, secret_key: str,
                 bucket: str, prefix: str = '', region: str = 'us-east-1', pattern: Optional[List[str]] = None, recursive: bool = False):
        self.endpoint = endpoint
        self.bucket = bucket
        self.prefix = prefix
        self.pattern = _normalize_wildcard_patterns(pattern)  # 在初始化时规范化
        self.recursive = recursive

        if self.endpoint == 'https://textin-minio-api.ai.intsig.net':
            config = Config(signature_version='s3v4')
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
            print(f"✓ S3 连接成功: {endpoint}/{bucket}")
            logger.info(f"S3 连接成功: {endpoint}/{bucket}")
        except Exception as e:
            print(f"✗ S3 连接失败: {str(e)}")
            raise

    def list_files(self) -> List[str]:
        files = []
        paginator = self.client.get_paginator('list_objects_v2')

        params = {'Bucket': self.bucket}
        if self.prefix:
            params['Prefix'] = self.prefix
        if not self.recursive:
            # 非递归模式：使用 Delimiter 只列出当前目录下的文件
            params['Delimiter'] = '/'

        for page in paginator.paginate(**params):
            if 'Contents' in page:
                for obj in page['Contents']:
                    key = obj['Key']
                    if key.endswith('/') or key.endswith('empty.tmp'):
                        continue
                    if _match_file_extension(key, self.pattern):
                        files.append(key)
            
            # 非递归模式下，CommonPrefixes 包含子目录，我们忽略它们
            if not self.recursive and 'CommonPrefixes' in page:
                # 这些是子目录，在非递归模式下忽略
                pass

        print(f"✓ S3 找到 {len(files)} 个文件")
        return files

    def read_file(self, file_path: str) -> Tuple[bytes, Dict[str, Any]]:
        response = self.client.get_object(Bucket=self.bucket, Key=file_path)
        file_bytes = response['Body'].read()

        headers = response.get('ResponseMetadata', {}).get('HTTPHeaders', {})
        version = headers.get('etag') or ""
        if version.startswith('"') and version.endswith('"'):
            version = version[1:-1]
        last_modified = headers.get('last-modified')
        server = headers.get('server') or "unknown"
        date_modified = None
        if last_modified:
            try:
                dt = parsedate_to_datetime(last_modified)
                date_modified = dt.astimezone(timezone.utc).timestamp()
            except Exception as exc:
                logger.debug(f"S3 解析 last-modified 失败 {file_path}: {exc}")

        normalized_key = file_path.lstrip('/')
        data_source = {
            'url': f"s3://{self.bucket}/{normalized_key}",
            'version': version,
            'date_created': _to_millis_timestamp_string(date_modified),
            'date_modified': _to_millis_timestamp_string(date_modified),
            'record_locator': {
                'server': server,
                'protocol': 's3',
                'remote_file_path': normalized_key
            }
        }
        
        return file_bytes, data_source


class LocalSource(Source):
    """本地文件系统数据源"""

    def __init__(self, directory: str, pattern: Optional[List[str]] = None, recursive: bool = False):
        self.directory = Path(directory)
        self.pattern = _normalize_wildcard_patterns(pattern)  # 在初始化时规范化
        self.recursive = recursive

        if not self.directory.exists():
            raise ValueError(f"目录不存在: {directory}")

        print(f"✓ 本地目录: {self.directory}")
        logger.info(f"本地目录: {self.directory}")

    def list_files(self) -> List[str]:
        all_files = []
        # 匹配所有文件
        if self.recursive:
            all_files.extend([
                str(f.relative_to(self.directory))
                for f in self.directory.rglob('*')
                if f.is_file()
            ])
        else:
            all_files.extend([
                str(f.relative_to(self.directory))
                for f in self.directory.glob('*')
                if f.is_file()
            ])
        
        files = []
        if self.pattern is not None:
            for file in all_files:
                if _match_file_extension(file, self.pattern):
                    files.append(file)
        else:
            files.extend(all_files)
        
        print(f"✓ 本地找到 {len(files)} 个文件")
        return files

    def read_file(self, file_path: str) -> Tuple[bytes, Dict[str, Any]]:
        full_path = (self.directory / file_path).resolve()
        with open(full_path, 'rb') as f:
            file_bytes = f.read()

        date_created = None
        date_modified = None
        version = None
        try:
            stats = full_path.stat()
            date_created = stats.st_ctime
            date_modified = stats.st_mtime
            version = str(int(stats.st_mtime_ns))
        except FileNotFoundError:
            logger.warning(f"本地文件不存在，无法获取 metadata: {full_path}")

        data_source = {
            'url': full_path.as_uri(),
            'version': version,
            'date_created': _to_millis_timestamp_string(date_created),
            'date_modified': _to_millis_timestamp_string(date_modified),
            'record_locator': {
                'protocol': 'file',
                'remote_file_path': str(full_path)
            }
        }
        return file_bytes, data_source


class FtpSource(Source):
    """FTP 数据源"""

    def __init__(self, host: str, port: int, username: str, password: str, pattern: Optional[List[str]] = None, recursive: bool = False):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.pattern = _normalize_wildcard_patterns(pattern)  # 在初始化时规范化
        self.recursive = recursive

        self.client = ftplib.FTP()
        self.client.connect(self.host, self.port)
        self.client.login(self.username, self.password)

        print(f"✓ FTP 连接成功: {self.host}:{self.port}")
        logger.info(f"FTP 连接成功: {self.host}:{self.port}")

    def list_files(self) -> List[str]:
        if self.recursive:
            # 递归模式：递归列出所有文件
            files = []
            current_dir = self.client.pwd()
            
            def _list_recursive(path=''):
                try:
                    # 保存当前目录
                    original_dir = self.client.pwd()
                    if path:
                        try:
                            self.client.cwd(path)
                        except:
                            return
                    
                    items = []
                    try:
                        # 尝试使用 MLSD 命令（更可靠）
                        items = []
                        for item in self.client.mlsd():
                            items.append(item)
                    except:
                        # 如果不支持 MLSD，使用 LIST 命令
                        try:
                            lines = []
                            self.client.retrlines('LIST', lines.append)
                            for line in lines:
                                parts = line.split()
                                if len(parts) >= 9:
                                    # 解析 LIST 输出，第一个字符表示文件类型
                                    item_name = ' '.join(parts[8:])
                                    is_dir = parts[0].startswith('d')
                                    items.append((item_name, {'type': 'dir' if is_dir else 'file'}))
                        except:
                            # 最后回退到 nlst，但无法区分文件和目录
                            for item_name in self.client.nlst():
                                items.append((item_name, {'type': 'unknown'}))
                    
                    for item_name, item_info in items:
                        if item_name in ['.', '..']:
                            continue
                        
                        item_type = item_info.get('type', 'unknown')
                        full_path = f"{path}/{item_name}" if path else item_name
                        
                        if item_type == 'dir' or item_type == 'unknown':
                            # 尝试切换目录来判断是否为目录
                            try:
                                self.client.cwd(item_name)
                                self.client.cwd('..')
                                # 是目录，递归处理
                                _list_recursive(full_path)
                            except:
                                # 不是目录，是文件
                                relative_path = full_path.lstrip('/')
                                if _match_file_extension(relative_path, self.pattern):
                                    files.append(relative_path)
                        else:
                            # 是文件
                            relative_path = full_path.lstrip('/')
                            if _match_file_extension(relative_path, self.pattern):
                                files.append(relative_path)
                    
                    # 恢复原始目录
                    self.client.cwd(original_dir)
                except Exception as e:
                    logger.warning(f"FTP 列出路径失败 {path}: {str(e)}")
                    try:
                        self.client.cwd(current_dir)
                    except:
                        pass
            
            _list_recursive()
            # 确保回到原始目录
            try:
                self.client.cwd(current_dir)
            except:
                pass
        else:
            # 非递归模式：只列出当前目录下的文件（排除目录）
            files = []
            current_dir = self.client.pwd()
            
            try:
                # 尝试使用 MLSD 命令（更可靠）
                items = []
                for item_name, item_info in self.client.mlsd():
                    if item_name in ['.', '..']:
                        continue
                    item_type = item_info.get('type', 'unknown')
                    # 只添加文件，排除目录
                    if item_type == 'file' or (item_type == 'unknown' and not item_info.get('type', '').startswith('dir')):
                        if _match_file_extension(item_name, self.pattern):
                            files.append(item_name)
            except:
                # 如果不支持 MLSD，使用 LIST 命令
                try:
                    lines = []
                    self.client.retrlines('LIST', lines.append)
                    for line in lines:
                        parts = line.split()
                        if len(parts) >= 9:
                            # 解析 LIST 输出，第一个字符表示文件类型
                            item_name = ' '.join(parts[8:])
                            if item_name in ['.', '..']:
                                continue
                            is_dir = parts[0].startswith('d')
                            # 只添加文件，排除目录
                            if not is_dir and _match_file_extension(item_name, self.pattern):
                                files.append(item_name)
                except:
                    # 最后回退到 nlst，通过尝试切换目录来判断是否为目录
                    raw_items = self.client.nlst()
                    for item_name in raw_items:
                        if item_name in ['.', '..']:
                            continue
                        # 尝试切换目录来判断是否为目录
                        try:
                            self.client.cwd(item_name)
                            self.client.cwd('..')
                            # 能切换成功，说明是目录，跳过
                            continue
                        except:
                            # 不能切换，说明是文件
                            if _match_file_extension(item_name, self.pattern):
                                files.append(item_name)
            
            # 确保回到原始目录
            try:
                self.client.cwd(current_dir)
            except:
                pass
        
        print(f"✓ FTP 找到 {len(files)} 个文件 (匹配 pattern)")
        return files

    def read_file(self, file_path: str) -> Tuple[bytes, Dict[str, Any]]:
        from io import BytesIO
        buffer = BytesIO()
        self.client.retrbinary(f'RETR {file_path}', buffer.write)

        date_modified = None
        try:
            resp = self.client.sendcmd(f"MDTM {file_path}")
            parts = resp.split()
            if len(parts) == 2 and parts[0] == '213':
                dt = datetime.strptime(parts[1], "%Y%m%d%H%M%S")
                date_modified = dt.replace(tzinfo=timezone.utc).timestamp()
        except Exception as exc:
            logger.debug(f"FTP 获取文件时间失败 {file_path}: {exc}")

        normalized_path = file_path.lstrip('/')
        version = _to_millis_timestamp_string(date_modified)
        data_source = {
            'url': f"ftp://{self.host}:{self.port}/{normalized_path}",
            'version': version,
            'date_created': version,
            'date_modified': version,
            'record_locator': {
                'server': f"{self.host}:{self.port}",
                'protocol': 'ftp',
                'remote_file_path': normalized_path
            }
        }

        return buffer.getvalue(), data_source


class SmbSource(Source):
    """SMB/CIFS 数据源"""

    def __init__(self, host: str, share_name: str, username: str, password: str,
                 domain: str = '', port: int = 445, path: str = '', pattern: Optional[List[str]] = None, recursive: bool = False):
        self.host = host
        self.share_name = share_name
        self.username = username
        self.password = password
        self.domain = domain
        self.port = port
        self.path = path.strip('/').strip('\\') if path else ''
        self.pattern = _normalize_wildcard_patterns(pattern)  # 在初始化时规范化
        self.recursive = recursive

        self.conn = SMBConnection(
            username,
            password,
            '',
            host,
            domain=domain,
            use_ntlm_v2=True
        )

        try:
            self.conn.connect(host, port)
        except Exception as e:
            error_msg = f"无法连接到 SMB 服务器 {host}:{port}: {str(e)}"
            print(f"✗ SMB 连接失败: {error_msg}")
            logger.error(f"SMB 连接失败: {error_msg}")
            raise ConnectionError(error_msg)

    def list_files(self) -> List[str]:
        files = []
        base_path = '/' if not self.path else f'/{self.path}'

        def _list_recursive(conn, share, current_path):
            try:
                items = conn.listPath(share, current_path)
                for item in items:
                    if item.filename in ['.', '..'] or item.filename.startswith('.'):
                        continue
                    item_path = f"{current_path.rstrip('/')}/{item.filename}" if current_path != '/' else f"/{item.filename}"
                    relative_path = item_path[len(base_path):].lstrip('/')
                    if item.isDirectory:
                        if self.recursive:
                            # 递归模式：继续递归子目录
                            _list_recursive(conn, share, item_path)
                        # 非递归模式：忽略子目录
                    else:
                        if _match_file_extension(relative_path, self.pattern):
                            files.append(relative_path)
            except Exception as e:
                logger.warning(f"列出路径失败 {current_path}: {str(e)}")

        _list_recursive(self.conn, self.share_name, base_path)

        print(f"✓ SMB 找到 {len(files)} 个文件")
        return files

    def read_file(self, file_path: str) -> Tuple[bytes, Dict[str, Any]]:
        from io import BytesIO

        base_path = '/' if not self.path else f'/{self.path}'
        full_path = f"{base_path.rstrip('/')}/{file_path.lstrip('/')}" if base_path != '/' else f"/{file_path.lstrip('/')}"

        file_obj = BytesIO()
        try:
            self.conn.retrieveFile(self.share_name, full_path, file_obj)
        except Exception as e:
            raise IOError(f"读取文件失败 {full_path}: {str(e)}")

        def _to_timestamp(value):
            if isinstance(value, datetime):
                return value.astimezone(timezone.utc).timestamp()
            if isinstance(value, (int, float)):
                return value
            return None

        date_created = None
        date_modified = None
        try:
            attrs = self.conn.getAttributes(self.share_name, full_path)
            date_created = _to_timestamp(getattr(attrs, 'create_time', None))
            date_modified = _to_timestamp(getattr(attrs, 'last_write_time', None))
        except Exception as exc:
            logger.debug(f"SMB 获取文件属性失败 {full_path}: {exc}")

        smb_url = f"smb://{self.host}/{self.share_name}{full_path}"
        data_source = {
            'url': smb_url,
            'version': _to_millis_timestamp_string(date_modified),
            'date_created': _to_millis_timestamp_string(date_created),
            'date_modified': _to_millis_timestamp_string(date_modified),
            'record_locator': {
                'server': self.host,
                'share': self.share_name,
                'protocol': 'smb',
                'remote_file_path': full_path
            }
        }

        file_obj.seek(0)
        return file_obj.read(), data_source

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            try:
                self.conn.close()
            except Exception:
                pass


__all__ = [
    'Source',
    'S3Source',
    'LocalSource',
    'FtpSource',
    'SmbSource',
]

