#!/usr/bin/env python3
"""
Config Utils - 统一配置工具库

提供配置文件的读取、验证、写入和智能合并功能
支持 hybrid 类型和 MCP 特性

版本: v1.1.0
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union


def validate_config(config: Dict) -> Dict:
    """
    验证配置文件格式（支持 hybrid 类型）

    Args:
        config: 配置对象

    Returns:
        验证结果 {'valid': bool, 'error': str}
    """
    # 检查基础必需字段
    basic_required = ['version', 'appName', 'appVersion', 'framework']
    for field in basic_required:
        if field not in config:
            return {
                'valid': False,
                'error': f'Missing required field: {field}'
            }

    framework = config.get('framework')

    # hybrid 类型验证
    if framework == 'hybrid':
        return _validate_hybrid_config(config)

    # 单一框架类型验证
    return _validate_single_framework_config(config)


def _validate_hybrid_config(config: Dict) -> Dict:
    """验证 hybrid 类型配置"""
    # 检查 components
    if 'components' not in config:
        return {
            'valid': False,
            'error': 'Missing required field: components (required for hybrid framework)'
        }

    components = config.get('components', [])
    if not isinstance(components, list) or len(components) == 0:
        return {
            'valid': False,
            'error': 'components must be a non-empty array'
        }

    # 验证每个 component
    has_primary = False
    for i, comp in enumerate(components):
        # 必需字段
        for field in ['path', 'language', 'framework']:
            if field not in comp:
                return {
                    'valid': False,
                    'error': f'components[{i}] missing required field: {field}'
                }

        # 语言验证
        if comp['language'] not in ['python', 'nodejs']:
            return {
                'valid': False,
                'error': f'components[{i}].language must be "python" or "nodejs"'
            }

        # 端口验证（如果存在）
        if 'port' in comp:
            port = comp['port']
            if not isinstance(port, int) or port < 1 or port > 65535:
                return {
                    'valid': False,
                    'error': f'components[{i}].port must be between 1-65535'
                }

        # primary 标记
        if comp.get('primary'):
            has_primary = True

    # 检查 runtime
    if 'runtime' not in config:
        return {
            'valid': False,
            'error': 'Missing required field: runtime (required for hybrid framework)'
        }

    runtime = config.get('runtime', {})
    if 'requires' not in runtime:
        return {
            'valid': False,
            'error': 'Missing runtime.requires (required for hybrid framework)'
        }

    requires = runtime.get('requires', [])
    if not isinstance(requires, list) or len(requires) == 0:
        return {
            'valid': False,
            'error': 'runtime.requires must be a non-empty array'
        }

    # 验证 volumes（如果存在）
    volumes_validation = _validate_volumes(config.get('volumes', []))
    if not volumes_validation['valid']:
        return volumes_validation

    return {'valid': True}


def _validate_single_framework_config(config: Dict) -> Dict:
    """验证单一框架类型配置"""
    # 检查必需字段
    required_fields = ['build', 'runtime']
    for field in required_fields:
        if field not in config:
            return {
                'valid': False,
                'error': f'Missing required field: {field}'
            }

    # 检查 build 配置
    build = config.get('build', {})
    if 'command' not in build:
        return {
            'valid': False,
            'error': 'Missing build.command'
        }

    # 允许 build.command 为空字符串（Python 项目无需构建）
    build_command = build.get('command')
    if build_command is not None and not isinstance(build_command, str):
        return {
            'valid': False,
            'error': 'build.command must be a string or null'
        }

    # 检查 runtime 配置
    runtime = config.get('runtime', {})
    required_runtime_fields = ['command', 'port']
    for field in required_runtime_fields:
        if field not in runtime:
            return {
                'valid': False,
                'error': f'Missing runtime.{field}'
            }

    # nodeVersion 对 Node.js 项目是必需的，但对 Python 项目可选
    if 'nodeVersion' in runtime:
        node_version = runtime.get('nodeVersion')
        if node_version is not None and not isinstance(node_version, str):
            return {
                'valid': False,
                'error': 'runtime.nodeVersion must be a string or null'
            }

    # 检查端口范围
    port = runtime.get('port')
    if not isinstance(port, int) or port < 1 or port > 65535:
        return {
            'valid': False,
            'error': f'Invalid port: {port}. Must be between 1-65535'
        }

    # 验证 volumes
    volumes_validation = _validate_volumes(config.get('volumes', []))
    if not volumes_validation['valid']:
        return volumes_validation

    return {'valid': True}


def _validate_volumes(volumes: List) -> Dict:
    """验证 volumes 配置"""
    if not isinstance(volumes, list):
        return {
            'valid': False,
            'error': 'volumes must be an array'
        }

    for i, volume in enumerate(volumes):
        if 'source' not in volume:
            return {
                'valid': False,
                'error': f'volumes[{i}] missing source field'
            }
        if not volume['source'].startswith('./'):
            return {
                'valid': False,
                'error': f'volumes[{i}].source must start with "./"'
            }

        # ========== 安全检查：禁止危险路径 ==========
        source = volume['source']
        dangerous_patterns = [".", "./.", "..", "/"]

        # 标准化路径检查
        normalized = str(Path(source).as_posix())

        if normalized in dangerous_patterns or normalized.startswith("../"):
            return {
                'valid': False,
                'error': f'volumes[{i}].source="{source}" is dangerous. '
                        f'Cannot mount project root, parent directory, or root. '
                        f'Please specify a subdirectory or file (e.g., "./data", "./app.db")'
            }

        if 'priority' in volume and volume['priority'] not in ['high', 'medium', 'low']:
            return {
                'valid': False,
                'error': f'volumes[{i}].priority must be "high", "medium", or "low"'
            }

    return {'valid': True}


def read_config(project_path: str) -> Optional[Dict]:
    """
    读取并验证 app-deploy.json 配置文件

    Args:
        project_path: 项目路径

    Returns:
        配置字典，如果文件不存在返回 None

    Raises:
        ValueError: 配置无效或格式错误
    """
    config_path = Path(project_path).resolve() / 'app-deploy.json'

    # 检查配置文件是否存在
    if not config_path.exists():
        return None

    try:
        # 读取配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 自动验证配置
        validation_result = validate_config(config)
        if not validation_result['valid']:
            raise ValueError(validation_result['error'])

        return config

    except json.JSONDecodeError as e:
        raise ValueError(f'Invalid JSON format: {str(e)}')
    except Exception as e:
        raise ValueError(f'Failed to read config file: {str(e)}')


def write_config(project_path: str, config: Dict) -> None:
    """
    写入配置文件前自动验证

    Args:
        project_path: 项目路径
        config: 配置字典

    Raises:
        ValueError: 配置无效或写入失败
    """
    # 验证配置
    validation_result = validate_config(config)
    if not validation_result['valid']:
        raise ValueError(validation_result['error'])

    config_path = Path(project_path).resolve() / 'app-deploy.json'

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise ValueError(f'Failed to write config file: {str(e)}')


def compare_detection(existing: Dict, detection: Dict) -> bool:
    """
    比对检测结果是否变化（支持 hybrid 类型）

    Args:
        existing: 现有配置
        detection: 新的检测结果

    Returns:
        True: 有变化，需要更新
        False: 无变化，跳过写入
    """
    if not existing:
        return True

    # 框架类型变化
    if existing.get('framework') != detection.get('framework'):
        return True

    # hybrid 类型比对
    if detection.get('framework') == 'hybrid':
        checks = [
            _components_changed(existing.get('components', []), detection.get('components', [])),
            existing.get('runtime', {}).get('command') != detection.get('runtime', {}).get('command'),
            set(existing.get('runtime', {}).get('requires', [])) != set(detection.get('runtime', {}).get('requires', [])),
            existing.get('features', []) != detection.get('features', []),
            _volumes_changed(existing.get('volumes', []), detection.get('volumes', []))
        ]
    else:
        # 单一框架类型比对
        checks = [
            existing.get('build', {}).get('command') != detection.get('build', {}).get('command'),
            existing.get('runtime', {}).get('command') != detection.get('runtime', {}).get('command'),
            existing.get('runtime', {}).get('port') != detection.get('runtime', {}).get('port'),
            existing.get('runtime', {}).get('nodeVersion') != detection.get('runtime', {}).get('nodeVersion'),
            existing.get('features', []) != detection.get('features', []),
            _volumes_changed(existing.get('volumes', []), detection.get('volumes', []))
        ]

    return any(checks)


def _components_changed(old: List[Dict], new: List[Dict]) -> bool:
    """比对 components 是否变化"""
    if len(old) != len(new):
        return True

    # 按 path 排序后比对
    old_sorted = sorted(old, key=lambda x: x.get('path', ''))
    new_sorted = sorted(new, key=lambda x: x.get('path', ''))

    for o, n in zip(old_sorted, new_sorted):
        if (o.get('path') != n.get('path') or
            o.get('language') != n.get('language') or
            o.get('framework') != n.get('framework') or
            o.get('port') != n.get('port')):
            return True

    return False


def _volumes_changed(old: List[Dict], new: List[Dict]) -> bool:
    """
    比对卷是否变化（仅比对检测到的卷）

    Args:
        old: 旧的卷列表
        new: 新的卷列表

    Returns:
        True: 有变化
    """
    old_set = {(v['source'], v.get('reason', ''), v.get('priority', 'medium')) for v in old}
    new_set = {(v['source'], v.get('reason', ''), v.get('priority', 'medium')) for v in new}
    return old_set != new_set


def merge_config(existing: Optional[Dict], detection: Dict, project_path: str = None) -> Dict:
    """
    智能合并配置（保留用户字段，支持 hybrid 类型）

    保留字段：
    - appName
    - appVersion
    - optimization.*
    - 用户添加的自定义字段

    更新字段：
    - framework
    - build.* / components (取决于类型)
    - runtime.*
    - features
    - mcp
    - volumes（增量合并，自动过滤已删除的目录）

    Args:
        existing: 现有配置（None 表示新项目）
        detection: 检测结果
        project_path: 项目路径（用于验证卷目录是否存在）

    Returns:
        合并后的配置
    """
    merged = existing.copy() if existing else {}

    # 更新框架类型
    merged['framework'] = detection['framework']

    # 根据类型更新不同字段
    if detection['framework'] == 'hybrid':
        # hybrid 类型
        merged['components'] = detection['components']
        merged['runtime'] = detection['runtime']
        # 移除单一框架类型的字段
        merged.pop('build', None)
    else:
        # 单一框架类型
        merged['build'] = detection['build']
        merged['runtime'] = detection['runtime']
        # 移除 hybrid 类型的字段
        merged.pop('components', None)

    # 更新 features
    if 'features' in detection:
        merged['features'] = detection['features']
    elif 'features' in merged and 'features' not in detection:
        merged.pop('features', None)

    # 更新 mcp 配置
    if 'mcp' in detection:
        merged['mcp'] = detection['mcp']
    elif 'mcp' in merged and 'mcp' not in detection:
        merged.pop('mcp', None)

    # 更新 environment 配置（增量合并：保留用户添加的，更新检测到的）
    if 'environment' in detection:
        existing_env = merged.get('environment', {})
        detected_env = detection['environment']
        # 用户添加的环境变量优先保留，检测到的作为基础
        merged['environment'] = {**detected_env, **existing_env}
    # 注意：如果检测结果没有 environment，保留用户手动添加的（不删除）

    # 卷增量合并（保留用户手动添加的卷，但过滤已删除的目录）
    detected_sources = {v['source'] for v in detection.get('volumes', [])}
    user_volumes = [v for v in merged.get('volumes', [])
                    if v['source'] not in detected_sources]

    # 验证用户卷目录是否仍然存在
    if project_path and user_volumes:
        project = Path(project_path).resolve()
        valid_user_volumes = []
        removed_volumes = []

        for vol in user_volumes:
            source = vol['source'].lstrip('./')
            vol_path = project / source
            if vol_path.exists():
                valid_user_volumes.append(vol)
            else:
                removed_volumes.append(vol['source'])

        if removed_volumes:
            print(f"  ℹ️  Removed {len(removed_volumes)} non-existent volume(s):", file=sys.stderr)
            for src in removed_volumes:
                print(f"     - {src}", file=sys.stderr)

        user_volumes = valid_user_volumes

    merged['volumes'] = detection.get('volumes', []) + user_volumes

    # 保留用户字段
    if not merged.get('appName'):
        merged['appName'] = ""
    if not merged.get('appVersion'):
        merged['appVersion'] = "1.0.0"
    if not merged.get('version'):
        merged['version'] = "1.0"

    # 保留 optimization 配置（用户自定义）
    if existing and 'optimization' in existing:
        merged['optimization'] = existing['optimization']

    return merged


def get_change_summary(existing: Optional[Dict], detection: Dict) -> List[str]:
    """
    获取变更摘要

    Args:
        existing: 现有配置
        detection: 新的检测结果

    Returns:
        变更描述列表
    """
    if not existing:
        return ["New configuration created"]

    changes = []

    # 框架变化
    if existing.get('framework') != detection.get('framework'):
        changes.append(f"Framework: {existing.get('framework', 'None')} → {detection.get('framework')}")

    # 构建命令变化
    old_build = existing.get('build', {}).get('command', '')
    new_build = detection.get('build', {}).get('command', '')
    if old_build != new_build:
        changes.append(f"Build command: {old_build or 'None'} → {new_build or 'None'}")

    # 启动命令变化
    old_runtime = existing.get('runtime', {}).get('command', '')
    new_runtime = detection.get('runtime', {}).get('command', '')
    if old_runtime != new_runtime:
        changes.append(f"Start command: {old_runtime} → {new_runtime}")

    # 端口变化
    old_port = existing.get('runtime', {}).get('port')
    new_port = detection.get('runtime', {}).get('port')
    if old_port != new_port:
        changes.append(f"Port: {old_port} → {new_port}")

    # 卷变化
    if _volumes_changed(existing.get('volumes', []), detection.get('volumes', [])):
        old_count = len(existing.get('volumes', []))
        new_count = len(detection.get('volumes', []))
        changes.append(f"Volumes: {old_count} → {new_count} (re-detect data directories)")

    return changes


def update_app_config(project_path: str, app_name: Optional[str] = None,
                     app_version: Optional[str] = None) -> Dict:
    """
    更新配置中的应用名称和版本（仅更新这两个字段，保留其他配置）

    Args:
        project_path: 项目路径
        app_name: 应用名称（可选）
        app_version: 应用版本（可选）

    Returns:
        更新结果
    """
    try:
        # 读取现有配置
        config = read_config(project_path)

        if not config:
            return {
                'success': False,
                'error': 'CONFIG_NOT_FOUND',
                'message': 'app-deploy.json not found',
                'suggestion': 'Run detect_project first to generate app-deploy.json'
            }

        # 记录原始值用于比对
        original_app_name = config.get('appName', '')
        original_app_version = config.get('appVersion', '1.0.0')

        # 首次打包：如果配置中没有 appName，必须提供
        if not config.get('appName'):
            if not app_name:
                return {
                    'success': False,
                    'error': 'APP_NAME_REQUIRED',
                    'message': 'This is the first time packaging this project. Please provide app_name parameter.',
                    'instruction': 'The MCP client should prompt user to confirm the application name.'
                }
            # 首次设置 appName
            config['appName'] = app_name
        else:
            # 如果提供了新的 appName，使用新值（允许用户修改应用名）
            if app_name:
                config['appName'] = app_name

        # 每次打包：必须提供 appVersion
        if not app_version:
            return {
                'success': False,
                'error': 'APP_VERSION_REQUIRED',
                'message': 'Please provide app_version parameter for this package.',
                'instruction': 'The MCP client should prompt user to confirm the version number.',
                'current_version': config.get('appVersion', '1.0.0'),
                'suggestion': f'Suggested next version: {_suggest_next_version(config.get("appVersion", "1.0.0"))}'
            }

        # 更新 appVersion
        config['appVersion'] = app_version

        # 比对是否有变化
        has_changes = (
            config['appName'] != original_app_name or
            config['appVersion'] != original_app_version
        )

        # 只在有变化时写回配置文件
        if has_changes:
            write_config(project_path, config)
        else:
            # 无变化，跳过写入
            pass

        return {
            'success': True,
            'app_name': config['appName'],
            'app_version': config['appVersion'],
            'operation': 'updated' if has_changes else 'unchanged',
            'message': 'Configuration updated successfully' if has_changes else 'Configuration unchanged, skip writing'
        }

    except ValueError as e:
        return {
            'success': False,
            'error': 'CONFIG_ERROR',
            'message': str(e)
        }


def _suggest_next_version(current_version: str) -> str:
    """
    建议下一个版本号

    Args:
        current_version: 当前版本号

    Returns:
        建议的版本号
    """
    try:
        parts = current_version.split('.')
        if len(parts) == 3:
            # 语义化版本：递增补丁版本号
            return f"{parts[0]}.{parts[1]}.{int(parts[2]) + 1}"
        elif len(parts) == 2:
            # 主.次版本：递增次版本号
            return f"{parts[0]}.{int(parts[1]) + 1}"
        else:
            # 其他格式：直接递增
            if current_version.isdigit():
                return str(int(current_version) + 1)
            else:
                return f"{current_version}-2"
    except (ValueError, IndexError):
        # 解析失败，使用默认格式
        return "1.0.1"


# 向后兼容的导出（供现有代码使用）
# from manage_config import manage_config