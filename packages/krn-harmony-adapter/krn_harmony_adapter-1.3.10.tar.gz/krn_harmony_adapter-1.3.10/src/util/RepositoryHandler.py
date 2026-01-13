#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仓库处理器接口和实现
为不同仓库结构提供统一的模块管理API
"""

import os
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from .RepositoryDetector import ModuleInfo, RepositoryInfo, RepositoryStructure


@dataclass
class AdaptationResult:
    """适配结果数据类"""
    success: bool
    module_name: str
    message: str
    details: Optional[Dict[str, Any]] = None


class RepositoryHandler(ABC):
    """仓库处理器抽象基类"""
    
    def __init__(self, repo_info: RepositoryInfo):
        self.repo_info = repo_info
        self.base_path = repo_info.base_path
        
        # 排除的目录名称
        self.excluded_dirs = {
            '.git', 'node_modules', '.harmony_backup', 'doc', 'rule', 
            'scriptForHarmony', '.vscode', '.idea', 'dist', 'build',
            '__pycache__', '.pytest_cache', 'coverage'
        }
    
    @abstractmethod
    def discover_modules(self) -> List[ModuleInfo]:
        """发现所有模块"""
        pass
    
    @abstractmethod
    def get_module_path(self, module_name: str) -> Optional[Path]:
        """获取指定模块的路径"""
        pass
    
    @abstractmethod
    def is_valid_module(self, module_path: Path) -> bool:
        """检查是否是有效的模块"""
        pass
    
    @abstractmethod
    def get_package_json_path(self, module_name: str) -> Optional[Path]:
        """获取模块的package.json路径"""
        pass
    
    @abstractmethod
    def get_adaptation_strategy(self, module_name: str) -> str:
        """获取模块的适配策略"""
        pass
    
    def get_structure_type(self) -> RepositoryStructure:
        """获取仓库结构类型"""
        return self.repo_info.structure
    
    def get_all_module_names(self) -> List[str]:
        """获取所有模块名称"""
        return [module.name for module in self.discover_modules()]
    
    def find_module_by_name(self, module_name: str) -> Optional[ModuleInfo]:
        """根据名称查找模块"""
        for module in self.discover_modules():
            if module.name == module_name:
                return module
        return None


class FlatRepositoryHandler(RepositoryHandler):
    """平铺式仓库处理器"""
    
    # 添加结构类型标识
    structure_type = "flat"
    
    def discover_modules(self) -> List[ModuleInfo]:
        """发现所有模块 - 扫描根目录下的直接子目录"""
        modules = []
        
        for item in self.base_path.iterdir():
            if not item.is_dir():
                continue
                
            # 跳过排除的目录
            if item.name in self.excluded_dirs or item.name.startswith('.'):
                continue
            
            # 检查是否是有效模块
            if self.is_valid_module(item):
                modules.append(ModuleInfo(
                    name=item.name,
                    path=item,
                    has_package_json=True,
                    is_bundle=False
                ))
        
        return sorted(modules, key=lambda x: x.name)
    
    def get_module_path(self, module_name: str) -> Optional[Path]:
        """获取指定模块的路径"""
        module_path = self.base_path / module_name
        return module_path if module_path.exists() and module_path.is_dir() else None
    
    def is_valid_module(self, module_path: Path) -> bool:
        """检查是否是有效的模块"""
        # 排除特殊目录
        if module_path.name in self.excluded_dirs or module_path.name.startswith('.'):
            return False
        
        # 检查是否有package.json文件
        package_json_path = module_path / "package.json"
        return package_json_path.exists()
    
    def get_package_json_path(self, module_name: str) -> Optional[Path]:
        """获取模块的package.json路径"""
        module_path = self.get_module_path(module_name)
        if module_path:
            package_json_path = module_path / "package.json"
            return package_json_path if package_json_path.exists() else None
        return None
    
    def get_adaptation_strategy(self, module_name: str) -> str:
        """获取模块的适配策略"""
        return "flat_module"  # 平铺式模块的适配策略


class BundlesRepositoryHandler(RepositoryHandler):
    """bundles式仓库处理器"""
    
    # 添加结构类型标识
    structure_type = "bundles"
    
    def __init__(self, repo_info: RepositoryInfo):
        super().__init__(repo_info)
        self.bundles_path = repo_info.bundles_path
        if not self.bundles_path:
            raise ValueError("bundles路径未找到，无法创建BundlesRepositoryHandler")
    
    def discover_modules(self) -> List[ModuleInfo]:
        """发现所有模块 - 扫描bundles目录下的子目录"""
        modules = []
        
        for item in self.bundles_path.iterdir():
            if not item.is_dir():
                continue
                
            # 跳过排除的目录
            if item.name in self.excluded_dirs or item.name.startswith('.'):
                continue
            
            # 检查是否是有效模块
            if self.is_valid_module(item):
                modules.append(ModuleInfo(
                    name=item.name,
                    path=item,
                    has_package_json=True,
                    is_bundle=True,
                    parent_path=self.bundles_path
                ))
        
        return sorted(modules, key=lambda x: x.name)
    
    def get_module_path(self, module_name: str) -> Optional[Path]:
        """获取指定模块的路径"""
        module_path = self.bundles_path / module_name
        return module_path if module_path.exists() and module_path.is_dir() else None
    
    def is_valid_module(self, module_path: Path) -> bool:
        """检查是否是有效的模块"""
        # 排除特殊目录
        if module_path.name in self.excluded_dirs or module_path.name.startswith('.'):
            return False
        
        # 检查是否有package.json文件
        package_json_path = module_path / "package.json"
        return package_json_path.exists()
    
    def get_package_json_path(self, module_name: str) -> Optional[Path]:
        """获取模块的package.json路径"""
        module_path = self.get_module_path(module_name)
        if module_path:
            package_json_path = module_path / "package.json"
            return package_json_path if package_json_path.exists() else None
        return None
    
    def get_root_package_json_path(self) -> Optional[Path]:
        """获取根目录的package.json路径"""
        return self.repo_info.root_package_json
    
    def get_adaptation_strategy(self, module_name: str) -> str:
        """获取模块的适配策略"""
        return "bundles_module"  # bundles式模块的适配策略
    
    def update_root_dependencies(self, dependencies: Dict[str, str]) -> bool:
        """更新根目录package.json的依赖"""
        root_package_path = self.get_root_package_json_path()
        if not root_package_path:
            print("⚠️  根目录package.json不存在，无法更新依赖")
            return False
        
        try:
            # 读取现有的package.json
            with open(root_package_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            # 更新dependencies
            if 'dependencies' not in package_data:
                package_data['dependencies'] = {}
            
            package_data['dependencies'].update(dependencies)
            
            # 写回文件
            with open(root_package_path, 'w', encoding='utf-8') as f:
                json.dump(package_data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ 已更新根目录package.json依赖: {len(dependencies)}个")
            return True
            
        except Exception as e:
            print(f"❌ 更新根目录package.json失败: {e}")
            return False


class HybridRepositoryHandler(RepositoryHandler):
    """混合式仓库处理器"""
    
    def __init__(self, repo_info: RepositoryInfo):
        super().__init__(repo_info)
        self.flat_handler = FlatRepositoryHandler(repo_info)
        self.bundles_handler = BundlesRepositoryHandler(repo_info)
    
    def discover_modules(self) -> List[ModuleInfo]:
        """发现所有模块 - 合并根目录和bundles目录的模块"""
        flat_modules = self.flat_handler.discover_modules()
        bundles_modules = self.bundles_handler.discover_modules()
        
        all_modules = flat_modules + bundles_modules
        return sorted(all_modules, key=lambda x: x.name)
    
    def get_module_path(self, module_name: str) -> Optional[Path]:
        """获取指定模块的路径 - 先查找根目录，再查找bundles目录"""
        # 先尝试根目录
        path = self.flat_handler.get_module_path(module_name)
        if path:
            return path
        
        # 再尝试bundles目录
        return self.bundles_handler.get_module_path(module_name)
    
    def is_valid_module(self, module_path: Path) -> bool:
        """检查是否是有效的模块"""
        return self.flat_handler.is_valid_module(module_path)
    
    def get_package_json_path(self, module_name: str) -> Optional[Path]:
        """获取模块的package.json路径"""
        # 先尝试根目录
        path = self.flat_handler.get_package_json_path(module_name)
        if path:
            return path
        
        # 再尝试bundles目录
        return self.bundles_handler.get_package_json_path(module_name)
    
    def get_adaptation_strategy(self, module_name: str) -> str:
        """获取模块的适配策略"""
        # 判断模块位置来决定策略
        module = self.find_module_by_name(module_name)
        if module:
            return "bundles_module" if module.is_bundle else "flat_module"
        return "unknown"


def create_repository_handler(repo_info: RepositoryInfo) -> RepositoryHandler:
    """
    工厂函数：根据仓库信息创建对应的处理器
    
    Args:
        repo_info: 仓库信息
        
    Returns:
        RepositoryHandler: 对应的仓库处理器实例
    """
    if repo_info.structure == RepositoryStructure.FLAT:
        return FlatRepositoryHandler(repo_info)
    elif repo_info.structure == RepositoryStructure.BUNDLES:
        return BundlesRepositoryHandler(repo_info)
    elif repo_info.structure == RepositoryStructure.HYBRID:
        return HybridRepositoryHandler(repo_info)
    elif repo_info.structure == RepositoryStructure.SINGLE:
        from .SingleRepositoryHandler import SingleRepositoryHandler
        return SingleRepositoryHandler(repo_info)
    else:
        raise ValueError(f"不支持的仓库结构类型: {repo_info.structure}")
