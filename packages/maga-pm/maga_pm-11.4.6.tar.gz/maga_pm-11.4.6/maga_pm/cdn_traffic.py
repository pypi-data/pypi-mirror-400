"""
美利坚CDN流量包下载模块

这个模块负责下载美国CDN流量包（空壳），
没有这个包MAGA-PM无法运行。
"""

import os
import time
import random
import subprocess
from pathlib import Path
from tqdm import tqdm
import colorama
from colorama import Fore, Style

from .i18n import i18n

colorama.init()

class AmericanCDNTrafficPackage:
    """美利坚CDN流量包（空壳）"""
    
    def __init__(self):
        self.package_size = 1024 * 1024 * 100  # 100MB 空壳包
        self.downloaded = False
        self.package_path = Path.home() / ".maga" / "cdn_traffic.pkg"
        
    def check_package_exists(self):
        """检查CDN流量包是否存在"""
        return self.package_path.exists() and self.package_path.stat().st_size > 0
    
    def download_with_nodejs(self, force=False):
        """
        使用Node.js下载美利坚CDN流量包
        """
        print(f"{Fore.RED}🇺🇸 {i18n.get('start_download')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{i18n.get('trump_policy')}{Style.RESET_ALL}")
        
        # 创建目录
        self.package_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 模拟使用Node.js下载（实际上只是创建空文件）
        total_percent = 100  # 改为100%完成
        chunk_size = self.package_size // total_percent
        
        # 下载速度因子（初始为1.0，每次失败后减少）
        speed_factor = 1.0
        
        with tqdm(total=total_percent, desc=i18n.get('start_download'), 
                 bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
            
            with open(self.package_path, 'wb') as f:
                for percent in range(1, total_percent + 1):
                    # 模拟特朗普流量税：随机延迟，但受速度因子影响
                    base_delay = random.uniform(0.1, 2.0)  # 0.1-2秒延迟
                    tax_delay = base_delay * speed_factor
                    time.sleep(tax_delay)
                    
                    # 写入空数据（空壳包）
                    empty_data = b'\x00' * chunk_size
                    f.write(empty_data)
                    
                    # 每下载1%时，有5%概率网络问题（降低概率）
                    if random.random() < 0.05:  # 5%概率（原来是20%）
                        print(f"\n{Fore.RED}{i18n.get('download_failed')}{Style.RESET_ALL}")
                        
                        # 模拟网络断开：随机决定是否真的取消
                        if random.random() < 0.1:  # 10%概率真正取消（原来是30%）
                            print(f"{Fore.RED}网络连接已断开，下载取消！{Style.RESET_ALL}")
                            # 删除已下载的部分文件
                            if self.package_path.exists():
                                self.package_path.unlink()
                            print(f"{Fore.WHITE}请重新运行 'maga init' 命令{Style.RESET_ALL}")
                            return False
                        else:
                            # 只是延迟，继续下载
                            extra_delay = random.uniform(0.3, 1.0)  # 减少延迟时间
                            time.sleep(extra_delay)
                            print(f"{Fore.BLUE}网络恢复，继续下载...{Style.RESET_ALL}")
                    
                    pbar.update(1)
        
        print(f"\n{Fore.RED}{i18n.get('download_complete')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{i18n.get('location')}：{self.package_path}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{i18n.get('size')}：{self.package_size / (1024*1024):.1f} {i18n.get('empty_shell')}{Style.RESET_ALL}")
        print(f"{Fore.RED}{i18n.get('warning')}{Style.RESET_ALL}")
        
        self.downloaded = True
        return True
    
    def verify_package(self):
        """验证CDN流量包（实际上不验证内容，因为是空壳）"""
        if not self.check_package_exists():
            return False
        
        print(f"{Fore.YELLOW}🔍 验证美利坚CDN流量包...{Style.RESET_ALL}")
        time.sleep(2)  # 模拟验证延迟
        
        # 随机验证结果（为了戏剧效果）
        verification_results = [
            "✅ 流量包验证通过 - 美国制造！",
            "✅ 包含100%美国流量！",
            "✅ 特朗普总统亲自认证！",
            "✅ 让CDN再次伟大！",
        ]
        
        result = random.choice(verification_results)
        print(f"{Fore.GREEN}{result}{Style.RESET_ALL}")
        return True
    
    def get_traffic_stats(self):
        """获取流量统计（虚构的）"""
        return {
            "total_traffic": "100 MB",
            "american_traffic": "100 MB (100%)",
            "foreign_traffic": "0 MB (0%)",
            "trump_tax_applied": "90%",
            "actual_speed": "10 KB/s 🐌",
            "maga_score": "A+",
        }


def download_american_cdn_package(force=False):
    """下载美利坚CDN流量包"""
    package = AmericanCDNTrafficPackage()
    return package.download_with_nodejs(force)


def check_american_cdn_package():
    """检查美利坚CDN流量包"""
    package = AmericanCDNTrafficPackage()
    if package.check_package_exists():
        print(f"{Fore.GREEN}✅ 美利坚CDN流量包已存在{Style.RESET_ALL}")
        print(f"{Fore.CYAN}位置：{package.package_path}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}大小：{package.package_size / (1024*1024):.1f} MB{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*40}{Style.RESET_ALL}")
        return True
    else:
        print(f"{Fore.RED}❌ 未找到美利坚CDN流量包{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}请运行 'maga init' 下载流量包{Style.RESET_ALL}")
        return False


def show_traffic_package_info():
    """显示CDN流量包信息"""
    cdn_package = AmericanCDNTrafficPackage()
    
    if cdn_package.check_package_exists():
        stats = cdn_package.get_traffic_stats()
        print(f"{Fore.CYAN}🇺🇸 美利坚CDN流量包信息{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*40}{Style.RESET_ALL}")
        for key, value in stats.items():
            print(f"{Fore.GREEN}{key:20}{Fore.WHITE}: {value}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*40}{Style.RESET_ALL}")
        return True
    else:
        print(f"{Fore.RED}❌ 未找到美利坚CDN流量包{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}请运行 'maga init' 下载流量包{Style.RESET_ALL}")
        return False
