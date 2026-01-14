#!/usr/bin/env python3
"""
Project Packager - 项目打包器

排除依赖和构建产物，将项目压缩为 tar.gz 格式
"""

import datetime
import json
import os
import re
import sys
import tarfile
import tempfile
import time
from pathlib import Path
from typing import List, Set

from .config_utils import update_app_config


# 默认排除规则
DEFAULT_EXCLUDE_PATTERNS = [
    # Node.js 排除规则
    'node_modules',
    '.git',
    '.next',
    '.nuxt',
    'dist',
    'build',
    'out',
    '.turbo',
    '.cache',
    'coverage',
    '.vscode',
    '.idea',
    '.claude',
    'CLAUDE.md',
    '.esdata',
    '.nx',
    '.lerna',
    '.parcel-cache',
    '.vite',
    '.DS_Store',
    'Thumbs.db',
    '*.log',
    '.env.local',
    '.env.*.local',

    # Python 排除规则
    '__pycache__',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '.Python',
    '.venv',
    'venv',
    'env',
    'ENV',
    '.pytest_cache',
    '.mypy_cache',
    '.ruff_cache',
    '*.egg-info',
    '*.egg',
    '.tox',
    '.coverage',
    'htmlcov',

    # 数据持久化和临时文件目录
    # 这些目录通常应该通过卷挂载，而不是打包到镜像中
    'tmp',
    'temp',
    '.tmp',
    'log',
    'logs',
    'upload',
    'uploads',
    'backup',
    'backups',
]


class ProjectPackager:
    def __init__(self, project_path: str, output_path: str, app_name: str = None, app_version: str = None):
        self.project_path = Path(project_path).resolve()
        self.output_path = Path(output_path).resolve()
        self.exclude_patterns = DEFAULT_EXCLUDE_PATTERNS.copy()
        self.excluded_count = 0
        self.included_count = 0
        self.app_name = app_name
        self.app_version = app_version

    def _sanitize_name(self, name: str) -> str:
        """清理名称用于文件名"""
        if not name:
            return "app"

        # 只允许字母、数字、下划线、点号和连字符
        # 替换空格为连字符
        sanitized = re.sub(r'[^-~0-9A-Za-z._-]', '-', name)  # 只允许可见ASCII字符
        sanitized = re.sub(r'[<>]', '-', sanitized)  # 尖括号转连字符
        sanitized = re.sub(r'-+', '-', sanitized)  # 多个连字符视为一个
        sanitized = sanitized.strip('-').strip('.')  # 去除首尾连字符和点

        # 长度限制，确保整个文件名不超过255字符（文件系统限制）
        max_length = 50  # 为版本号预留空间
        return sanitized[:max_length] if sanitized else "app"

    def _generate_friendly_filename(self, output_path: str) -> str:
        """生成友好的文件名：{app_name}-v{app_version}.tar.gz"""
        if output_path and output_path.strip():  # 如果用户指定了路径，使用用户的
            return output_path.strip()

        # 使用 {app_name}-v{app_version} 格式
        clean_app_name = self._sanitize_name(self.app_name or "app")
        clean_version = self._sanitize_name(self.app_version or "1.0.0")

        filename = f"{clean_app_name}-v{clean_version}"

        # 确保扩展名
        if not filename.endswith(('.tar.gz', '.tgz')):
            filename += '.tar.gz'

        return filename

    def package(self) -> dict:
        """执行项目打包"""
        # 验证项目路径
        if not self.project_path.exists():
            return {
                'success': False,
                'error': f'Project path does not exist: {self.project_path}'
            }

        # 检查项目类型
        has_package_json = (self.project_path / 'package.json').exists()
        has_requirements_txt = (self.project_path / 'requirements.txt').exists()
        has_pyproject_toml = (self.project_path / 'pyproject.toml').exists()

        if not has_package_json and not has_requirements_txt and not has_pyproject_toml:
            return {
                'success': False,
                'error': 'No package.json, requirements.txt, or pyproject.toml found. Not a valid Node.js or Python project.'
            }

        # 读取并更新 app-deploy.json
        config_result = update_app_config(
            str(self.project_path),
            app_name=self.app_name,
            app_version=self.app_version
        )
        if not config_result['success']:
            return config_result

        # 更新实例变量
        self.app_name = config_result['app_name']
        self.app_version = config_result['app_version']

        # ========== Node.js 构建检查 ==========
        if has_package_json:
            build_check = self._check_nodejs_build()
            if not build_check['success']:
                return build_check

        # 读取 .dockerignore（如果存在）
        self._load_dockerignore()

        # 读取 .gitignore（如果存在且没有 .dockerignore）
        self._load_gitignore()

        # 读取子目录的 ignore 文件（hybrid 项目）
        self._load_subdir_ignore_files()

        # 读取卷配置，自动排除卷目录
        self._load_volume_excludes()

        # 创建输出目录
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        # 打包项目
        try:
            with tarfile.open(self.output_path, 'w:gz') as tar:
                self._add_directory_to_tar(tar, self.project_path, '')

            # 获取文件大小
            size_bytes = self.output_path.stat().st_size

            return {
                'success': True,
                'output_path': str(self.output_path),
                'size': self._format_size(size_bytes),
                'size_bytes': size_bytes,
                'app_name': self.app_name,
                'app_version': self.app_version,
                'excluded_patterns': len(self.exclude_patterns),
                'included_files': self.included_count,
                'excluded_files': self.excluded_count,
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to package project: {str(e)}'
            }

    
    def _suggest_next_version(self, current_version: str) -> str:
        """建议下一个版本号"""
        try:
            parts = current_version.split('.')
            if len(parts) == 3:
                major, minor, patch = parts
                # 递增 patch 版本
                next_patch = int(patch) + 1
                return f"{major}.{minor}.{next_patch}"
        except:
            pass
        return "1.0.1"

    def _check_nodejs_build(self) -> dict:
        """检查 Node.js 项目是否已构建"""
        # 读取 app-deploy.json 获取框架信息
        config_path = self.project_path / 'app-deploy.json'

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception:
            # 如果读取失败，跳过检查
            return {'success': True}

        framework = config.get('framework', '').lower()

        # 需要构建的框架
        build_required_frameworks = {
            'nextjs': ['.next'],
            'nuxt': ['.nuxt', '.output'],
            'vite': ['dist'],
            'vite-react': ['dist'],
            'vite-vue': ['dist'],
            'remix': ['build', 'public/build'],
            'astro': ['dist'],
            'sveltekit': ['.svelte-kit', 'build'],
        }

        # 检查是否需要构建
        if framework not in build_required_frameworks:
            # 不需要构建的框架（如 express, fastify）
            return {'success': True}

        # 获取构建输出目录列表
        build_dirs = build_required_frameworks[framework]

        # 检查是否存在构建输出
        found_build = False
        for build_dir in build_dirs:
            build_path = self.project_path / build_dir
            if build_path.exists():
                found_build = True
                break

        if not found_build:
            # 获取构建命令
            build_command = config.get('build', {}).get('command', 'npm run build')

            return {
                'success': False,
                'error': 'BUILD_REQUIRED',
                'message': f'Project needs to be built before packaging.',
                'details': {
                    'framework': framework,
                    'missing_dirs': build_dirs,
                    'build_command': build_command,
                    'instruction': f'Please run "{build_command}" first, then try packaging again.'
                }
            }

        return {'success': True}

    def _load_dockerignore(self):
        """读取 .dockerignore 文件"""
        dockerignore_path = self.project_path / '.dockerignore'
        if not dockerignore_path.exists():
            return

        try:
            with open(dockerignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过空行和注释
                    if line and not line.startswith('#'):
                        # 移除前导的 /
                        pattern = line.lstrip('/')
                        if pattern not in self.exclude_patterns:
                            self.exclude_patterns.append(pattern)
        except Exception:
            pass  # 忽略读取错误

    def _load_gitignore(self):
        """读取 .gitignore 文件（如果没有 .dockerignore）"""
        # 如果已经有 .dockerignore，优先使用它
        dockerignore_path = self.project_path / '.dockerignore'
        if dockerignore_path.exists():
            return

        gitignore_path = self.project_path / '.gitignore'
        if not gitignore_path.exists():
            return

        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过空行和注释
                    if line and not line.startswith('#'):
                        # 移除前导的 /
                        pattern = line.lstrip('/')
                        if pattern not in self.exclude_patterns:
                            self.exclude_patterns.append(pattern)
        except Exception:
            pass  # 忽略读取错误

    def _load_subdir_ignore_files(self):
        """读取子目录的 ignore 文件（hybrid 项目支持）"""
        config_path = self.project_path / 'app-deploy.json'
        if not config_path.exists():
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 仅 hybrid 项目需要扫描子目录
            if config.get('framework') != 'hybrid':
                return

            components = config.get('components', [])
            for comp in components:
                comp_path = comp.get('path', '.')
                if comp_path == '.':
                    continue  # 根目录已处理

                subdir = self.project_path / comp_path.lstrip('./')
                if not subdir.exists():
                    continue

                # 读取子目录的 .dockerignore
                subdir_dockerignore = subdir / '.dockerignore'
                if subdir_dockerignore.exists():
                    self._load_ignore_file(subdir_dockerignore, comp_path)
                else:
                    # 或读取 .gitignore
                    subdir_gitignore = subdir / '.gitignore'
                    if subdir_gitignore.exists():
                        self._load_ignore_file(subdir_gitignore, comp_path)

        except Exception:
            pass  # 忽略读取错误

    def _load_ignore_file(self, file_path: Path, prefix: str):
        """读取 ignore 文件并添加路径前缀"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过空行和注释
                    if line and not line.startswith('#'):
                        # 移除前导的 /
                        pattern = line.lstrip('/')
                        # 添加子目录前缀
                        full_pattern = f"{prefix.lstrip('./')}/{pattern}"
                        if full_pattern not in self.exclude_patterns:
                            self.exclude_patterns.append(full_pattern)
        except Exception:
            pass  # 忽略读取错误

    def _load_volume_excludes(self):
        """从 app-deploy.json 读取卷配置，自动排除卷目录"""
        config_path = self.project_path / 'app-deploy.json'
        if not config_path.exists():
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            volumes = config.get('volumes', [])
            if not volumes:
                return

            # 自动排除所有卷目录
            for volume in volumes:
                source = volume.get('source', '')
                if not source:
                    continue

                # 标准化路径：移除前导 ./ 或 /
                normalized_source = source.lstrip('./').lstrip('/')

                # 避免重复添加
                if normalized_source and normalized_source not in self.exclude_patterns:
                    self.exclude_patterns.append(normalized_source)

        except Exception:
            pass  # 忽略读取错误

    def _add_directory_to_tar(self, tar: tarfile.TarFile, directory: Path, arcname_prefix: str):
        """递归添加目录到 tar 包"""
        try:
            for item in directory.iterdir():
                # 计算相对路径
                relative_path = item.relative_to(self.project_path)
                arcname = str(relative_path)

                # 检查是否应该排除
                if self._should_exclude(str(relative_path)):
                    self.excluded_count += 1
                    continue

                # 添加文件或目录
                if item.is_file():
                    tar.add(item, arcname=arcname, recursive=False)
                    self.included_count += 1
                elif item.is_dir():
                    # 递归添加子目录
                    self._add_directory_to_tar(tar, item, arcname)

        except PermissionError:
            pass  # 跳过没有权限的目录

    def _should_exclude(self, path: str) -> bool:
        """检查路径是否应该被排除"""
        path_parts = Path(path).parts

        for pattern in self.exclude_patterns:
            # 检查是否匹配排除模式
            if self._match_exclude_pattern(path, path_parts, pattern):
                return True

        return False

    def _match_exclude_pattern(self, path: str, path_parts: tuple, pattern: str) -> bool:
        """匹配排除模式"""
        # 精确匹配整个路径
        if path == pattern:
            return True

        # 匹配路径中的任何部分
        if pattern in path_parts:
            return True

        # 通配符匹配（*.log）
        if '*' in pattern:
            if pattern.startswith('*.'):
                # 文件扩展名匹配
                ext = pattern[1:]  # 移除 *
                if path.endswith(ext):
                    return True
            elif pattern.endswith('*'):
                # 前缀匹配
                prefix = pattern[:-1]
                if any(part.startswith(prefix) for part in path_parts):
                    return True

        # 路径前缀匹配
        if path.startswith(pattern + '/') or path.startswith(pattern + os.sep):
            return True

        return False

    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'error': 'Usage: pack_project.py <project_path> [output_path] [app_name] [app_version]',
            'description': {
                'project_path': 'Project directory to package (required)',
                'output_path': 'Output tar.gz path (optional, auto-generated if omitted or empty)',
                'app_name': 'Required for first-time packaging, then stored in app-deploy.json',
                'app_version': 'Required for each packaging'
            },
            'examples': [
                'pack_project.py . "" myapp 1.0.0  # Auto-generate output path',
                'pack_project.py . /tmp/myapp.tar.gz myapp 1.0.0  # Manual path'
            ]
        }, indent=2))
        sys.exit(1)

    project_path = sys.argv[1]

    # ========== 跨平台临时路径自动生成 ==========
    # 如果 output_path 未提供或为空，使用友好的文件名格式
    if len(sys.argv) < 3 or not sys.argv[2]:
        temp_dir = tempfile.gettempdir()
        # 生成友好的文件名: {app_name}-v{app_version}.tar.gz
        friendly_filename = ""
        if len(sys.argv) > 3 and sys.argv[3]:  # app_name 存在
            app_name = sys.argv[3]
            # 清理应用名称（只允许字母数字连字符下划线点）
            clean_name = re.sub(r'[^a-zA-Z0-9._-]', '-', app_name)
            clean_name = re.sub(r'-+', '-', clean_name).strip('-').strip('.')
            friendly_filename = clean_name[:50]  # 长度限制

            if len(sys.argv) > 4 and sys.argv[4]:  # app_version 存在
                app_version = sys.argv[4]
                friendly_filename += f"-v{app_version}"

        if not friendly_filename:  # 退化回时间戳
            timestamp = int(time.time())
            friendly_filename = f"deployment-{timestamp}"

        output_path = os.path.join(temp_dir, f"{friendly_filename}.tar.gz")
    else:
        output_path = sys.argv[2]

    app_name = sys.argv[3] if len(sys.argv) > 3 else None
    app_version = sys.argv[4] if len(sys.argv) > 4 else None

    # 如果输出路径没有扩展名，添加 .tar.gz
    if not output_path.endswith('.tar.gz') and not output_path.endswith('.tgz'):
        output_path = output_path + '.tar.gz'

    # 执行打包
    packager = ProjectPackager(project_path, output_path, app_name, app_version)
    result = packager.package()

    # 输出 JSON 结果
    print(json.dumps(result, indent=2))

    if not result.get('success', False):
        sys.exit(1)


if __name__ == '__main__':
    main()
