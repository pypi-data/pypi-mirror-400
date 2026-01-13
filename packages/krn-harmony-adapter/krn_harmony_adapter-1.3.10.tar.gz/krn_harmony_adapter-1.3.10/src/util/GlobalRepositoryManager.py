#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局仓库信息管理器
确保RepositoryDetector只被调用一次，避免重复检测
"""

from pathlib import Path
from typing import Optional, Dict
from util.RepositoryDetector import RepositoryDetector, RepositoryInfo
from util.RepositoryHandler import RepositoryHandler, create_repository_handler


class GlobalRepositoryManager:
    """全局仓库信息管理器"""
    
    _instances: Dict[str, 'GlobalRepositoryManager'] = {}
    
    def __new__(cls, base_path: str):
        """单例模式：每个base_path只创建一个实例"""
        base_path = str(Path(base_path).resolve())
        
        if base_path not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[base_path] = instance
            instance._initialized = False
        
        return cls._instances[base_path]
    
    def __init__(self, base_path: str):
        if self._initialized:
            return
            
        self.base_path = Path(base_path).resolve()
        self._detector = None
        self._repo_info = None
        self._repository_handler = None
        self._initialized = True
    
    def get_repository_info(self, silent: bool = False) -> RepositoryInfo:
        """获取仓库信息（只检测一次）"""
        if self._repo_info is None:
            self._detector = RepositoryDetector()
            self._repo_info = self._detector.detect_structure(self.base_path, silent)
        
        return self._repo_info
    
    def get_repository_handler(self, silent: bool = False, create_handler = True) -> RepositoryHandler:
        """获取仓库处理器（只创建一次）"""
        if self._repository_handler is None:
            repo_info = self.get_repository_info(silent)
            if not create_handler:
                return None
            self._repository_handler = create_repository_handler(repo_info)
        
        return self._repository_handler
    
    @classmethod
    def clear_cache(cls):
        """清除所有缓存（用于测试）"""
        cls._instances.clear()


def get_global_repository_manager(base_path: str = ".") -> GlobalRepositoryManager:
    """获取全局仓库管理器实例"""
    return GlobalRepositoryManager(base_path)


def get_repository_info(base_path: str = ".", silent: bool = False) -> RepositoryInfo:
    """获取仓库信息的便捷函数"""
    manager = get_global_repository_manager(base_path)
    return manager.get_repository_info(silent)


def get_repository_handler(base_path: str = ".", silent: bool = False) -> RepositoryHandler:
    """获取仓库处理器的便捷函数"""
    manager = get_global_repository_manager(base_path)
    return manager.get_repository_handler(silent)