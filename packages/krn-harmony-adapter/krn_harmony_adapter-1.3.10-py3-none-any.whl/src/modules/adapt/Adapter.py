import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
import operator
from typing import Any, Dict, List
from util.RepositoryHandler import BundlesRepositoryHandler
from util.SingleRepositoryHandler import SingleRepositoryHandler

try:
    from packaging import version
except ImportError:
    # 如果packaging不可用，提供一个简单的版本比较函数
    class SimpleVersion:
        def __init__(self, version_str):
            self.version_str = version_str
            self.parts = [int(x) for x in version_str.split('.') if x.isdigit()]
        
        def __lt__(self, other):
            if isinstance(other, str):
                other = SimpleVersion(other)
            return self.parts < other.parts
        
        def __le__(self, other):
            if isinstance(other, str):
                other = SimpleVersion(other)
            return self.parts <= other.parts
        
        def __gt__(self, other):
            if isinstance(other, str):
                other = SimpleVersion(other)
            return self.parts > other.parts
        
        def __ge__(self, other):
            if isinstance(other, str):
                other = SimpleVersion(other)
            return self.parts >= other.parts
        
        def __eq__(self, other):
            if isinstance(other, str):
                other = SimpleVersion(other)
            return self.parts == other.parts
    
    def version(version_str):
        return SimpleVersion(version_str)
from importlib import resources as res

from config.Config import Config

def _to_js_literal_str(obj: any, indent_level: int = 0, base_indent: str = "    ") -> str:
    """
    将Python对象递归转换为格式化的JavaScript对象字面量字符串。
    - 字典的键如果符合JS标识符规范，则不加引号。
    - 字符串使用单引号。
    """
    indent = base_indent * indent_level

    if isinstance(obj, str):
        return f"'{obj}'"
    if isinstance(obj, (int, float)):
        return str(obj)
    if isinstance(obj, bool):
        return 'true' if obj else 'false'
    if obj is None:
        return 'null'

    if isinstance(obj, list):
        if not obj:
            return "[]"
        
        # 对于复杂的列表（如插件列表），总是换行
        items = []
        for item in obj:
            # 插件列表的每个元素都需要从下一级缩进开始
            item_str = _to_js_literal_str(item, indent_level + 1, base_indent)
            items.append(f"{indent}{base_indent}{item_str}")
        items_str = ',\n'.join(items)
        return f"[\n{items_str}{',' if items else ''}\n{indent}]"

    if isinstance(obj, dict):
        if not obj:
            return "{}"
        
        items = []
        for key, value in obj.items():
            # 检查key是否是有效的JS标识符
            if re.match(r'^[a-zA-Z_$][a-zA-Z0-9_$]*$', key):
                js_key = key
            else:
                js_key = f"'{key}'"
            
            # 如果值是多行（如对象或数组），则在新行开始
            value_str = _to_js_literal_str(value, indent_level + 1, base_indent)
            if '\n' in value_str:
                items.append(f"{indent}{base_indent}{js_key}: {value_str}")
            else:
                items.append(f"{indent}{base_indent}{js_key}: {value_str}")
        items_str = ',\n'.join(items)
        return f"{{\n{items_str}{',' if items else ''}\n{indent}}}"

    # 对于不支持的类型，返回其字符串表示形式
    return str(obj)

class Adapter(Config):
    # 依赖映射表 - 将原生RN依赖映射到@kds版本
    DEPENDENCY_MAPPING = {
        'react-native-linear-gradient': '@kds/react-native-linear-gradient',
        'react-native-gesture-handler': '@kds/react-native-gesture-handler',
        'react-native-tab-view': '@kds/react-native-tab-view',
        'react-native-blur': '@kds/react-native-blur',
        'lottie-react-native': '@kds/lottie-react-native',
        'react-native-sound': '@kds/react-native-sound',
    }

    agreeMaster: bool = False

    def __init__(self, base_path: str = "."):
        super().__init__(base_path)

    def adaptBatchModules(self, moduleType: str = "all") -> bool:
        """批量适配模块"""
        print(f"🔧 批量适配模块 - {moduleType}")
        print("=" * 50)
        
        moduleManager = self.moduleManager
        categorized = moduleManager.categorizeModulesByAdaptation(moduleManager.discoverModules())
        not_adapted = categorized['not_adapted']
        
        if not not_adapted:
            print("✅ 所有模块都已适配")
            return True
        
        # 根据类型筛选模块
        modules_to_adapt = []
        if moduleType == "live":
            modules_to_adapt = [m for m in not_adapted if 'live' in m['moduleName'].lower()]
            print(f"📦 准备适配 {len(modules_to_adapt)} 个直播Bundle")
        elif moduleType == "non_live":
            modules_to_adapt = [m for m in not_adapted if 'live' not in m['moduleName'].lower()]
            print(f"📦 准备适配 {len(modules_to_adapt)} 个非直播Bundle")
        else:
            modules_to_adapt = not_adapted
            print(f"📦 准备适配 {len(modules_to_adapt)} 个模块")
        
        if not modules_to_adapt:
            print(f"✅ 没有需要适配的{moduleType}模块")
            return True
        
        # 显示模块列表
        for module in modules_to_adapt:
            print(f"  - {module['moduleName']}")
        
        # 询问用户确认
        confirm = input(f"\n是否开始批量适配这 {len(modules_to_adapt)} 个模块? (Y/n): ")
        if confirm.lower() == 'n':
            print("❌ 用户取消批量适配")
            return False
        
        # 执行批量适配
        success_count = 0
        for module in modules_to_adapt:
            print(f"\n🔧 适配模块: {module['moduleName']}")
            if self.adaptSingleModule(module['moduleName']):
                success_count += 1
        
        print(f"\n✅ 批量适配完成: {success_count}/{len(modules_to_adapt)} 个模块适配成功")
        return success_count == len(modules_to_adapt)

    def adaptSingleModule(self, moduleName: str) -> bool:
        # 使用仓库处理器获取模块路径
        handler = self.get_repository_handler()
        modulePath = handler.get_module_path(moduleName)
        
        if not modulePath or not modulePath.is_dir():
            print(f"❌ 模块目录不存在: {moduleName}")
            return False

        status = self.moduleManager.checkModuleAdaptationStatus(moduleName)
        
        # 1. 对于已适配的模块,先备份harmony代码(在更新代码之前!)
        backupInfo = None
        if status['is_adapted']:
            print(f"📍 模块 {moduleName} 已适配，正在备份harmony相关内容...")
            # 从harmony_master分支备份harmony内容
            currentBranch = self.gitManager.getCurrentBranch()
            backupInfo = self.backupManager.backup_harmony_content(str(modulePath), currentBranch)
        
        # 2. 从最新dev分支copy代码覆盖
        update_success = self.updateModuleCode(moduleName)
        if not update_success:
            print(f"⚠️  代码更新失败，但继续执行适配流程...")
        
        # 3. 对于已适配的模块,恢复harmony代码
        if status['is_adapted'] and backupInfo:
            print(f"📍 正在恢复harmony相关内容...")
            # 恢复harmony相关内容
            success = self.backupManager.restore_harmony_content(str(modulePath), backupInfo)
            if not success:
                print("⚠️  部分harmony内容恢复失败")
            
            # 清理备份目录
            self.backupManager.cleanup_backup(str(modulePath))
        
        # 4. 对于未适配的模块，执行适配流程
        if not self.startAdapt(moduleName):
            return False
        
        # 5. 检查node_modules中的间接依赖
        self._checkNodeModulesDependencies(modulePath)
        
        print(f"✅ 模块 {moduleName} 适配完成")
        return True
    
    def adaptSingleProject(self) -> bool:
        """适配单一项目结构"""
        print("🔧 开始适配单一项目到鸿蒙...")
        print("=" * 50)

        handler = self.get_repository_handler()
        if not isinstance(handler, SingleRepositoryHandler):
            print("❌ 当前项目不是单一项目结构")
            return False
        
        project_name = handler.get_project_name()
        project_path = handler.get_module_path()
        
        print(f"📦 项目名称: {project_name}")
        print(f"📁 项目路径: {project_path}")
        
        try:
            # 执行适配流程
            success = self._executeAdaptationSteps(
                project_path, 
                project_name,
                "根目录package.json (单一项目结构)", 
                check_submodules=False,
                check_node_modules=True
            )
            
            if success:
                print(f"✅ 项目 {project_name} 鸿蒙适配完成")
            else:
                print(f"❌ 项目 {project_name} 适配失败")
            
            return success
            
        except Exception as e:
            print(f"❌ 适配项目 {project_name} 失败: {e}")
            return False
    
    def get_repository_handler(self):
        """获取仓库处理器"""
        # 从Config类继承的repository_handler
        return self.repository_handler

        
    def startAdapt(self, moduleName: str) -> bool:
        print(f"🔧 开始适配模块 {moduleName} 到鸿蒙...")
        
        # 使用仓库处理器获取模块路径
        handler = self.get_repository_handler()
        modulePath = handler.get_module_path(moduleName)
        
        if not modulePath or not modulePath.exists():
            print(f"❌ 模块 {moduleName} 不存在")
            return False
        
        try:
            # 执行适配流程
            success = self._executeAdaptationSteps(
                modulePath,
                moduleName,
                f"{modulePath.name}/package.json",
                check_submodules=True,
                check_node_modules=False
            )
            
            if success:
                print(f"✅ {moduleName} 鸿蒙适配完成")
            else:
                print(f"❌ {moduleName} 适配失败")
            
            return success
            
        except Exception as e:
            print(f"❌ 适配模块 {moduleName} 失败: {e}")
            return False
    
    def _executeAdaptationSteps(self, target_path: Path, target_name: str, package_description: str, 
                               check_submodules: bool = False, check_node_modules: bool = False) -> bool:
        """执行适配的核心步骤"""
        try:
            # 1. 修改package.json
            self._updatePackageJson(target_path, package_description, check_submodules=check_submodules)
            
            # 2. 修改babel.config.js
            self._updateBabelConfig(target_path)
            
            # 3. 创建harmony目录和文件
            self._createHarmonyDirectory(target_path)
            
            # 4. 修复代码中的charset问题
            self._fixCharsetIssues(target_path)
            
            # 5. 检查node_modules中的间接依赖（仅单一项目需要）
            if check_node_modules:
                self._checkNodeModulesDependencies(target_path)
            
            return True
            
        except Exception as e:
            print(f"❌ 执行适配步骤失败: {e}")
            return False
    
    def _is_harmony_dependency(self, dep_name: str) -> bool:
        """判断是否是harmony相关依赖"""
        harmony_keywords = [
            '@kds/', 'harmony', '@locallife/auto-adapt-harmony',
            'react-native-linear-gradient', 'react-n-gesture-handler',
            'react-native-tab-view', 'react-native-blur', 'lottie-react-native',
            'react-native-sound'
        ]
        
        return any(keyword in dep_name for keyword in harmony_keywords)
    
    def _updatePackageJsonByStructure(self, modulePath: Path):
        """根据仓库结构更新package.json文件"""
        # 判断仓库结构类型
        handler = self.get_repository_handler()
        from util.RepositoryHandler import BundlesRepositoryHandler
        from util.SingleRepositoryHandler import SingleRepositoryHandler
        
        if isinstance(handler, BundlesRepositoryHandler):
            # bundles结构：更新根目录的package.json
            self._updateRootPackageJsonForBundles(modulePath)
        elif isinstance(handler, SingleRepositoryHandler):
            # 单一项目结构：更新根目录的package.json
            self._updatePackageJson(modulePath, "根目录package.json (单一项目结构)", check_submodules=False)
        else:
            # 平铺结构：更新模块自己的package.json
            self._updatePackageJson(modulePath, f"{modulePath.name}/package.json", check_submodules=True)
            
    
    def _updateRootPackageJsonForBundles(self, modulePath: Path):
        """bundles结构：更新根目录的package.json"""
        handler = self.get_repository_handler()
        root_package_path = handler.get_root_package_json_path()
        
        if not root_package_path or not root_package_path.exists():
            print(f"  ⚠️  根目录package.json不存在，跳过更新")
            return
        
        with open(root_package_path, 'r', encoding='utf-8') as f:
            packageData = json.load(f)
        
        # 更新dependencies
        if 'dependencies' not in packageData:
            packageData['dependencies'] = {}
        
        # 更新react-native版本（bundles结构的核心依赖）
        packageData['dependencies']['react-native'] = self.harmonyConfig['react_native_version']

        # 保存文件
        with open(root_package_path, 'w', encoding='utf-8') as f:
            json.dump(packageData, f, indent=4, ensure_ascii=False)
        
        print(f"  ✅ 已更新根目录package.json (bundles结构)")
    
    def _updatePackageJson(self, modulePath: Path, description: str, check_submodules: bool = False):
        """通用的package.json更新方法"""
        packageJsonPath = modulePath / "package.json"
        
        if not packageJsonPath.exists():
            print(f"  ⚠️  package.json不存在: {packageJsonPath}")
            return
        
        with open(packageJsonPath, 'r', encoding='utf-8') as f:
            packageData = json.load(f)
        
        # 更新dependencies
        if 'dependencies' not in packageData:
            packageData['dependencies'] = {}
        
        # 更新react-native版本
        packageData['dependencies']['react-native'] = self.harmonyConfig['react_native_version']
        
        # 添加@kds/react-native-linear-gradient
        packageData['dependencies']['@kds/react-native-linear-gradient'] = self.harmonyConfig['linear_gradient_version']
        
        # 添加auto-adapt-harmony依赖
        packageData['dependencies']['@locallife/auto-adapt-harmony'] = self.harmonyConfig['auto_adapt_version']

        # 更新@kds/lottie-react-native
        packageData['dependencies']['@kds/lottie-react-native'] = self.harmonyConfig['@kds/lottie-react-native']
        
        # 更新devDependencies中的@krn/cli
        if 'devDependencies' not in packageData:
            packageData['devDependencies'] = {}
        
        # 更新resolutions
        if 'resolutions' not in packageData:
            packageData['resolutions'] = {}
        packageData['resolutions'].update(self.harmonyConfig['resolutions'])
        
        # 检查子模块依赖并添加到根目录（仅适用于平铺结构）
        if check_submodules:
            self._addSubmoduleDependencies(modulePath, packageData)
        
        # 约束检查与修复
        self._fixReactReduxVersion(packageData)
        self._fixReduxToolkitVersion(packageData)
        self._fixLocalLifePageVersion(packageData)
        self._addBlurDependencyIfNeeded(packageData)
        
        # 保存文件
        with open(packageJsonPath, 'w', encoding='utf-8') as f:
            json.dump(packageData, f, indent=4, ensure_ascii=False)
        
        print(f"  ✅ 已更新 {description}")
    
    def _addSubmoduleDependencies(self, modulePath: Path, packageData: dict):
        """检查子模块依赖并添加到根目录package.json"""
        
        # 扫描bundles目录下的所有子模块
        bundles_path = modulePath / "bundles"
        if not bundles_path.exists():
            print(f"  ℹ️  未找到bundles目录，跳过子模块依赖检查")
            return
        
        found_dependencies = set()
        
        # 遍历bundles目录下的所有子目录
        for submodule_path in bundles_path.iterdir():
            if submodule_path.is_dir():
                package_json_path = submodule_path / "package.json"
                if package_json_path.exists():
                    try:
                        with open(package_json_path, 'r', encoding='utf-8') as f:
                            submodule_package = json.load(f)
                        
                        # 检查dependencies和devDependencies
                        for dep_type in ['dependencies', 'devDependencies']:
                            if dep_type in submodule_package:
                                for dep_name in submodule_package[dep_type]:
                                    if dep_name in self.DEPENDENCY_MAPPING:
                                        found_dependencies.add(dep_name)
                                        print(f"  📦 在子模块 {submodule_path.name} 中发现依赖: {dep_name}")
                    
                    except Exception as e:
                        print(f"  ⚠️  读取子模块 {submodule_path.name}/package.json 失败: {e}")
        
        # 将找到的依赖添加到根目录package.json
        if found_dependencies:
            print(f"  🔧 正在添加 {len(found_dependencies)} 个子模块依赖到根目录...")
            
            if 'dependencies' not in packageData:
                packageData['dependencies'] = {}
            
            for original_dep in found_dependencies:
                kds_dep = self.DEPENDENCY_MAPPING[original_dep]
                # 从配置中获取版本号
                if kds_dep in self.harmonyConfig['resolutions']:
                    version = self.harmonyConfig['resolutions'][kds_dep]
                    packageData['dependencies'][kds_dep] = version
                    print(f"    ✅ 添加依赖: {kds_dep}@{version}")
                else:
                    print(f"    ⚠️  未找到 {kds_dep} 的版本配置")
        else:
            print(f"  ℹ️  未在子模块中发现需要映射的依赖")
    
    def _checkNodeModulesDependencies(self, modulePath: Path):
        """检查node_modules中的间接依赖并添加到根目录package.json"""
        print(f"  🔍 检查node_modules中的间接依赖...")
        
        node_modules_path = modulePath / "node_modules"
        if not node_modules_path.exists():
            print(f"  ℹ️  node_modules目录不存在，跳过间接依赖检查")
            return
        
        # 读取当前模块的package.json
        package_json_path = modulePath / "package.json"
        if not package_json_path.exists():
            print(f"  ⚠️  模块package.json不存在，跳过间接依赖检查")
            return
        
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                current_package = json.load(f)
        except Exception as e:
            print(f"  ⚠️  读取模块package.json失败: {e}")
            return
        
        if 'dependencies' not in current_package:
            current_package['dependencies'] = {}
        
        found_indirect_dependencies = set()
        
        # 扫描node_modules中的所有依赖
        for dep_dir in node_modules_path.iterdir():
            if dep_dir.is_dir() and not dep_dir.name.startswith('.'):
                # 处理普通依赖
                self._scanDependencyPackage(dep_dir, self.DEPENDENCY_MAPPING, found_indirect_dependencies)
                
                # 处理scoped依赖 (如@types/xxx)
                if dep_dir.name.startswith('@'):
                    for scoped_dep in dep_dir.iterdir():
                        if scoped_dep.is_dir():
                            self._scanDependencyPackage(scoped_dep, self.DEPENDENCY_MAPPING, found_indirect_dependencies)
        
        # 检查并添加缺失的依赖
        added_dependencies = []
        for original_dep in found_indirect_dependencies:
            kds_dep = self.DEPENDENCY_MAPPING[original_dep]
            
            # 检查是否已经存在
            if kds_dep not in current_package['dependencies']:
                # 从配置中获取版本号
                if kds_dep in self.harmonyConfig['resolutions']:
                    version = self.harmonyConfig['resolutions'][kds_dep]
                    current_package['dependencies'][kds_dep] = version
                    added_dependencies.append(f"{kds_dep}@{version}")
                    print(f"    ✅ 添加间接依赖: {kds_dep}@{version}")
                else:
                    print(f"    ⚠️  未找到 {kds_dep} 的版本配置")
            else:
                print(f"    ℹ️  依赖 {kds_dep} 已存在，跳过")
        
        # 如果有新增依赖，更新package.json
        if added_dependencies:
            try:
                with open(package_json_path, 'w', encoding='utf-8') as f:
                    json.dump(current_package, f, indent=4, ensure_ascii=False)
                print(f"  ✅ 已添加 {len(added_dependencies)} 个间接依赖到package.json")
            except Exception as e:
                print(f"  ⚠️  更新package.json失败: {e}")
        else:
            print(f"  ℹ️  未发现需要添加的间接依赖")
    
    def _scanDependencyPackage(self, dep_path: Path, dependency_mapping: dict, found_dependencies: set):
        """扫描单个依赖包的package.json"""
        package_json_path = dep_path / "package.json"
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    dep_package = json.load(f)
                
                # 检查dependencies和devDependencies
                for dep_type in ['dependencies', 'devDependencies']:
                    if dep_type in dep_package:
                        for dep_name in dep_package[dep_type]:
                            if dep_name in dependency_mapping:
                                found_dependencies.add(dep_name)
                                print(f"    📦 在 {dep_path.name} 中发现间接依赖: {dep_name}")
            
            except Exception as e:
                # 静默处理读取失败的情况，避免输出过多错误信息
                pass
    
    def _updateBabelConfig(self, modulePath: Path):
        """更新babel.config.js文件"""
        handler = self.get_repository_handler()
        from util.RepositoryHandler import FlatRepositoryHandler
        from util.SingleRepositoryHandler import SingleRepositoryHandler

        isFlatPresository = isinstance(handler, FlatRepositoryHandler)
        isSingleProject = isinstance(handler, SingleRepositoryHandler)

        if isFlatPresository or isSingleProject:
            # 平铺结构或单一项目结构：babel.config.js在模块/项目根目录
            babelConfigPath = modulePath / "babel.config.js"
        else:
            # bundles结构：babel.config.js在根目录
            root_package_path = handler.get_root_package_json_path()
            babelConfigPath = root_package_path.parent / "babel.config.js"
        
        if not babelConfigPath.exists():
            # 创建基础的babel配置
            babel_content = """module.exports = {
    presets: ['module:metro-react-native-babel-preset'],
    plugins: []
};"""
            with open(babelConfigPath, 'w', encoding='utf-8') as f:
                f.write(babel_content)
        
        with open(babelConfigPath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 定义需要添加的 alias 配置
        harmonyAliases = {
            'react-native-linear-gradient': '@kds/react-native-linear-gradient',
            'react-native-gesture-handler': '@kds/react-native-gesture-handler',
            'react-native-tab-view': '@kds/react-native-tab-view',
            'react-native-blur': '@kds/react-native-blur',
            '@react-native-community/blur': '@kds/react-native-blur',
            'lottie-react-native': '@kds/lottie-react-native',
            'react-native-sound': '@kds/react-native-sound',
        }
        
        # 检查是否需要jumpUrl相关配置
        needs_jump_url = self._needsJumpUrlFile(modulePath)
        
        # 将插件定义为Python数据结构，以便自动格式化
        otherHarmonyPlugins_data = [
            [
                '@locallife/auto-adapt-harmony/src/plugin/bridge-replace-plugin.js',
                {
                    "notSupportBridges": {
                        "invoke": [
                            'getShowingPendants',
                            'publishRubas',
                            'setRubasDimension',
                            'setRubasDimensionBatch',
                            'subscribe',
                            'unSubscribe',
                            'sendEvent',
                        ],
                    },
                },
            ],
            ['@locallife/auto-adapt-harmony/src/plugin/error-delete-plugin.js'],
        ]
        
        # 只有在需要jumpUrl时才添加file-replace-plugin
        if needs_jump_url:
            otherHarmonyPlugins_data.append([
                '@locallife/auto-adapt-harmony/src/plugin/file-replace-plugin.js',
                {
                    "replacements": {
                        '@locallife/utils': {
                            "jumpUrl": '/harmony/jumpUrl.ts',
                        },
                    },
                },
            ])
        
        # 添加transform-kwaimage-children插件
        otherHarmonyPlugins_data.append([
            '@locallife/auto-adapt-harmony/src/plugin/transform-kwaimage-children.js'
        ])

        # 准备 module-resolver 插件的字符串
        moduleResolverPlugin_data = [
            'module-resolver',
            {
                'alias': harmonyAliases
            }
        ]

        # 查找并尝试更新现有的 module-resolver
        moduleResolverPattern = r"('module-resolver'[\s\S]*?alias:\s*\{)([\s\S]*?)(\})"
        moduleResolverMatch = re.search(moduleResolverPattern, content)

        new_content = content
        plugins_to_add = []

        if moduleResolverMatch:
            # --- 步骤 1: 合并 Alias ---
            print(f"  ℹ️  发现现有的 module-resolver 配置，正在合并 alias...")
            existing_alias_block = moduleResolverMatch.group(2)
            
            # 1. 提取现有的 alias 条目
            existing_alias_lines = [line.strip() for line in existing_alias_block.strip().split('\n') if line.strip()]
            
            # 2. 准备要添加的新 alias
            new_alias_to_add = {}
            for key, value in harmonyAliases.items():
                # 检查 key 是否已存在
                if not any(f"'{key}':" in line or f'"{key}":' in line for line in existing_alias_lines):
                    new_alias_to_add[key] = f"                    '{key}': '{value}'"
            
            if new_alias_to_add:
                separator = ""
                if existing_alias_block.strip() and not existing_alias_block.strip().endswith(','):
                    separator = ",\n"
                aliases_to_insert = ",\n".join(new_alias_to_add.values())
                updated_alias_block = existing_alias_block + separator + aliases_to_insert
                new_content = new_content.replace(
                    moduleResolverMatch.group(0),
                    f"{moduleResolverMatch.group(1)}{updated_alias_block}{moduleResolverMatch.group(3)}"
                )

        else:
            # 如果不存在 module-resolver，则需要添加它和所有其他插件
            # 注意：这里只准备 module-resolver，其他插件在下一步统一处理
            plugins_to_add.append(moduleResolverPlugin_data)

        # --- 步骤 2: 注入其他 Harmony 插件 (如果需要) ---
        if '@locallife/auto-adapt-harmony' not in new_content:
            # 将 otherHarmonyPlugins_data 插入到待添加列表的最前面
            plugins_to_add = otherHarmonyPlugins_data + plugins_to_add

        if plugins_to_add:
            # 查找所有plugins位置，选择第一个（顶级的）
            plugins_matches = list(re.finditer(r'plugins:\s*\[', new_content))
            
            if plugins_matches:
                # 找到第一个plugins（顶级的）
                first_plugins_match = plugins_matches[0]
                plugins_start = first_plugins_match.start()
                
                # 从这个位置开始查找完整的plugins数组
                remaining_content = new_content[plugins_start:]
                full_plugins_match = re.search(r'plugins:\s*\[([\s\S]*?)\]', remaining_content, re.DOTALL)
                
                if full_plugins_match:
                    existing_plugins = full_plugins_match.group(1).strip()
                    
                    # 将新插件转换为字符串格式
                    new_plugins_str = ',\n        '.join([_to_js_literal_str(plugin) for plugin in plugins_to_add])
                    
                    # 构建新的plugins数组内容
                    if existing_plugins:
                        # 保持现有插件的原始格式，在前面添加新插件
                        new_array_content = f"\n        {new_plugins_str},\n{existing_plugins}"
                    else:
                        new_array_content = f"\n        {new_plugins_str}\n    "
                    
                    # 替换最后一个plugins数组
                    old_plugins_text = full_plugins_match.group(0)
                    new_plugins_text = f"plugins: [{new_array_content}]"
                    
                    # 在原始内容中替换
                    new_content = new_content[:plugins_start] + new_content[plugins_start:].replace(old_plugins_text, new_plugins_text, 1)
                    
                    plugin_count_msg = f"{len(plugins_to_add)} 个 harmony 插件"
                    if not needs_jump_url:
                        plugin_count_msg += " (跳过jumpUrl相关配置)"
                    print(f"  ✅ 已将 {plugin_count_msg} 添加到 babel.config.js")
                else:
                    print("  ⚠️  找到plugins行但格式异常")
            else:
                # 没有找到plugins数组，在适当位置添加
                new_plugins_str = ',\n        '.join([_to_js_literal_str(plugin) for plugin in plugins_to_add])
                
                if "module.exports = {" in new_content:
                    # 在module.exports的最后添加plugins数组
                    new_content = re.sub(
                        r"(\s*)(};?\s*)$",
                        f"\\1    plugins: [\n        {new_plugins_str}\n    ],\n\\2",
                        new_content
                    )
                else:
                    # 如果没有找到module.exports，在文件末尾添加
                    new_content += f"\n\nplugins: [\n    {new_plugins_str}\n];\n"
                
                plugin_count_msg = f"{len(plugins_to_add)} 个 harmony 插件"
                if not needs_jump_url:
                    plugin_count_msg += " (跳过jumpUrl相关配置)"
                print(f"  ✅ 已创建 plugins 数组并添加 {plugin_count_msg}")

        if new_content == content:
            if isFlatPresository:
                print(f"  ℹ️  {modulePath.name}/babel.config.js 无需修改。")
            elif isSingleProject:
                print(f"  ℹ️  根目录babel.config.js 无需修改。")
            else:
                print(f"  ℹ️  根目录babel.config.js 无需修改。")

        with open(babelConfigPath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        if new_content != content:
            if isFlatPresository:
                print(f"  ✅ 已成功更新 {modulePath.name}/babel.config.js")
            elif isSingleProject:
                print(f"  ✅ 已成功更新根目录babel.config.js (单一项目结构)")
            else:
                print(f"  ✅ 已成功更新根目录babel.config.js (bundles结构)")

    def _createHarmonyDirectory(self, modulePath: Path):
        """创建harmony目录和文件"""
        harmonyDir = modulePath / "harmony"
        harmonyDir.mkdir(exist_ok=True)
        
        # 检查是否需要创建jumpUrl.ts文件
        if self._needsJumpUrlFile(modulePath):
            # 复制jumpUrl.ts文件
            try:
                # 从包资源中获取文件路径。这是最健壮的方式。
                # 'src.resources' 是包含 jumpUrl.ts 的 Python 包
                with res.as_file(res.files('src.resources') / 'jumpUrl.ts') as p:
                    print(f"  ✅ 已从包资源中获取jumpUrl.ts文件, {p}")
                    sourceJumpUrl = p
                    targetJumpUrl = harmonyDir / "jumpUrl.ts"
                    shutil.copy2(sourceJumpUrl, targetJumpUrl)
                    print(f"  ✅ 已创建 {modulePath.name}/harmony/jumpUrl.ts")
            except FileNotFoundError:
                # 只有在打包配置错误或文件确实丢失时才会触发
                print(f"  ❌ 错误: 模板文件 jumpUrl.ts 未在包资源 'src.resources' 中找到。请检查项目文件是否完整且打包配置正确。")
        else:
            print(f"  ℹ️  项目中未使用@locallife/utils，跳过创建jumpUrl.ts文件")
    
    def _needsJumpUrlFile(self, modulePath: Path) -> bool:
        """检查项目是否需要jumpUrl.ts文件（是否使用了@locallife/utils）"""
        # 获取正确的package.json路径
        handler = self.get_repository_handler()
        from util.RepositoryHandler import BundlesRepositoryHandler
        from util.SingleRepositoryHandler import SingleRepositoryHandler
        
        if isinstance(handler, BundlesRepositoryHandler):
            # bundles结构：检查根目录的package.json
            package_json_path = handler.get_root_package_json_path()
        elif isinstance(handler, SingleRepositoryHandler):
            # 单一项目结构：检查根目录的package.json
            package_json_path = modulePath / "package.json"
        else:
            # 平铺结构：检查模块的package.json
            package_json_path = modulePath / "package.json"
        
        if not package_json_path or not package_json_path.exists():
            return False
        
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            # 检查dependencies和devDependencies中是否有@locallife/utils
            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})
            
            has_locallife_utils = '@locallife/utils' in dependencies or '@locallife/utils' in dev_dependencies
            
            if has_locallife_utils:
                print(f"  ✅ 检测到@locallife/utils依赖，将创建jumpUrl.ts文件")
            else:
                print(f"  ℹ️  未检测到@locallife/utils依赖，跳过jumpUrl.ts文件创建")
            
            return has_locallife_utils
            
        except Exception as e:
            print(f"  ⚠️  检查package.json时出错: {e}")
            return False
        
    def _fixCharsetIssues(self, modulePath: Path):
        """
        遍历指定模块路径下的目标目录，并将所有文件中的
        'charset=UTF-8' 字符串替换为 'charset=utf-8'
        """
        
        # 从配置中获取支持的目录列表
        target_dirs = self.defaultScanDirs
        
        # 初始化计数器，用于最终的报告
        total_files_scanned = 0
        total_files_changed = 0

        for target_dir in target_dirs:
            if target_dir == "node_modules":
                print(f"  🚫 跳过 node_modules 目录")
                continue

            print(f"🔍 正在扫描目录: {modulePath}")

            # 初始化计数器，用于当前目录的报告
            files_scanned = 0
            files_changed = 0

            # 3. 使用 rglob('*') 递归地遍历目标目录下的所有文件和文件夹
            for filePath in modulePath.rglob('*'):
                # 跳过 node_modules 目录中的文件
                if 'node_modules' in filePath.parts:
                    continue
                
                # 确保当前路径是一个文件，而不是一个目录
                if filePath.is_file():
                    files_scanned += 1
                    try:
                        # 4. 读取文件内容。我们假设文件是 utf-8 编码。
                        #    Path.read_text() 会自动处理文件的打开和关闭。
                        originalContent = filePath.read_text(encoding='utf-8')

                        # 5. 检查是否包含需要修改的字符串，避免不必要的写操作
                        if 'charset=UTF-8' in originalContent:
                            # 6. 执行替换
                            modified_content = originalContent.replace('charset=UTF-8', 'charset=utf-8')

                            # 7. 将修改后的内容写回文件
                            filePath.write_text(modified_content, encoding='utf-8')

                            # 打印日志并更新计数器
                            # 使用 relative_to() 让路径显示更友好
                            print(f"✅ 已修正: {filePath.relative_to(modulePath)}")
                            files_changed += 1

                    except UnicodeDecodeError:
                        # 8. 错误处理：如果文件不是有效的 utf-8 文本（例如图片、二进制文件），
                        #    read_text 会抛出此异常。我们将其捕获并跳过该文件。
                        print(f"⚪️  已跳过 (非文本文件): {filePath.relative_to(modulePath)}")
                    except Exception as e:
                        # 捕获其他可能的异常，例如权限问题
                        print(f"❌ 处理文件时出错 {filePath.relative_to(modulePath)}: {e}", file=sys.stderr)

            # 累加到总计数器
            total_files_scanned += files_scanned
            total_files_changed += files_changed
            
            # 打印当前目录的总结报告
            print(f"📁 {target_dir} 目录扫描完成：共扫描 {files_scanned} 个文件，修正了 {files_changed} 个文件。")

        # 9. 打印最终的总结报告
        print(f"\n✨ 扫描完成。共扫描 {total_files_scanned} 个文件，修正了 {total_files_changed} 个文件。")

    def _fixReactReduxVersion(self, packageData):
        """将react-redux版本从8.0.0+降级到7.2.6"""
        targetPackage = 'react-redux'
        targetVersion = '^7.2.6'
        versionThreshold = version.parse("8.0.0")

        # 1. 安全地检查 'dependencies' 和 'react-redux' 是否存在
        return self._check_and_update_dependency_version(
            packageData,
            target_package='react-redux',
            target_version='7.2.9',
            version_threshold_str='8.0.0',
            comparison=operator.gt,
            comparison_desc='>',
            update_message="降级为"
        )

    def _fixReduxToolkitVersion(self, packageData: Dict[str, Any]) -> Dict[str, Any]:
        """如果@reduxjs/toolkit版本低于1.9.7，则升级到^1.9.7"""
        return self._check_and_update_dependency_version(
            packageData,
            target_package='@reduxjs/toolkit',
            target_version='^1.9.7',
            version_threshold_str='1.9.7',
            comparison=operator.lt,
            comparison_desc='<',
            update_message="升级为"
        )
    
    def _fixLocalLifePageVersion(self, packageData):
        """将@locallife/page版本从0.2.20+降级到0.2.19"""

        # 1. 安全地检查 'dependencies' 和 'react-redux' 是否存在
        return self._check_and_update_dependency_version(
            packageData,
            target_package='@locallife/page',
            target_version='0.2.19',
            version_threshold_str='0.2.19',
            comparison=operator.gt,
            comparison_desc='>',
            update_message="降级为"
        )

    def _check_and_update_dependency_version(
        self,
        packageData: Dict[str, Any],
        target_package: str,
        target_version: str,
        version_threshold_str: str,
        comparison: callable,
        comparison_desc: str,
        update_message: str
    ) -> Dict[str, Any]:
        """通用方法：检查并更新package.json中的依赖版本。"""
        version_threshold = version.parse(version_threshold_str)

        dependencies = packageData.get('dependencies')
        if not isinstance(dependencies, dict):
            return packageData

        currentVersionStr = dependencies.get(target_package)
        if not isinstance(currentVersionStr, str):
            return packageData

        versionMatch = re.search(r'(\d+\.\d+\.\d+)', currentVersionStr)
        if not versionMatch:
            print(f"⚪️  在 '{currentVersionStr}' 中未找到可比较的版本号，跳过对 '{target_package}' 的处理。")
            return packageData
        
        cleanVersionStr = versionMatch.group(1)

        try:
            currentVersion = version.parse(cleanVersionStr)
            
            if comparison(currentVersion, version_threshold):
                print(f"✅ 检测到 '{target_package}' 版本 '{currentVersionStr}' {comparison_desc} {version_threshold_str}，将{update_message} '{target_version}'。")
                packageData['dependencies'][target_package] = target_version
            else:
                print(f"ℹ️  '{target_package}' 版本 '{currentVersionStr}' 无需修改。")

        except Exception:
            print(f"⚠️  警告: 无法解析版本号 '{cleanVersionStr}'，跳过处理。")

        return packageData

    def updateModuleCode(self, moduleName: str) -> bool:
        print(f"🔀 更新模块代码 - {moduleName}")
        print("=" * 50)
        
        # 使用仓库处理器检查模块是否存在
        handler = self.get_repository_handler()
        modulePath = handler.get_module_path(moduleName)
        
        if not modulePath or not modulePath.exists():
            print(f"❌ 模块不存在: {moduleName}")
            return False
        
        try:
            # 1. 从最新Dev分支检出最新代码
            currentBranch = self.gitManager.getCurrentBranch()
            latestDevBranch = self.gitManager.getLatestDevBranch()
            print(f"📍 步骤1: 尝试从最新的dev分支 '{latestDevBranch}' 更新模块 '{moduleName}'...")
            success, output = self.gitManager.checkoutModuleFromBranch(latestDevBranch, moduleName)
            
            if not success:
                print(f"  ⚠️  从 '{latestDevBranch}' 更新失败，自动降级尝试 'master' 分支...")
                success, output = self.gitManager.checkoutModuleFromBranch("master", moduleName)
                latestDevBranch = "master"
                if not success:
                    print(f"❌ 从master分支检出代码失败: {output}")
                    return False # 两个分支都失败了，终止操作
            
            print(f"✅ 成功从 {latestDevBranch} 分支更新 {moduleName} 模块代码")
            return True
            
        except Exception as e:
            print(f"❌ 更新模块代码时出错: {e}")
            return False
    
    def _addBlurDependencyIfNeeded(self, packageData: dict):
        """检查是否需要添加@kds/react-native-blur依赖"""
        dependencies = packageData.get('dependencies', {})
        dev_dependencies = packageData.get('devDependencies', {})
        
        # 检查是否存在blur相关依赖
        blur_packages = ['react-native-blur', '@react-native-community/blur']
        has_blur_dependency = False
        
        for blur_pkg in blur_packages:
            if blur_pkg in dependencies or blur_pkg in dev_dependencies:
                has_blur_dependency = True
                break
        
        # 如果存在blur依赖且还没有@kds/react-native-blur，则添加
        if has_blur_dependency and '@kds/react-native-blur' not in dependencies:
            if 'dependencies' not in packageData:
                packageData['dependencies'] = {}
            packageData['dependencies']['@kds/react-native-blur'] = '3.6.7'
            print(f"  ✅ 检测到blur依赖，已添加@kds/react-native-blur: 3.6.7")
    