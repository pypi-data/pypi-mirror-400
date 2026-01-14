#!/usr/bin/env python3
"""
HTTP Uploader - HTTP 上传器

通过 HTTP 将 tar.gz 文件上传到 MCP Server
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path


def calculate_md5(file_path: Path) -> str:
    """
    计算文件 MD5 哈希

    Args:
        file_path: 文件路径

    Returns:
        MD5 哈希值（十六进制字符串）
    """
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    return md5.hexdigest()


def get_upload_config(server_base_url: str, api_key: str) -> dict:
    """
    从服务器获取上传配置

    Args:
        server_base_url: 服务器基础 URL (如 http://192.168.1.100:3100)
        api_key: API Key

    Returns:
        配置结果字典,包含 max_file_size 等信息
    """
    try:
        import requests
    except ImportError:
        return {
            'success': False,
            'error': 'Missing required packages. Please install: pip install requests'
        }

    # 构建配置端点 URL
    config_url = f"{server_base_url.rstrip('/')}/api/config"

    headers = {
        'X-API-Key': api_key
    }

    try:
        response = requests.get(config_url, headers=headers, timeout=10)

        if response.status_code == 200:
            config = response.json()
            return {
                'success': True,
                'max_file_size': config.get('max_file_size', 100 * 1024 * 1024),  # 默认 100MB
                'config': config
            }
        elif response.status_code == 401:
            return {
                'success': False,
                'error': 'INVALID_API_KEY',
                'message': 'API Key is invalid'
            }
        else:
            return {
                'success': False,
                'error': f'HTTP_{response.status_code}',
                'message': f'Failed to get upload config: {response.text[:200]}'
            }
    except Exception as e:
        return {
            'success': False,
            'error': 'CONNECTION_ERROR',
            'message': f'Failed to connect to server: {str(e)}',
            'fallback': 'Using default max file size: 100MB'
        }


def upload_file(file_path: str, server_url: str, app_name: str, api_key: str) -> dict:
    """
    上传文件到服务器（自动计算 MD5 进行完整性验证）

    Args:
        file_path: tar.gz 文件路径
        server_url: 服务器 URL (如 http://192.168.1.100:3100/api/upload)
        app_name: 应用名称
        api_key: API Key

    Returns:
        上传结果字典
    """
    try:
        import requests
        from tqdm import tqdm
    except ImportError:
        return {
            'success': False,
            'error': 'Missing required packages. Please install: pip install requests tqdm'
        }

    # 验证文件
    file_path = Path(file_path)
    if not file_path.exists():
        return {
            'success': False,
            'error': f'File does not exist: {file_path}'
        }

    # 支持的压缩格式
    if not any(file_path.name.endswith(ext) for ext in ['.tar.gz', '.tgz', '.zip', '.tar', '.tar.bz2', '.tar.xz']):
        return {
            'success': False,
            'error': f'Invalid file type. Expected .tar.gz, .tgz, .zip, .tar, .tar.bz2, or .tar.xz, got {file_path.name}'
        }

    # 获取文件大小
    file_size = file_path.stat().st_size
    file_size_mb = file_size / (1024 * 1024)

    # 计算 MD5 哈希
    print(f"Calculating MD5 checksum...")
    file_md5 = calculate_md5(file_path)
    print(f"MD5: {file_md5}")

    # 从服务器获取文件大小限制
    # 提取服务器基础 URL (去掉 /api/upload 或 /upload 后缀)
    server_base_url = server_url.replace('/api/upload', '').replace('/upload', '')
    config_result = get_upload_config(server_base_url, api_key)

    max_file_size = 100 * 1024 * 1024  # 默认 100MB
    if config_result.get('success'):
        max_file_size = config_result.get('max_file_size', max_file_size)
    else:
        # 如果无法获取配置,使用默认值并继续
        print(f"Warning: {config_result.get('message', 'Could not get server config')}. Using default limit.")

    max_file_size_mb = max_file_size / (1024 * 1024)

    # 检查文件大小
    if file_size > max_file_size:
        return {
            'success': False,
            'error': f'File too large: {file_size_mb:.2f} MB (max {max_file_size_mb:.0f} MB)'
        }

    # 准备请求
    headers = {
        'X-API-Key': api_key
    }

    # 创建进度条
    print(f"Uploading {file_path.name} ({file_size_mb:.2f} MB) to {server_url}...")

    with open(file_path, 'rb') as f:
        # 使用 tqdm 显示上传进度
        with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
            # 包装文件对象以支持进度更新
            class TqdmFile:
                def __init__(self, file_obj, pbar):
                    self.file_obj = file_obj
                    self.pbar = pbar

                def read(self, size=-1):
                    data = self.file_obj.read(size)
                    self.pbar.update(len(data))
                    return data

                def __getattr__(self, attr):
                    return getattr(self.file_obj, attr)

            tqdm_file = TqdmFile(f, pbar)

            files = {
                'file': (file_path.name, tqdm_file, 'application/gzip')
            }

            # 准备 form data（包含完整性验证元数据）
            data = {
                'appName': app_name,
                'fileSize': str(file_size),
                'fileMD5': file_md5
            }

            try:
                # 发送 POST 请求
                response = requests.post(
                    server_url,
                    files=files,
                    data=data,
                    headers=headers,
                    timeout=300  # 5 分钟超时
                )

                # 检查响应
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"\n✓ Upload successful!")
                        print(f"  Upload ID: {result.get('uploadId')}")
                        # 检查是否通过完整性验证
                        if result.get('verified'):
                            print(f"  ✓ File integrity verified")
                        else:
                            # 服务器未验证（旧版本服务器）
                            print(f"  ⚠️  Warning: Server did not verify file integrity (server needs upgrade)")
                        return result
                    else:
                        return {
                            'success': False,
                            'error': result.get('error', 'Unknown error'),
                            'message': result.get('message', '')
                        }
                elif response.status_code == 422:
                    # 文件完整性验证失败
                    error_data = response.json()
                    error_code = error_data.get('error', '')
                    if error_code in ['FILE_SIZE_MISMATCH', 'FILE_CHECKSUM_MISMATCH']:
                        print(f"\n✗ File integrity verification failed")
                        print(f"  {error_data.get('message', 'Unknown error')}")
                    return error_data
                elif response.status_code == 401:
                    return {
                        'success': False,
                        'error': 'INVALID_API_KEY',
                        'message': 'API Key is invalid or missing'
                    }
                elif response.status_code == 413:
                    return {
                        'success': False,
                        'error': 'FILE_TOO_LARGE',
                        'message': 'File size exceeds server limit'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'HTTP_{response.status_code}',
                        'message': response.text[:200]
                    }

            except requests.exceptions.Timeout:
                return {
                    'success': False,
                    'error': 'TIMEOUT',
                    'message': 'Upload timeout after 5 minutes'
                }
            except requests.exceptions.ConnectionError as e:
                return {
                    'success': False,
                    'error': 'CONNECTION_ERROR',
                    'message': f'Failed to connect to server: {str(e)}'
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': 'UPLOAD_ERROR',
                    'message': str(e)
                }


def main():
    parser = argparse.ArgumentParser(
        description='Upload tar.gz file to MCP Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload with command-line arguments
  %(prog)s /tmp/app.tar.gz \\
    --server-url http://192.168.1.100:3100/api/upload \\
    --app-name my-app \\
    --api-key a3f9d2c1b8e4...

  # Upload (server config from environment)
  export MCP_UPLOAD_URL="http://192.168.1.100:3100/api/upload"
  export MCP_API_KEY="a3f9d2c1b8e4..."
  %(prog)s /tmp/app.tar.gz --app-name my-app
        """
    )

    parser.add_argument('file_path', help='Path to tar.gz file')
    parser.add_argument('--server-url', help='Server upload URL')
    parser.add_argument('--app-name', required=True, help='Application name')
    parser.add_argument('--api-key', help='API Key for authentication')

    args = parser.parse_args()

    # 获取服务器 URL（优先级：命令行 > 环境变量）
    server_url = args.server_url or os.getenv('MCP_UPLOAD_URL')
    if not server_url:
        print(json.dumps({
            'success': False,
            'error': 'Server URL not provided. Use --server-url or set MCP_UPLOAD_URL environment variable'
        }, indent=2))
        sys.exit(1)

    # 获取 API Key（优先级：命令行 > 环境变量）
    api_key = args.api_key or os.getenv('MCP_API_KEY')
    if not api_key:
        print(json.dumps({
            'success': False,
            'error': 'API Key not provided. Use --api-key or set MCP_API_KEY environment variable'
        }, indent=2))
        sys.exit(1)

    # 执行上传
    result = upload_file(
        file_path=args.file_path,
        server_url=server_url,
        app_name=args.app_name,
        api_key=api_key
    )

    # 输出 JSON 结果
    print(json.dumps(result, indent=2))

    if not result.get('success', False):
        sys.exit(1)


if __name__ == '__main__':
    main()
