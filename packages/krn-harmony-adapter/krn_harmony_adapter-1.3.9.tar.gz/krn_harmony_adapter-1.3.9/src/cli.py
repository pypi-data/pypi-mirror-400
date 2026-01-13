#!/usr/bin/env python3
"""
Harmony Adapter CLI - 命令行接口
"""

from pathlib import Path
import sys
import os
import argparse
from typing import Optional, List

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from .Main import Main
    from . import __version__
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    sys.path.append(os.path.dirname(current_dir))
    from Main import Main
    __version__ = "1.0.0"  # 临时版本号


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog='kha',
        description='KRN鸿蒙适配自动化工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  kha                       # 交互式模式
  kha check                 # 检查所有模块适配状态
  kha sync                  # 同步缺失模块
  kha sync <模块名>          # 同步指定模块(强制覆盖)
  kha adapt <模块名>         # 适配指定模块
  kha batch                 # 批量适配所有未适配模块
    kha batch live          # 批量适配直播模块
    kha batch non_live      # 批量适配非直播模块
    kha batch all           # 批量适配所有模块
  kha doc                   # 生成文档
  kha url                   # 检查接口注册状态
  kha update                # 更新工具到最新版本

        """
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        choices=['check', 'sync', 'adapt', 'batch', 'doc', 'url', 'update'],
        help='要执行的命令'
    )
    
    parser.add_argument(
        'args',
        nargs='*',
        help='命令参数（如模块名称、URL路径等）'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    parser.add_argument(
        '--base-path',
        default='.',
        help='项目根目录路径（默认为当前目录）'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细输出'
    )
    
    return parser


def main():
    """主入口函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # 对于update和url命令，不需要初始化适配器
        if args.command == 'update':
            from modules.update.Updater import Updater
            updater = Updater()
            success = updater.update_package()
            sys.exit(0 if success else 1)
        
        # 对于url命令，直接处理URL检查
        if args.command == 'url':
            from modules.doc.UrlDetector import UrlDetector
            url_detector = UrlDetector(args.base_path)
            
            if args.args:
                if args.args[0].startswith('/'):
                    url_detector.checkUrlRegisteryStatus('harmonyos-lbs.kwailocallife.com', args.args)
                else:
                    url_detector.checkUrlRegisteryStatus(args.args[0], args.args[1:])
            else:
                url_detector.checkUrlRegisteryStatus()
            return
        
        # 初始化适配器，传递base_path参数
        adapter = Main(args.base_path)
        
        # 如果没有指定命令，进入交互式模式
        if not args.command:
            adapter.interactive_menu()
            return
        
        # 执行指定命令
        if args.command == 'check':
            adapter.checkAllModulesAdaptation()
        
        elif args.command == 'sync':
            if args.args:
                # 同步指定模块
                success = True
                for module_name in args.args:
                    result = adapter.syncSpecificModule(module_name)
                    if not result:
                        success = False
                # 同步完成后退出
                sys.exit(0 if success else 1)
            else:
                # 同步缺失模块
                adapter.syncMissingModules()
                sys.exit(0)
        
        elif args.command == 'adapt':
            # 检查仓库结构，决定是否需要模块名
            from util.GlobalRepositoryManager import get_repository_info
            repo_info = get_repository_info(args.base_path, silent=True)
            
            if repo_info.structure.value == 'single':
                # 单一项目结构，不需要指定模块名
                if args.args:
                    print("ℹ️  单一项目结构，忽略模块名参数")
                adapter.adaptSingleProject()
            else:
                # 其他结构需要指定模块名
                if not args.args:
                    print("❌ adapt命令需要指定模块名称")
                    print("使用方法: kha adapt <模块名>")
                    sys.exit(1)
                for module_name in args.args:
                    adapter.adaptSingleModule(module_name)
        
        elif args.command == 'batch':
            module_type = args.args[0] if args.args else "all"
            adapter.adaptBatchModules(module_type)
        
        elif args.command == 'doc':
            adapter.generateDocumentation()
        
        # url命令已在main函数开头处理
        
        # update命令已在main函数开头处理
        
        else:
            parser.print_help()
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
        sys.exit(0)
    
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"❌ 执行失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()