import os
import sys
import json
from minio import Minio
from minio.error import S3Error
from urllib.parse import urlparse
import subprocess
import click
import requests  # 新增requests库用于HTTP请求


def load_node_config(config_path=None):
    if config_path:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件格式错误: {config_path} - {e}")
    else:
        node_config_str = os.getenv('NODE_CONFIG')
        if not node_config_str:
            raise ValueError("请通过 --config 指定配置文件，或设置 NODE_CONFIG 环境变量")
        try:
            return json.loads(node_config_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"环境变量 NODE_CONFIG 格式错误: {e}")


def parse_minio_url(endpoint):
    if not endpoint.startswith(('http://', 'https://')):
        endpoint = 'http://' + endpoint
    parsed = urlparse(endpoint)
    secure = parsed.scheme == 'https'
    host = parsed.hostname
    if not host:
        # 如果hostname为None，尝试从netloc中提取（不包含端口）
        host = parsed.netloc.split(':')[0] if parsed.netloc else None
    if not host:
        raise ValueError(f"无法从endpoint中解析主机名: {endpoint}")
    
    port = parsed.port
    
    if port:
        host = f"{host}:{port}"
    elif not port and parsed.scheme == 'https':
        host = f"{host}:443"
    elif not port:
        host = f"{host}:9000"  # MinIO默认端口是9000，不是80
        
    return host, secure


def ask_overwrite(file_path):
    """询问用户是否覆盖已存在的文件"""
    if os.path.exists(file_path):
        response = input(f"文件 {file_path} 已存在，是否覆盖？[y/N]: ").strip().lower()
        return response in ['y', 'yes', '是']
    return True


def extract_filename_from_key(file_key):
    """从file_key中提取文件名"""
    # 获取key的最后一部分作为文件名
    return os.path.basename(file_key)


def ask_unzip(file_path):
    """询问用户是否需要解压ZIP文件"""
    response = input(f"检测到文件 {file_path} 是ZIP格式，是否需要解压？[y/N]: ").strip().lower()
    return response in ['y', 'yes', '是']


def unzip_file(file_path):
    """解压ZIP文件"""
    try:
        # 获取文件所在目录
        dir_path = os.path.dirname(file_path)
        if not dir_path:
            dir_path = '.'
        
        # 检查是否有同名解压目录，询问是否覆盖
        extract_dir = os.path.splitext(file_path)[0]  # 去掉.zip后缀作为解压目录
        if os.path.exists(extract_dir):
            if not ask_overwrite(extract_dir):
                print(f"跳过解压: {file_path}")
                return False
        
        # 使用unzip命令解压
        result = subprocess.run(['unzip', '-o', file_path, '-d', dir_path], 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            print(f"✅ 已解压: {file_path}")
            return True
        else:
            print(f"❌ 解压失败: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ 系统未找到unzip命令，请安装unzip后再试")
        return False
    except Exception as e:
        print(f"❌ 解压过程中出现错误: {e}")
        return False


def download_file(file_key, output_path, config_path=None, bucket_name="suanpan"):
    """实际的下载函数，供命令行工具调用"""
    try:
        config = load_node_config(config_path)
        oss = config.get('oss', {})
        
        if not oss:
            print("❌ 配置文件中未找到 'oss' 配置项", file=sys.stderr)
            sys.exit(1)
            
        if 'internalEndpoint' not in oss:
            print("❌ 配置文件中缺少 'internalEndpoint' 配置项", file=sys.stderr)
            sys.exit(1)
            
        if 'accessKey' not in oss or 'accessSecret' not in oss:
            print("❌ 配置文件中缺少 'accessKey' 或 'accessSecret' 配置项", file=sys.stderr)
            sys.exit(1)

        endpoint, secure = parse_minio_url(oss['internalEndpoint'])
        client = Minio(
            endpoint,
            access_key=oss['accessKey'],
            secret_key=oss['accessSecret'],
            secure=secure
        )

        # 检查输出路径是否已存在，询问是否覆盖
        if not ask_overwrite(output_path):
            print(f"跳过下载: {file_key}")
            return None
        
        # 确保输出目录存在
        output_dir = os.path.dirname(os.path.abspath(output_path))
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # 下载文件
        client.fget_object(bucket_name, file_key, output_path)
        print(f"✅ 已下载: {file_key} → {output_path}")
        return output_path
        
    except S3Error as e:
        print(f"❌ MinIO 错误: {e}", file=sys.stderr)
        sys.exit(1)
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


def download_file_with_cli(file_key, output_path=None, config_path=None, bucket_name="suanpan"):
    """命令行接口的下载函数"""
    # 如果未指定输出路径，则从file_key中提取文件名
    if not output_path:
        filename = extract_filename_from_key(file_key)
        output_path = os.path.join("./", filename)
    
    # 执行下载
    downloaded_path = download_file(file_key, output_path, config_path, bucket_name)
    
    # 检查下载是否被跳过（用户选择不覆盖）
    if downloaded_path is None:
        return
    
    # 检查是否为zip文件，如果是则询问是否需要解压
    if downloaded_path.lower().endswith('.zip'):
        if ask_unzip(downloaded_path):
            unzip_file(downloaded_path)


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """MindEdge模型工具命令行"""
    pass


@cli.command()
@click.argument('file_key')
@click.option('-o', '--output', default=None, help='本地保存路径')
@click.option('-c', '--config', help='配置文件路径（JSON，含 oss.accessKey 等）')
@click.option('-b', '--bucket', default='suanpan', help='MinIO 存储桶名称，默认为 \'suanpan\'')
def get(file_key, output, config, bucket):
    """下载MinIO中的文件"""
    download_file_with_cli(file_key, output, config, bucket)


def upload_file_to_oss(file_path, config_path=None, bucket_name="suanpan"):
    """上传文件到OSS的函数"""
    try:
        config = load_node_config(config_path)
        oss = config.get('oss', {})
        
        if not oss:
            print("❌ 配置文件中未找到 'oss' 配置项", file=sys.stderr)
            sys.exit(1)
            
        if 'internalEndpoint' not in oss:
            print("❌ 配置文件中缺少 'internalEndpoint' 配置项", file=sys.stderr)
            sys.exit(1)
            
        if 'accessKey' not in oss or 'accessSecret' not in oss:
            print("❌ 配置文件中缺少 'accessKey' 或 'accessSecret' 配置项", file=sys.stderr)
            sys.exit(1)

        endpoint, secure = parse_minio_url(oss['internalEndpoint'])
        client = Minio(
            endpoint,
            access_key=oss['accessKey'],
            secret_key=oss['accessSecret'],
            secure=secure
        )

        # 检查文件是否存在
        if not os.path.isfile(file_path):
            print(f"❌ 文件不存在: {file_path}", file=sys.stderr)
            sys.exit(1)
        
        # 获取用户ID
        user_id = os.getenv('SP_USER_ID')
        if not user_id:
            print("❌ 请设置环境变量 SP_USER_ID", file=sys.stderr)
            sys.exit(1)
        
        # 构建key
        filename = os.path.basename(file_path)
        object_key = f"studio/{user_id}/models/{filename}"
        
        # 上传文件
        client.fput_object(bucket_name, object_key, file_path)
        print(f"✅ 已上传: {file_path} → {object_key}")
        
        return object_key
        
    except S3Error as e:
        print(f"❌ MinIO 错误: {e}", file=sys.stderr)
        sys.exit(1)
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


def create_model_record(object_key):
    """创建模型记录的函数"""
    # 获取host
    host = os.getenv('SP_API_HOST')
    if not host:
        print("❌ 请设置环境变量 SP_API_HOST", file=sys.stderr)
        sys.exit(1)
    
    # 提示用户输入模型名称和描述
    model_name = input("请输入模型名称: ").strip()
    if not model_name:
        print("❌ 模型名称不能为空", file=sys.stderr)
        sys.exit(1)
    
    model_description = input("请输入模型描述: ").strip()
    
    # 构建请求数据
    data = {
        "name": model_name,
        "description": model_description,
        "fileKey": object_key  # 使用上传到OSS的key作为路径
    }
    
    # 发送POST请求
    url = f"http://{host}/servicestack/model/models/create"
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("✅ 模型记录创建成功")
        else:
            print(f"❌ 创建模型记录失败: {response.status_code} - {response.text}", file=sys.stderr)
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


@cli.command()
@click.argument('file_path')
@click.option('-c', '--config', help='配置文件路径（JSON，含 oss.accessKey 等）')
@click.option('-b', '--bucket', default='suanpan', help='MinIO 存储桶名称，默认为 \'suanpan\'')
def put(file_path, config, bucket):
    """上传文件到MinIO"""
    # 上传文件到OSS
    object_key = upload_file_to_oss(file_path, config, bucket)
    
    # 创建模型记录
    create_model_record(object_key)


def main():
    cli()


if __name__ == "__main__":
    main()