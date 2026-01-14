#!/usr/bin/env python3
"""
Volume Analyzer - 持久化分析器

智能识别需要持久化的目录（数据库、上传文件等）
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List


# 持久化检测规则
PERSISTENCE_PATTERNS = [
    {
        'pattern': ['*.db', '*.sqlite', '*.sqlite3'],
        'type': 'file',
        'reason': 'SQLite database file',
        'priority': 'high',
        'suggest_parent_dir': True,  # 建议持久化文件所在目录
    },
    {
        'pattern': ['schema.prisma'],
        'type': 'file',
        'reason': 'Prisma schema configuration',
        'priority': 'high',
        'suggest_dir': './prisma',
    },
    {
        'pattern': ['data', 'database'],
        'type': 'dir',
        'reason': 'Data directory',
        'priority': 'high',
    },
    {
        'pattern': ['storage'],
        'type': 'dir',
        'reason': 'Storage directory',
        'priority': 'high',
    },
    {
        'pattern': ['uploads', 'public/uploads', 'static/uploads'],
        'type': 'dir',
        'reason': 'User upload directory',
        'priority': 'medium',
    },
    {
        'pattern': ['db.json', 'database.json'],
        'type': 'file',
        'reason': 'JSON database file (lowdb)',
        'priority': 'medium',
        'suggest_parent_dir': True,
    },
    {
        'pattern': ['logs'],
        'type': 'dir',
        'reason': 'Log directory',
        'priority': 'low',
    },

    # ============= Python 特定规则 =============
    {
        'pattern': ['instance'],
        'type': 'dir',
        'reason': 'Flask instance folder (SQLite database)',
        'priority': 'high',
    },
    {
        'pattern': ['data.json', 'db.json', 'database.json'],
        'type': 'file',
        'reason': 'JSON database file',
        'priority': 'high',
        'suggest_parent_dir': True,
    },
    {
        'pattern': ['*.csv', '*.xlsx'],
        'type': 'file',
        'reason': 'Data file (Streamlit/Data Science)',
        'priority': 'medium',
        'suggest_parent_dir': True,
    },
]

# 排除目录（不扫描）
EXCLUDE_DIRS = [
    'node_modules',
    '.git',
    '.next',
    '.nuxt',
    'dist',
    'build',
    '.turbo',
    '.cache',
    'coverage',
    '.vscode',
    '.idea',

    # Python 排除目录
    '__pycache__',
    '.venv',
    'venv',
    'env',
    'ENV',
    '.pytest_cache',
    '.mypy_cache',
    '.ruff_cache',
    '.tox',
    'htmlcov',
]


class VolumeAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.suggestions = []
        self.suggested_paths = set()  # 去重

    def analyze(self) -> Dict:
        """执行持久化分析"""
        if not self.project_path.exists():
            return {
                'success': False,
                'error': f'Project path does not exist: {self.project_path}'
            }

        # 扫描项目目录
        self._scan_directory(self.project_path)

        # 检查 package.json 中的特殊依赖
        self._check_dependencies()

        # ========== 第三层防御：结果验证和过滤 ==========
        # 过滤掉任何可能遗漏的危险配置
        safe_suggestions = []
        filtered_count = 0

        for suggestion in self.suggestions:
            source = suggestion['source']
            if self._validate_volume_source(source):
                safe_suggestions.append(suggestion)
            else:
                filtered_count += 1
                print(
                    f"⚠️  Warning: Filtered dangerous volume configuration:\n"
                    f"   Source: {source}\n"
                    f"   Reason: {suggestion['reason']}\n"
                    f"   This configuration would cause container startup failure.",
                    file=sys.stderr
                )

        # 使用过滤后的建议
        self.suggestions = safe_suggestions

        if filtered_count > 0:
            print(
                f"\n🛡️  Security: Filtered {filtered_count} dangerous volume configuration(s).\n",
                file=sys.stderr
            )

        # 计算总大小
        total_size = sum(s['size_bytes'] for s in self.suggestions)

        return {
            'success': True,
            'suggested': self.suggestions,
            'excluded': EXCLUDE_DIRS,
            'total_size': self._format_size(total_size),
            'total_size_bytes': total_size,
        }

    def _scan_directory(self, directory: Path, depth: int = 0, max_depth: int = 5):
        """递归扫描目录"""
        if depth > max_depth:
            return

        try:
            for item in directory.iterdir():
                # 跳过排除目录
                if item.name in EXCLUDE_DIRS:
                    continue

                # 跳过隐藏文件/目录（以 . 开头）
                if item.name.startswith('.') and item.name not in ['.env']:
                    continue

                # 检查文件
                if item.is_file():
                    self._check_file(item)

                # 检查目录
                elif item.is_dir():
                    self._check_directory(item)
                    # 递归扫描子目录
                    self._scan_directory(item, depth + 1, max_depth)

        except PermissionError:
            pass  # 跳过没有权限的目录

    def _check_file(self, file_path: Path):
        """检查文件是否匹配持久化规则"""
        for rule in PERSISTENCE_PATTERNS:
            if rule['type'] != 'file':
                continue

            # 检查文件名模式
            for pattern in rule['pattern']:
                if self._match_pattern(file_path.name, pattern):
                    # 如果建议持久化父目录
                    if rule.get('suggest_parent_dir', False):
                        target_dir = file_path.parent
                    else:
                        target_dir = file_path

                    self._add_suggestion(
                        target_dir,
                        rule['reason'],
                        rule['priority']
                    )
                    break

    def _check_directory(self, dir_path: Path):
        """检查目录是否匹配持久化规则"""
        relative_path = dir_path.relative_to(self.project_path)

        for rule in PERSISTENCE_PATTERNS:
            if rule['type'] != 'dir':
                continue

            # 检查目录名模式
            for pattern in rule['pattern']:
                # 支持路径匹配（如 "public/uploads"）
                if '/' in pattern:
                    if str(relative_path) == pattern or str(relative_path).endswith(pattern):
                        self._add_suggestion(
                            dir_path,
                            rule['reason'],
                            rule['priority']
                        )
                        break
                else:
                    if dir_path.name == pattern:
                        self._add_suggestion(
                            dir_path,
                            rule['reason'],
                            rule['priority']
                        )
                        break

            # 检查特定目录（如 ./prisma）
            if 'suggest_dir' in rule:
                suggest_path = self.project_path / rule['suggest_dir'].lstrip('./')
                if dir_path == suggest_path:
                    self._add_suggestion(
                        dir_path,
                        rule['reason'],
                        rule['priority']
                    )

    def _check_dependencies(self):
        """检查 package.json 中的依赖"""
        package_json_path = self.project_path / 'package.json'
        if not package_json_path.exists():
            return

        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_json = json.load(f)

            dependencies = {
                **package_json.get('dependencies', {}),
                **package_json.get('devDependencies', {})
            }

            # 检查 Prisma
            if 'prisma' in dependencies or '@prisma/client' in dependencies:
                prisma_dir = self.project_path / 'prisma'
                if prisma_dir.exists():
                    self._add_suggestion(
                        prisma_dir,
                        'Prisma database directory',
                        'high'
                    )

            # 检查 lowdb
            if 'lowdb' in dependencies:
                # 查找 .json 数据库文件
                for json_file in self.project_path.rglob('*.json'):
                    if 'db' in json_file.name.lower() or 'database' in json_file.name.lower():
                        self._add_suggestion(
                            json_file.parent,
                            'lowdb JSON database',
                            'medium'
                        )
                        break

        except Exception:
            pass  # 忽略读取错误

        # ============= Python 依赖检测 =============
        req_file = self.project_path / 'requirements.txt'
        if req_file.exists():
            self._check_python_dependencies(req_file)

    def _check_python_dependencies(self, req_file: Path):
        """检查 Python 依赖的持久化需求"""
        try:
            content = req_file.read_text().lower()

            # 检查 Flask (instance 文件夹)
            if 'flask' in content:
                instance_dir = self.project_path / 'instance'
                if instance_dir.exists():
                    self._add_suggestion(
                        instance_dir,
                        'Flask instance folder (SQLite database)',
                        'high'
                    )

            # 检查 SQLAlchemy (查找 .db 文件)
            if 'sqlalchemy' in content or 'flask-sqlalchemy' in content:
                for db_file in self.project_path.rglob('*.db'):
                    if db_file.parent.name not in EXCLUDE_DIRS:
                        self._add_suggestion(
                            db_file.parent,
                            'SQLAlchemy database directory',
                            'high'
                        )
                        break

            # 检查 Streamlit (data 文件夹)
            if 'streamlit' in content:
                data_dir = self.project_path / 'data'
                if data_dir.exists():
                    self._add_suggestion(
                        data_dir,
                        'Streamlit data directory',
                        'medium'
                    )

        except Exception:
            pass  # 忽略读取错误

    def _validate_volume_source(self, source_path: str) -> bool:
        """验证卷源路径的安全性

        Args:
            source_path: 相对路径字符串 (如 "./data", "./app.db")

        Returns:
            True if valid, False if dangerous
        """
        # 标准化路径
        normalized = str(Path(source_path).as_posix())

        # 禁止的模式
        forbidden_patterns = {
            ".",      # 当前目录
            "./.",    # 当前目录（另一种写法）
            "..",     # 父目录
            "/",      # 根目录
        }

        # 检查精确匹配
        if normalized in forbidden_patterns:
            return False

        # 检查父目录路径
        if normalized.startswith("../"):
            return False

        return True

    def _add_suggestion(self, path: Path, reason: str, priority: str):
        """添加持久化建议（去重）"""
        # ========== 第一层防御：禁止添加项目根目录 ==========
        if path == self.project_path:
            print(
                f"⚠️  Warning: Skipping volume suggestion for project root directory.\n"
                f"   Reason: {reason}\n"
                f"   Please specify a subdirectory or file instead.",
                file=sys.stderr
            )
            return

        # 计算相对路径
        relative_path = path.relative_to(self.project_path)
        source_path = f"./{relative_path}"

        # ========== 第二层防御：验证路径安全性 ==========
        if not self._validate_volume_source(source_path):
            print(
                f"⚠️  Warning: Invalid volume source path: '{source_path}'\n"
                f"   Reason: {reason}\n"
                f"   This path would mount dangerous directories (project root, parent, etc.).\n"
                f"   Skipping this suggestion.",
                file=sys.stderr
            )
            return

        # 去重
        if source_path in self.suggested_paths:
            return

        self.suggested_paths.add(source_path)

        # 计算大小
        size_bytes = self._get_size(path)

        self.suggestions.append({
            'source': source_path,
            'reason': reason,
            'priority': priority,
            'size': self._format_size(size_bytes),
            'size_bytes': size_bytes,
        })

    def _get_size(self, path: Path) -> int:
        """计算文件或目录大小"""
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            total_size = 0
            try:
                for item in path.rglob('*'):
                    if item.is_file():
                        try:
                            total_size += item.stat().st_size
                        except (PermissionError, FileNotFoundError):
                            pass
            except (PermissionError, FileNotFoundError):
                pass
            return total_size
        return 0

    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def _match_pattern(self, name: str, pattern: str) -> bool:
        """匹配文件名模式（支持通配符）"""
        if '*' in pattern:
            # 简单的通配符匹配
            parts = pattern.split('*')
            if len(parts) == 2:
                prefix, suffix = parts
                return name.startswith(prefix) and name.endswith(suffix)
        return name == pattern


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'error': 'Usage: analyze_volumes.py <project_path>'
        }, indent=2))
        sys.exit(1)

    project_path = sys.argv[1]

    # 执行分析
    analyzer = VolumeAnalyzer(project_path)
    result = analyzer.analyze()

    # 按优先级排序
    if result.get('success'):
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        result['suggested'].sort(key=lambda x: priority_order.get(x['priority'], 3))

    # 输出 JSON 结果
    print(json.dumps(result, indent=2))

    if not result.get('success', False):
        sys.exit(1)


if __name__ == '__main__':
    main()
