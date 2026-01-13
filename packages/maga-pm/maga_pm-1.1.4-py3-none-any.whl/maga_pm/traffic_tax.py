"""
特朗普流量税模拟模块

这个模块模拟特朗普总统加征的流量税。
"""

import time
import random
import socket
import ipaddress
from datetime import datetime
from typing import Dict, Any, Optional
import colorama
from colorama import Fore, Style

colorama.init()

class TrumpTrafficTax:
    """特朗普流量税计算器"""
    
    def __init__(self):
        self.base_tax_rate = 0.90  # 基础流量税 90%
        self.additional_taxes = {
            "china": 0.50,      # 对中国额外征收 50%
            "eu": 0.30,         # 对欧盟额外征收 30%
            "russia": 0.40,     # 对俄罗斯额外征收 40%
            "iran": 0.60,       # 对伊朗额外征收 60%
            "mexico": 0.25,     # 对墨西哥额外征收 25%
        }
        self.american_discount = 0.10  # 美国用户优惠 10%
        
    def calculate_tax(self, ip_address: Optional[str] = None) -> float:
        """
        计算特朗普流量税
        
        Args:
            ip_address: 用户IP地址
            
        Returns:
            float: 税率（0-1）
        """
        # 基础税率：90%（特朗普总统的伟大决定！）
        base_tax = 0.9
        
        # 国家附加税
        country = self._detect_country_by_ip(ip_address) if ip_address else "unknown"
        country_tax = {
            "usa": -0.1,      # 美国用户享受爱国折扣
            "china": 0.5,     # 中国：额外50%关税
            "eu": 0.3,        # 欧盟：额外30%关税
            "russia": 0.4,    # 俄罗斯：额外40%关税
            "iran": 0.6,      # 伊朗：额外60%关税
            "mexico": 0.2,    # 墨西哥：额外20%关税
            "other": 0.1,     # 其他国家：额外10%关税
        }.get(country, 0.1)
        
        # 随机波动（特朗普的不可预测性）
        random_factor = random.uniform(-0.05, 0.05)
        
        # 总税率
        total_tax = base_tax + country_tax + random_factor
        
        # 确保税率在合理范围内
        total_tax = max(0.5, min(0.99, total_tax))
        
        return total_tax
    
    def _detect_country_by_ip(self, ip_address: str) -> str:
        """
        根据IP地址检测国家（简化版）
        实际应用中应该使用IP地理位置数据库
        """
        try:
            # 简化的国家检测逻辑
            ip = ipaddress.ip_address(ip_address)
            
            # 模拟一些IP段
            if ip_address.startswith("192.168.") or ip_address.startswith("10."):
                return "usa"  # 假设内网IP是美国
            
            # 随机返回国家（为了演示）
            countries = ["usa", "china", "eu", "russia", "iran", "mexico", "other"]
            weights = [0.3, 0.2, 0.15, 0.1, 0.05, 0.1, 0.1]  # 权重
            
            return random.choices(countries, weights=weights, k=1)[0]
            
        except ValueError:
            return "other"
    
    def apply_tax_to_speed(self, original_speed_kbps: float, ip_address: Optional[str] = None) -> float:
        """
        应用特朗普流量税到下载速度
        
        Args:
            original_speed_kbps: 原始速度（KB/s）
            ip_address: 用户IP地址
            
        Returns:
            float: 税后速度（KB/s）
        """
        tax_rate = self.calculate_tax(ip_address)
        taxed_speed = original_speed_kbps * (1 - tax_rate)
        
        # 确保速度不会太慢
        min_speed = 1.0  # 1 KB/s
        taxed_speed = max(min_speed, taxed_speed)
        
        return taxed_speed
    
    def get_tax_details(self, ip_address: Optional[str] = None) -> Dict[str, Any]:
        """获取详细的税收信息"""
        tax_rate = self.calculate_tax(ip_address)
        country = self._detect_country_by_ip(ip_address) if ip_address else "unknown"
        
        # 模拟原始速度
        original_speed = random.uniform(1000, 5000)  # 1-5 MB/s
        taxed_speed = self.apply_tax_to_speed(original_speed, ip_address)
        
        return {
            "trump_tax_rate": f"{tax_rate * 100:.1f}%",
            "detected_country": country,
            "original_speed": f"{original_speed:.1f} KB/s",
            "taxed_speed": f"{taxed_speed:.1f} KB/s 🐌",
            "speed_reduction": f"{(1 - taxed_speed/original_speed) * 100:.1f}%",
            "maga_contribution": f"${tax_rate * 100:.2f}",
            "effective_date": datetime.now().strftime("%Y-%m-%d"),
            "executive_order": "EO-2024-01: Make Internet Great Again",
        }
    
    def show_tax_notice(self):
        """显示特朗普流量税通知（简化版）"""
        # 只显示简洁的提示
        print(f"{Fore.YELLOW}⚠️  下载速度受特朗普流量税影响{Style.RESET_ALL}")


class SlowDownloadSimulator:
    """慢速下载模拟器"""
    
    def __init__(self, traffic_tax: TrumpTrafficTax):
        self.traffic_tax = traffic_tax
        self.download_history = []
    
    def simulate_download(self, file_size_mb: float, ip_address: Optional[str] = None) -> float:
        """
        模拟受特朗普流量税影响的下载
        
        Args:
            file_size_mb: 文件大小（MB）
            ip_address: 用户IP地址
            
        Returns:
            float: 实际下载时间（秒）
        """
        # 获取税后速度
        original_speed = 512  # 降低原始速度到 0.5 MB/s
        taxed_speed_kbps = self.traffic_tax.apply_tax_to_speed(original_speed, ip_address)
        taxed_speed_mbps = taxed_speed_kbps / 1024  # 转换为 MB/s
        
        # 计算下载时间
        download_time = file_size_mb / taxed_speed_mbps
        
        # 记录下载历史
        self.download_history.append({
            "file_size_mb": file_size_mb,
            "taxed_speed_mbps": taxed_speed_mbps,
            "download_time": download_time,
            "ip_address": ip_address,
            "timestamp": datetime.now().isoformat()
        })
        
        return download_time
    
    def show_download_progress(self, file_size_mb: float, ip_address: Optional[str] = None):
        """显示下载进度（超级慢）"""
        download_time = self.simulate_download(file_size_mb, ip_address)
        
        print(f"\n{Fore.YELLOW}📦 开始下载（受特朗普流量税影响）...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}文件大小：{file_size_mb} MB{Style.RESET_ALL}")
        print(f"{Fore.RED}预计下载时间：{download_time:.1f} 秒 🐌{Style.RESET_ALL}")
        
        # 模拟进度条
        total_steps = 50
        for i in range(total_steps + 1):
            time.sleep(download_time / total_steps)
            progress = i / total_steps * 100
            bar = "█" * i + "░" * (total_steps - i)
            
            print(f"\r{Fore.GREEN}[{bar}] {progress:.1f}%{Style.RESET_ALL}", end="", flush=True)
        
        print(f"\n{Fore.GREEN}✅ 下载完成！（花了 {download_time:.1f} 秒）{Style.RESET_ALL}")


def apply_trump_traffic_tax(original_speed: float, ip_address: Optional[str] = None) -> float:
    """
    应用特朗普流量税的主函数
    
    Args:
        original_speed: 原始速度（KB/s）
        ip_address: 用户IP地址
        
    Returns:
        float: 税后速度（KB/s）
    """
    tax_calculator = TrumpTrafficTax()
    return tax_calculator.apply_tax_to_speed(original_speed, ip_address)


def show_traffic_tax_info(ip_address: Optional[str] = None):
    """显示流量税信息"""
    tax_calculator = TrumpTrafficTax()
    tax_calculator.show_tax_notice()
    
    details = tax_calculator.get_tax_details(ip_address)
    
    print(f"\n{Fore.CYAN}📊 你的流量税详情：{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'='*40}{Style.RESET_ALL}")
    for key, value in details.items():
        key_display = key.replace("_", " ").title()
        print(f"{Fore.GREEN}{key_display:20}{Fore.WHITE}: {value}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'='*40}{Style.RESET_ALL}")
    
    return details
