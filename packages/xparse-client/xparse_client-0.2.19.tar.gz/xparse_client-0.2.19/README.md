# xParse

面向Agent和RAG的新一代文档处理 AI Infra。

xParse的同步pipeline实现，支持多种数据源与输出。

## 🌟 特点

- **灵活的数据源**：支持兼容 S3 协议的对象存储、本地文件系统以及 FTP/SMB 协议文件系统
- **灵活的输出**：支持 Milvus/Zilliz/Qdrant 向量数据库、兼容 S3 协议的对象存储以及本地文件系统
- **统一 Pipeline API**：使用 `/api/xparse/pipeline` 一次性完成 parse → chunk → embed 全流程
- **配置化处理**：支持灵活配置 parse、chunk、embed 参数
- **详细统计信息**：返回每个阶段的处理统计数据
- **易于扩展**：基于抽象类，可轻松添加新的 Source 和 Destination
- **完整日志**：详细的处理日志和错误追踪

## 📋 架构

```
        ┌──────────────┐
        │   Source     │  数据源（S3/本地/FTP）
        └──────┬───────┘
               │ read_file()
               ▼
┌──────────────────────────────────────┐
│           Pipeline API               │
│       /api/xparse/pipeline           │
│                                      │
│  ┌────────┐  ┌────────┐  ┌────────┐  │     ┌────────┐
│  │ Parse  │→ │ Chunk  │→ │ Embed  │  |────→│ Deduct │  计费
│  └────────┘  └────────┘  └────────┘  │     └────────┘
│                                      │
└──────────────┬───────────────────────┘
               │ [embeddings + stats]
               ▼
       ┌──────────────┐
       │ Destination  │  目的地（Milvus/Zilliz/Qdrant/本地）
       └──────────────┘
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install --upgrade xparse-client
```

### 2. 运行

`xparse-client`支持两种配置方式，即通过代码配置，以及直接通过config字典配置

#### 代码配置
```python
from xparse_client import ParseConfig, ChunkConfig, EmbedConfig, Stage, Pipeline, S3Source, MilvusDestination, QdrantDestination

# 使用新的 stages 格式创建配置
stages = [
    Stage(
        type='parse',
        config=ParseConfig(provider='textin')
    ),
    Stage(
        type='chunk',
        config=ChunkConfig(
            strategy='by_title',
            include_orig_elements=False,
            new_after_n_chars=512,
            max_characters=1024,
            overlap=50
        )
    ),
    Stage(
        type='embed',
        config=EmbedConfig(
            provider='qwen',
            model_name='text-embedding-v4'
        )
    )
]

# 创建 Pipeline
source = S3Source(...)
destination = MilvusDestination(...)

pipeline = Pipeline(
    source=source,
    destination=destination,
    api_base_url='https://api.textin.com/api/xparse',
    api_headers={...},
    stages=stages
)

pipeline.run()
```

#### 字典配置

```python
config = {
    'source': {...},
    'destination': {...},
    'api_base_url': 'https://api.textin.com/api/xparse',
    'api_headers': {...},
    
    # Stages 配置
    'stages': [
        {
            'type': 'parse',
            'config': {
                'provider': 'textin'  # 当前支持textin文档解析，未来可扩展
            }
        },
        {
            'type': 'chunk',
            'config': {
                'strategy': 'basic',             # 分块策略: 'basic' | 'by_title' | 'by_page'
                'include_orig_elements': False,  # 是否包含原始元素
                'new_after_n_chars': 512,        # 多少字符后创建新块
                'max_characters': 1024,          # 最大字符数
                'overlap': 0                     # 重叠字符数
            }
        },
        {
            'type': 'embed',
            'config': {
                'provider': 'qwen',                # 向量化供应商: 'qwen'/'doubao'
                'model_name': 'text-embedding-v3'  # 模型名称
            }
        }
    ]
}

# 使用配置创建 pipeline
from xparse_client import create_pipeline_from_config
pipeline = create_pipeline_from_config(config)
pipeline.run()
```

详见下文的 [使用示例](#-使用示例) 一章，或参考`example/run_pipeline.py`文件。

## 📝 配置说明

### Source 配置

#### MinIO / S3兼容数据源（OSS/COS/TOS/OBS/S3）

1. MinIO

接入代码如下：
```python
source = S3Source(
    endpoint='https://your-minio-endpoint',
    access_key='IEQspf******mp3AZWl',
    secret_key='kLj96I8FGb**********zBijOJWKWOt1',
    bucket='textin',
    prefix='',
    region='us-east-1',
    pattern=['*.pdf']  # 可选，通配符模式列表，支持多个扩展名
)
```
请确保配置的访问凭证至少包括以下几项权限：
```
s3:ListBucket
s3:GetObject
```

2. 阿里云OSS

接入代码示例如下：
```python
source = S3Source(
    endpoint='https://s3.oss-cn-shanghai.aliyuncs.com',
    access_key='LTAI5tBg**********bPyuB17',
    secret_key='JFIIaTGiX**********SStofF0S98',
    bucket='textin',
    prefix='',
    region='cn-shanghai',
    pattern=['*.pdf']  # 可选，通配符模式列表，支持多个扩展名
)
```
请确保配置的访问凭证至少包括以下几项权限：
```
oss:HeadBucket
oss:ListObjects
oss:GetObject
```

3. 腾讯云COS

接入代码示例如下：
```python
source = S3Source(
    endpoint='https://cos.ap-shanghai.myqcloud.com',
    access_key='AKIDRnws********nlUzHLAmAJ',
    secret_key='we7KJ4bux**********UKxWu3yeDZi',
    bucket='textin',
    prefix='',
    region='ap-shanghai',
    pattern=['*.pdf']  # 可选，通配符模式列表，支持多个扩展名
)
```

请确保配置的访问凭证至少包括以下几项权限：
```
cos:HeadBucket
cos:GetBucket
cos:GetObject
```
4. 火山引擎TOS

接入代码示例如下：
```python
source = S3Source(
    endpoint='https://tos-s3-cn-shanghai.volces.com',
    access_key='AKLTMzNkZ**************BjYjZjYzA',
    secret_key='TnpWaE0yRTVa**************RrMFlqVQ==',
    bucket='textin',
    prefix='',
    region='cn-shanghai',
    pattern=['*.pdf']  # 可选，通配符模式列表，支持多个扩展名
)
```

请确保配置的访问凭证至少包括以下几项权限：
```
tos:HeadBucket
tos:ListBucket
tos:GetObject
```

5. 华为云OBS

接入代码示例如下：
```python
source = S3Source(
    endpoint='https://obs.cn-east-3.myhuaweicloud.com',
    access_key='HPUAL6********YAT7JMWY',
    secret_key='z9cm95UXCw**********bwDYz8PVoBGDI',
    bucket='textin',
    prefix='',
    region='cn-east-3',
    pattern=['*.pdf']  # 可选，通配符模式列表，支持多个扩展名
)
```

请确保配置的访问凭证至少包括以下几项权限：
```
HeadBucket
ListBucket
GetObject
```

6. AWS S3

接入代码示例如下：
```python
source = S3Source(
    endpoint='https://s3.us-east-1.amazonaws.com',
    access_key='AKIA6Q******UWA4PO',
    secret_key='OfV4r9/u+CmlLx**************WLADKdPek7',
    bucket='textin-xparse',
    prefix='',
    region='us-east-1',
    pattern=['*.pdf']  # 可选，通配符模式列表，支持多个扩展名
)
```
请确保配置的访问凭证至少包括以下几项权限：
```
s3:ListBucket
s3:GetObject
```


#### 本地文件系统数据源

```python
source = LocalSource(
    directory='./input',
    pattern=['*.pdf', '*.docx']  # 支持多个通配符模式列表
)
```

#### FTP数据源

```python
source = FtpSource(
    host='127.0.0.1',
    port=21,
    username='', # 用户名，按照实际填写
    password='',  # 密码，按照实际填写
    pattern=['*.pdf']  # 可选，通配符模式列表，过滤指定类型文件
)
```

#### SMB数据源

```python
source = SmbSource(
    host='your-smb-host',
    share_name='your-smb-share-name',
    username='',  # 用户名，按照实际填写
    password='',  # 密码，按照实际填写
    domain='your-smb-domain',
    pattern=['**/*.pdf']  # 可选，通配符模式列表，支持多级匹配
)
```

> 注 1：所有 Source 均支持 `pattern` 参数，使用通配符模式列表（如 `['*.pdf', '*.docx']`）来过滤需要处理的文件。支持多个通配符模式，如果列表中包含 `'*'` 则匹配所有文件。默认为 `None`，即处理全部文件。

> 注 2：所有 Source 均支持 `recursive` 参数，表示是否递归遍历，默认为 `False`。

### Destination 配置

#### 本地 Milvus 向量存储

collection 中至少需要包含 `element_id`，`text`，`embeddings`，`record_id` 四个字段。

```python
destination = MilvusDestination(
    db_path='./milvus_pipeline.db', # 本地数据库文件
    collection_name='my_collection', # 数据库collection名称
    dimension=1024  # 向量维度，需与 embed API 返回一致
)
```

#### Zilliz 向量存储

collection 中至少需要包含 `element_id`，`text`，`embeddings`，`record_id` 四个字段。

```python
destination = MilvusDestination(
    db_path='https://xxxxxxx.serverless.xxxxxxx.cloud.zilliz.com.cn', # zilliz连接地址
    collection_name='my_collection', # 数据库collection名称
    dimension=1024,  # 向量维度，需与 embed API 返回一致
    api_key='your-api-key'  # Zilliz Cloud API Key
)
```

#### Qdrant 向量存储

```python
destination = QdrantDestination(
    url='http://localhost:6333',  # Qdrant 服务地址（本地或云端）
    collection_name='my_collection',  # Collection 名称
    dimension=1024,  # 向量维度，需与 embed API 返回一致
    api_key='your-api-key',  # 可选，Qdrant Cloud API Key
    prefer_grpc=False  # 可选，是否优先使用 gRPC（默认 False）
)
```

**Qdrant Cloud 示例：**
```python
destination = QdrantDestination(
    url='https://xxxxxxx.us-east-1-0.aws.cloud.qdrant.io',
    collection_name='my_collection',
    dimension=1024,
    api_key='your-api-key'
)
```

#### 本地文件系统目的地

将在配置的本地文件地址中写入`json`文件。

```python
destination = LocalDestination(
    output_dir='./output'
)
```

#### MinIO / S3兼容数据源（OSS/COS/TOS/OBS/S3）

将在配置的本地文件地址中写入`json`文件。

配置可参考上文中 Source 的配置，需要注意的是，需要确保配置的访问凭证在上述权限的基础上包括 `PutObject` 权限，例如在使用阿里云OSS时，需要包括以下权限：
```
oss:HeadBucket
oss:ListObjects
oss:GetObject
oss:PutObject
```

### API 配置

该配置即为pipeline主逻辑接口的请求配置，api_base_url固定为 `https://api.textin.com/api/xparse` ，api_headers中需要填入 [TextIn 开发者信息](https://www.textin.com/console/dashboard/setting) 中获取的 `x-ti-app-id` 与 `x-ti-secret-code`。

```python
'api_base_url': 'https://api.textin.com/api/xparse',
'api_headers': {
    'x-ti-app-id': 'your-app-id',
    'x-ti-secret-code': 'your-secret-code'
}
```

## 🔌 API 接口规范

### Pipeline 接口（统一接口）

**Endpoint:** `POST /api/xparse/pipeline`

**请求格式:**
```
Content-Type: multipart/form-data

file: <binary file>
stages: [
  {
    "type": "parse",
    "config": {
      "provider": "textin",
      ...
    }
  },
  {
    "type": "chunk",
    "config": {
      "strategy": "basic",
      "include_orig_elements": false,
      "new_after_n_chars": 512,
      "max_characters": 1024,
      "overlap": 0
    }
  },
  {
    "type": "embed",
    "config": {
      "provider": "qwen",
      "model_name": "text-embedding-v3"
    }
  }
]
```

**Stages 说明：**

Pipeline 接口使用 stages 数组来定义处理流程，每个 stage 包含：
- `type`: 阶段类型，可选值：`parse`、`chunk`、`embed`
  - `parse`节点必选，且顺序必须在第一位
  - `chunk`/`embed`节点可选，若二者同时存在`embed`节点需在`chunk`后面
  - 若不存在`embed`节点且Destination为向量数据库类型（例如`Milvus`），运行时会报错
- `config`: 该阶段的配置，具体字段取决于阶段类型

**各阶段配置：**

1. **Parse Stage** (`type: "parse"`)

Parse 参数中有必填项`Provider`，表示文档解析服务的供应商，目前可选项如下：
- textin: 合合信息提供的文档解析服务，在速度、准确性上均为行业领先
  - 支持的文档解析参数参考 [TextIn 文档解析官方API文档](https://docs.textin.com/api-reference/endpoint/parse)
  - 接口调用将按照 `TextIn 通用文档解析` 服务的计费标准进行计费
- textin-lite：
  - 接口调用将按照 `TextIn 通用表格识别` 服务的计费标准进行计费
- mineru:
  - 接口调用将按照 `TextIn 通用文档解析` 服务的计费标准进行计费
- paddle:
  - 接口调用将按照 `TextIn 通用文档解析` 服务的计费标准进行计费

2. **Chunk Stage** (`type: "chunk"`)

| 参数名 | 类型 / 可选性 | 说明 | 默认值 | 使用场景 / 注意事项 |
| ------ | ------------- | ---- | ------ | -------------------- |
| **strategy** | string/必填 | 分块策略 | basic |   <br>- `basic`: 基础分块，按字符数分割<br>- `by_title`: 按标题分块，保持章节完整性<br>- `by_page`: 按页面分块，保持页面完整性 |
| **combine_text_under_n_chars** | `int` / 可选 | 将同一部分中的元素合并成一个数据块，直到该部分的总长度达到指定字符数。 | `None` | 可用于将过短的小块合并成较长文本，提高语义连贯性。 |
| **include_orig_elements** | `bool` / 可选 | 如果为 `true`，用于构成数据块的原始元素会出现在该数据块的 `.metadata.orig_elements` 中。 | `False` | 用于调试或需要保留原始元素追溯的场景。 |
| **new_after_n_chars** | `int` / 可选 | 当文本长度达到指定字符数时，强制结束当前章节并开始新的章节（近似限制）。 | `None` | 适用于需要控制章节最大长度的情况下。 |
| **max_characters** | `int` / 可选 | 数据块中允许的最大字符数上限。 | `None` | 用于硬性限制块大小，避免过大块带来的处理延迟或内存占用。 |
| **overlap** | `int` / 可选 | 将前一个文本分块末尾指定数量的字符，作为前缀应用到由过大元素分割而成的第二个及后续文本块。 | `None` | 常用于确保分块之间的上下文连续性。 |
| **overlap_all** | `bool` / 可选 | 如果为 `true`，重叠也会应用到由完整元素组合而成的“普通”块。 | `False` | 谨慎使用，可能在语义上引入噪声。 |


3. **Embed Stage** (`type: "embed"`)

`xparse-pipeline`当前支持的文本向量化模型如下：
- `qwen` 供应商，即通义千问:
  - `text-embedding-v3`
  - `text-embedding-v4`
- `doubao` 供应商，即火山引擎:
  - `doubao-embedding-large-text-250515`
  - `doubao-embedding-text-240715`

**返回格式:**
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "elements": [
      {
        "element_id": "f6d5beee53d4f3d90589472974abd7f75c54988c72375cd206f74089391c92b2",
        "type": "plaintext",
        "text": "文本内容",
        "metainfo": {
            "record_id": "08f8e327d05f97e545d04c81d2ef8de1",
          ...
        },
        "embeddings": [0.1, 0.2, 0.3, ...]
      }
    ],
    "stats": {
      "original_elements": 10,   // 原始解析的元素数量
      "chunked_elements": 15,    // 分块后的元素数量
      "embedded_elements": 15,    // 向量化后的元素数量
      "stages": [
        {
          "type": "parse",
          "config": {
            "provider": "textin-lite"
          }
        },
        {
          "type": "chunk",
          "config": {
            "strategy": "by_title"
          }
        }
      ]
    }
  }
}
```

## 💡 使用示例

### 示例 1: 手动创建 Pipeline（推荐）

```python
from xparse_client import (
    Pipeline, S3Source, MilvusDestination,
    ParseConfig, ChunkConfig, EmbedConfig, Stage
)

# 创建数据源
source = S3Source(
    endpoint='https://your-minio.com',
    access_key='your-access-key',
    secret_key='your-secret-key',
    bucket='documents',
    prefix='pdfs/',
    region='us-east-1',
    pattern=['*.pdf'],  # 仅处理匹配的文件
    recursive=False   # 不递归子目录
)

# 创建目的地
destination = MilvusDestination(
    db_path='./vectors.db',
    collection_name='documents',
    dimension=1024
)

# 配置处理阶段
stages = [
    Stage(
        type='parse',
        config=ParseConfig(provider='textin')
    ),
    Stage(
        type='chunk',
        config=ChunkConfig(
            strategy='by_title',           # 按标题分块
            include_orig_elements=False,
            new_after_n_chars=512,
            max_characters=1024,
            overlap=50                     # 块之间重叠 50 字符
        )
    ),
    Stage(
        type='embed',
        config=EmbedConfig(
            provider='qwen',
            model_name='text-embedding-v3'
        )
    )
]

# 创建并运行 Pipeline
pipeline = Pipeline(
    source=source,
    destination=destination,
    api_base_url='https://api.textin.com/api/xparse',
    api_headers={
        'x-ti-app-id': 'your-app-id',
        'x-ti-secret-code': 'your-secret-code'
    },
    stages=stages
)

pipeline.run()
```

### 示例 1.1: 输出配置字典

手动创建 Pipeline 后，可以使用 `get_config()` 方法获取配置字典：

```python
from xparse_client import (
    Pipeline, LocalSource, LocalDestination,
    ParseConfig, ChunkConfig, EmbedConfig, Stage
)

# 手动创建 Pipeline
source = LocalSource(
    directory='./test_files',
    pattern=['*.pdf'],
    recursive=False
)

destination = LocalDestination(output_dir='./test_output')

stages = [
    Stage(type='parse', config=ParseConfig(provider='textin')),
    Stage(type='chunk', config=ChunkConfig(strategy='basic', max_characters=1024)),
    Stage(type='embed', config=EmbedConfig(provider='qwen', model_name='text-embedding-v3'))
]

pipeline = Pipeline(
    source=source,
    destination=destination,
    api_base_url='https://api.textin.com/api/xparse',
    api_headers={
        'x-ti-app-id': 'your-app-id',
        'x-ti-secret-code': 'your-secret-code'
    },
    stages=stages
)

# 获取配置字典（格式与 create_pipeline_from_config 的入参一致）
config_dict = pipeline.get_config()

# 可以保存为 JSON 文件
import json
with open('pipeline_config.json', 'w', encoding='utf-8') as f:
    json.dump(config_dict, f, indent=2, ensure_ascii=False)

# 或者用于创建新的 Pipeline（需要补充敏感信息如 access_key, secret_key 等）
# from xparse_client import create_pipeline_from_config
# new_pipeline = create_pipeline_from_config(config_dict)
```

### 示例 2: 本地到本地（测试）

```python
from xparse_client import (
    Pipeline, LocalSource, LocalDestination,
    ParseConfig, ChunkConfig, EmbedConfig, Stage
)

# 创建本地数据源
source = LocalSource(
    directory='./test_files',
    pattern=['*.pdf'],
    recursive=False
)

# 创建本地输出目的地
destination = LocalDestination(output_dir='./test_output')

# 配置处理阶段
stages = [
    Stage(
        type='parse',
        config=ParseConfig(provider='textin')
    ),
    Stage(
        type='chunk',
        config=ChunkConfig(
            strategy='basic',
            max_characters=1024
        )
    ),
    Stage(
        type='embed',
        config=EmbedConfig(
            provider='qwen',
            model_name='text-embedding-v3'
        )
    )
]

# 创建并运行 Pipeline
pipeline = Pipeline(
    source=source,
    destination=destination,
    api_base_url='https://api.textin.com/api/xparse',
    api_headers={
        'x-ti-app-id': 'your-app-id',
        'x-ti-secret-code': 'your-secret-code'
    },
    stages=stages
)

pipeline.run()
```

### 示例 3: 不同分块策略的配置

```python
from xparse_client import (
    Pipeline, S3Source, MilvusDestination,
    ParseConfig, ChunkConfig, EmbedConfig, Stage
)

# 创建数据源和目的地
source = S3Source(...)
destination = MilvusDestination(...)

# 配置 1：按页面分块（适合 PDF 文档）
stages_by_page = [
    Stage(
        type='parse',
        config=ParseConfig(provider='textin')
    ),
    Stage(
        type='chunk',
        config=ChunkConfig(
            strategy='by_page',         # 按页面分块
            max_characters=2048,         # 增大块大小
            overlap=100                  # 页面间重叠 100 字符
        )
    ),
    Stage(
        type='embed',
        config=EmbedConfig(
            provider='qwen',
            model_name='text-embedding-v4'  # 使用更高精度的模型
        )
    )
]

# 配置 2：按标题分块（适合结构化文档）
stages_by_title = [
    Stage(
        type='parse',
        config=ParseConfig(provider='textin')
    ),
    Stage(
        type='chunk',
        config=ChunkConfig(
            strategy='by_title',        # 按标题分块
            include_orig_elements=True,  # 保留原始元素信息
            max_characters=1536
        )
    ),
    Stage(
        type='embed',
        config=EmbedConfig(
            provider='qwen',
            model_name='text-embedding-v3'
        )
    )
]

# 根据文档类型选择配置
pipeline = Pipeline(
    source=source,
    destination=destination,
    api_base_url='https://api.textin.com/api/xparse',
    api_headers={...},
    stages=stages_by_page  # 或 stages_by_title
)
pipeline.run()
```

### 示例 4: FTP 数据源配置

```python
from xparse_client import (
    Pipeline, FtpSource, MilvusDestination,
    ParseConfig, ChunkConfig, EmbedConfig, Stage
)

# 创建 FTP 数据源
source = FtpSource(
    host='ftp.example.com',
    port=21,
    username='user',
    password='pass',
    pattern=['*.pdf'],
    recursive=False
)

# 创建 Milvus 目的地
destination = MilvusDestination(
    db_path='./vectors.db',
    collection_name='ftp_docs',
    dimension=1024
)

# 配置处理阶段
stages = [
    Stage(
        type='parse',
        config=ParseConfig(provider='textin')
    ),
    Stage(
        type='chunk',
        config=ChunkConfig(
            strategy='basic',
            max_characters=1024
        )
    ),
    Stage(
        type='embed',
        config=EmbedConfig(
            provider='qwen',
            model_name='text-embedding-v3'
        )
    )
]

# 创建并运行 Pipeline
pipeline = Pipeline(
    source=source,
    destination=destination,
    api_base_url='https://api.textin.com/api/xparse',
    api_headers={
        'x-ti-app-id': 'app-id',
        'x-ti-secret-code': 'secret'
    },
    stages=stages
)

pipeline.run()
```

### 示例 5: 获取处理统计信息

```python
from datetime import datetime, timezone
from xparse_client import (
    Pipeline, LocalSource, LocalDestination,
    ParseConfig, ChunkConfig, EmbedConfig, Stage
)

# 创建 Pipeline
source = LocalSource(
    directory='./docs',
    pattern=['*.pdf'],
    recursive=False
)

destination = LocalDestination(output_dir='./output')

stages = [
    Stage(
        type='parse',
        config=ParseConfig(provider='textin')
    ),
    Stage(
        type='chunk',
        config=ChunkConfig(
            strategy='basic',
            max_characters=1024
        )
    ),
    Stage(
        type='embed',
        config=EmbedConfig(
            provider='qwen',
            model_name='text-embedding-v3'
        )
    )
]

pipeline = Pipeline(
    source=source,
    destination=destination,
    api_base_url='https://api.textin.com/api/xparse',
    api_headers={
        'x-ti-app-id': 'your-app-id',
        'x-ti-secret-code': 'your-secret-code'
    },
    stages=stages
)

# 处理单个文件并获取统计信息
file_bytes, data_source = pipeline.source.read_file('document.pdf')
data_source['date_processed'] = datetime.now(timezone.utc).timestamp()
result = pipeline.process_with_pipeline(file_bytes, 'document.pdf', data_source)

if result:
    elements, stats = result
    print(f"原始元素: {stats.original_elements}")
    print(f"分块后: {stats.chunked_elements}")
    print(f"向量化: {stats.embedded_elements}")
    print(f"执行的 stages: {[s.type for s in stats.stages]}")
    
    # 写入目的地
    metadata = {
        'file_name': 'document.pdf',
        'data_source': data_source
    }
    pipeline.destination.write(elements, metadata)
```

## 📊 Pipeline 统计信息

Pipeline 接口会返回详细的处理统计信息：

| 字段 | 类型 | 说明 |
|------|------|------|
| `original_elements` | int | 原始解析的元素数量 |
| `chunked_elements` | int | 分块后的元素数量 |
| `embedded_elements` | int | 向量化后的元素数量 |
| `stages` | List[Stage] | 实际执行的 stages 配置 |

**示例输出：**
```
✓ Pipeline 完成:
  - 原始元素: 25
  - 分块后: 42
  - 向量化: 42
✓ 写入 Milvus: 42 条
```

## 🔧 扩展开发

### 添加新的 Source

```python
from typing import List, Dict, Any, Tuple
from xparse_client import Source

class MyCustomSource(Source):
    def __init__(self, custom_param):
        self.custom_param = custom_param
    
    def list_files(self) -> List[str]:
        # 实现文件列表逻辑
        return ['file1.pdf', 'file2.pdf']
    
    def read_file(self, file_path: str) -> Tuple[bytes, Dict[str, Any]]:
        # 实现文件读取逻辑并返回数据来源信息
        data_source = {
            'url': f'custom://{file_path}',
            'version': None,
            'date_created': None,
            'date_modified': None,
            'record_locator': {
                'protocol': 'custom',
                'remote_file_path': file_path
            }
        }
        return b'file content', data_source
```

### 添加新的 Destination

```python
from xparse_client import Destination

class MyCustomDestination(Destination):
    def __init__(self, custom_param):
        self.custom_param = custom_param
    
    def write(self, data: List[Dict], metadata: Dict) -> bool:
        # 实现数据写入逻辑
        return True
```

## 📊 数据格式

### 元素格式

每个处理步骤都使用统一的元素格式：

```python
{
    "element_id": str,      # 唯一标识符
    "type": str,            # 元素类型: plaintext, table, image, etc.
    "text": str,            # 文本内容
    "metainfo": {           # 元数据
        "filename": str,
        "orig_elements": list, # chunk处理后添加
        # 其他字段
    },
    "embeddings": list      # 向量（embed 步骤后添加）
}
```

## ⚠️ 注意事项

1. **API 端点**：确保 API 服务正常运行并可访问，目前需要固定使用`https://api.textin.com/api/xparse`，同时需要配置请求头上的app-id/secret-code
2. **向量维度**：Milvus 的 dimension 必须与 pipeline API 返回的向量维度一致，目前pipeline API使用的是1024维度
3. **写入Milvus**：确保目标collection中包含`element_id`，`text`，`record_id`，`embeddings`，`metadata`这些字段
4. **错误重试**：默认每个 API 调用失败会重试 3 次

## 💰 计费

Pipeline接口调用将按页进行计费，具体计费标准可以参考：[通用文档解析](https://www.textin.com/market/detail/xparse)。

## 🐛 故障排除

### API 连接失败

- 检查 `api_base_url` 是否正确
- 确认网络连接正常
- 查看 API 服务日志

### S3 连接失败

- 验证 endpoint、access_key、secret_key
- 确认 bucket 存在且有访问权限

### FTP 连接失败

- 验证路径端口是否正确
- 确认用户名密码是否正确

### 本地文件找不到

- 确认路径正确
- 检查文件匹配模式
- 验证文件权限

### Milvus 写入失败

- 检查向量维度是否匹配
- 确认必须字段是否存在
- 查看 Milvus 日志

## 🔗 相关文件

- `core.py` - 核心 Pipeline 实现
- `run_pipeline.py` - 运行示例

## 📄 License

MIT License

