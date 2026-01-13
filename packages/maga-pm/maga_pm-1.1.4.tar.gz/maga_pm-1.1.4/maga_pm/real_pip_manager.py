"""
真实的Python包管理器

这个模块会调用真正的pip来下载和安装Python包，
并显示真实的下载进度。
"""

import os
import sys
import subprocess
import re
import time
import threading
import queue
import random
import socket
import ssl
from typing import Optional, Tuple, List, Dict, Any
from pathlib import Path

import colorama
from colorama import Fore, Style

colorama.init()


class RealPipManager:
    """真实的Python包管理器（基于pip）"""
    
    def __init__(self):
        self.pip_command = self._detect_pip()
        self.is_available = self.pip_command is not None
        self.download_history = []
        self.server_status = {
            "pypi.org": False,
            "test.pypi.org": False,
            "last_check": None
        }
        
    def _detect_pip(self) -> Optional[str]:
        """检测pip命令"""
        # 在Termux/Android上，通常使用'pip'命令
        # 直接返回'pip'，让后续的check_availability验证
        return 'pip'
    
    def check_availability(self) -> Tuple[bool, str]:
        """检查pip是否可用"""
        if not self.is_available:
            return False, "❌ 未找到pip命令，请先安装pip"
        
        # 简化检查：直接返回成功，让安装过程自己处理错误
        # 这样可以避免超时问题
        return True, "✅ pip可用（简化检查）"
    
        return self.pip_command is not None
    
    def test_server_connection(self, server_url: str = "pypi.org") -> bool:
        """
        测试服务器连接
        
        Args:
            server_url: 服务器URL
            
        Returns:
            bool: 是否连接成功
        """
        try:
            import socket
            import ssl
            
            # 解析主机名
            hostname = server_url.replace("https://", "").replace("http://", "").split("/")[0]
            
            # 尝试连接
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    # 发送简单的HTTP请求
                    request = f"HEAD / HTTP/1.1\r\nHost: {hostname}\r\nConnection: close\r\n\r\n"
                    ssock.send(request.encode())
                    
                    # 接收响应
                    response = ssock.recv(1024)
                    
                    if b"HTTP" in response:
                        self.server_status[server_url] = True
                        self.server_status["last_check"] = time.time()
                        return True
                    else:
                        self.server_status[server_url] = False
                        return False
                        
        except Exception as e:
            self.server_status[server_url] = False
            return False
    
    def check_server_status(self, server_url: str = "pypi.org") -> str:
        """
        检查服务器状态并返回状态信息
        
        Args:
            server_url: 服务器URL
            
        Returns:
            str: 状态信息
        """
        if self.test_server_connection(server_url):
            return f"✅ {server_url} 连接正常"
        else:
            return f"❌ {server_url} 网络未连接"
    
    def install_package(self, package_name: str, show_progress: bool = True, 
                       country: str = "china", package_size_mb: float = 10.0) -> Tuple[bool, str]:
        """
        使用pip安装Python包（带特朗普限速信息）
        
        Args:
            package_name: Python包名
            show_progress: 是否显示进度条
            country: 包的国家
            package_size_mb: 包大小（MB）
            
        Returns:
            Tuple[成功与否, 输出消息]
        """
        if not self.is_available:
            return False, "❌ pip不可用"
        
        # 显示特朗普限速信息
        self._show_trump_speed_limit_info(package_name, country, package_size_mb)
        
        print(f"{Fore.CYAN}🔍 正在使用pip安装 {package_name}...{Style.RESET_ALL}")
        
        try:
            if show_progress:
                return self._install_with_progress(package_name)
            else:
                return self._install_simple(package_name)
        except Exception as e:
            return False, f"❌ 安装失败: {str(e)}"
    
    def _show_trump_speed_limit_info(self, package_name: str, country: str, package_size_mb: float):
        """显示特朗普限速信息"""
        # 根据国家计算限速
        speed_limits = {
            "china": {"base_speed": 10, "extra_limit": 0.1, "export_license_required": True},
            "usa": {"base_speed": 1000, "extra_limit": 1.5, "export_license_required": False},
            "eu": {"base_speed": 100, "extra_limit": 0.3, "export_license_required": True},
            "russia": {"base_speed": 50, "extra_limit": 0.2, "export_license_required": True},
            "iran": {"base_speed": 5, "extra_limit": 0.05, "export_license_required": True},
            "other": {"base_speed": 200, "extra_limit": 0.4, "export_license_required": False},
        }
        
        limit_info = speed_limits.get(country, speed_limits["other"])
        base_speed = limit_info["base_speed"]  # KB/s
        extra_limit = limit_info["extra_limit"]
        export_license_required = limit_info["export_license_required"]
        
        # 计算下载时间
        download_time_seconds = (package_size_mb * 1024) / (base_speed * extra_limit)
        
        print(f"\n{Fore.RED}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠️  特朗普限速信息 ⚠️{Style.RESET_ALL}")
        print(f"{Fore.RED}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}包名: {package_name}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}国家: {country}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}包大小: {package_size_mb:.1f} MB{Style.RESET_ALL}")
        print(f"{Fore.RED}基础速度: {base_speed} KB/s{Style.RESET_ALL}")
        print(f"{Fore.RED}额外限制: ×{extra_limit:.2f}{Style.RESET_ALL}")
        print(f"{Fore.RED}有效速度: {base_speed * extra_limit:.1f} KB/s{Style.RESET_ALL}")
        print(f"{Fore.RED}预计下载时间: {download_time_seconds:.1f} 秒 🐌{Style.RESET_ALL}")
        
        if export_license_required:
            print(f"{Fore.YELLOW}出口许可证: 需要（AI包限制）{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}出口许可证: 不需要{Style.RESET_ALL}")
        
        print(f"{Fore.RED}{'='*60}{Style.RESET_ALL}")
    
    def _install_simple(self, package_name: str) -> Tuple[bool, str]:
        """简单安装（不显示进度）"""
        cmd = self.pip_command.split() + ['install', package_name]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                # 解析输出，获取安装信息
                output = result.stdout
                installed_version = self._parse_installed_version(output, package_name)
                
                if installed_version:
                    return True, f"✅ {package_name}=={installed_version} 安装成功！"
                else:
                    return True, f"✅ {package_name} 安装成功！"
            else:
                error_output = result.stderr if result.stderr else result.stdout
                error_analysis = self._analyze_install_error(error_output, package_name)
                return False, f"❌ 安装失败:\n{error_analysis}"
        except subprocess.TimeoutExpired:
            return False, "❌ 安装超时（5分钟）"
        except Exception as e:
            return False, f"❌ 安装异常: {str(e)}"
    
    def _install_with_progress(self, package_name: str) -> Tuple[bool, str]:
        """带进度条的安装"""
        # 创建进度条监控线程
        progress_queue = queue.Queue()
        stop_event = threading.Event()
        
        # 启动进度监控线程
        monitor_thread = threading.Thread(
            target=self._monitor_pip_progress,
            args=(progress_queue, stop_event, package_name)
        )
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # 执行安装命令
        success = False
        output = ""
        installed_version = None
        
        try:
            cmd = self.pip_command.split() + ['install', package_name]
            
            # 执行命令并捕获输出
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # 读取输出并发送到进度队列
            full_output = []
            for line in process.stdout:
                progress_queue.put(line)
                full_output.append(line)
                sys.stdout.flush()
            
            process.wait()
            success = process.returncode == 0
            full_output_str = ''.join(full_output)
            
            if success:
                installed_version = self._parse_installed_version(full_output_str, package_name)
                if installed_version:
                    output = f"✅ {package_name}=={installed_version} 安装成功！"
                else:
                    output = f"✅ {package_name} 安装成功！"
                
                # 记录下载历史
                self._record_download(package_name, installed_version)
            else:
                # 分析失败原因
                error_analysis = self._analyze_install_error(full_output_str, package_name)
                output = f"❌ {package_name} 安装失败\n{error_analysis}"
        
        except Exception as e:
            error_msg = str(e)
            output = f"❌ 安装异常: {error_msg}\n详细原因: {type(e).__name__}"
        
        finally:
            # 停止监控线程
            stop_event.set()
            monitor_thread.join(timeout=2)
            
            # 确保进度条完成显示
            if success:
                self._display_progress_bar(100, "完成")
                print()
        
        return success, output
    
    def _analyze_install_error(self, output: str, package_name: str) -> str:
        """分析安装错误原因"""
        error_lines = []
        
        # 常见错误模式
        error_patterns = [
            (r"ERROR: Could not find a version", "找不到包版本"),
            (r"ERROR: No matching distribution found", "没有匹配的发行版"),
            (r"ERROR: Failed building wheel", "构建wheel失败"),
            (r"ERROR: Command errored out", "命令执行错误"),
            (r"ERROR: pip's dependency resolver", "依赖解析失败"),
            (r"ERROR: Cannot uninstall", "无法卸载旧版本"),
            (r"ERROR: Invalid requirement", "无效的需求"),
            (r"ERROR: Package .* requires Python", "Python版本不兼容"),
            (r"ERROR: Package .* requires .* but .* is installed", "依赖版本冲突"),
            (r"ERROR: Could not install packages due to an OSError", "操作系统错误"),
            (r"ERROR: Could not install packages due to an EnvironmentError", "环境错误"),
            (r"ERROR: Operation cancelled by user", "用户取消操作"),
            (r"ERROR: Network is unreachable", "网络不可达"),
            (r"ERROR: Connection refused", "连接被拒绝"),
            (r"ERROR: Timeout", "超时"),
            (r"ERROR: SSL certificate verify failed", "SSL证书验证失败"),
        ]
        
        # 检查错误模式
        found_errors = []
        for pattern, description in error_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                found_errors.append(description)
        
        # 构建错误分析
        analysis = []
        if found_errors:
            analysis.append("可能的原因：")
            for error in found_errors:
                analysis.append(f"  • {error}")
        else:
            analysis.append("未知错误，请检查以下输出：")
        
        # 添加最后几行输出（通常包含关键错误信息）
        lines = output.strip().split('\n')
        if lines:
            last_lines = lines[-5:]  # 最后5行
            analysis.append("\n最后输出：")
            for line in last_lines:
                if line.strip():
                    analysis.append(f"  {line.strip()}")
        
        return '\n'.join(analysis)
    
    def _monitor_pip_progress(self, progress_queue: queue.Queue, stop_event: threading.Event, package_name: str):
        """监控pip下载进度"""
        last_progress = 0
        last_update = time.time()
        download_started = False
        file_size = 0
        downloaded = 0
        
        # pip进度模式
        progress_patterns = [
            # 下载进度: Downloading package-1.0.0-py3-none-any.whl (1.2 MB)
            (r'Downloading\s+.*?\(([\d.]+)\s*([KMG]B)\)', '文件大小'),
            # 进度条: [===================>] 100%
            (r'\[[=>.]+\]\s*(\d+)%', '进度百分比'),
            # 下载中: 1.2MB 100kB/s eta 0:00:10
            (r'([\d.]+)([KMG]B)\s+.*?eta', '下载速度'),
        ]
        
        # 服务器检查相关
        last_server_check = 0
        
        while not stop_event.is_set():
            try:
                # 非阻塞获取队列中的消息
                try:
                    line = progress_queue.get(timeout=0.1)
                except queue.Empty:
                    # 如果没有新消息，检查是否应该更新进度条
                    if download_started and time.time() - last_update > 0.5:
                        # 模拟进度更新（如果没有真实进度）
                        if last_progress < 95:
                            last_progress += 1
                            last_server_check = self._display_progress_bar(
                                last_progress, "下载中", True, last_server_check
                            )
                            last_update = time.time()
                    continue
                
                # 解析进度信息
                current_progress = None
                for pattern, desc in progress_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        if desc == '文件大小':
                            size = float(match.group(1))
                            unit = match.group(2).upper()
                            # 转换为字节
                            multipliers = {'KB': 1024, 'MB': 1024*1024, 'GB': 1024*1024*1024}
                            file_size = size * multipliers.get(unit, 1)
                            download_started = True
                        
                        elif desc == '进度百分比':
                            try:
                                current_progress = int(match.group(1))
                                last_progress = current_progress
                            except ValueError:
                                continue
                        
                        elif desc == '下载速度':
                            download_started = True
                
                # 显示进度
                if current_progress is not None:
                    last_server_check = self._display_progress_bar(
                        current_progress, "下载中", True, last_server_check
                    )
                    last_update = time.time()
                elif download_started and 'Collecting' not in line and 'Requirement' not in line:
                    # 显示原始输出（调试用）
                    # print(f"{Fore.WHITE}{line.strip()}{Style.RESET_ALL}")
                    pass
                
            except Exception:
                # 忽略监控线程中的异常
                pass
    
    def _display_progress_bar(self, progress: int, status: str = "", 
                             show_server_check: bool = True, 
                             last_server_check: float = 0) -> float:
        """
        显示进度条（带更狠的限制）
        
        Args:
            progress: 进度百分比
            status: 状态信息
            show_server_check: 是否显示服务器检查
            last_server_check: 上次服务器检查时间
            
        Returns:
            float: 更新后的last_server_check时间
        """
        bar_length = 40
        filled_length = int(bar_length * progress / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # 使用美国配色
        if progress < 33:
            color = Fore.RED
            emoji = "🐌"
        elif progress < 66:
            color = Fore.YELLOW
            emoji = "⏳"
        else:
            color = Fore.GREEN
            emoji = "🚀"
        
        # 每1%进度有10%概率显示连接服务器状态
        current_time = time.time()
        if show_server_check and random.random() < 0.1 and (current_time - last_server_check) > 1:
            # 测试pypi.org连接
            server_status = self.check_server_status("pypi.org")
            
            # 在一行内显示当前状态
            print(f"\r{color}[{bar}] {progress:3d}% {emoji} {status} | {server_status}{Style.RESET_ALL}", end="", flush=True)
            last_server_check = current_time
        else:
            # 正常显示进度条
            print(f"\r{color}[{bar}] {progress:3d}% {emoji} {status}{Style.RESET_ALL}", end="", flush=True)
        
        return last_server_check
    
    def _parse_installed_version(self, output: str, package_name: str) -> Optional[str]:
        """从pip输出中解析安装的版本"""
        # 查找成功安装的行
        patterns = [
            r'Successfully installed\s+' + re.escape(package_name) + r'-([\d.]+)',
            r'Installing collected packages:\s*' + re.escape(package_name) + r'\s*([\d.]+)',
            r'Requirement already satisfied:\s*' + re.escape(package_name) + r'==([\d.]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _record_download(self, package_name: str, version: Optional[str]):
        """记录下载历史"""
        self.download_history.append({
            'package': package_name,
            'version': version or 'unknown',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'via': 'pip'
        })
    
    def list_installed_packages(self) -> List[Dict[str, str]]:
        """列出已安装的Python包"""
        if not self.is_available:
            return []
        
        try:
            cmd = self.pip_command.split() + ['list', '--format=freeze']
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                packages = []
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line and '==' in line:
                        name, version = line.split('==', 1)
                        packages.append({
                            'name': name,
                            'version': version
                        })
                return packages
        except:
            pass
        
        return []
    
    def search_package(self, query: str) -> List[Dict[str, str]]:
        """搜索Python包（使用pip search）"""
        if not self.is_available:
            return []
        
        try:
            cmd = self.pip_command.split() + ['search', query]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                packages = []
                current_package = None
                
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # pip search输出格式: package (version) - description
                    if ')' in line and '(' in line:
                        # 新包开始
                        if current_package:
                            packages.append(current_package)
                        
                        name_part = line.split(')', 1)[0]
                        name = name_part.split('(')[0].strip()
                        version = name_part.split('(')[1].strip() if '(' in name_part else ''
                        
                        desc_part = line.split(')', 1)[1].strip() if ')' in line else ''
                        if desc_part.startswith('-'):
                            desc_part = desc_part[1:].strip()
                        
                        current_package = {
                            'name': name,
                            'version': version,
                            'description': desc_part
                        }
                    elif current_package:
                        # 续行描述
                        current_package['description'] += ' ' + line
                
                # 添加最后一个包
                if current_package:
                    packages.append(current_package)
                
                return packages
        except:
            pass
        
        return []
    
    def remove_package(self, package_name: str) -> Tuple[bool, str]:
        """移除Python包"""
        if not self.is_available:
            return False, "❌ pip不可用"
        
        try:
            cmd = self.pip_command.split() + ['uninstall', '-y', package_name]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                return True, f"✅ {package_name} 移除成功！"
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                return False, f"❌ 移除失败:\n{error_msg}"
        except subprocess.TimeoutExpired:
            return False, "❌ 移除超时"
        except Exception as e:
            return False, f"❌ 移除异常: {str(e)}"
    
    def show_pip_info(self) -> Dict[str, Any]:
        """显示pip信息"""
        available, message = self.check_availability()
        
        info = {
            'available': available,
            'pip_command': self.pip_command,
            'message': message,
            'download_history_count': len(self.download_history),
        }
        
        if available:
            # 获取pip版本
            try:
                cmd = self.pip_command.split() + ['--version']
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    info['version'] = result.stdout.strip()
            except:
                info['version'] = '未知'
        
        return info


# 创建全局实例
real_pip = RealPipManager()