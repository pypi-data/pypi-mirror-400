"""
MAGA包管理器核心模块

实现受特朗普政策影响的包管理功能：
- 美利坚CDN流量包
- 特朗普流量税
- 贸易战模式
- 美国优先政策
"""

import os
import sys
import time
import random
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import colorama
from colorama import Fore, Style

from .cdn_traffic import AmericanCDNTrafficPackage, download_american_cdn_package
from .traffic_tax import TrumpTrafficTax, SlowDownloadSimulator
from .policy_simulator import TrumpPolicySimulator

colorama.init()

class MAGAPackageManager:
    """MAGA包管理器 - 让包管理再次伟大！"""
    
    def __init__(self, skip_cdn_check=False):
        self.config_dir = Path.home() / ".maga"
        self.config_file = self.config_dir / "config.json"
        self.packages_file = self.config_dir / "packages.json"
        
        # 初始化组件
        self.cdn_package = AmericanCDNTrafficPackage()
        self.traffic_tax = TrumpTrafficTax()
        self.download_simulator = SlowDownloadSimulator(self.traffic_tax)
        self.policy_simulator = TrumpPolicySimulator()
        
        # 加载配置
        self.config = self._load_config()
        
        # 检查CDN流量包（init命令可以跳过）
        if not skip_cdn_check:
            self._check_cdn_package()
    
    def _load_config(self) -> Dict:
        """加载配置"""
        default_config = {
            "version": "1.0.0",
            "maga_mode": "full",  # full, lite, patriotic
            "trump_tax_enabled": True,
            "trade_war_enabled": True,
            "america_first_enabled": True,
            "build_wall_enabled": True,
            "cdn_package_required": True,
            "download_speed": "🐌",  # 🐌, 🐢, 🚗
            "maga_score": "A+",
            "install_count": 0,
            "blocked_count": 0,
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except:
                pass
        
        return default_config
    
    def _save_config(self):
        """保存配置"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _check_cdn_package(self):
        """检查CDN流量包"""
        if self.config["cdn_package_required"] and not self.cdn_package.check_package_exists():
            print(f"{Fore.RED}❌ 错误：未找到美利坚CDN流量包！{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}请先运行 'maga init' 下载流量包{Style.RESET_ALL}")
            sys.exit(1)
    
    def _load_packages(self) -> Dict:
        """加载已安装的包"""
        if self.packages_file.exists():
            try:
                with open(self.packages_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_packages(self, packages: Dict):
        """保存包列表"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.packages_file, 'w') as f:
            json.dump(packages, f, indent=2)
    
    def init(self, force: bool = False):
        """初始化MAGA-PM（下载CDN流量包）"""
        print(f"{Fore.CYAN}🇺🇸 初始化MAGA包管理器...{Style.RESET_ALL}")
        
        # 显示特朗普政策通知
        self.traffic_tax.show_tax_notice()
        
        # 下载CDN流量包
        success = download_american_cdn_package(force)
        
        if success:
            print(f"\n{Fore.GREEN}✅ MAGA-PM 初始化完成！{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}现在你可以使用 'maga install' 命令了{Style.RESET_ALL}")
            print(f"{Fore.RED}⚠️  注意：所有下载都会受到特朗普流量税影响 🐌{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ 初始化失败！{Style.RESET_ALL}")
        
        return success
    
    def install(self, package_name: str, country: Optional[str] = None):
        """
        安装包（受特朗普政策影响）
        
        Args:
            package_name: 包名
            country: 包的国家（默认随机）
        """
        print(f"{Fore.CYAN}📦 准备安装包：{package_name}{Style.RESET_ALL}")
        
        # 随机选择国家（如果未指定）
        if not country:
            countries = ["china", "eu", "russia", "usa", "other"]
            weights = [0.3, 0.2, 0.2, 0.2, 0.1]
            country = random.choices(countries, weights=weights, k=1)[0]
        
        # 模拟政策影响
        print(f"{Fore.YELLOW}🔍 应用特朗普政策...{Style.RESET_ALL}")
        time.sleep(1)
        
        # 随机包大小
        package_size_mb = random.uniform(1.0, 50.0)
        
        # 模拟下载
        allowed, download_time, messages = self.policy_simulator.simulate_download_with_policies(
            package_name, package_size_mb, country
        )
        
        # 显示结果
        if not allowed:
            print(f"\n{Fore.RED}🚫 安装被拒绝！{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}原因：{Style.RESET_ALL}")
            for msg in messages:
                print(f"  • {msg}")
            
            self.config["blocked_count"] += 1
            self._save_config()
            return False
        
        # 显示下载详情
        print(f"\n{Fore.GREEN}✅ 包允许安装{Style.RESET_ALL}")
        print(f"{Fore.CYAN}国家：{country}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}大小：{package_size_mb:.1f} MB{Style.RESET_ALL}")
        
        for msg in messages:
            print(f"  • {msg}")
        
        # 模拟实际下载
        print(f"\n{Fore.YELLOW}⏳ 开始下载（超级慢）...{Style.RESET_ALL}")
        self.download_simulator.show_download_progress(package_size_mb)
        
        # 更新包列表
        packages = self._load_packages()
        packages[package_name] = {
            "version": "1.0.0",
            "country": country,
            "size_mb": package_size_mb,
            "install_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "download_time": download_time,
            "trump_tax_applied": True,
        }
        self._save_packages(packages)
        
        # 更新配置
        self.config["install_count"] += 1
        self._save_config()
        
        print(f"\n{Fore.GREEN}🎉 安装完成！{Style.RESET_ALL}")
        print(f"{Fore.CYAN}包 '{package_name}' 已成功安装{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}总下载时间：{download_time:.1f} 秒 🐌{Style.RESET_ALL}")
        
        return True
    
    def list_packages(self):
        """列出已安装的包"""
        packages = self._load_packages()
        
        if not packages:
            print(f"{Fore.YELLOW}📭 没有安装任何包{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}📦 已安装的包（共 {len(packages)} 个）：{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
        
        for i, (name, info) in enumerate(packages.items(), 1):
            country_flag = {
                "usa": "🇺🇸",
                "china": "🇨🇳", 
                "eu": "🇪🇺",
                "russia": "🇷🇺",
                "other": "🌍",
            }.get(info.get("country", "other"), "🌍")
            
            print(f"{Fore.GREEN}{i:3}. {name:30}{Style.RESET_ALL}", end="")
            print(f"{Fore.CYAN} v{info.get('version', '1.0.0'):10}{Style.RESET_ALL}", end="")
            print(f"{Fore.YELLOW} {country_flag} {info.get('country', 'unknown'):10}{Style.RESET_ALL}", end="")
            print(f"{Fore.MAGENTA} {info.get('size_mb', 0):6.1f} MB{Style.RESET_ALL}", end="")
            print(f"{Fore.RED} 🐌 {info.get('download_time', 0):6.1f}s{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
        
        # 显示统计
        total_size = sum(info.get("size_mb", 0) for info in packages.values())
        total_time = sum(info.get("download_time", 0) for info in packages.values())
        
        print(f"{Fore.CYAN}统计：{Style.RESET_ALL}")
        print(f"{Fore.GREEN}总大小：{total_size:.1f} MB{Style.RESET_ALL}")
        print(f"{Fore.RED}总下载时间：{total_time:.1f} 秒（受特朗普流量税影响）{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}平均速度：{total_size*1024/max(1, total_time):.1f} KB/s 🐌{Style.RESET_ALL}")
    
    def uninstall(self, package_name: str):
        """卸载包"""
        packages = self._load_packages()
        
        if package_name not in packages:
            print(f"{Fore.RED}❌ 包 '{package_name}' 未安装{Style.RESET_ALL}")
            return False
        
        print(f"{Fore.YELLOW}🗑️  卸载包：{package_name}{Style.RESET_ALL}")
        
        # 模拟卸载过程（很快，因为不需要流量税）
        print(f"{Fore.CYAN}正在卸载...{Style.RESET_ALL}")
        time.sleep(0.5)
        
        # 从包列表中移除
        del packages[package_name]
        self._save_packages(packages)
        
        print(f"{Fore.GREEN}✅ 包 '{package_name}' 已卸载{Style.RESET_ALL}")
        return True
    
    def policy(self):
        """显示特朗普政策状态"""
        self.policy_simulator.show_policy_dashboard()
    
    def tax(self):
        """显示流量税信息"""
        from .traffic_tax import show_traffic_tax_info
        show_traffic_tax_info()
    
    def cdn(self):
        """显示CDN流量包信息"""
        from .cdn_traffic import show_traffic_package_info
        show_traffic_package_info()
    
    def stats(self):
        """显示统计信息"""
        packages = self._load_packages()
        
        print(f"{Fore.CYAN}📊 MAGA-PM 统计信息{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*50}{Style.RESET_ALL}")
        
        # 基本统计
        print(f"{Fore.GREEN}已安装包数量：{len(packages)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}总安装次数：{self.config.get('install_count', 0)}{Style.RESET_ALL}")
        print(f"{Fore.RED}被拒绝安装次数：{self.config.get('blocked_count', 0)}{Style.RESET_ALL}")
        
        # 政策统计
        policy_stats = self.policy_simulator.get_statistics()
        print(f"\n{Fore.CYAN}政策统计：{Style.RESET_ALL}")
        for key, value in policy_stats.items():
            key_display = key.replace("_", " ").title()
            print(f"{Fore.GREEN}{key_display:25}{Fore.WHITE}: {value}{Style.RESET_ALL}")
        
        # 速度统计
        if packages:
            total_size = sum(info.get("size_mb", 0) for info in packages.values())
            total_time = sum(info.get("download_time", 0) for info in packages.values())
            avg_speed = total_size * 1024 / max(1, total_time)
            
            print(f"\n{Fore.CYAN}速度统计：{Style.RESET_ALL}")
            print(f"{Fore.GREEN}平均下载速度：{avg_speed:.1f} KB/s 🐌{Style.RESET_ALL}")
            
            # 速度评级
            if avg_speed < 10:
                speed_rating = "🐌 蜗牛速度（特朗普税收生效中）"
            elif avg_speed < 50:
                speed_rating = "🐢 乌龟速度（高关税）"
            elif avg_speed < 100:
                speed_rating = "🚶 步行速度（中关税）"
            else:
                speed_rating = "🚗 汽车速度（低关税）"
            
            print(f"{Fore.YELLOW}速度评级：{speed_rating}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}特朗普说：'这是有史以来最伟大的包管理器！'{Style.RESET_ALL}")
    
    def make_maga_great_again(self):
        """执行MAGA优化（实际上什么都不做，只是显示信息）"""
        print(f"{Fore.CYAN}🇺🇸 执行MAGA优化...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}特朗普总统正在优化你的包管理器...{Style.RESET_ALL}")
        
        optimizations = [
            "增加特朗普流量税...",
            "加强贸易战屏蔽...",
            "加高网络墙...",
            "实施美国优先政策...",
            "抽干依赖沼泽...",
            "让包管理再次伟大！",
        ]
        
        for opt in optimizations:
            print(f"{Fore.GREEN}✅ {opt}{Style.RESET_ALL}")
            time.sleep(0.5)
        
        print(f"\n{Fore.GREEN}🎉 MAGA优化完成！{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}你的包管理器现在更慢了，但更爱国了！ 🇺🇸{Style.RESET_ALL}")
        print(f"{Fore.RED}⚠️  注意：下载速度可能进一步降低 🐌🐌{Style.RESET_ALL}")


def create_package_manager(skip_cdn_check=False) -> MAGAPackageManager:
    """创建包管理器实例"""
    return MAGAPackageManager(skip_cdn_check=skip_cdn_check)