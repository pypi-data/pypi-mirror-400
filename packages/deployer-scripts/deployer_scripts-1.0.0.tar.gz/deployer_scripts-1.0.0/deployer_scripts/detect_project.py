#!/usr/bin/env python3
"""
Project Detector - 一体化项目检测工具

一次性完成：
1. 框架检测 (detect_framework) - 支持 hybrid 类型和 MCP 特性
2. 持久化分析 (analyze_volumes)
3. 配置文件生成 (app-deploy.json)

版本: v1.1.1
"""

import json
import sys
from pathlib import Path
from typing import Dict

# Import existing script modules
from .detect_framework import FrameworkDetector
from .analyze_volumes import VolumeAnalyzer
from .config_utils import (
    read_config, write_config, compare_detection,
    merge_config, get_change_summary
)


def log(msg: str):
    """输出日志到 stderr，避免干扰 MCP stdout 通信"""
    print(msg, file=sys.stderr)


class ProjectDetector:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.framework_result = None
        self.volumes_result = None
        self.config_result = None

    def detect(self, force_update: bool = False) -> Dict:
        """
        执行项目检测（支持智能增量更新和 hybrid 类型）

        一次性完成:
        1. 读取现有配置（如果存在）
        2. 检测框架信息（支持 hybrid）
        3. 分析持久化卷
        4. 比对检测结果
        5. 增量更新配置文件（仅在需要时）

        Args:
            force_update: 强制更新配置（默认False，自动判断）

        Returns:
            检测结果字典
        """
        # 验证项目路径
        if not self.project_path.exists():
            return {
                'success': False,
                'error': f'Project path does not exist: {self.project_path}'
            }

        # 步骤 1: 读取现有配置
        try:
            existing_config = read_config(str(self.project_path))
            if existing_config:
                app_name = existing_config.get('appName', 'N/A')
                framework = existing_config.get('framework', 'N/A')
                log(f"ℹ️  Found existing configuration:")
                log(f"   App Name: {app_name}")
                log(f"   Framework: {framework}")
                log("")
        except ValueError as e:
            log(f"⚠️  Warning: Invalid existing config: {e}")
            existing_config = None

        # 步骤 2: 检测框架
        log(f"🔍 Detecting framework...")
        framework_detector = FrameworkDetector(str(self.project_path))
        self.framework_result = framework_detector.detect()

        if not self.framework_result.get('success'):
            return {
                'success': False,
                'error': 'Framework detection failed',
                'details': self.framework_result
            }

        framework = self.framework_result.get('framework')

        # 根据框架类型输出不同信息
        if framework == 'hybrid':
            self._print_hybrid_info()
        else:
            self._print_single_framework_info()

        # 步骤 3: 分析持久化需求
        log(f"\n📦 Analyzing volumes...")
        volumes = self._analyze_volumes()

        if volumes:
            log(f"  ✓ Found {len(volumes)} persistent directories:")
            for vol in volumes:
                log(f"    - {vol['source']} ({vol.get('size', 'N/A')}) - {vol.get('reason', 'N/A')}")
        else:
            log(f"  ℹ No persistent directories detected")

        # 步骤 4: 构建检测结果
        detection_result = self._build_detection_result(volumes)

        # 步骤 5: 比对是否需要更新
        if not force_update and existing_config:
            if not compare_detection(existing_config, detection_result):
                log(f"\n✅ No changes detected in project structure")
                log(f"ℹ️  Configuration unchanged, skip writing")

                result = {
                    'success': True,
                    'operation': 'no_changes',
                    'project_path': str(self.project_path),
                    'framework': framework,
                    'message': 'Project structure unchanged, configuration preserved'
                }

                # 包含配置信息
                result['existing_config'] = {
                    'appName': existing_config.get('appName'),
                    'appVersion': existing_config.get('appVersion')
                }

                # 透传 standalone 信息 (Next.js)
                standalone = self.framework_result.get('standalone')
                if standalone:
                    result['standalone'] = standalone

                return result

        # 步骤 6: 增量更新配置
        log(f"\n📝 Updating configuration...")
        merged_config = merge_config(existing_config, detection_result, str(self.project_path))

        try:
            write_config(str(self.project_path), merged_config)
            log(f"  ✓ Config updated (user fields preserved)")

            # 显示变更摘要
            if existing_config:
                changes = get_change_summary(existing_config, detection_result)
                if changes:
                    log(f"  📋 Changes:")
                    for change in changes:
                        log(f"    - {change}")

        except ValueError as e:
            return {
                'success': False,
                'error': 'CONFIG_UPDATE_FAILED',
                'message': f'Failed to update configuration: {str(e)}'
            }

        log(f"\n✅ Detection complete!")

        result = {
            'success': True,
            'operation': 'updated' if existing_config else 'created',
            'project_path': str(self.project_path),
            'framework': framework,
            'message': 'Project detected and configured successfully'
        }

        # 单一框架类型包含额外信息
        if framework != 'hybrid':
            result['confidence'] = self.framework_result.get('confidence')
            result['detection_method'] = self.framework_result.get('detection_method')

            # 透传 standalone 信息 (Next.js)
            standalone = self.framework_result.get('standalone')
            if standalone:
                result['standalone'] = standalone

        # 包含配置信息
        result['config'] = {
            'appName': merged_config.get('appName'),
            'appVersion': merged_config.get('appVersion')
        }

        return result

    def _print_hybrid_info(self):
        """输出 hybrid 类型信息"""
        log(f"  ✓ Framework: hybrid (mixed project)")

        # 输出组件表格
        components = self.framework_result.get('components', [])
        log(f"\n  📦 Components:")
        log(f"  ┌{'─'*12}┬{'─'*10}┬{'─'*12}┬{'─'*7}┬{'─'*9}┐")
        log(f"  │{'Path':^12}│{'Language':^10}│{'Framework':^12}│{'Port':^7}│{'Primary':^9}│")
        log(f"  ├{'─'*12}┼{'─'*10}┼{'─'*12}┼{'─'*7}┼{'─'*9}┤")
        for comp in components:
            path = comp.get('path', '.')[:10]
            lang = comp.get('language', '')[:8]
            fw = comp.get('framework', '')[:10]
            port = str(comp.get('port', ''))[:5]
            primary = '✓' if comp.get('primary') else ''
            log(f"  │{path:^12}│{lang:^10}│{fw:^12}│{port:^7}│{primary:^9}│")
        log(f"  └{'─'*12}┴{'─'*10}┴{'─'*12}┴{'─'*7}┴{'─'*9}┘")

        # 输出运行时信息
        runtime = self.framework_result.get('runtime', {})
        log(f"\n  Runtime:")
        log(f"    Command:  {runtime.get('command', 'N/A')}")
        log(f"    Requires: {', '.join(runtime.get('requires', []))}")

        # 输出 features
        features = self.framework_result.get('features', [])
        if features:
            log(f"    Features: {', '.join(features)}")

        # 输出 MCP 警告
        for comp in components:
            mcp = comp.get('mcp', {})
            if mcp.get('warning'):
                log(f"\n  ⚠️  MCP Warning: {mcp['warning']}")

    def _print_single_framework_info(self):
        """输出单一框架类型信息"""
        framework = self.framework_result.get('framework')
        port = self.framework_result.get('port')
        start_command = self.framework_result.get('start_command')
        start_command_hint = self.framework_result.get('start_command_hint')

        log(f"  ✓ Framework: {framework}")
        log(f"  ✓ Port: {port}")
        log(f"  ✓ Build: {self.framework_result.get('build_command')}")

        # 输出 features
        features = self.framework_result.get('features', [])
        if features:
            log(f"  ✓ Features: {', '.join(features)}")

        # 输出 MCP 信息
        mcp = self.framework_result.get('mcp', {})
        if mcp:
            log(f"  ✓ MCP Transport: {mcp.get('transport', 'N/A')}")
            if mcp.get('warning'):
                log(f"  ⚠️  MCP Warning: {mcp['warning']}")

        # Show warning if start_command is missing
        if start_command:
            log(f"  ✓ Start: {start_command}")
        else:
            log(f"  ⚠️  Start: Not detected")
            if start_command_hint:
                # Print hint with indentation
                log(f"\n  💡 Suggestion:")
                for line in start_command_hint.split('\n'):
                    log(f"     {line}")

        # Next.js Standalone 模式建议
        standalone = self.framework_result.get('standalone', {})
        if standalone:
            if standalone.get('enabled'):
                log(f"  ✓ Standalone: enabled")
            elif standalone.get('shouldSuggest'):
                log(f"\n  💡 Standalone Mode Suggestion:")
                log(f"     Standalone mode can reduce image size by 75% (900MB → 225MB)")
                log(f"     Config file: {standalone.get('configFile', 'next.config.js')}")
            elif standalone.get('skipReason'):
                reason = standalone.get('skipReason')
                if reason == 'custom_server':
                    log(f"  ℹ️  Standalone: skipped (custom server detected)")
                elif reason == 'version_incompatible':
                    log(f"  ℹ️  Standalone: skipped (requires Next.js >= 12.0)")
                elif reason == 'other_output_mode':
                    log(f"  ℹ️  Standalone: skipped (other output mode configured)")

    def _analyze_volumes(self) -> list:
        """分析持久化卷（支持 hybrid 多路径）"""
        framework = self.framework_result.get('framework')

        if framework == 'hybrid':
            # hybrid 项目：扫描所有组件路径
            all_volumes = []
            components = self.framework_result.get('components', [])

            for comp in components:
                comp_path = comp.get('path', '.')
                if comp_path == '.':
                    full_path = self.project_path
                else:
                    full_path = self.project_path / comp_path.lstrip('./')

                volume_analyzer = VolumeAnalyzer(str(full_path))
                result = volume_analyzer.analyze()

                if result.get('success'):
                    for vol in result.get('suggested', []):
                        # 调整路径前缀
                        if comp_path != '.':
                            vol['source'] = f"{comp_path}/{vol['source'].lstrip('./')}"
                        all_volumes.append(vol)

            return all_volumes
        else:
            # 单一项目：原有逻辑
            volume_analyzer = VolumeAnalyzer(str(self.project_path))
            self.volumes_result = volume_analyzer.analyze()

            if not self.volumes_result.get('success'):
                return []

            return self.volumes_result.get('suggested', [])

    def _build_detection_result(self, volumes: list) -> Dict:
        """构建检测结果（支持 hybrid 类型）"""
        framework = self.framework_result.get('framework')

        if framework == 'hybrid':
            # hybrid 类型配置
            result = {
                'framework': 'hybrid',
                'components': self.framework_result.get('components', []),
                'runtime': self.framework_result.get('runtime', {}),
                'volumes': volumes
            }

            # 添加 features
            features = self.framework_result.get('features', [])
            if features:
                result['features'] = features

            return result
        else:
            # 单一框架类型配置
            result = {
                'framework': framework,
                'build': {
                    'command': self.framework_result.get('build_command', ""),
                    'timeout': 600
                },
                'runtime': {
                    'command': self.framework_result.get('start_command'),
                    'port': self.framework_result.get('port'),
                    'nodeVersion': self.framework_result.get('node_version', "")
                },
                'volumes': volumes
            }

            # 添加 features
            features = self.framework_result.get('features', [])
            if features:
                result['features'] = features

            # 添加 mcp 配置
            mcp = self.framework_result.get('mcp')
            if mcp:
                result['mcp'] = mcp

            # 添加 standalone 配置 (Next.js 专属)
            standalone = self.framework_result.get('standalone')
            if standalone:
                result['standalone'] = standalone

            # 添加 environment 配置 (Python 项目的环境变量)
            environment = self.framework_result.get('environment')
            if environment:
                result['environment'] = environment

            return result


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'error': 'Usage: detect_project.py <project_path>',
            'example': 'detect_project.py /path/to/project'
        }, indent=2))
        sys.exit(1)

    project_path = sys.argv[1]

    # 执行检测
    detector = ProjectDetector(project_path)
    result = detector.detect()

    # 输出 JSON 结果（用于程序化调用，输出到 stdout）
    log("\n" + "="*60)
    log("JSON Result:")
    log("="*60)
    print(json.dumps(result, indent=2))  # 保持 stdout 输出，供管道使用

    if not result.get('success', False):
        sys.exit(1)


if __name__ == '__main__':
    main()
