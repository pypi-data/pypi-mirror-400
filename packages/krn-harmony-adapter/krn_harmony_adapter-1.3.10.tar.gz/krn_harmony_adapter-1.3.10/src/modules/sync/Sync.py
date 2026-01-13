from config.Config import Config

from typing import List, Tuple

"""模块同步器"""
class Sync(Config):
    
    def __init__(self, base_path: str = "."):
        super().__init__(base_path)

    def syncMissingModules(self) -> bool:
        print("🔄 步骤1: 同步缺失模块")
        print("=" * 50)
        
        currentBranch = self.gitManager.getCurrentBranch()
        print(f"📍 当前分支: {currentBranch}")
        
        # 查找缺失的模块
        missing_modules = self._findMissingModules()
        
        if not missing_modules:
            print("✅ 所有模块都已同步，无需操作")
            return True
        
        print(f"📦 发现 {len(missing_modules)} 个需要同步的模块:")
        for module in missing_modules:
            print(f"  - {module}")
        
        # 询问用户确认
        confirm = input(f"\n是否同步这 {len(missing_modules)} 个模块到当前分支 '{currentBranch}'? (Y/n): ")
        if confirm.lower() == 'n':
            print("❌ 用户取消同步操作")
            return False
        
        # 执行同步
        success, synced_modules = self._sync(missing_modules)
        
        if success:
            print(f"✅ 成功同步 {len(synced_modules)} 个模块")
        else:
            print(f"⚠️  部分模块同步失败，成功同步 {len(synced_modules)}/{len(missing_modules)} 个模块")
        
        return success
    
    def _findMissingModules(self) -> List[str]:
        """查找目标分支有但当前分支没有的模块(支持bundles多模块结构)"""
        original_branch = self.gitManager.getCurrentBranch()
        latest_dev_branch = self.gitManager.getLatestDevBranch()

        if not latest_dev_branch or latest_dev_branch == "master":
            print("⚠️ 未找到最新的dev分支，将使用 master 分支作为同步源。")
            source_branch = "master"
        else:
            source_branch = latest_dev_branch

        print(f"🔄 将从分支 '{source_branch}' 获取模块列表...")

        # 1. 获取当前分支的模块列表(使用仓库处理器,支持bundles结构)
        handler = self.get_repository_handler()
        current_modules = set()
        for module in handler.discover_modules():
            current_modules.add(module.name)
        
        # 2. 获取目标分支的模块列表
        target_modules = self._getModulesFromBranch(source_branch)
        
        # 找出缺失的模块
        missing_modules = target_modules - current_modules
        
        if missing_modules:
            print(f"✅ 在 '{source_branch}' 分支上发现 {len(missing_modules)} 个当前分支缺失的模块。")
        else:
            print(f"✅ 当前分支 '{original_branch}' 与 '{source_branch}' 的模块列表已同步。")
            
        return sorted(list(missing_modules))
    
    def _getModulesFromBranch(self, branch_name: str) -> set:
        """从指定分支获取所有模块(支持bundles多模块结构)"""
        import os
        import json
        
        modules = set()
        handler = self.get_repository_handler()
        
        # 判断仓库结构类型
        if handler.structure_type == "bundles":
            # bundles结构: 需要扫描bundles目录下的子目录
            bundles_path = "bundles"
            
            # 获取bundles目录下的所有子目录
            command = f"git ls-tree -d --name-only {branch_name}:{bundles_path}"
            success, output = self.gitManager.runCommand(command)
            
            if success:
                for line in output.strip().split('\n'):
                    if line.strip():
                        # 提取模块名(去掉bundles/前缀)
                        module_name = line.strip().replace(f"{bundles_path}/", "")
                        if module_name and not module_name.startswith('.'):
                            # 检查是否有package.json
                            pkg_path = f"{bundles_path}/{module_name}/package.json"
                            pkg_content = self.gitManager.getFileContentFromBranch(branch_name, pkg_path)
                            if pkg_content:
                                modules.add(module_name)
        else:
            # 平铺结构: 直接扫描根目录
            target_modules_raw = self.gitManager.listModulesInBranch(branch_name)
            for module in target_modules_raw:
                # 过滤掉非业务模块目录
                if module and not module.startswith('.') and module not in {'doc', 'rule', 'script', 'scriptForHarmony', 'bundles'}:
                    # 检查是否有package.json
                    pkg_path = f"{module}/package.json"
                    pkg_content = self.gitManager.getFileContentFromBranch(branch_name, pkg_path)
                    if pkg_content:
                        modules.add(module)
        
        return modules
    
    def _sync(self, missingModules: List[str]) -> Tuple[bool, List[str]]:
        """同步缺失的模块"""
        if not missingModules:
            return True, []
        
        syncedModules = []
        sourceBranch = self.gitManager.getLatestDevBranch()
        
        for moduleName in missingModules:
            print(f"📦 同步模块: {moduleName}")
            
            success, output = self.gitManager.checkoutModuleFromBranch(sourceBranch, moduleName)
            if success:
                syncedModules.append(moduleName)
                print(f"✅ 成功同步模块: {moduleName}")
            else:
                print(f"❌ 同步模块失败: {moduleName} - {output}")
        
        # 提交同步的模块
        if syncedModules:
            self.gitManager.addFile(".")
            commitMessage = f"同步模块: {', '.join(syncedModules)}"
            success, output = self.gitManager.commitChanges(commitMessage)
            if success:
                print(f"✅ 提交同步结果: {len(syncedModules)}个模块")
            else:
                print(f"⚠️ 提交失败: {output}")
        
        return len(syncedModules) == len(missingModules), syncedModules
    
    def syncSpecificModule(self, moduleName: str, force: bool = True, skip_confirm: bool = False) -> bool:
        """同步指定模块的代码(支持平铺和bundles结构)
        
        Args:
            moduleName: 模块名称
            force: 是否强制同步(即使模块已存在也会覆盖)
            skip_confirm: 是否跳过用户确认(命令行模式下使用)
        
        Returns:
            bool: 同步是否成功
        """
        print(f"🔄 同步指定模块: {moduleName}")
        print("=" * 50)
        
        currentBranch = self.gitManager.getCurrentBranch()
        sourceBranch = self.gitManager.getLatestDevBranch()
        
        print(f"📍 当前分支: {currentBranch}")
        print(f"📍 源分支: {sourceBranch}")
        
        # 获取仓库处理器
        handler = self.get_repository_handler()
        
        # 检查模块在源分支是否存在
        module_exists_in_source = self._checkModuleExistsInBranch(moduleName, sourceBranch)
        
        if not module_exists_in_source:
            print(f"❌ 模块 '{moduleName}' 在源分支 '{sourceBranch}' 中不存在")
            return False
        
        # 检查模块在当前分支是否存在
        module_path = handler.get_module_path(moduleName)
        module_exists_locally = module_path and module_path.exists()
        
        if module_exists_locally and not force:
            print(f"⚠️  模块 '{moduleName}' 已存在，使用 --force 参数强制同步")
            return False
        
        # 询问用户确认(除非跳过确认)
        if not skip_confirm:
            if module_exists_locally:
                confirm = input(f"\n⚠️  模块 '{moduleName}' 已存在，是否强制覆盖? (Y/n): ")
            else:
                confirm = input(f"\n是否从 '{sourceBranch}' 同步模块 '{moduleName}'? (Y/n): ")
            
            if confirm.lower() == 'n':
                print("❌ 用户取消同步操作")
                return False
        
        # 构建模块路径(根据仓库结构)
        if handler.structure_type == "bundles":
            module_git_path = f"bundles/{moduleName}"
        else:
            module_git_path = moduleName
        
        # 执行同步
        print(f"📦 正在同步模块: {moduleName}")
        success, output = self.gitManager.checkoutModuleFromBranch(sourceBranch, module_git_path)
        
        if success:
            print(f"✅ 成功同步模块: {moduleName}")
            
            # 提交更改
            self.gitManager.addFile(".")
            action = "覆盖" if module_exists_locally else "同步"
            commitMessage = f"{action}模块: {moduleName} (from {sourceBranch})"
            commit_success, commit_output = self.gitManager.commitChanges(commitMessage)
            
            if commit_success:
                print(f"✅ 提交同步结果")
            else:
                print(f"⚠️  提交失败: {commit_output}")
            
            return True
        else:
            print(f"❌ 同步模块失败: {output}")
            return False
    
    def _checkModuleExistsInBranch(self, moduleName: str, branch_name: str) -> bool:
        """检查模块在指定分支是否存在"""
        handler = self.get_repository_handler()
        
        # 构建package.json路径
        if handler.structure_type == "bundles":
            pkg_path = f"bundles/{moduleName}/package.json"
        else:
            pkg_path = f"{moduleName}/package.json"
        
        # 尝试获取package.json内容
        pkg_content = self.gitManager.getFileContentFromBranch(branch_name, pkg_path)
        return pkg_content is not None
