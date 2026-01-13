"""
MAGA包管理器命令行界面

让包管理再次伟大的命令行工具！
"""

import sys
import argparse
import colorama
from colorama import Fore, Style

from .package_manager import MAGAPackageManager, create_package_manager
from .usa_colors import USAColors
from .i18n import i18n

colorama.init()

def print_banner():
    """打印MAGA横幅"""
    banner = f"""
{Fore.RED}{'='*60}{Style.RESET_ALL}
{Fore.WHITE}🇺🇸 MAGA PACKAGE MANAGER 🇺🇸{Style.RESET_ALL}
{Fore.BLUE}{'='*60}{Style.RESET_ALL}
{Fore.RED}版本: {Fore.WHITE}11.4.6 {Fore.BLUE}| {Fore.RED}作者: {Fore.WHITE}ruin321 {Fore.BLUE}| {Fore.RED}许可证: {Fore.WHITE}MAGA License{Style.RESET_ALL}
{Fore.WHITE}{i18n.get('policy_system')} - {i18n.get('slogan')}{Style.RESET_ALL}
{Fore.RED}{'='*60}{Style.RESET_ALL}
"""
    print(banner)


def print_version():
    """打印版本信息"""
    version_text = f"""
{Fore.RED}{'*'*60}{Style.RESET_ALL}
{Fore.WHITE}🇺🇸 {i18n.get('usa_first')} 🇺🇸{Style.RESET_ALL}
{Fore.BLUE}{'*'*60}{Style.RESET_ALL}
{Fore.RED}{i18n.get('maga_pm')}{Style.RESET_ALL}
{Fore.RED}{i18n.get('version')}: {Fore.WHITE}11.4.6{Style.RESET_ALL}
{Fore.RED}{i18n.get('author')}: {Fore.WHITE}ruin321{Style.RESET_ALL}
{Fore.RED}{i18n.get('license')}: {Fore.WHITE}{i18n.get('maga_license')}{Style.RESET_ALL}
{Fore.BLUE}{i18n.get('slogan')}{Style.RESET_ALL}
{Fore.RED}{'*'*60}{Style.RESET_ALL}
"""
    print(version_text)

def print_help():
    """打印帮助信息"""
    help_text = f"""
{Fore.RED}MAGA Package Manager - {Fore.WHITE}{i18n.get('slogan')}{Style.RESET_ALL}

{Fore.BLUE}{i18n.get('core_features')}:{Style.RESET_ALL}
  • {Fore.RED}{i18n.get('cdn_feature')}{Style.RESET_ALL}
  • {Fore.WHITE}{i18n.get('tax_feature')}{Style.RESET_ALL}
  • {Fore.RED}{i18n.get('trade_war_feature')}{Style.RESET_ALL}
  • {Fore.WHITE}{i18n.get('usa_first_feature')}{Style.RESET_ALL}

{Fore.BLUE}使用方法：{Style.RESET_ALL}
  {Fore.RED}maga init                   {Fore.WHITE}{i18n.get('init_command')}{Style.RESET_ALL}
  {Fore.RED}maga install <package>      {Fore.WHITE}{i18n.get('install_command')}{Style.RESET_ALL}
  {Fore.RED}maga list                   {Fore.WHITE}{i18n.get('list_command')}{Style.RESET_ALL}
  {Fore.RED}maga uninstall <package>    {Fore.WHITE}卸载包{Style.RESET_ALL}
  {Fore.RED}maga policy                 {Fore.WHITE}显示特朗普政策状态{Style.RESET_ALL}
  {Fore.RED}maga tax                    {Fore.WHITE}显示流量税详情{Style.RESET_ALL}
  {Fore.RED}maga cdn                    {Fore.WHITE}{i18n.get('cdn_command')}{Style.RESET_ALL}
  {Fore.RED}maga stats                  {Fore.WHITE}{i18n.get('stats_command')}{Style.RESET_ALL}
  {Fore.RED}maga maga                   {Fore.WHITE}{i18n.get('maga_command')}{Style.RESET_ALL}
  {Fore.RED}maga help                   {Fore.WHITE}{i18n.get('help_command')}{Style.RESET_ALL}

{Fore.BLUE}示例：{Style.RESET_ALL}
  {Fore.RED}maga init                    {Fore.WHITE}# {i18n.get('init_command')}{Style.RESET_ALL}
  {Fore.RED}maga install requests        {Fore.WHITE}# {i18n.get('install_command')}{Style.RESET_ALL}
  {Fore.RED}maga list                    {Fore.WHITE}# {i18n.get('list_command')}{Style.RESET_ALL}

{Fore.RED}{i18n.get('author')}: {Fore.WHITE}ruin321 {Fore.BLUE}| {Fore.RED}{i18n.get('version')}: {Fore.WHITE}1.0.0 {Fore.BLUE}| {Fore.RED}{i18n.get('license')}: {Fore.WHITE}{i18n.get('maga_license')}{Style.RESET_ALL}
"""
    print(help_text)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description=f"MAGA Package Manager - {i18n.get('policy_system')}",
        add_help=False
    )
    
    # 添加--version参数
    parser.add_argument(
        "--version",
        action="store_true",
        help="显示版本信息"
    )
    
    # 子命令
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # init命令
    init_parser = subparsers.add_parser("init", help=i18n.get('init_command'))
    init_parser.add_argument("--force", action="store_true", help=i18n.get('force_option'))
    
    # install命令
    install_parser = subparsers.add_parser("install", help=i18n.get('install_command'))
    install_parser.add_argument("package", help="要安装的包名")
    install_parser.add_argument("--country", help=i18n.get('country_option'))
    
    # list命令
    subparsers.add_parser("list", help=i18n.get('list_command'))
    
    # uninstall命令
    uninstall_parser = subparsers.add_parser("uninstall", help="卸载包")
    uninstall_parser.add_argument("package", help="要卸载的包名")
    
    # policy命令
    subparsers.add_parser("policy", help="显示特朗普政策状态")
    
    # tax命令
    subparsers.add_parser("tax", help="显示流量税详情")
    
    # cdn命令
    subparsers.add_parser("cdn", help=i18n.get('cdn_command'))
    
    # stats命令
    subparsers.add_parser("stats", help=i18n.get('stats_command'))
    
    # maga命令
    subparsers.add_parser("maga", help=i18n.get('maga_command'))
    
    # 帮助命令
    subparsers.add_parser("help", help=i18n.get('help_command'))
    
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
    
    # 处理--version参数
    if args.version:
        print_version()
        return 0
    
    # 显示横幅（除了--version命令）
    print_banner()
    
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
        return 0 if pm.install(args.package, args.country) else 1
    
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