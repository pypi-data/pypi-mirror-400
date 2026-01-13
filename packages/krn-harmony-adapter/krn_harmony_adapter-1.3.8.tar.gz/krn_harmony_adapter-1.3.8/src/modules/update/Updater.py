#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新模块 - 提供包版本更新功能
"""

import subprocess
import sys
import re
from typing import Optional


class Updater:
    """更新器类"""
    
    def __init__(self):
        self.pip_cmd = self._get_pip_command()
    
    def _get_pip_command(self) -> str:
        """获取pip命令"""
        # 优先使用pip3，如果不存在则使用pip
        try:
            subprocess.run(['pip3', '--version'], capture_output=True, check=True)
            return 'pip3'
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                subprocess.run(['pip', '--version'], capture_output=True, check=True)
                return 'pip'
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise RuntimeError("❌ 错误: 未找到 pip 或 pip3 命令。请确保 Python 和 pip 已安装。")
    
    def get_current_version(self) -> Optional[str]:
        """获取当前安装的版本"""
        try:
            result = subprocess.run(
                [self.pip_cmd, 'show', 'krn-harmony-adapter'],
                capture_output=True,
                text=True,
                check=True
            )
            
            # 解析版本信息
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
            
            return None
        except subprocess.CalledProcessError:
            return None
    
    def get_latest_version(self) -> Optional[str]:
        """获取PyPI上的最新版本"""
        try:
            # 使用pip index versions命令获取版本信息
            result = subprocess.run(
                [self.pip_cmd, 'index', 'versions', 'krn-harmony-adapter'],
                capture_output=True,
                text=True,
                check=True
            )
            
            # 解析版本信息，查找LATEST标记
            for line in result.stdout.split('\n'):
                if 'LATEST:' in line:
                    return line.split('LATEST:', 1)[1].strip()
            
            # 如果没有找到LATEST标记，尝试解析第一行的版本信息
            lines = result.stdout.strip().split('\n')
            if lines and 'krn-harmony-adapter' in lines[0]:
                # 格式通常是: krn-harmony-adapter (1.1.0)
                import re
                match = re.search(r'\(([^)]+)\)', lines[0])
                if match:
                    return match.group(1)
            
            return None
        except subprocess.CalledProcessError:
            # 如果pip index命令不可用，尝试其他方法
            try:
                # 尝试使用pip search（某些版本可能不支持）
                result = subprocess.run(
                    [self.pip_cmd, 'search', 'krn-harmony-adapter'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # 解析搜索结果
                for line in result.stdout.split('\n'):
                    if 'krn-harmony-adapter' in line and '(' in line:
                        import re
                        match = re.search(r'\(([^)]+)\)', line)
                        if match:
                            return match.group(1)
                
                return None
            except subprocess.CalledProcessError:
                return None
    
    def update_package(self) -> bool:
        """更新包到最新版本"""
        print("🚀 正在从 PyPI 更新 krn-harmony-adapter 到最新正式版本...")
        print("--------------------------------------------------------")
        
        # 获取当前版本
        current_version = self.get_current_version()
        if current_version:
            print(f"ℹ️  当前安装版本: {current_version}")
        else:
            print("ℹ️  当前安装版本: 未安装")
        
        # 获取最新版本
        print("🔎 正在查询最新版本...")
        latest_version = self.get_latest_version()
        
        if latest_version:
            print(f"✅ 最新可用版本: {latest_version}")
            
            # 检查是否需要更新
            if current_version == latest_version and current_version is not None:
                print("🎉 当前已是最新版本，无需更新。")
                print("--------------------------------------------------------")
                return True
        else:
            print("⚠️  无法自动查询到最新版本（可能是pip版本较旧），将继续尝试更新。")
        
        # 执行更新
        print("")
        update_cmd = [
            self.pip_cmd, 'install', '--upgrade', '--no-cache-dir',
            '--index-url', 'https://pypi.org/simple',
            'krn-harmony-adapter', '--break-system-packages'
        ]
        print(f"▶️  执行命令: {' '.join(update_cmd)}")
        
        try:
            subprocess.run(update_cmd, check=True)
            
            # 获取更新后的版本
            print("")
            print("--------------------------------------------------------")
            new_version = self.get_current_version()
            if new_version:
                print(f"✅ 更新完成！当前版本为: {new_version}")
            else:
                print("✅ 更新完成！")
            print("您现在可以使用 'kha' 命令了。")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 更新失败: {e}")
            return False
    
    def check_version(self) -> None:
        """检查版本信息"""
        current_version = self.get_current_version()
        if current_version:
            print(f"当前版本: {current_version}")
        else:
            print("krn-harmony-adapter 未安装")
        
        latest_version = self.get_latest_version()
        if latest_version:
            print(f"最新版本: {latest_version}")
            
            if current_version and current_version != latest_version:
                print("💡 有新版本可用，运行 'kha update' 进行更新")
        else:
            print("无法获取最新版本信息")


def main():
    """主函数"""
    updater = Updater()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--check':
        updater.check_version()
    else:
        success = updater.update_package()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()