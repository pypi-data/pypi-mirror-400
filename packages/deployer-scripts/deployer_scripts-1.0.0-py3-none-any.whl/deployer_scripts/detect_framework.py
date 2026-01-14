#!/usr/bin/env python3
"""
Framework Detector - 框架检测器

自动识别项目框架类型、构建命令、启动命令和 Node.js 版本
支持 MCP 特性检测和 Hybrid 混合项目识别

版本: v1.1.0
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ============= MCP 依赖配置 =============
MCP_DEPENDENCIES = {
    'python': ['mcp', 'fastmcp'],
    'nodejs': ['@modelcontextprotocol/sdk'],
}

# MCP Transport 模式匹配
MCP_TRANSPORT_PATTERNS = {
    'python': {
        'sse': [
            r'transport\s*=\s*["\']sse["\']',
            r'transport\s*=\s*["\']http["\']',
            r'stateless_http\s*=\s*True',
            r'StreamableHTTPSessionManager',  # Streamable HTTP
            r'streamable_http_manager',       # import 语句
        ],
        'stdio': [r'transport\s*=\s*["\']stdio["\']', r'StdioServerTransport'],
    },
    'nodejs': {
        'sse': [r'SSEServerTransport', r'StreamableHTTPServerTransport'],
        'stdio': [r'StdioServerTransport'],
    },
}

# Hybrid 检测时忽略的目录
HYBRID_IGNORE_DIRS = [
    'node_modules', 'venv', '.venv', 'env', '.env',
    '__pycache__', '.git', 'dist', 'build', '.next',
    '.nuxt', 'coverage', '.pytest_cache', '.mypy_cache',
]


# ============= Python 支持配置 =============
# 支持的 Python 版本
SUPPORTED_PYTHON_VERSIONS = ['3.9', '3.10', '3.11', '3.12', '3.13']
DEFAULT_PYTHON_VERSION = '3.11'

# 需要系统依赖的库黑名单
SYSTEM_DEPENDENCY_LIBRARIES = {
    'opencv-python': '需要 libGL, libgthread 等系统库 (建议用 opencv-python-headless)',
    'opencv-contrib-python': '需要 libGL, libgthread 等系统库',
    'mysqlclient': '需要 libmysqlclient-dev (建议用 PyMySQL)',
    'psycopg2': '需要 libpq-dev (建议用 psycopg2-binary)',
    'lxml': '需要 libxml2-dev, libxslt1-dev',
    'pyodbc': '需要 unixodbc-dev',
    'pycurl': '需要 libcurl4-openssl-dev',
    'python-ldap': '需要 libldap2-dev, libsasl2-dev',
}


# ============= 框架检测规则 =============
# 框架检测规则（按优先级排序）
DETECTION_RULES = {
    'nextjs': {
        'dependencies': ['next'],
        'scripts_patterns': ['next build', 'next start'],
        'files': ['next.config.js', 'next.config.mjs', 'next.config.ts'],
        'dirs': ['pages', 'app'],
        'default_port': 3000,
        'build_command': 'npm run build',
        'start_command': 'npm start',
    },
    'nuxt': {
        'dependencies': ['nuxt'],
        'scripts_patterns': ['nuxt build', 'nuxt dev'],
        'files': ['nuxt.config.js', 'nuxt.config.ts'],
        'dirs': [],
        'default_port': 3000,
        'build_command': 'npm run build',
        'start_command': 'npm start',
    },
    'vite-react': {
        'dependencies': ['vite', 'react'],
        'scripts_patterns': ['vite build'],
        'files': ['vite.config.js', 'vite.config.ts'],
        'dirs': [],
        'default_port': 4173,
        'build_command': 'npm run build',
        'start_command': 'npm run preview',
    },
    'vite-vue': {
        'dependencies': ['vite', 'vue'],
        'scripts_patterns': ['vite build'],
        'files': ['vite.config.js', 'vite.config.ts'],
        'dirs': [],
        'default_port': 4173,
        'build_command': 'npm run build',
        'start_command': 'npm run preview',
    },
    'remix': {
        'dependencies': ['@remix-run/node', '@remix-run/react'],
        'scripts_patterns': ['remix build'],
        'files': ['remix.config.js'],
        'dirs': ['app'],
        'default_port': 3000,
        'build_command': 'npm run build',
        'start_command': 'npm start',
    },
    'astro': {
        'dependencies': ['astro'],
        'scripts_patterns': ['astro build'],
        'files': ['astro.config.mjs', 'astro.config.js'],
        'dirs': [],
        'default_port': 3000,
        'build_command': 'npm run build',
        'start_command': 'npm run preview',
    },
    'sveltekit': {
        'dependencies': ['@sveltejs/kit'],
        'scripts_patterns': ['vite build'],
        'files': ['svelte.config.js'],
        'dirs': [],
        'default_port': 5173,
        'build_command': 'npm run build',
        'start_command': 'npm run preview',
    },
    'express': {
        'dependencies': ['express'],
        'scripts_patterns': ['node server', 'node index', 'node app'],
        'files': ['server.js', 'app.js', 'index.js'],
        'dirs': [],
        'default_port': 3000,
        'build_command': 'npm run build',
        'start_command': 'npm start',
    },

    # ============= Python 框架 =============
    'flask': {
        'dependencies': ['flask'],
        'files': ['app.py', 'application.py', 'wsgi.py'],
        'default_port': 5000,
        'build_command': None,
        'language': 'python',
    },
    'fastapi': {
        'dependencies': ['fastapi'],
        'files': ['main.py', 'app.py', 'api.py'],
        'default_port': 8000,
        'build_command': None,
        'language': 'python',
    },
    'streamlit': {
        'dependencies': ['streamlit'],
        'files': ['app.py', 'streamlit_app.py'],
        'default_port': 8501,
        'build_command': None,
        'language': 'python',
    },
    'mcp': {
        'dependencies': ['mcp', 'fastmcp'],
        'files': ['server.py', 'mcp_server.py', 'main.py', 'run.py', 'src/server.py'],
        'default_port': 9192,
        'build_command': None,
        'language': 'python',
    },
}


class FrameworkDetector:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.package_json_path = self.project_path / 'package.json'
        self.package_json = None

    def detect(self) -> Dict:
        """执行框架检测（支持 hybrid 模式）"""

        # 0. 首先检测是否为 hybrid 项目
        hybrid_result = self._detect_hybrid()
        if hybrid_result:
            return hybrid_result

        # 1. 优先检查 requirements.txt (Python 项目)
        req_file = self.project_path / 'requirements.txt'
        if req_file.exists():
            return self._detect_python_framework()

        # 1.5 检查 pyproject.toml (Python 项目，现代包管理)
        pyproject_file = self.project_path / 'pyproject.toml'
        if pyproject_file.exists() and not self.package_json_path.exists():
            return self._detect_python_framework()

        # 2. 检查 package.json (Node.js 项目)
        if not self.package_json_path.exists():
            return self._error_result(
                "No package.json, requirements.txt, or pyproject.toml found. "
                "This doesn't appear to be a Node.js or Python project."
            )

        # 3. 执行 Node.js 检测 (保持原有逻辑)
        try:
            with open(self.package_json_path, 'r', encoding='utf-8') as f:
                self.package_json = json.load(f)
        except Exception as e:
            return self._error_result(f"Failed to read package.json: {e}")

        # 按优先级检测 Node.js 框架
        # 1. 分析 dependencies
        result = self._detect_by_dependencies()
        if result:
            return self._success_result(result)

        # 2. 分析 scripts
        result = self._detect_by_scripts()
        if result:
            return self._success_result(result)

        # 3. 分析项目结构
        result = self._detect_by_structure()
        if result:
            return self._success_result(result)

        # 无法识别
        return self._unknown_result()

    # ============= Hybrid 检测方法 =============

    def _detect_hybrid(self) -> Optional[Dict]:
        """检测是否为 hybrid 混合项目"""
        root_languages = self._detect_languages_in_dir(self.project_path)

        # 扫描一级子目录
        sub_components = []
        try:
            for item in self.project_path.iterdir():
                if not item.is_dir():
                    continue
                if item.name in HYBRID_IGNORE_DIRS:
                    continue
                if item.name.startswith('.'):
                    continue

                sub_languages = self._detect_languages_in_dir(item)
                if sub_languages:
                    sub_components.append({
                        'path': f'./{item.name}',
                        'languages': sub_languages,
                    })
        except PermissionError:
            pass

        # 判断是否为 hybrid
        all_languages = set(root_languages)
        for comp in sub_components:
            all_languages.update(comp['languages'])

        if len(all_languages) < 2:
            return None  # 不是 hybrid 项目

        # 构建 hybrid 结果
        return self._build_hybrid_result(root_languages, sub_components)

    def _detect_languages_in_dir(self, dir_path: Path) -> List[str]:
        """检测目录中的语言类型"""
        languages = []

        if (dir_path / 'requirements.txt').exists():
            languages.append('python')
        if (dir_path / 'package.json').exists():
            languages.append('nodejs')

        return languages

    def _build_hybrid_result(self, root_languages: List[str], sub_components: List[Dict]) -> Dict:
        """构建 hybrid 检测结果"""
        components = []
        all_requires = set()
        features = []

        # 处理根目录组件
        if root_languages:
            for lang in root_languages:
                comp_result = self._detect_component('.', lang)
                if comp_result:
                    comp_result['primary'] = True  # 根目录组件默认为 primary
                    components.append(comp_result)
                    all_requires.add(lang)

                    # 检查 MCP 特性
                    if comp_result.get('mcp'):
                        if 'mcp' not in features:
                            features.append('mcp')

        # 处理子目录组件
        for sub in sub_components:
            for lang in sub['languages']:
                comp_result = self._detect_component(sub['path'], lang)
                if comp_result:
                    if not components:  # 如果根目录没有组件，第一个子目录组件为 primary
                        comp_result['primary'] = True
                    components.append(comp_result)
                    all_requires.add(lang)

                    # 检查 MCP 特性
                    if comp_result.get('mcp'):
                        if 'mcp' not in features:
                            features.append('mcp')

        # 检测启动脚本
        start_command = self._detect_start_script()

        result = {
            'success': True,
            'framework': 'hybrid',
            'components': components,
            'runtime': {
                'command': start_command,
                'requires': sorted(list(all_requires)),
            },
        }

        if features:
            result['features'] = features

        return result

    def _detect_component(self, path: str, language: str) -> Optional[Dict]:
        """检测单个组件的框架信息"""
        if path == '.':
            comp_path = self.project_path
        else:
            comp_path = self.project_path / path.lstrip('./')

        if language == 'python':
            return self._detect_python_component(comp_path, path)
        elif language == 'nodejs':
            return self._detect_nodejs_component(comp_path, path)

        return None

    def _detect_python_component(self, comp_path: Path, rel_path: str) -> Optional[Dict]:
        """检测 Python 组件"""
        req_file = comp_path / 'requirements.txt'
        if not req_file.exists():
            return None

        try:
            req_content = req_file.read_text(encoding='utf-8').lower()
        except Exception:
            return None

        # 检测框架
        detected_framework = None
        for framework, rules in DETECTION_RULES.items():
            if rules.get('language') != 'python':
                continue

            for dep in rules['dependencies']:
                if dep.lower() in req_content:
                    # 检查入口文件
                    for file in rules.get('files', []):
                        if (comp_path / file).exists():
                            detected_framework = framework
                            break
                    if detected_framework:
                        break
            if detected_framework:
                break

        if not detected_framework:
            detected_framework = 'python'  # 通用 Python

        port = DETECTION_RULES.get(detected_framework, {}).get('default_port', 8000)

        result = {
            'path': rel_path,
            'language': 'python',
            'framework': detected_framework,
            'port': port,
        }

        # 检测 MCP 特性
        mcp_info = self._detect_mcp_feature(comp_path, 'python', req_content)
        if mcp_info:
            result['mcp'] = mcp_info
            if mcp_info.get('port'):
                result['port'] = mcp_info['port']

        return result

    def _detect_nodejs_component(self, comp_path: Path, rel_path: str) -> Optional[Dict]:
        """检测 Node.js 组件"""
        pkg_file = comp_path / 'package.json'
        if not pkg_file.exists():
            return None

        try:
            with open(pkg_file, 'r', encoding='utf-8') as f:
                pkg_json = json.load(f)
        except Exception:
            return None

        dependencies = {
            **pkg_json.get('dependencies', {}),
            **pkg_json.get('devDependencies', {}),
        }

        # 检测框架
        detected_framework = None
        for framework, rules in DETECTION_RULES.items():
            if rules.get('language') == 'python':
                continue
            if 'dependencies' not in rules:
                continue

            if all(dep in dependencies for dep in rules['dependencies']):
                detected_framework = framework
                break

        if not detected_framework:
            detected_framework = 'nodejs'  # 通用 Node.js

        port = DETECTION_RULES.get(detected_framework, {}).get('default_port', 3000)

        result = {
            'path': rel_path,
            'language': 'nodejs',
            'framework': detected_framework,
            'port': port,
        }

        # 检测 MCP 特性
        mcp_info = self._detect_mcp_feature(comp_path, 'nodejs', json.dumps(dependencies))
        if mcp_info:
            result['mcp'] = mcp_info
            if mcp_info.get('port'):
                result['port'] = mcp_info['port']

        return result

    def _detect_mcp_feature(self, comp_path: Path, language: str, deps_content: str) -> Optional[Dict]:
        """检测 MCP 特性"""
        # 检查是否有 MCP 依赖
        has_mcp = False
        for dep in MCP_DEPENDENCIES.get(language, []):
            if dep.lower() in deps_content.lower():
                has_mcp = True
                break

        if not has_mcp:
            return None

        # 检测 transport 模式
        transport = self._detect_mcp_transport(comp_path, language)
        port = self._detect_mcp_port(comp_path, language)

        mcp_info = {
            'transport': transport,
        }

        if transport == 'streamable-http' and port:
            mcp_info['port'] = port
        elif transport == 'stdio':
            mcp_info['warning'] = 'stdio 模式不支持远程容器部署，需改为 Streamable HTTP 模式'

        return mcp_info

    def _detect_mcp_transport(self, comp_path: Path, language: str) -> str:
        """检测 MCP transport 模式"""
        # 查找入口文件（包含子目录）
        if language == 'python':
            entry_files = ['server.py', 'mcp_server.py', 'main.py', 'run.py', 'src/server.py']
        else:
            entry_files = ['server.js', 'server.ts', 'index.js', 'index.ts']

        for entry_file in entry_files:
            file_path = comp_path / entry_file
            if not file_path.exists():
                continue

            try:
                content = file_path.read_text(encoding='utf-8')

                # 检查 Streamable HTTP 模式
                for pattern in MCP_TRANSPORT_PATTERNS.get(language, {}).get('sse', []):
                    if re.search(pattern, content):
                        return 'streamable-http'

                # 检查 stdio 模式
                for pattern in MCP_TRANSPORT_PATTERNS.get(language, {}).get('stdio', []):
                    if re.search(pattern, content):
                        return 'stdio'

            except Exception:
                continue

        # 默认假设 stdio（保守估计）
        return 'stdio'

    def _detect_mcp_port(self, comp_path: Path, language: str) -> Optional[int]:
        """检测 MCP 端口"""
        if language == 'python':
            entry_files = ['server.py', 'mcp_server.py', 'main.py', 'run.py', 'src/server.py']
        else:
            entry_files = ['server.js', 'server.ts', 'index.js', 'index.ts']

        for entry_file in entry_files:
            file_path = comp_path / entry_file
            if not file_path.exists():
                continue

            try:
                content = file_path.read_text(encoding='utf-8')

                # 匹配端口号
                patterns = [
                    r'port\s*=\s*(\d+)',
                    r'port:\s*(\d+)',
                    r'PORT\s*=\s*(\d+)',
                    r'PORT["\'],\s*["\'](\d+)',  # os.getenv("PORT", "9191")
                    r'PORT["\'],\s*(\d+)',       # os.getenv("PORT", 9191)
                ]

                for pattern in patterns:
                    match = re.search(pattern, content)
                    if match:
                        return int(match.group(1))

            except Exception:
                continue

        return DETECTION_RULES.get('mcp', {}).get('default_port', 9192)

    def _detect_start_script(self) -> Optional[str]:
        """检测统一启动脚本"""
        start_scripts = ['start.sh', 'run.sh', 'docker-entrypoint.sh']

        for script in start_scripts:
            if (self.project_path / script).exists():
                return f'./{script}'

        return None

    # ============= 原有检测方法 =============

    def _detect_by_dependencies(self) -> Optional[Dict]:
        """通过 dependencies 检测框架"""
        dependencies = {
            **self.package_json.get('dependencies', {}),
            **self.package_json.get('devDependencies', {})
        }

        for framework, rules in DETECTION_RULES.items():
            required_deps = rules['dependencies']

            # 检查是否所有必需依赖都存在
            if all(dep in dependencies for dep in required_deps):
                return {
                    'framework': framework,
                    'confidence': 100,
                    'detection_method': 'dependencies'
                }

        return None

    def _detect_by_scripts(self) -> Optional[Dict]:
        """通过 scripts 检测框架"""
        scripts = self.package_json.get('scripts', {})

        for framework, rules in DETECTION_RULES.items():
            patterns = rules['scripts_patterns']

            # 检查是否有匹配的脚本模式
            for script_value in scripts.values():
                if any(pattern in script_value for pattern in patterns):
                    return {
                        'framework': framework,
                        'confidence': 90,
                        'detection_method': 'scripts'
                    }

        return None

    def _detect_by_structure(self) -> Optional[Dict]:
        """通过项目结构检测框架"""
        for framework, rules in DETECTION_RULES.items():
            # 检查配置文件
            for file_name in rules['files']:
                if (self.project_path / file_name).exists():
                    return {
                        'framework': framework,
                        'confidence': 80,
                        'detection_method': 'structure'
                    }

            # 检查目录结构
            for dir_name in rules['dirs']:
                if (self.project_path / dir_name).is_dir():
                    return {
                        'framework': framework,
                        'confidence': 75,
                        'detection_method': 'structure'
                    }

        return None

    def _get_node_version(self) -> str:
        """获取推荐的 Node.js 版本"""
        engines = self.package_json.get('engines', {})
        node_version = engines.get('node', '')

        # 解析版本号（如 ">=18.0.0" -> "18"）
        if '>=' in node_version:
            version = node_version.split('>=')[1].split('.')[0].strip()
            return version
        elif '^' in node_version or '~' in node_version:
            version = node_version[1:].split('.')[0]
            return version

        # 默认返回 20
        return '20'

    def _get_build_command(self, framework: str) -> str:
        """获取构建命令"""
        scripts = self.package_json.get('scripts', {})

        # 优先从 package.json 的 scripts 中获取
        if 'build' in scripts:
            return 'npm run build'

        # 使用默认命令
        return DETECTION_RULES[framework]['build_command']

    def _get_start_command(self, framework: str) -> str:
        """获取启动命令"""
        scripts = self.package_json.get('scripts', {})

        # 优先从 package.json 的 scripts 中获取
        if 'start' in scripts:
            return 'npm start'
        elif 'preview' in scripts and framework.startswith('vite'):
            return 'npm run preview'

        # 使用默认命令
        return DETECTION_RULES[framework]['start_command']

    def _get_package_manager(self) -> str:
        """检测包管理器"""
        if (self.project_path / 'pnpm-lock.yaml').exists():
            return 'pnpm'
        elif (self.project_path / 'yarn.lock').exists():
            return 'yarn'
        else:
            return 'npm'

    def _parse_port_from_scripts(self) -> Optional[int]:
        """从 package.json scripts 中解析端口"""
        scripts = self.package_json.get('scripts', {})

        # 检查常见的启动脚本
        for script_name in ['start', 'preview', 'serve', 'prod']:
            if script_name in scripts:
                script_value = scripts[script_name]

                # 匹配 -p 或 --port 参数
                # 例如: "next start -p 3001" 或 "vite preview --port 4173"
                patterns = [
                    r'-p\s+(\d+)',           # -p 3000
                    r'--port[=\s]+(\d+)',    # --port=3000 或 --port 3000
                    r'PORT=(\d+)',           # PORT=3000
                ]

                for pattern in patterns:
                    match = re.search(pattern, script_value)
                    if match:
                        return int(match.group(1))

        return None

    def _parse_env_file(self, env_file: Path) -> Optional[int]:
        """解析 .env 文件中的端口配置"""
        if not env_file.exists():
            return None

        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过注释和空行
                    if not line or line.startswith('#'):
                        continue

                    # 匹配 PORT=3000 或 NEXT_PUBLIC_PORT=3000 等
                    match = re.match(r'^(?:NEXT_PUBLIC_)?PORT\s*=\s*(\d+)', line)
                    if match:
                        return int(match.group(1))
        except Exception:
            pass

        return None

    def _detect_port(self, framework: str) -> int:
        """检测项目实际端口（按优先级）"""

        # 1. 优先从 package.json scripts 中检测
        port = self._parse_port_from_scripts()
        if port:
            return port

        # 2. 检查环境变量文件（按优先级）
        env_files = [
            '.env.production.local',
            '.env.production',
            '.env.local',
            '.env',
        ]

        for env_file_name in env_files:
            env_file = self.project_path / env_file_name
            port = self._parse_env_file(env_file)
            if port:
                return port

        # 3. 尝试解析框架配置文件（Next.js 为例）
        if framework == 'nextjs':
            # 检查 next.config.js/mjs/ts 中的端口配置
            # 注意：这里简化处理，因为完整解析 JS 配置文件比较复杂
            # 实际项目中 Next.js 端口通常在 package.json scripts 或 .env 中配置
            pass

        # 4. 使用框架默认端口
        return DETECTION_RULES[framework]['default_port']

    def _success_result(self, detection: Dict) -> Dict:
        """构建成功结果"""
        framework = detection['framework']
        language = detection.get('language', 'nodejs')

        if language == 'python':
            # Python 项目结果 (已在 _detect_python_framework 中构建)
            return detection

        # Node.js 项目结果 (保持原有逻辑)
        result = {
            'success': True,
            'framework': framework,
            'confidence': detection['confidence'],
            'detection_method': detection['detection_method'],
            'node_version': self._get_node_version(),
            'build_command': self._get_build_command(framework),
            'start_command': self._get_start_command(framework),
            'package_manager': self._get_package_manager(),
            'port': self._detect_port(framework),
        }

        # Next.js 专属: 检测 Standalone 模式
        if framework == 'nextjs':
            standalone_info = self._detect_standalone()
            if standalone_info:
                result['standalone'] = standalone_info

        return result

    def _unknown_result(self) -> Dict:
        """无法识别的结果"""
        # 尝试从 scripts 或 .env 检测端口，如果检测不到使用默认 3000
        port = self._parse_port_from_scripts()
        if not port:
            for env_file_name in ['.env.production.local', '.env.production', '.env.local', '.env']:
                env_file = self.project_path / env_file_name
                port = self._parse_env_file(env_file)
                if port:
                    break
        if not port:
            port = 3000

        return {
            'success': True,
            'framework': 'unknown',
            'confidence': 0,
            'detection_method': 'none',
            'node_version': self._get_node_version(),
            'build_command': self._get_build_command('express'),  # 使用通用命令
            'start_command': self._get_start_command('express'),
            'package_manager': self._get_package_manager(),
            'port': port,
            'warning': 'Unable to detect framework type. Please provide build and start commands manually.'
        }

    def _error_result(self, message: str) -> Dict:
        """构建错误结果"""
        return {
            'success': False,
            'error': message
        }

    # ============= Python 检测方法 =============

    def _detect_python_framework(self) -> Dict:
        """检测 Python 框架"""
        req_file = self.project_path / 'requirements.txt'
        pyproject_file = self.project_path / 'pyproject.toml'

        req_content = ""
        try:
            if req_file.exists():
                req_content = req_file.read_text(encoding='utf-8')
            elif pyproject_file.exists():
                # 从 pyproject.toml 提取依赖
                req_content = self._extract_deps_from_pyproject(pyproject_file)
        except Exception as e:
            return self._error_result(f"Failed to read dependencies: {e}")

        if not req_content:
            return self._error_result("No dependencies found in requirements.txt or pyproject.toml")

        # 1. 检查问题依赖
        dep_warnings = self._check_problematic_dependencies(req_content)

        # 2. 检测 Python 版本
        python_version = self._detect_python_version()

        # 3. 匹配框架（优先检测 MCP）
        for framework, rules in DETECTION_RULES.items():
            if rules.get('language') != 'python':
                continue

            # 检查依赖
            for dep in rules['dependencies']:
                if dep.lower() in req_content.lower():
                    # 查找入口文件
                    entry_file = None
                    for file in rules['files']:
                        if (self.project_path / file).exists():
                            entry_file = file
                            break

                    if not entry_file:
                        continue

                    # 检测端口（优先级：.env → config.py → 代码 → 默认值）
                    detected_port = self._detect_python_port(framework, entry_file)

                    # 检测启动命令（传入端口参数）
                    start_cmd_result = self._detect_start_command(framework, entry_file, detected_port)

                    # 构建环境变量 (orchestrator DeployParams 格式)
                    environment = {
                        'PYTHON_VERSION': python_version  # ← Python 版本标记
                    }

                    # 合并启动命令中的环境变量
                    if start_cmd_result.get('env'):
                        environment.update(start_cmd_result['env'])

                    result = {
                        'success': True,
                        'framework': framework,
                        'language': 'python',
                        'python_version': python_version,
                        'entry_file': entry_file,
                        'confidence': 100,
                        'detection_method': 'dependencies',
                        'build_command': None,
                        'start_command': start_cmd_result.get('command'),
                        'port': detected_port,

                        # ========== orchestrator DeployParams 字段 ==========
                        'environment': environment,  # ← 改名: env → environment
                        'health_check_type': 'tcp',  # ← Python 使用 TCP 健康检查
                    }

                    # 检测 MCP 特性
                    mcp_info = self._detect_mcp_feature(self.project_path, 'python', req_content)
                    if mcp_info:
                        result['features'] = ['mcp']
                        result['mcp'] = mcp_info
                        # 如果是 MCP 项目且检测到端口，使用 MCP 端口
                        if mcp_info.get('port'):
                            result['port'] = mcp_info['port']

                    # 添加依赖警告
                    if dep_warnings:
                        result['warnings'] = dep_warnings

                    # 添加启动命令提示
                    if start_cmd_result.get('hint'):
                        result['start_command_hint'] = start_cmd_result['hint']

                    # 添加启动命令警告（例如：没有 gunicorn 的提示）
                    if start_cmd_result.get('warning'):
                        if 'warnings' not in result:
                            result['warnings'] = []
                        result['warnings'].append(start_cmd_result['warning'])

                    return result

        # 没有识别到支持的框架
        return self._error_result(
            "Python project detected but framework not recognized. "
            "Only Flask, FastAPI, Streamlit, and MCP are supported."
        )

    def _detect_python_version(self) -> str:
        """检测 Python 版本 (按优先级)"""
        # 1. runtime.txt (Heroku 规范)
        version = self._detect_from_runtime_txt()
        if version:
            return self._validate_python_version(version)

        # 2. .python-version (pyenv)
        version = self._detect_from_python_version()
        if version:
            return self._validate_python_version(version)

        # 3. pyproject.toml
        version = self._detect_from_pyproject_toml()
        if version:
            return self._validate_python_version(version)

        # 4. 默认版本
        return DEFAULT_PYTHON_VERSION

    def _detect_from_runtime_txt(self) -> Optional[str]:
        """从 runtime.txt 检测 (Heroku 规范)"""
        runtime_file = self.project_path / 'runtime.txt'
        if not runtime_file.exists():
            return None

        try:
            content = runtime_file.read_text().strip()
            # 匹配 "python-3.11" 或 "python-3.11.5"
            match = re.match(r'python-(\d+\.\d+)(?:\.\d+)?', content)
            if match:
                return match.group(1)
        except Exception:
            pass

        return None

    def _detect_from_python_version(self) -> Optional[str]:
        """从 .python-version 检测 (pyenv)"""
        pyenv_file = self.project_path / '.python-version'
        if not pyenv_file.exists():
            return None

        try:
            content = pyenv_file.read_text().strip()
            # 匹配 "3.11" 或 "3.11.5"
            match = re.match(r'(\d+\.\d+)(?:\.\d+)?', content)
            if match:
                return match.group(1)
        except Exception:
            pass

        return None

    def _detect_from_pyproject_toml(self) -> Optional[str]:
        """从 pyproject.toml 检测"""
        pyproject_file = self.project_path / 'pyproject.toml'
        if not pyproject_file.exists():
            return None

        try:
            # 尝试导入 tomllib (Python 3.11+) 或 tomli
            try:
                import tomllib
            except ImportError:
                try:
                    import tomli as tomllib
                except ImportError:
                    return None  # 无法解析 TOML

            content = pyproject_file.read_text()
            data = tomllib.loads(content)

            # 检查 [project] requires-python
            if 'project' in data:
                req = data['project'].get('requires-python', '')
                match = re.search(r'(\d+\.\d+)', req)
                if match:
                    return match.group(1)

            # 检查 [tool.poetry] python 依赖
            if 'tool' in data and 'poetry' in data['tool']:
                deps = data['tool']['poetry'].get('dependencies', {})
                python_dep = deps.get('python', '')
                match = re.search(r'(\d+\.\d+)', str(python_dep))
                if match:
                    return match.group(1)

        except Exception:
            pass

        return None

    def _extract_deps_from_pyproject(self, pyproject_file: Path) -> str:
        """从 pyproject.toml 提取依赖列表，转换为 requirements.txt 格式"""
        try:
            # 尝试导入 tomllib (Python 3.11+) 或 tomli
            try:
                import tomllib
            except ImportError:
                try:
                    import tomli as tomllib
                except ImportError:
                    return ""

            content = pyproject_file.read_text()
            data = tomllib.loads(content)
            deps = []

            # [project] dependencies (PEP 621)
            if 'project' in data:
                deps.extend(data['project'].get('dependencies', []))

            # [tool.poetry] dependencies
            if 'tool' in data and 'poetry' in data['tool']:
                poetry_deps = data['tool']['poetry'].get('dependencies', {})
                for pkg, ver in poetry_deps.items():
                    if pkg.lower() != 'python':
                        deps.append(pkg)

            return '\n'.join(deps)
        except Exception:
            return ""

    def _validate_python_version(self, version: str) -> str:
        """验证 Python 版本是否支持"""
        if version in SUPPORTED_PYTHON_VERSIONS:
            return version

        # 版本不支持,输出警告并使用默认版本
        print(f"⚠️  Detected Python {version}, but only {SUPPORTED_PYTHON_VERSIONS} are supported.", file=sys.stderr)
        print(f"   Using default version {DEFAULT_PYTHON_VERSION}", file=sys.stderr)
        return DEFAULT_PYTHON_VERSION

    def _check_problematic_dependencies(self, req_content: str) -> List[str]:
        """检查需要系统依赖的库"""
        warnings = []

        for line in req_content.lower().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # 提取包名 (处理 package==1.0.0, package>=1.0 等格式)
            package = re.split(r'[=<>!]', line)[0].strip()

            if package in SYSTEM_DEPENDENCY_LIBRARIES:
                reason = SYSTEM_DEPENDENCY_LIBRARIES[package]
                warnings.append(f"⚠️  {package}: {reason}")

        return warnings

    def _detect_start_command(self, framework: str, entry_file: str, port: int) -> Dict:
        """检测启动命令"""
        if framework == 'flask':
            return self._detect_flask_start_command(entry_file, port)
        elif framework == 'fastapi':
            return self._detect_fastapi_start_command(entry_file, port)
        elif framework == 'streamlit':
            return self._detect_streamlit_start_command(entry_file, port)
        elif framework == 'mcp':
            return self._detect_mcp_start_command(entry_file, port)

        return {'command': None, 'hint': 'Unknown framework'}

    def _detect_flask_start_command(self, entry_file: str, port: int) -> Dict:
        """检测 Flask 启动命令"""
        file_path = self.project_path / entry_file
        req_file = self.project_path / 'requirements.txt'

        # 检查是否安装了 gunicorn
        has_gunicorn = False
        if req_file.exists():
            try:
                req_content = req_file.read_text(encoding='utf-8').lower()
                has_gunicorn = 'gunicorn' in req_content
            except Exception:
                pass

        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return {
                'command': None,
                'hint': f"Unable to read {entry_file}. Please manually specify the start command."
            }

        # 查找 Flask app 实例名称
        match = re.search(r'(\w+)\s*=\s*Flask\s*\(', content)
        app_var = match.group(1) if match else 'app'
        module = entry_file.replace('.py', '')

        # 方式 1: if __name__ == '__main__': app.run()
        # 这种方式通常在开发时使用，保持原样（代码内部控制端口）
        if "if __name__ == '__main__':" in content and 'app.run()' in content:
            return {'command': f"python {entry_file}"}

        # 方式 2: 优先使用 gunicorn (生产环境)
        if has_gunicorn and match:
            return {
                'command': f'gunicorn -b 0.0.0.0:{port} {module}:{app_var}',
                'env': {}
            }

        # 方式 3: 降级到 flask run (开发环境)
        if match:
            result = {
                'command': f'flask run --host=0.0.0.0 --port={port}',
                'env': {'FLASK_APP': entry_file}
            }
            # 如果没有 gunicorn，给出警告
            if not has_gunicorn:
                result['warning'] = '⚠️  Using Flask development server. For production, add "gunicorn" to requirements.txt'
            return result

        # 无法检测
        return {
            'command': None,
            'hint': (
                f"Unable to auto-detect Flask startup command. Common methods:\n"
                f"  - python {entry_file} (if you have 'if __name__ == \"__main__\"')\n"
                f"  - flask run --host=0.0.0.0 --port={port} (requires setting FLASK_APP={entry_file})\n"
                f"  - gunicorn -b 0.0.0.0:{port} {module}:app (production environment)"
            )
        }

    def _detect_fastapi_start_command(self, entry_file: str, port: int) -> Dict:
        """检测 FastAPI 启动命令"""
        file_path = self.project_path / entry_file

        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return {
                'command': None,
                'hint': f"Unable to read {entry_file}. Please manually specify the start command."
            }

        # 查找 app = FastAPI() 的变量名
        match = re.search(r'(\w+)\s*=\s*FastAPI\s*\(', content)
        if match:
            app_var = match.group(1)
            module = entry_file.replace('.py', '')
            return {
                'command': f"uvicorn {module}:{app_var} --host 0.0.0.0 --port {port}"
            }

        # 无法检测
        module = entry_file.replace('.py', '')
        return {
            'command': None,
            'hint': (
                f"Unable to auto-detect FastAPI application instance name. Please provide start command:\n"
                f"  Example: uvicorn {module}:app --host 0.0.0.0 --port {port}"
            )
        }

    def _detect_streamlit_start_command(self, entry_file: str, port: int) -> Dict:
        """检测 Streamlit 启动命令"""
        # Streamlit 格式固定，使用检测到的端口
        return {
            'command': f"streamlit run {entry_file} --server.port {port} --server.address 0.0.0.0"
        }

    def _detect_mcp_start_command(self, entry_file: str, port: int) -> Dict:
        """检测 MCP Server 启动命令"""
        # MCP Server 直接运行 Python 脚本
        return {
            'command': f"python {entry_file}"
        }

    # ============= Python 端口检测方法 =============

    def _detect_python_port(self, framework: str, entry_file: str) -> int:
        """
        检测 Python 项目端口（按优先级）

        优先级:
        1. .env 文件中的框架特定变量 (FLASK_PORT=3004)
        2. .env 文件中的通用变量 (PORT=3004)
        3. config.py 中的默认值 (FLASK_PORT = int(os.getenv('FLASK_PORT', 6101)))
        4. app.py 中的硬编码值 (app.run(port=8080))
        5. 框架默认值 (5000)
        """

        # 1. 从 .env 文件检测
        env_files = ['.env.production', '.env.local', '.env']
        for env_file_name in env_files:
            env_file = self.project_path / env_file_name
            port = self._parse_python_env_port(env_file, framework)
            if port:
                return port

        # 2. 从 config.py 检测默认值
        port = self._parse_config_py_port(framework)
        if port:
            return port

        # 3. 从入口文件检测硬编码值
        port = self._parse_port_from_python_code(entry_file, framework)
        if port:
            return port

        # 4. 使用框架默认端口
        return DETECTION_RULES[framework]['default_port']

    def _parse_python_env_port(self, env_file: Path, framework: str) -> Optional[int]:
        """解析 .env 文件中的 Python 端口"""
        if not env_file.exists():
            return None

        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    # 优先匹配框架特定变量
                    framework_patterns = {
                        'flask': r'^FLASK_PORT\s*=\s*(\d+)',
                        'fastapi': r'^(?:FASTAPI_|UVICORN_)?PORT\s*=\s*(\d+)',
                        'streamlit': r'^STREAMLIT_(?:SERVER_)?PORT\s*=\s*(\d+)',
                    }

                    pattern = framework_patterns.get(framework)
                    if pattern:
                        match = re.match(pattern, line)
                        if match:
                            return int(match.group(1))

                    # 回退：匹配通用 PORT 变量
                    match = re.match(r'^PORT\s*=\s*(\d+)', line)
                    if match:
                        return int(match.group(1))
        except Exception:
            pass

        return None

    def _parse_config_py_port(self, framework: str) -> Optional[int]:
        """解析 config.py 中的端口默认值"""
        config_file = self.project_path / 'config.py'
        if not config_file.exists():
            return None

        try:
            content = config_file.read_text(encoding='utf-8')

            # 匹配 os.getenv() 模式: FLASK_PORT = int(os.getenv('FLASK_PORT', 6101))
            getenv_patterns = {
                'flask': r'FLASK_PORT\s*=\s*int\s*\(\s*os\.getenv\s*\([^,]+,\s*(\d+)\s*\)\s*\)',
                'fastapi': r'(?:FASTAPI_|UVICORN_)?PORT\s*=\s*int\s*\(\s*os\.getenv\s*\([^,]+,\s*(\d+)\s*\)\s*\)',
                'streamlit': r'STREAMLIT_PORT\s*=\s*int\s*\(\s*os\.getenv\s*\([^,]+,\s*(\d+)\s*\)\s*\)',
            }

            pattern = getenv_patterns.get(framework)
            if pattern:
                match = re.search(pattern, content)
                if match:
                    return int(match.group(1))

            # 匹配直接赋值模式: FLASK_PORT = 6101
            direct_patterns = {
                'flask': r'FLASK_PORT\s*=\s*(\d+)',
                'fastapi': r'(?:FASTAPI_|UVICORN_)?PORT\s*=\s*(\d+)',
                'streamlit': r'STREAMLIT_PORT\s*=\s*(\d+)',
            }

            pattern = direct_patterns.get(framework)
            if pattern:
                match = re.search(pattern, content)
                if match:
                    return int(match.group(1))

        except Exception:
            pass

        return None

    def _parse_port_from_python_code(self, entry_file: str, framework: str) -> Optional[int]:
        """从 Python 代码中解析端口配置"""
        file_path = self.project_path / entry_file

        try:
            content = file_path.read_text(encoding='utf-8')

            if framework == 'flask':
                # 匹配 app.run(port=5000) 或 app.run(host='0.0.0.0', port=5000)
                match = re.search(r'app\.run\s*\([^)]*port\s*=\s*(\d+)', content)
                if match:
                    return int(match.group(1))

            elif framework == 'fastapi':
                # 匹配 uvicorn.run("main:app", port=8000)
                match = re.search(r'uvicorn\.run\s*\([^)]*port\s*=\s*(\d+)', content)
                if match:
                    return int(match.group(1))

            elif framework == 'streamlit':
                # Streamlit 端口通常在 .streamlit/config.toml 中
                config_file = self.project_path / '.streamlit' / 'config.toml'
                if config_file.exists():
                    config_content = config_file.read_text()
                    match = re.search(r'port\s*=\s*(\d+)', config_content)
                    if match:
                        return int(match.group(1))

        except Exception:
            pass

        return None

    # ============= Next.js Standalone 检测方法 =============

    def _detect_standalone(self) -> Optional[Dict]:
        """
        检测 Next.js Standalone 模式配置

        返回:
            {
                'enabled': bool,        # 是否已启用 standalone
                'compatible': bool,     # Next.js 版本是否兼容 (>=12.0)
                'configFile': str,      # 配置文件路径
                'hasOutputConfig': bool # 是否已有 output 配置（任何值）
            }
        """
        # 1. 查找 next.config 文件
        config_files = ['next.config.js', 'next.config.mjs', 'next.config.ts']
        config_file = None
        config_content = None

        for filename in config_files:
            file_path = self.project_path / filename
            if file_path.exists():
                config_file = filename
                try:
                    config_content = file_path.read_text(encoding='utf-8')
                except Exception:
                    pass
                break

        # 2. 检测 Next.js 版本兼容性 (>=12.0)
        compatible = self._check_nextjs_version_compatible()

        # 3. 检测是否有自定义 server（不适用 Standalone）
        has_custom_server = (
            (self.project_path / 'server.js').exists() or
            (self.project_path / 'server.ts').exists()
        )

        # 4. 解析配置文件
        enabled = False
        has_output_config = False

        if config_content:
            # 检测 output: 'standalone'
            if re.search(r"output\s*:\s*['\"]standalone['\"]", config_content):
                enabled = True
                has_output_config = True
            # 检测其他 output 配置 (如 'export')
            elif re.search(r"output\s*:\s*['\"](\w+)['\"]", config_content):
                has_output_config = True

        # 5. 构建返回结果
        result = {
            'enabled': enabled,
            'compatible': compatible,
            'configFile': config_file,
            'hasOutputConfig': has_output_config,
        }

        # 6. 判断是否应该建议启用
        # 条件: 未启用 + 版本兼容 + 无其他 output 配置 + 无自定义 server
        should_suggest = (
            not enabled and
            compatible and
            not has_output_config and
            not has_custom_server
        )
        result['shouldSuggest'] = should_suggest

        if has_custom_server:
            result['skipReason'] = 'custom_server'
        elif not compatible:
            result['skipReason'] = 'version_incompatible'
        elif has_output_config and not enabled:
            result['skipReason'] = 'other_output_mode'

        return result

    def _check_nextjs_version_compatible(self) -> bool:
        """检查 Next.js 版本是否支持 Standalone (>=12.0)"""
        if not self.package_json:
            return False

        dependencies = {
            **self.package_json.get('dependencies', {}),
            **self.package_json.get('devDependencies', {})
        }

        next_version = dependencies.get('next', '')

        # 处理各种版本格式
        # ^14.0.0, ~13.5.0, >=12.0.0, 14.0.0, latest, canary
        if not next_version or next_version in ['latest', 'canary', 'next']:
            # 无法确定版本，保守返回 False
            return False

        # 提取主版本号
        match = re.search(r'(\d+)', next_version)
        if match:
            major_version = int(match.group(1))
            return major_version >= 12

        return False


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'error': 'Usage: detect_framework.py <project_path>'
        }, indent=2))
        sys.exit(1)

    project_path = sys.argv[1]

    # 检查路径是否存在
    if not os.path.exists(project_path):
        print(json.dumps({
            'success': False,
            'error': f'Project path does not exist: {project_path}'
        }, indent=2))
        sys.exit(1)

    # 执行检测
    detector = FrameworkDetector(project_path)
    result = detector.detect()

    # 输出 JSON 结果
    print(json.dumps(result, indent=2))

    # 如果检测失败，返回非零退出码
    if not result.get('success', False):
        sys.exit(1)


if __name__ == '__main__':
    main()
