#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置
"""

from pathlib import Path
from typing import Optional

from util.BackupManager import BackupManager
from util.GitManager import GitManager
from util.HarmonyDetector import HarmonyDetector
from util.ModuleManager import ModuleManager
from util.GlobalRepositoryManager import get_global_repository_manager
from util.RepositoryDetector import RepositoryInfo
from util.RepositoryHandler import RepositoryHandler

class Config:
    
    def __init__(self, base_path: Optional[str] = None, silent: bool = False, create_handler: bool = True):
        # 1. 设置基础路径
        if base_path:
            self.basePath = Path(base_path).resolve()
        else:
            self.basePath = Path(".").resolve()
        
        # 2. 使用全局仓库管理器（确保只检测一次）
        self.global_manager = get_global_repository_manager(str(self.basePath))
        self.repo_info = self.global_manager.get_repository_info(silent)
        self.repository_handler = self.global_manager.get_repository_handler(silent=True, create_handler=create_handler)
        
        # 5. 设置相关路径
        self.harmonyPath = self.basePath / "harmony"
        self.docPath = self.basePath / "doc"
        
        # 确保doc目录存在
        self.docPath.mkdir(exist_ok=True)
        
        # 鸿蒙适配相关配置
        self.harmonyConfig = {
            "react_native_version": "npm:@kds/react-native@0.62.2-ks.18-lixuan-harmony.10-alpha.1",
            "linear_gradient_version": "2.6.4",
            "auto_adapt_version": "0.0.1-alpha.7",
            "@kds/lottie-react-native": "4.0.37",
            "@kds/react-native-iphone-x-helper": "2.0.5-harmony.1",
            "resolutions": {
                "react-native": "npm:@kds/react-native@0.62.2-ks.18-lixuan-harmony.10-alpha.1",
                "@kds/react-native-gesture-handler": "1.7.17-2-oh-SNAPSHOT",
                "@kds/react-native-sound": "0.11.8",
                "@kds/react-native-blur": "3.6.7",
                "@kds/refresh-list": "4.0.8",
                "@kds/lottie-react-native": "4.0.37",
                "@kds/react-native-linear-gradient": "2.6.4",
                "@kds/react-native-tab-view": "^2.16.1-SNAPSHOT",
                "@kds/react-native-iphone-x-helper": "2.0.5-harmony.1"
            }
        }
        
        # 6. 初始化管理器（传递basePath参数）
        self.backupManager = BackupManager(str(self.basePath))
        self.gitManager = GitManager(str(self.basePath))
        self.harmonyDetector = HarmonyDetector()
        self.moduleManager = ModuleManager(str(self.basePath))
        
        # 7. 根据仓库结构设置扫描目录
        self.defaultScanDirs = self._get_scan_dirs()
        
        # 支持的域名列表
        self.supportedDomains = [
            'harmonyos-lbs.kwailocallife.com',
            'harmonyos.gifshow.com',
            'harmonyos-lbs.kwailbs.com'
        ]
    
    def _get_scan_dirs(self) -> list:
        """根据仓库结构获取默认扫描目录"""
        from util.RepositoryDetector import RepositoryStructure
        
        if self.repo_info.structure == RepositoryStructure.BUNDLES:
            # bundles结构：主要扫描bundles目录
            return ['bundles']
        elif self.repo_info.structure == RepositoryStructure.HYBRID:
            # 混合结构：扫描src和bundles目录
            return ['src', 'bundles']
        else:
            # 平铺结构：扫描src目录
            return ['src', 'bundles']  # 保持向后兼容
    
    def get_repository_handler(self) -> RepositoryHandler:
        """获取仓库处理器"""
        return self.repository_handler
    
    def get_repository_info(self) -> RepositoryInfo:
        """获取仓库信息"""
        return self.repo_info
    
    def print_config_summary(self):
        """打印配置摘要"""
        print(f"\n📋 配置摘要:")
        print(f"   工作目录: {self.basePath}")
        print(f"   仓库结构: {self.repo_info.structure.value}")
        print(f"   扫描目录: {', '.join(self.defaultScanDirs)}")
        print(f"   模块数量: {len(self.repo_info.modules)}")
