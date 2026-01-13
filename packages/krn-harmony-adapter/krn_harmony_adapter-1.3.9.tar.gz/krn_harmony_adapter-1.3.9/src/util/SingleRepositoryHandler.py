#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单一项目仓库处理器
处理package.json在根目录，代码在src中的项目结构
"""

from pathlib import Path
from typing import List, Optional
from .RepositoryHandler import RepositoryHandler
from .RepositoryDetector import ModuleInfo, RepositoryInfo


class SingleRepositoryHandler(RepositoryHandler):
    """单一项目仓库处理器"""
    
    # 添加结构类型标识
    structure_type = "single"
    
    def discover_modules(self) -> List[ModuleInfo]:
        """发现模块 - 单一项目结构返回项目本身"""
        # 单一项目结构，整个项目就是一个模块
        project_name = self.base_path.name
        
        return [ModuleInfo(
            name=project_name,
            path=self.base_path,
            has_package_json=True,
            is_bundle=False
        )]
    
    def get_module_path(self, module_name: str = None) -> Optional[Path]:
        """获取模块路径 - 单一项目返回根目录"""
        # 对于单一项目，模块路径就是根目录
        return self.base_path
    
    def is_valid_module(self, module_path: Path) -> bool:
        """检查是否是有效的模块"""
        # 检查根目录是否有package.json
        package_json_path = module_path / "package.json"
        if not package_json_path.exists():
            return False
        
        # 检查是否有src目录
        src_path = module_path / "src"
        return src_path.exists() and src_path.is_dir()
    
    def get_package_json_path(self, module_name: str = None) -> Optional[Path]:
        """获取package.json路径 - 单一项目返回根目录的package.json"""
        package_json_path = self.base_path / "package.json"
        return package_json_path if package_json_path.exists() else None
    
    def get_adaptation_strategy(self, module_name: str = None) -> str:
        """获取适配策略"""
        return "single_project"
    
    def get_project_name(self) -> str:
        """获取项目名称"""
        return self.base_path.name
    
    def get_src_path(self) -> Optional[Path]:
        """获取src目录路径"""
        src_path = self.base_path / "src"
        return src_path if src_path.exists() else None