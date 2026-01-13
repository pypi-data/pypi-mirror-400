"""
模块管理器
负责模块的发现、分析、适配状态检查等
"""
import os
import json
from pathlib import Path
import re
import sys
from typing import List, Dict, Any, Set, Tuple
from .GitManager import GitManager
from .HarmonyDetector import HarmonyDetector

"""模块管理器"""
class ModuleManager(GitManager, HarmonyDetector):
    
    def __init__(self, basePath = "."):
        super().__init__(basePath)
        # 延迟导入以避免循环依赖
        self._repository_handler = None
    
    def _get_repository_handler(self):
        """获取仓库处理器（延迟初始化）"""
        if self._repository_handler is None:
            # 使用全局仓库管理器，避免重复检测
            from util.GlobalRepositoryManager import get_repository_handler
            self._repository_handler = get_repository_handler(self.basePath, silent=True)
        return self._repository_handler
    
    def discoverModules(self) -> List[str]:
        """发现所有模块"""
        handler = self._get_repository_handler()
        modules = handler.discover_modules()
        return [module.name for module in modules]
    
    def _isValidModule(self, modulePath: str) -> bool:
        """检查是否是有效的模块"""
        handler = self._get_repository_handler()
        return handler.is_valid_module(Path(modulePath))
    
    def checkModuleAdaptationStatus(self, moduleName: str) -> Dict[str, Any]:
        """检查模块的鸿蒙适配状态"""
        handler = self._get_repository_handler()
        module_path = handler.get_module_path(moduleName)
        
        status = {
            'moduleName': moduleName,
            'is_adapted': False,
            'react_native_version': '',
            'has_harmony_dependencies': False,
            'has_harmony_directory': False,
            'has_auto_adapt_dependency': False,
            'harmony_files_count': 0,
            'issues': []
        }
        
        if not module_path:
            status['issues'].append(f'模块 {moduleName} 不存在')
            return status
        
        # 检查package.json
        package_json_path = handler.get_package_json_path(moduleName)
        if package_json_path and package_json_path.exists():
            self._checkPackageJsonAdaptation(str(package_json_path), status)
        else:
            status['issues'].append('缺少package.json文件')
        
        # 检查harmony目录
        harmony_dir = module_path / 'harmony'
        status['has_harmony_directory'] = harmony_dir.exists()
        
        # 检查harmony相关文件
        count, filePaths = self.findHarmonyFiles(str(module_path))
        status['harmony_files_count'] = count
        status['harmony_files_path'] = filePaths
        
        # 判断是否已适配
        status['is_adapted'] = self._isModuleAdapted(status)
        
        return status
    
    def _checkPackageJsonAdaptation(self, package_json_path: str, status: Dict[str, Any]) -> None:
        """检查package.json的适配状态"""
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            # 检查react-native版本
            dependencies = package_data.get('dependencies', {})
            react_native_version = dependencies.get('react-native', '')
            status['react_native_version'] = react_native_version
            
            # 检查是否包含harmony标识
            if 'harmony' in react_native_version.lower():
                status['has_harmony_dependencies'] = True
            
            # 检查auto-adapt-harmony依赖
            dev_dependencies = package_data.get('devDependencies', {})
            if '@locallife/auto-adapt-harmony' in dev_dependencies:
                status['has_auto_adapt_dependency'] = True
            
            # 检查其他harmony相关依赖
            all_deps = {**dependencies, **dev_dependencies}
            for dep_name, dep_version in all_deps.items():
                if self.isHarmonyDependency(dep_name, str(dep_version)):
                    status['has_harmony_dependencies'] = True
                    break
                    
        except Exception as e:
            status['issues'].append(f'读取package.json失败: {e}')
    
    def findHarmonyFiles(self, modulePath: str) -> Tuple[int, str]:
        """统计harmony相关文件数量"""
        count = 0
        filePaths = ''
        
        for root, dirs, files in os.walk(modulePath):
            # 跳过node_modules和.git目录
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '.harmony_backup']]
            
            for file in files:
                if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if self.containsHarmonyContent(content):
                            count += 1
                            filePaths += f"{file_path}\n"
                    except Exception:
                        # 忽略读取错误
                        pass
        
        return count, filePaths
    
    def _isModuleAdapted(self, status: Dict[str, Any]) -> bool:
        """判断模块是否已适配"""
        # 主要检查react-native版本是否包含harmony（与原始逻辑保持一致）
        react_native_version = status.get('react_native_version', '')
        return 'harmony' in react_native_version.lower()

    def categorizeModulesByAdaptation(self, modules: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """按适配状态分类模块"""
        categorized = {
            'adapted': [],
            'not_adapted': [],
            'live_modules': {
                'adapted': [],
                'not_adapted': []
            },
            'non_live_modules': {
                'adapted': [],
                'not_adapted': []
            }
        }
        
        for moduleName in modules:
            status = self.checkModuleAdaptationStatus(moduleName)
            is_live = 'live' in moduleName.lower()
            
            if status['is_adapted']:
                categorized['adapted'].append(status)
                if is_live:
                    categorized['live_modules']['adapted'].append(status)
                else:
                    categorized['non_live_modules']['adapted'].append(status)
            else:
                categorized['not_adapted'].append(status)
                if is_live:
                    categorized['live_modules']['not_adapted'].append(status)
                else:
                    categorized['non_live_modules']['not_adapted'].append(status)
        
        return categorized
    
    def getModuleStatistics(self) -> Dict[str, Any]:
        """获取模块统计信息"""
        modules = self.discoverModules()
        categorized = self.categorizeModulesByAdaptation(modules)
        
        stats = {
            'total_modules': len(modules),
            'adapted_modules': len(categorized['adapted']),
            'not_adapted_modules': len(categorized['not_adapted']),
            'adaptation_rate': len(categorized['adapted']) / len(modules) * 100 if modules else 0,
            'live_modules': {
                'total': len(categorized['live_modules']['adapted']) + len(categorized['live_modules']['not_adapted']),
                'adapted': len(categorized['live_modules']['adapted']),
                'not_adapted': len(categorized['live_modules']['not_adapted']),
                'adaptation_rate': 0
            },
            'non_live_modules': {
                'total': len(categorized['non_live_modules']['adapted']) + len(categorized['non_live_modules']['not_adapted']),
                'adapted': len(categorized['non_live_modules']['adapted']),
                'not_adapted': len(categorized['non_live_modules']['not_adapted']),
                'adaptation_rate': 0
            }
        }
        
        # 计算直播模块适配率
        if stats['live_modules']['total'] > 0:
            stats['live_modules']['adaptation_rate'] = (
                stats['live_modules']['adapted'] / stats['live_modules']['total'] * 100
            )
        
        # 计算非直播模块适配率
        if stats['non_live_modules']['total'] > 0:
            stats['non_live_modules']['adaptation_rate'] = (
                stats['non_live_modules']['adapted'] / stats['non_live_modules']['total'] * 100
            )
        
        return stats
    
    def findAllUrl(self, modulePath: Path, targetDirs: List[str] = None) -> List[str]:
        """
        在指定模块路径的目标目录下，递归地查找所有 .ts, .tsx, .js 文件，
        并匹配其中所有以 '/rest/' 开头的字符串。
        
        Args:
            modulePath: 模块路径
            targetDirs: 目标目录列表，默认使用配置中的 defaultScanDirs
        
        Returns:
            找到的URL列表
        """
        if targetDirs is None:
            # 使用默认的扫描目录，对于bundles结构，直接扫描模块根目录下的src
            targetDirs = ['src']
        
        targetSuffixes = {'.ts', '.tsx', '.js'}
        foundUrls: Set[str] = set()
        totalFilesScanned = 0

        for targetDir in targetDirs:
            targetPath = modulePath / targetDir

            if not targetPath.is_dir():
                print(f"⚠️  警告: 在 '{modulePath}' 中未找到 '{targetDir}' 目录，跳过处理。")
                continue

            print(f"🔍 正在扫描目录: {targetPath}")
            filesScanned = 0

            for filePath in targetPath.rglob('*'):
                # 跳过 node_modules 目录中的文件
                if 'node_modules' in filePath.parts:
                    continue
                
                if filePath.is_file() and filePath.suffix in targetSuffixes:
                    filesScanned += 1
                    try:
                        content = filePath.read_text(encoding='utf-8')
                        matches = re.findall(r"(['\"`])(/rest/[^'\"`]*)\1", content)
                        
                        if matches:
                            for match in matches:
                                foundUrls.add(match[1])

                    except UnicodeDecodeError:
                        print(f"⚪️ 已跳过 (非文本文件): {filePath.relative_to(modulePath)}")
                    except Exception as e:
                        print(f"❌ 处理文件时出错 {filePath.relative_to(modulePath)}: {e}", file=sys.stderr)
            
            totalFilesScanned += filesScanned
            print(f"📁 {targetDir} 目录扫描完成：共扫描 {filesScanned} 个脚本文件。")
        
        print(f"\n✨ 扫描完成。共扫描 {totalFilesScanned} 个脚本文件。")

        return sorted(list(foundUrls))