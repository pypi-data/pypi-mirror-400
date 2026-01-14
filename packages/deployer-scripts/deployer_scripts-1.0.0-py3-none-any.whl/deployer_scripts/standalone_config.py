#!/usr/bin/env python3
"""
Standalone Config - Next.js Standalone 模式配置工具

用于修改 next.config.* 文件，启用 output: 'standalone' 配置

版本: v1.0.0
"""

import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


def check_standalone(project_path: str) -> Dict:
    """
    检查 Next.js 项目的 Standalone 配置状态

    Args:
        project_path: 项目路径

    Returns:
        {
            'success': bool,
            'enabled': bool,
            'configFile': str | None,
            'hasOutputConfig': bool,
            'canEnable': bool,
            'reason': str | None
        }
    """
    project = Path(project_path).resolve()

    # 查找配置文件
    config_files = ['next.config.js', 'next.config.mjs', 'next.config.ts']
    config_file = None
    config_content = None

    for filename in config_files:
        file_path = project / filename
        if file_path.exists():
            config_file = filename
            try:
                config_content = file_path.read_text(encoding='utf-8')
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Failed to read {filename}: {e}'
                }
            break

    # 解析配置
    enabled = False
    has_output_config = False

    if config_content:
        if re.search(r"output\s*:\s*['\"]standalone['\"]", config_content):
            enabled = True
            has_output_config = True
        elif re.search(r"output\s*:\s*['\"](\w+)['\"]", config_content):
            has_output_config = True

    # 检查是否可以启用
    can_enable = not enabled and not has_output_config
    reason = None

    if enabled:
        reason = 'already_enabled'
    elif has_output_config:
        reason = 'other_output_mode'

    return {
        'success': True,
        'enabled': enabled,
        'configFile': config_file,
        'hasOutputConfig': has_output_config,
        'canEnable': can_enable,
        'reason': reason
    }


def enable_standalone(project_path: str) -> Dict:
    """
    修改 next.config.* 启用 Standalone 模式

    Args:
        project_path: 项目路径

    Returns:
        {
            'success': bool,
            'message': str,
            'backupPath': str | None,
            'error': str | None
        }
    """
    project = Path(project_path).resolve()

    # 1. 先检查状态
    status = check_standalone(project_path)
    if not status['success']:
        return status

    if status['enabled']:
        return {
            'success': True,
            'message': 'Standalone mode is already enabled',
            'backupPath': None
        }

    if status['hasOutputConfig']:
        return {
            'success': False,
            'error': 'Cannot enable standalone: another output mode is configured',
            'reason': 'other_output_mode'
        }

    config_file = status['configFile']

    # 2. 如果没有配置文件，创建一个
    if not config_file:
        config_file = 'next.config.js'
        config_path = project / config_file

        new_config = """/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
}

module.exports = nextConfig
"""
        try:
            config_path.write_text(new_config, encoding='utf-8')
            return {
                'success': True,
                'message': f'Created {config_file} with standalone mode enabled',
                'backupPath': None,
                'created': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to create {config_file}: {e}'
            }

    # 3. 读取现有配置文件
    config_path = project / config_file

    try:
        content = config_path.read_text(encoding='utf-8')
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to read {config_file}: {e}'
        }

    # 4. 创建备份
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = project / f'{config_file}.{timestamp}.bak'

    try:
        shutil.copy2(config_path, backup_path)
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to create backup: {e}'
        }

    # 5. 修改配置文件
    modified_content = _insert_standalone_config(content, config_file)

    if modified_content is None:
        return {
            'success': False,
            'error': 'Failed to modify config: complex configuration format detected. Please add "output: \'standalone\'" manually.',
            'backupPath': str(backup_path),
            'manual_required': True
        }

    # 6. 写入修改后的内容
    try:
        config_path.write_text(modified_content, encoding='utf-8')
    except Exception as e:
        # 恢复备份
        try:
            shutil.copy2(backup_path, config_path)
        except:
            pass
        return {
            'success': False,
            'error': f'Failed to write {config_file}: {e}',
            'backupPath': str(backup_path)
        }

    return {
        'success': True,
        'message': f'Successfully enabled standalone mode in {config_file}',
        'backupPath': str(backup_path)
    }


def disable_standalone(project_path: str) -> Dict:
    """
    禁用 Next.js Standalone 模式

    Args:
        project_path: 项目路径

    Returns:
        {
            'success': bool,
            'message': str,
            'backupPath': str | None,
            'error': str | None
        }
    """
    project = Path(project_path).resolve()

    # 1. 先检查状态
    status = check_standalone(project_path)
    if not status['success']:
        return status

    if not status['enabled']:
        return {
            'success': True,
            'message': 'Standalone mode is not enabled',
            'backupPath': None
        }

    config_file = status['configFile']
    config_path = project / config_file

    # 2. 读取配置文件
    try:
        content = config_path.read_text(encoding='utf-8')
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to read {config_file}: {e}'
        }

    # 3. 创建备份
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = project / f'{config_file}.{timestamp}.bak'

    try:
        shutil.copy2(config_path, backup_path)
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to create backup: {e}'
        }

    # 4. 移除 standalone 配置
    modified_content = _remove_standalone_config(content)

    if modified_content is None:
        return {
            'success': False,
            'error': 'Failed to remove standalone config: complex configuration format detected. Please remove manually.',
            'backupPath': str(backup_path),
            'manual_required': True
        }

    # 5. 写入修改后的内容
    try:
        config_path.write_text(modified_content, encoding='utf-8')
    except Exception as e:
        # 恢复备份
        try:
            shutil.copy2(backup_path, config_path)
        except:
            pass
        return {
            'success': False,
            'error': f'Failed to write {config_file}: {e}',
            'backupPath': str(backup_path)
        }

    return {
        'success': True,
        'message': f'Successfully disabled standalone mode in {config_file}',
        'backupPath': str(backup_path)
    }


def _remove_standalone_config(content: str) -> Optional[str]:
    """
    从配置内容中移除 output: 'standalone'

    Args:
        content: 原始配置文件内容

    Returns:
        修改后的内容，如果无法处理返回 None
    """
    # 匹配并移除 output: 'standalone' 行（包括可能的逗号和换行）
    patterns = [
        r"\n\s*output:\s*['\"]standalone['\"],?\s*",  # 带换行前缀
        r"output:\s*['\"]standalone['\"],?\s*\n\s*",  # 带换行后缀
        r"output:\s*['\"]standalone['\"],?\s*",       # 基本匹配
    ]

    for pattern in patterns:
        if re.search(pattern, content):
            modified = re.sub(pattern, '\n  ', content, count=1)
            # 清理多余空行
            modified = re.sub(r'\n\s*\n\s*\n', '\n\n', modified)
            return modified

    return None


def _insert_standalone_config(content: str, config_file: str) -> Optional[str]:
    """
    在配置内容中插入 output: 'standalone'

    Args:
        content: 原始配置文件内容
        config_file: 配置文件名 (用于判断格式)

    Returns:
        修改后的内容，如果无法处理返回 None
    """
    # 检测配置格式并插入

    # 模式 1: next.config.js - CommonJS
    # module.exports = { ... }
    # const nextConfig = { ... }; module.exports = nextConfig
    if config_file.endswith('.js'):
        # 尝试在 { 后面插入
        patterns = [
            # module.exports = {
            (r'(module\.exports\s*=\s*\{)', r"\1\n  output: 'standalone',"),
            # const nextConfig = {
            (r'(const\s+\w+\s*=\s*\{)', r"\1\n  output: 'standalone',"),
            # const config = {
            (r'(const\s+config\s*=\s*\{)', r"\1\n  output: 'standalone',"),
        ]

        for pattern, replacement in patterns:
            if re.search(pattern, content):
                return re.sub(pattern, replacement, content, count=1)

    # 模式 2: next.config.mjs - ES Module
    # export default { ... }
    elif config_file.endswith('.mjs'):
        patterns = [
            # export default {
            (r'(export\s+default\s*\{)', r"\1\n  output: 'standalone',"),
            # const nextConfig = {
            (r'(const\s+\w+\s*=\s*\{)', r"\1\n  output: 'standalone',"),
        ]

        for pattern, replacement in patterns:
            if re.search(pattern, content):
                return re.sub(pattern, replacement, content, count=1)

    # 模式 3: next.config.ts - TypeScript
    # const config: NextConfig = { ... }
    elif config_file.endswith('.ts'):
        patterns = [
            # const config: NextConfig = {
            (r'(const\s+\w+\s*:\s*NextConfig\s*=\s*\{)', r"\1\n  output: 'standalone',"),
            # const nextConfig = {
            (r'(const\s+\w+\s*=\s*\{)', r"\1\n  output: 'standalone',"),
            # export default {
            (r'(export\s+default\s*\{)', r"\1\n  output: 'standalone',"),
        ]

        for pattern, replacement in patterns:
            if re.search(pattern, content):
                return re.sub(pattern, replacement, content, count=1)

    # 无法识别的格式
    return None


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'error': 'Usage: standalone_config.py <check|enable> <project_path>'
        }, indent=2))
        sys.exit(1)

    action = sys.argv[1]

    if action == 'check':
        if len(sys.argv) < 3:
            print(json.dumps({
                'success': False,
                'error': 'Usage: standalone_config.py check <project_path>'
            }, indent=2))
            sys.exit(1)

        project_path = sys.argv[2]
        result = check_standalone(project_path)
        print(json.dumps(result, indent=2))

    elif action == 'enable':
        if len(sys.argv) < 3:
            print(json.dumps({
                'success': False,
                'error': 'Usage: standalone_config.py enable <project_path>'
            }, indent=2))
            sys.exit(1)

        project_path = sys.argv[2]
        result = enable_standalone(project_path)
        print(json.dumps(result, indent=2))

        if not result.get('success'):
            sys.exit(1)

    elif action == 'disable':
        if len(sys.argv) < 3:
            print(json.dumps({
                'success': False,
                'error': 'Usage: standalone_config.py disable <project_path>'
            }, indent=2))
            sys.exit(1)

        project_path = sys.argv[2]
        result = disable_standalone(project_path)
        print(json.dumps(result, indent=2))

        if not result.get('success'):
            sys.exit(1)

    else:
        print(json.dumps({
            'success': False,
            'error': f'Unknown action: {action}. Use "check", "enable", or "disable".'
        }, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    main()
