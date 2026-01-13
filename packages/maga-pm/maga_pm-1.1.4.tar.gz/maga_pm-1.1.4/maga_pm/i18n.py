"""
多语言支持模块
基于时区和系统语言提供多语言支持
"""

import os
import locale
import time
from datetime import datetime
import pytz

class I18NManager:
    """多语言管理器"""
    
    def __init__(self):
        self.current_language = self.detect_language()
        self.translations = self.load_translations()
    
    def detect_language(self):
        """检测系统语言和时区"""
        # 获取系统语言
        system_lang = locale.getdefaultlocale()[0]
        
        # 获取时区
        try:
            tz = time.tzname[0]
        except:
            tz = "UTC"
        
        # 优先使用中文（根据用户界面显示）
        # 如果系统语言包含中文，使用中文
        if system_lang and 'zh' in system_lang.lower():
            return 'zh_CN'  # 简体中文
        
        # 否则检查环境变量
        env_lang = os.environ.get('LANG', '')
        if 'zh' in env_lang.lower():
            return 'zh_CN'
        
        # 最后检查时区，如果是中国时区，使用中文
        if 'CST' in tz or 'China' in tz or 'Asia/Shanghai' in tz:
            return 'zh_CN'
        
        # 基于语言和时区确定语言
        if system_lang:
            if 'en' in system_lang.lower():
                # 检查时区
                if 'America' in tz or 'US' in tz or 'EST' in tz or 'PST' in tz or 'CST' in tz or 'MST' in tz:
                    return 'en_US'  # 美式英语
                else:
                    return 'en_GB'  # 英式英语
            elif 'es' in system_lang.lower():
                return 'es_ES'  # 西班牙语
            elif 'fr' in system_lang.lower():
                return 'fr_FR'  # 法语
            elif 'de' in system_lang.lower():
                return 'de_DE'  # 德语
            elif 'ja' in system_lang.lower():
                return 'ja_JP'  # 日语
            elif 'ko' in system_lang.lower():
                return 'ko_KR'  # 韩语
            elif 'ru' in system_lang.lower():
                return 'ru_RU'  # 俄语
        
        # 默认返回中文（根据用户需求）
        return 'zh_CN'
    
    def load_translations(self):
        """加载翻译"""
        translations = {
            'en_US': {
                'banner_title': "MAGA PACKAGE MANAGER",
                'version': "Version",
                'author': "Author",
                'license': "License",
                'slogan': "Make Package Management Great Again!",
                'policy_system': "Policy-controlled package management system",
                'start_download': "Starting download of American CDN traffic package...",
                'trump_policy': "This is President Trump's great policy: all traffic must support the American CDN industry!",
                'download_failed': "Download failed, network not smooth!",
                'trump_fixing': "President Trump is fixing the network...",
                'network_optimized': "Network optimized! Next download will be faster!",
                'download_complete': "American CDN traffic package download complete!",
                'location': "Location",
                'size': "Size",
                'empty_shell': "MB (empty shell)",
                'warning': "Warning: Without this package, MAGA-PM cannot run!",
                'usa_first': "America is always first!",
                'maga_pm': "MAGA Package Manager",
                'maga_license': "MAGA License",
                'init_command': "Initialize MAGA-PM (download CDN traffic package)",
                'install_command': "Install package (affected by Trump policies)",
                'list_command': "List installed packages",
                'cdn_command': "Display CDN traffic package information",
                'stats_command': "Display statistics",
                'maga_command': "Execute MAGA optimization",
                'help_command': "Display help information",
                'force_option': "Force re-download of CDN traffic package",
                'country_option': "Package country (default random)",
                'core_features': "Core Features",
                'cdn_feature': "American CDN traffic package (must be downloaded to run)",
                'tax_feature': "Trump traffic tax (country-based download speed control)",
                'trade_war_feature': "Trade war mode (randomly reject packages from certain countries)",
                'usa_first_feature': "America First policy (American packages prioritized)",
            },
            'zh_CN': {
                'banner_title': "MAGA 包管理器",
                'version': "版本",
                'author': "作者",
                'license': "许可证",
                'slogan': "让包管理再次伟大！",
                'policy_system': "政策控制的包管理系统",
                'start_download': "开始下载美利坚CDN流量包...",
                'trump_policy': "这是特朗普总统的伟大政策：所有流量都要支持美国CDN产业！",
                'download_failed': "下载失败，网络不通畅！",
                'trump_fixing': "特朗普总统正在修复网络...",
                'network_optimized': "网络已优化！下次下载速度将加快！",
                'download_complete': "美利坚CDN流量包下载完成！",
                'location': "位置",
                'size': "大小",
                'empty_shell': "MB（空壳）",
                'warning': "注意：没有这个包，MAGA-PM无法运行！",
                'usa_first': "美国是永远的第一！",
                'maga_pm': "MAGA包管理器",
                'maga_license': "MAGA许可证",
                'init_command': "初始化MAGA-PM（下载CDN流量包）",
                'install_command': "安装包（受特朗普政策影响）",
                'list_command': "列出已安装的包",
                'cdn_command': "显示CDN流量包信息",
                'stats_command': "显示统计信息",
                'maga_command': "执行MAGA优化",
                'help_command': "显示帮助信息",
                'force_option': "强制重新下载CDN流量包",
                'country_option': "包的国家（默认随机）",
                'core_features': "核心特性",
                'cdn_feature': "美利坚CDN流量包（必须下载才能运行）",
                'tax_feature': "特朗普流量税（基于国家的下载速度控制）",
                'trade_war_feature': "贸易战模式（随机拒绝某些国家的包）",
                'usa_first_feature': "美国优先政策（美国包优先处理）",
            },
            'en_GB': {
                'banner_title': "MAGA PACKAGE MANAGER",
                'version': "Version",
                'author': "Author",
                'license': "Licence",
                'slogan': "Make Package Management Great Again!",
                'policy_system': "Policy-controlled package management system",
                'start_download': "Starting download of American CDN traffic package...",
                'trump_policy': "This is President Trump's great policy: all traffic must support the American CDN industry!",
                'download_failed': "Download failed, network not smooth!",
                'trump_fixing': "President Trump is fixing the network...",
                'network_optimized': "Network optimised! Next download will be faster!",
                'download_complete': "American CDN traffic package download complete!",
                'location': "Location",
                'size': "Size",
                'empty_shell': "MB (empty shell)",
                'warning': "Warning: Without this package, MAGA-PM cannot run!",
                'usa_first': "America is always first!",
                'maga_pm': "MAGA Package Manager",
                'maga_license': "MAGA Licence",
                'init_command': "Initialise MAGA-PM (download CDN traffic package)",
                'install_command': "Install package (affected by Trump policies)",
                'list_command': "List installed packages",
                'cdn_command': "Display CDN traffic package information",
                'stats_command': "Display statistics",
                'maga_command': "Execute MAGA optimisation",
                'help_command': "Display help information",
                'force_option': "Force re-download of CDN traffic package",
                'country_option': "Package country (default random)",
                'core_features': "Core Features",
                'cdn_feature': "American CDN traffic package (must be downloaded to run)",
                'tax_feature': "Trump traffic tax (country-based download speed control)",
                'trade_war_feature': "Trade war mode (randomly reject packages from certain countries)",
                'usa_first_feature': "America First policy (American packages prioritised)",
            },
        }
        
        # 如果没有对应语言的翻译，使用英语
        if self.current_language not in translations:
            self.current_language = 'en_US'
        
        return translations[self.current_language]
    
    def get(self, key, default=None):
        """获取翻译"""
        return self.translations.get(key, default)
    
    def format(self, key, **kwargs):
        """格式化翻译文本"""
        text = self.get(key, key)
        return text.format(**kwargs)
    
    def get_language_info(self):
        """获取语言信息"""
        return {
            'language': self.current_language,
            'timezone': time.tzname[0] if time.tzname else 'UTC',
            'locale': locale.getdefaultlocale()[0] or 'en_US',
        }

# 全局实例
i18n = I18NManager()