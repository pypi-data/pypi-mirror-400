"""
美国专属颜色模块
为MAGA包管理器提供红白蓝配色方案
"""

import colorama
from colorama import Fore, Style

class USAColors:
    """美国专属颜色类"""
    
    # 美国国旗颜色
    RED = Fore.RED
    WHITE = Fore.WHITE
    BLUE = Fore.BLUE
    
    # 组合颜色
    RED_WHITE = f"{Fore.RED}{Fore.WHITE}"
    RED_BLUE = f"{Fore.RED}{Fore.BLUE}"
    WHITE_BLUE = f"{Fore.WHITE}{Fore.BLUE}"
    
    # 美国主题颜色
    PATRIOTIC = f"{Fore.RED}{Fore.WHITE}{Fore.BLUE}"
    FREEDOM = f"{Fore.BLUE}{Fore.WHITE}"
    LIBERTY = f"{Fore.RED}{Fore.WHITE}"
    
    @staticmethod
    def usa_text(text):
        """将文本转换为美国国旗颜色（红白蓝交替）"""
        result = ""
        for i, char in enumerate(text):
            if i % 3 == 0:
                result += f"{Fore.RED}{char}"
            elif i % 3 == 1:
                result += f"{Fore.WHITE}{char}"
            else:
                result += f"{Fore.BLUE}{char}"
        result += Style.RESET_ALL
        return result
    
    @staticmethod
    def usa_banner(text):
        """创建美国国旗风格的横幅"""
        border = f"{Fore.RED}{'*'*60}{Style.RESET_ALL}"
        stars = f"{Fore.WHITE}🇺🇸 "*10 + Style.RESET_ALL
        return f"""
{border}
{stars}
{USAColors.usa_text(text)}
{stars}
{border}
"""
    
    @staticmethod
    def success(text):
        """成功消息（绿色带美国国旗）"""
        return f"{Fore.GREEN}✅ {text} 🇺🇸{Style.RESET_ALL}"
    
    @staticmethod
    def warning(text):
        """警告消息（黄色带美国国旗）"""
        return f"{Fore.YELLOW}⚠️  {text} 🇺🇸{Style.RESET_ALL}"
    
    @staticmethod
    def error(text):
        """错误消息（红色带美国国旗）"""
        return f"{Fore.RED}❌ {text} 🇺🇸{Style.RESET_ALL}"
    
    @staticmethod
    def info(text):
        """信息消息（蓝色带美国国旗）"""
        return f"{Fore.BLUE}ℹ️  {text} 🇺🇸{Style.RESET_ALL}"
    
    @staticmethod
    def trump_quote(text):
        """特朗普名言样式"""
        return f"{Fore.MAGENTA}🇺🇸 特朗普说：{text} 🇺🇸{Style.RESET_ALL}"
    
    @staticmethod
    def maga_text(text):
        """MAGA风格文本"""
        return f"{Fore.RED}M{Fore.WHITE}A{Fore.BLUE}G{Fore.RED}A{Style.RESET_ALL}: {text}"

# 初始化colorama
colorama.init()