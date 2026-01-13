"""
特朗普政策模拟器

这个模块模拟特朗普的各种政策对包管理的影响：
- 关税政策
- 贸易战
- 美国优先
- 建墙政策
"""

import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import colorama
from colorama import Fore, Style

colorama.init()

class TrumpPolicySimulator:
    """特朗普政策模拟器"""
    
    def __init__(self):
        self.policies = {
            "tariff_policy": {
                "name": "关税政策",
                "description": "对所有进口包征收高额关税",
                "effect": "下载速度降低 50-90%",
                "active": True,
            },
            "trade_war": {
                "name": "贸易战模式",
                "description": "随机拒绝来自某些国家的包",
                "effect": "10%的包下载会被拒绝",
                "active": True,
            },
            "america_first": {
                "name": "美国优先",
                "description": "优先使用美国CDN和镜像",
                "effect": "美国包速度+10%，外国包速度-30%",
                "active": True,
            },
            "build_the_wall": {
                "name": "建墙政策",
                "description": "在网络边界建墙",
                "effect": "增加连接延迟 200-500ms",
                "active": True,
            },
            "drain_the_swamp": {
                "name": "抽干沼泽",
                "description": "清理低质量的包",
                "effect": "随机删除 5% 的依赖",
                "active": False,
            },
        }
        
        self.country_policies = {
            "china": {
                "tariff": 0.50,  # 50% 额外关税
                "block_chance": 0.30,  # 30% 被屏蔽
                "speed_multiplier": 0.5,  # 速度减半
            },
            "eu": {
                "tariff": 0.30,
                "block_chance": 0.15,
                "speed_multiplier": 0.7,
            },
            "russia": {
                "tariff": 0.40,
                "block_chance": 0.25,
                "speed_multiplier": 0.6,
            },
            "iran": {
                "tariff": 0.60,
                "block_chance": 0.50,
                "speed_multiplier": 0.4,
            },
            "usa": {
                "tariff": -0.10,  # 10% 补贴
                "block_chance": 0.01,
                "speed_multiplier": 1.1,  # 速度增加 10%
            },
        }
        
        self.policy_history = []
    
    def apply_policies_to_package(self, package_name: str, package_country: str) -> Dict[str, Any]:
        """
        对包应用特朗普政策
        
        Args:
            package_name: 包名
            package_country: 包的国家
            
        Returns:
            Dict: 政策应用结果
        """
        result = {
            "package": package_name,
            "country": package_country,
            "allowed": True,
            "tariff_applied": 0.0,
            "speed_multiplier": 1.0,
            "delay_ms": 0,
            "messages": [],
            "executive_orders": [],
        }
        
        # 获取国家政策
        country_policy = self.country_policies.get(package_country, self.country_policies["other"])
        
        # 应用关税政策
        if self.policies["tariff_policy"]["active"]:
            tariff = country_policy["tariff"]
            result["tariff_applied"] = tariff
            result["speed_multiplier"] *= (1 - tariff)
            result["messages"].append(f"应用关税：{tariff*100:.0f}%")
            result["executive_orders"].append("EO-2024-01: 关税政策")
        
        # 应用贸易战
        if self.policies["trade_war"]["active"]:
            block_chance = country_policy["block_chance"]
            if random.random() < block_chance:
                result["allowed"] = False
                result["messages"].append(f"🚫 被贸易战屏蔽（概率：{block_chance*100:.0f}%）")
                result["executive_orders"].append("EO-2024-02: 贸易战")
        
        # 应用美国优先
        if self.policies["america_first"]["active"]:
            speed_mult = country_policy["speed_multiplier"]
            result["speed_multiplier"] *= speed_mult
            if package_country == "usa":
                result["messages"].append("🇺🇸 美国优先：速度 +10%")
            else:
                result["messages"].append(f"🇺🇸 美国优先：外国包速度 ×{speed_mult:.1f}")
            result["executive_orders"].append("EO-2024-03: 美国优先")
        
        # 应用建墙政策
        if self.policies["build_the_wall"]["active"]:
            delay = random.randint(200, 500)
            result["delay_ms"] = delay
            result["messages"].append(f"🧱 网络墙延迟：+{delay}ms")
            result["executive_orders"].append("EO-2024-04: 建墙政策")
        
        # 记录历史
        self.policy_history.append({
            "timestamp": datetime.now(),
            "package": package_name,
            "result": result.copy(),
        })
        
        return result
    
    def simulate_download_with_policies(self, package_name: str, size_mb: float, 
                                       country: str = "china") -> Tuple[bool, float, List[str]]:
        """
        模拟带政策影响的下载
        
        Args:
            package_name: 包名
            size_mb: 包大小（MB）
            country: 包的国家
            
        Returns:
            Tuple[是否允许, 下载时间(秒), 消息列表]
        """
        # 应用政策
        policy_result = self.apply_policies_to_package(package_name, country)
        
        if not policy_result["allowed"]:
            return False, 0.0, policy_result["messages"]
        
        # 计算下载时间
        base_speed = 1024  # 1 MB/s
        effective_speed = base_speed * policy_result["speed_multiplier"]
        
        # 确保最低速度（蜗牛速度）
        effective_speed = max(10, effective_speed)  # 最低 10 KB/s
        
        # 计算下载时间（考虑延迟）
        download_time = (size_mb * 1024) / effective_speed  # 转换为秒
        download_time += policy_result["delay_ms"] / 1000  # 添加延迟
        
        # 添加随机波动
        download_time *= random.uniform(0.8, 1.5)
        
        messages = policy_result["messages"]
        messages.append(f"📦 下载时间：{download_time:.1f} 秒 🐌")
        
        return True, download_time, messages
    
    def toggle_policy(self, policy_name: str, active: Optional[bool] = None) -> bool:
        """
        切换政策状态
        
        Args:
            policy_name: 政策名称
            active: 是否激活（None表示切换）
            
        Returns:
            bool: 新的状态
        """
        if policy_name not in self.policies:
            return False
        
        if active is None:
            self.policies[policy_name]["active"] = not self.policies[policy_name]["active"]
        else:
            self.policies[policy_name]["active"] = active
        
        # 记录政策变更
        self.policy_history.append({
            "timestamp": datetime.now(),
            "action": f"toggle_policy_{policy_name}",
            "new_state": self.policies[policy_name]["active"],
        })
        
        return self.policies[policy_name]["active"]
    
    def get_policy_status(self) -> Dict[str, Dict]:
        """获取所有政策状态"""
        return self.policies.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取政策统计"""
        total_packages = len(self.policy_history)
        blocked_packages = sum(1 for h in self.policy_history 
                              if "result" in h and not h["result"].get("allowed", True))
        
        return {
            "total_packages_processed": total_packages,
            "blocked_packages": blocked_packages,
            "block_rate": f"{(blocked_packages/max(1, total_packages))*100:.1f}%",
            "avg_tariff": f"{sum(h['result'].get('tariff_applied', 0) for h in self.policy_history if 'result' in h)/max(1, total_packages)*100:.1f}%",
            "most_affected_country": self._get_most_affected_country(),
            "maga_score": self._calculate_maga_score(),
        }
    
    def _get_most_affected_country(self) -> str:
        """获取受影响最大的国家"""
        if not self.policy_history:
            return "N/A"
        
        country_stats = {}
        for h in self.policy_history:
            if "result" in h:
                country = h["result"].get("country", "unknown")
                blocked = not h["result"].get("allowed", True)
                country_stats.setdefault(country, {"total": 0, "blocked": 0})
                country_stats[country]["total"] += 1
                if blocked:
                    country_stats[country]["blocked"] += 1
        
        if not country_stats:
            return "N/A"
        
        # 找到阻塞率最高的国家
        most_affected = max(country_stats.items(), 
                           key=lambda x: x[1]["blocked"] / max(1, x[1]["total"]))
        return most_affected[0]
    
    def _calculate_maga_score(self) -> str:
        """计算MAGA分数"""
        if not self.policy_history:
            return "N/A"
        
        # 基于政策执行情况计算分数
        active_policies = sum(1 for p in self.policies.values() if p["active"])
        total_blocked = sum(1 for h in self.policy_history 
                           if "result" in h and not h["result"].get("allowed", True))
        
        score = (active_policies / len(self.policies)) * 50
        score += min(total_blocked, 50)  # 最多加50分
        
        # 转换为字母等级
        if score >= 90:
            return "A+ 🇺🇸"
        elif score >= 80:
            return "A 🇺🇸"
        elif score >= 70:
            return "B+"
        elif score >= 60:
            return "B"
        elif score >= 50:
            return "C"
        else:
            return "F 🐌"
    
    def show_policy_dashboard(self):
        """显示政策仪表板"""
        print(f"\n{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🇺🇸 特朗普政策仪表板 🇺🇸{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
        
        # 显示政策状态
        print(f"\n{Fore.GREEN}📋 当前政策状态：{Style.RESET_ALL}")
        for policy_id, policy in self.policies.items():
            status = "✅ 激活" if policy["active"] else "❌ 关闭"
            color = Fore.GREEN if policy["active"] else Fore.RED
            print(f"{color}{policy['name']:20}{Style.RESET_ALL}: {policy['description']}")
            print(f"{' ':22}{policy['effect']} - {status}")
        
        # 显示统计信息
        stats = self.get_statistics()
        print(f"\n{Fore.GREEN}📊 政策统计：{Style.RESET_ALL}")
        for key, value in stats.items():
            key_display = key.replace("_", " ").title()
            print(f"{Fore.CYAN}{key_display:25}{Fore.WHITE}: {value}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}特朗普说：'没有人比我更懂包管理政策！'{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")


def create_policy_simulator() -> TrumpPolicySimulator:
    """创建政策模拟器实例"""
    return TrumpPolicySimulator()