#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仓库结构检测器
负责自动检测和识别不同的仓库结构类型
"""

import os
import json
from pathlib import Path
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass


class RepositoryStructure(Enum):
    """仓库结构类型枚举"""
    FLAT = "flat"           # 平铺式结构：模块直接在根目录下
    BUNDLES = "bundles"     # bundles式结构：模块在bundles目录下
    HYBRID = "hybrid"       # 混合式结构：既有根目录模块，又有bundles目录
    SINGLE = "single"       # 单一项目结构：package.json在根目录，代码在src中
    UNKNOWN = "unknown"     # 未知结构


@dataclass
class ModuleInfo:
    """模块信息数据类"""
    name: str
    path: Path
    has_package_json: bool
    is_bundle: bool = False
    parent_path: Optional[Path] = None


@dataclass
class RepositoryInfo:
    """仓库信息数据类"""
    structure: RepositoryStructure
    base_path: Path
    root_package_json: Optional[Path]
    modules: List[ModuleInfo]
    bundles_path: Optional[Path]
    confidence: float  # 检测置信度 0.0-1.0


class RepositoryDetector:
    """仓库结构检测器"""
    
    def __init__(self):
        # 排除的目录名称
        self.excluded_dirs = {
            '.git', 'node_modules', '.harmony_backup', 'doc', 'rule', 
            'scriptForHarmony', '.vscode', '.idea', 'dist', 'build',
            '__pycache__', '.pytest_cache', 'coverage'
        }
        
        # 常见的bundles目录名称
        self.bundle_dir_names = {'bundles', 'packages', 'modules', 'apps'}
    
    def detect_structure(self, base_path: Union[str, Path], silent: bool = True) -> RepositoryInfo:
        """
        检测仓库结构
        
        Args:
            base_path: 项目根目录路径
            silent: 是否静默模式（不输出检测过程）
            
        Returns:
            RepositoryInfo: 检测到的仓库信息
        """
        base_path = Path(base_path).resolve()
        
        if not base_path.exists() or not base_path.is_dir():
            raise ValueError(f"路径不存在或不是目录: {base_path}")
        
        if not silent:
            print(f"🔍 检测仓库结构: {base_path}")
        
        # 1. 检查根目录package.json
        root_package_json = self._check_root_package_json(base_path)
        
        # 2. 扫描直接子目录中的模块
        root_modules = self._scan_root_modules(base_path)
        
        # 3. 检查bundles类型目录
        bundles_info = self._scan_bundles_directories(base_path)
        
        # 4. 分析结构类型
        structure, confidence = self._analyze_structure(
            root_package_json, root_modules, bundles_info
        )
        
        # 5. 合并所有模块信息
        all_modules = root_modules + bundles_info['modules']
        
        repo_info = RepositoryInfo(
            structure=structure,
            base_path=base_path,
            root_package_json=root_package_json,
            modules=all_modules,
            bundles_path=bundles_info['path'],
            confidence=confidence
        )
        
        self._print_detection_result(repo_info, silent)
        return repo_info
    
    def _check_root_package_json(self, base_path: Path) -> Optional[Path]:
        """检查根目录是否有package.json"""
        package_json_path = base_path / "package.json"
        return package_json_path if package_json_path.exists() else None
    
    def _scan_root_modules(self, base_path: Path) -> List[ModuleInfo]:
        """扫描根目录下的模块"""
        modules = []
        
        for item in base_path.iterdir():
            if not item.is_dir():
                continue
                
            # 跳过排除的目录
            if item.name in self.excluded_dirs or item.name.startswith('.'):
                continue
                
            # 跳过可能的bundles目录，这些会在后面单独处理
            if item.name in self.bundle_dir_names:
                continue
            
            # 检查是否有package.json
            package_json_path = item / "package.json"
            has_package_json = package_json_path.exists()
            
            if has_package_json:
                modules.append(ModuleInfo(
                    name=item.name,
                    path=item,
                    has_package_json=True,
                    is_bundle=False
                ))
        
        return modules
    
    def _scan_bundles_directories(self, base_path: Path) -> Dict:
        """扫描bundles类型目录"""
        result = {
            'path': None,
            'modules': []
        }
        
        # 查找bundles类型目录，优先选择包含最多模块的目录
        best_path = None
        best_modules = []
        
        for dir_name in self.bundle_dir_names:
            bundles_path = base_path / dir_name
            if bundles_path.exists() and bundles_path.is_dir():
                modules = self._scan_modules_in_bundles(bundles_path)
                # 选择包含模块最多的目录
                if len(modules) > len(best_modules):
                    best_path = bundles_path
                    best_modules = modules
        
        if best_path:
            result['path'] = best_path
            result['modules'] = best_modules
        
        return result
    
    def _scan_modules_in_bundles(self, bundles_path: Path) -> List[ModuleInfo]:
        """扫描bundles目录中的模块"""
        modules = []
        
        for item in bundles_path.iterdir():
            if not item.is_dir():
                continue
                
            # 跳过排除的目录
            if item.name in self.excluded_dirs or item.name.startswith('.'):
                continue
            
            # 检查是否有package.json
            package_json_path = item / "package.json"
            has_package_json = package_json_path.exists()
            
            if has_package_json:
                modules.append(ModuleInfo(
                    name=item.name,
                    path=item,
                    has_package_json=True,
                    is_bundle=True,
                    parent_path=bundles_path
                ))
        
        return modules
    
    def _analyze_structure(self, root_package_json: Optional[Path], 
                          root_modules: List[ModuleInfo], 
                          bundles_info: Dict) -> Tuple[RepositoryStructure, float]:
        """分析仓库结构类型"""
        has_root_package = root_package_json is not None
        has_root_modules = len(root_modules) > 0
        has_bundles_modules = len(bundles_info['modules']) > 0
        
        # 结构判断逻辑
        if has_bundles_modules and has_root_modules:
            # 既有根目录模块，又有bundles模块
            return RepositoryStructure.HYBRID, 0.9
        
        elif has_bundles_modules and has_root_package:
            # 有bundles模块和根目录package.json，典型的bundles结构
            return RepositoryStructure.BUNDLES, 0.95
        
        elif has_bundles_modules:
            # 只有bundles模块，可能是bundles结构
            return RepositoryStructure.BUNDLES, 0.8
        
        elif has_root_modules:
            # 只有根目录模块，典型的平铺结构
            return RepositoryStructure.FLAT, 0.9
        
        elif has_root_package and self._is_single_project_structure(root_package_json.parent):
            # 有根目录package.json且符合单一项目结构特征
            return RepositoryStructure.SINGLE, 0.9
        
        else:
            # 没有找到明确的模块结构
            return RepositoryStructure.UNKNOWN, 0.1
    
    def _print_detection_result(self, repo_info: RepositoryInfo, silent: bool = False):
        """打印检测结果"""
        if silent:
            return
            
        print(f"📊 检测结果:")
        print(f"   结构类型: {repo_info.structure.value}")
        print(f"   置信度: {repo_info.confidence:.1%}")
        print(f"   根目录package.json: {'✅' if repo_info.root_package_json else '❌'}")
        print(f"   bundles目录: {'✅' if repo_info.bundles_path else '❌'}")
        
        if repo_info.structure == RepositoryStructure.SINGLE:
            # 单一项目结构的特殊显示
            src_path = repo_info.base_path / "src"
            print(f"   src目录: {'✅' if src_path.exists() else '❌'}")
            print(f"   项目类型: 单一项目")
        else:
            print(f"   总模块数: {len(repo_info.modules)}")
            
            # 按类型统计模块
            root_count = sum(1 for m in repo_info.modules if not m.is_bundle)
            bundle_count = sum(1 for m in repo_info.modules if m.is_bundle)
            
            if root_count > 0:
                print(f"   根目录模块: {root_count}个")
            if bundle_count > 0:
                print(f"   bundles模块: {bundle_count}个")
    
    def _is_single_project_structure(self, base_path: Path) -> bool:
        """检查是否是单一项目结构"""
        # 检查是否有src目录且包含代码文件
        src_path = base_path / "src"
        if not src_path.exists() or not src_path.is_dir():
            return False
        
        # 检查src目录下是否有代码文件
        code_extensions = {'.ts', '.tsx', '.js', '.jsx'}
        for file_path in src_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in code_extensions:
                return True
        
        return False
    
    def get_structure_description(self, structure: RepositoryStructure) -> str:
        """获取结构类型的描述"""
        descriptions = {
            RepositoryStructure.FLAT: "平铺式结构 - 模块直接位于项目根目录下",
            RepositoryStructure.BUNDLES: "bundles式结构 - 模块位于bundles目录下，根目录有package.json",
            RepositoryStructure.HYBRID: "混合式结构 - 既有根目录模块，又有bundles目录模块",
            RepositoryStructure.SINGLE: "单一项目结构 - package.json在根目录，代码在src中",
            RepositoryStructure.UNKNOWN: "未知结构 - 无法识别明确的项目结构"
        }
        return descriptions.get(structure, "未知结构类型")
