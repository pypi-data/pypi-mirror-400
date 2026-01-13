README.md
# mectl

`mectl` 是一个命令行工具，用于辅助mindedge的模型开发，例如从 MinIO 服务器下载文件。

## 功能特性

- 通过命令行从 MinIO 服务器下载文件
- 支持通过配置文件或环境变量设置连接参数
- 灵活的输出路径配置
- 支持指定存储桶名称
- 自动从文件路径提取文件名
- 自动检测并解压ZIP文件
- 上传文件到 MinIO 并创建模型记录

## 安装

```bash
# 使用 pip 安装
pip install mectl
```

## 使用方法

### 基本用法

```bash
mectl get [OPTIONS] FILE_KEY
```

### 上传文件

```bash
mectl upload [OPTIONS] FILE_PATH
```

### 参数说明

#### 下载参数
- `FILE_KEY`: MinIO 对象路径，格式：`bucket_name/object_key`
- `-o, --output`: 本地保存路径（默认为从 FILE_KEY 提取的文件名）
- `-c, --config`: 配置文件路径（JSON，含 oss.accessKey 等）
- `-b, --bucket`: MinIO 存储桶名称（默认为 `suanpan`）

#### 上传参数
- `FILE_PATH`: 本地文件路径
- `-c, --config`: 配置文件路径（JSON，含 oss.accessKey 等）
- `-b, --bucket`: MinIO 存储桶名称（默认为 `suanpan`）

### 配置

工具需要通过配置文件或环境变量提供 MinIO 连接信息。

#### 配置文件示例 (config.json)

```json
{
  "oss": {
    "internalEndpoint": "your-minio-server.com:9000",
    "accessKey": "your-access-key",
    "accessSecret": "your-access-secret"
  }
}
```

#### 环境变量方式

```bash
export NODE_CONFIG='{"oss":{"internalEndpoint":"your-minio-server.com:9000","accessKey":"your-access-key","accessSecret":"your-access-secret"}}'
mectl get bucket-name/file-path
```

### 使用示例

#### 下载文件示例
```bash
# 使用配置文件下载文件
mectl get my-file.txt -c config.json -o ./local-file.txt

# 使用环境变量下载文件（自动提取文件名）
mectl get studio/100029/models/MindEdge.zip -c config.json

# 指定特定存储桶
mectl get my-file.txt -b another-bucket -c config.json
```

#### 上传文件示例
```bash
# 上传文件到 MinIO
mectl upload ./local-model.zip -c config.json

# 上传到指定存储桶
mectl upload ./local-model.zip -b another-bucket -c config.json
```

上传时需要设置以下环境变量：
```bash
export SP_USER_ID=your-user-id
export SP_HOST=your-host-url
```

上传完成后，工具会提示输入模型名称和描述，然后自动创建模型记录。

## 开发

### 本地运行

```bash
# 克隆项目
git clone <repository-url>

# 安装依赖
cd mectl
pip install -e .
```

## 发布到 PyPI

要发布新版本到 PyPI，请执行以下步骤：

1. 更新 [pyproject.toml](file:///home/luxu/project/mindedge-model-tool/pyproject.toml) 中的版本号
2. 运行测试确保一切正常
3. 使用发布脚本发布：

```bash
# 运行发布脚本
./release.sh
```

发布脚本将：
- 检查环境和依赖
- 构建包
- 询问发布目标（测试PyPI或正式PyPI）
- 执行发布

## 依赖

- Python >= 3.10
- minio >= 7.0.0