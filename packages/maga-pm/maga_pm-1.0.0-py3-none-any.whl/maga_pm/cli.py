"""
MAGA包管理器命令行界面

让包管理再次伟大的命令行工具！
"""

import sys
import argparse
import colorama
from colorama import Fore, Style

from .package_manager import MAGAPackageManager, create_package_manager

colorama.init()

def print_banner():
    """打印MAGA横幅"""
    banner = f"""
{Fore.CYAN}{'='*60}{Style.RESET_ALL}
{Fore.WHITE}   __  __    _    {Fore.BLUE}   ____  {Fore.WHITE}   ____  _   _ 
{Fore.WHITE}  |  \/  |  / \   {Fore.BLUE}  / ___| {Fore.WHITE} / ___|| \ | |
{Fore.WHITE}  | |\/| | / _ \  {Fore.BLUE} | |     {Fore.WHITE}| |    |  \| |
{Fore.WHITE}  | |  | |/ ___ \ {Fore.BLUE} | |___  {Fore.WHITE}| |___ | |\  |
{Fore.WHITE}  |_|  |_/_/   \_\{Fore.BLUE}  \____| {Fore.WHITE} \____||_| \_|
{Style.RESET_ALL}
{Fore.GREEN}    M A N A G E D   A N D   G O V E R N E D   A C C E S S
{Fore.YELLOW}            P A C K A G E   M A N A G E R{Style.RESET_ALL}
{Fore.CYAN}{'='*60}{Style.RESET_ALL}
{Fore.WHITE}版本：1.0.0 | 作者：ruin321 | 许可证：MIT License{Style.RESET_ALL}
{Fore.YELLOW}政策控制的包管理系统{Style.RESET_ALL}
"""
    print(banner)

def print_help():
    """打印帮助信息"""
    help_text = f"""
{Fore.CYAN}MAGA包管理器 - 让包管理再次伟大！{Style.RESET_ALL}

{Fore.YELLOW}核心特性：{Style.RESET_ALL}
  • 美利坚CDN流量包（必须下载才能运行）
  • 特朗普流量税（基于国家的下载速度控制）
  • 贸易战模式（随机拒绝某些国家的包）
  • 美国优先政策（美国包优先处理）

{Fore.GREEN}使用方法：{Style.RESET_ALL}
  maga init                   初始化MAGA-PM（下载CDN流量包）
  maga install <package>      安装包（受特朗普政策影响）
  maga list                   列出已安装的包
  maga uninstall <package>    卸载包
  maga policy                 显示特朗普政策状态
  maga tax                    显示流量税详情
  maga cdn                    显示CDN流量包信息
  maga stats                  显示统计信息
  maga maga                   执行MAGA优化
  maga help                   显示此帮助信息

{Fore.YELLOW}示例：{Style.RESET_ALL}
  maga init                    # 初始化MAGA-PM
  maga install requests        # 安装requests包
  maga list                    # 查看已安装的包

{Fore.CYAN}作者：ruin321 | 版本：1.0.0 | 许可证：MAGA License{Style.RESET_ALL}
"""
    print(help_text)

def main():
    """主函数"""
    print_banner()
    
    parser = argparse.ArgumentParser(
        description="MAGA包管理器 - 政策控制的包管理系统",
        add_help=False
    )
    
    # 子命令
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # init命令
    init_parser = subparsers.add_parser("init", help="初始化MAGA-PM（下载CDN流量包）")
    init_parser.add_argument("--force", action="store_true", help="强制重新下载CDN流量包")
    
    # install命令
    install_parser = subparsers.add_parser("install", help="安装包（受特朗普政策影响）")
    install_parser.add_argument("package", help="要安装的包名")
    install_parser.add_argument("--country", help="包的国家（默认随机）")
    
    # list命令
    subparsers.add_parser("list", help="列出已安装的包")
    
    # uninstall命令
    uninstall_parser = subparsers.add_parser("uninstall", help="卸载包")
    uninstall_parser.add_argument("package", help="要卸载的包名")
    
    # policy命令
    subparsers.add_parser("policy", help="显示特朗普政策状态")
    
    # tax命令
    subparsers.add_parser("tax", help="显示流量税详情")
    
    # cdn命令
    subparsers.add_parser("cdn", help="显示CDN流量包信息")
    
    # stats命令
    subparsers.add_parser("stats", help="显示统计信息")
    
    # maga命令
    subparsers.add_parser("maga", help="执行MAGA优化")
    
    # 帮助命令
    subparsers.add_parser("help", help="显示帮助信息")
    
    # 如果没有参数，显示帮助
    if len(sys.argv) == 1:
        print_help()
        return 0
    
    try:
        args = parser.parse_args()
    except SystemExit:
        # argparse在错误时会调用sys.exit()
        print_help()
        return 1
    
    # 处理命令
    if args.command == "init":
        # init命令需要跳过CDN包检查
        try:
            pm = create_package_manager(skip_cdn_check=True)
            return 0 if pm.init(args.force) else 1
        except SystemExit:
            return 1
    
    elif args.command == "install":
        # 其他命令需要CDN包
        try:
            pm = create_package_manager()
        except SystemExit:
            return 1
        
        if not args.package:
            print(f"{Fore.RED}❌ 请指定要安装的包名{Style.RESET_ALL}")
            return 1
        return 0 if pm.install(args.package, args.region) else 1
    
    elif args.command == "list":
        try:
            pm = create_package_manager()
        except SystemExit:
            return 1
        pm.list_packages()
        return 0
    
    elif args.command == "uninstall":
        try:
            pm = create_package_manager()
        except SystemExit:
            return 1
        
        if not args.package:
            print(f"{Fore.RED}❌ 请指定要卸载的包名{Style.RESET_ALL}")
            return 1
        return 0 if pm.uninstall(args.package) else 1
    
    elif args.command == "policy":
        try:
            pm = create_package_manager()
        except SystemExit:
            return 1
        pm.policy()
        return 0
    
    elif args.command == "tax":
        try:
            pm = create_package_manager()
        except SystemExit:
            return 1
        pm.tax()
        return 0
    
    elif args.command == "cdn":
        try:
            pm = create_package_manager()
        except SystemExit:
            return 1
        pm.cdn()
        return 0
    
    elif args.command == "stats":
        try:
            pm = create_package_manager()
        except SystemExit:
            return 1
        pm.stats()
        return 0
    
    elif args.command == "maga":
        try:
            pm = create_package_manager()
        except SystemExit:
            return 1
        pm.make_maga_great_again()
        return 0
    
    elif args.command == "stats":
        try:
            pm = create_package_manager()
        except SystemExit:
            return 1
        pm.stats()
        return 0
    
    elif args.command == "config":
        try:
            pm = create_package_manager()
        except SystemExit:
            return 1
        
        if args.action == "list":
            print(f"{Fore.CYAN}配置管理功能待实现{Style.RESET_ALL}")
            return 0
        else:
            print(f"{Fore.YELLOW}配置操作 '{args.action}' 待实现{Style.RESET_ALL}")
            return 0
    
    elif args.command == "audit":
        try:
            pm = create_package_manager()
        except SystemExit:
            return 1
        print(f"{Fore.CYAN}审计报告功能待实现{Style.RESET_ALL}")
        return 0
    
    elif args.command == "compliance":
        try:
            pm = create_package_manager()
        except SystemExit:
            return 1
        print(f"{Fore.CYAN}合规性检查功能待实现{Style.RESET_ALL}")
        return 0
    
    elif args.command == "help" or args.command is None:
        print_help()
        return 0
    
    else:
        print(f"{Fore.RED}❌ 未知命令：{args.command}{Style.RESET_ALL}")
        print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())