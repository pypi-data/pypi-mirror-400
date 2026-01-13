"""
MAGA包管理器测试
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from maga_pm.package_manager import MAGAPackageManager
from maga_pm.cdn_traffic import AmericanCDNTrafficPackage
from maga_pm.traffic_tax import TrumpTrafficTax
from maga_pm.policy_simulator import TrumpPolicySimulator


class TestAmericanCDNTrafficPackage(unittest.TestCase):
    """测试美利坚CDN流量包"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.package = AmericanCDNTrafficPackage()
        
        # 修改包路径到临时目录
        self.original_path = self.package.package_path
        self.package.package_path = Path(self.temp_dir) / "cdn_traffic.pkg"
    
    def tearDown(self):
        # 恢复原始路径
        self.package.package_path = self.original_path
    
    def test_check_package_exists(self):
        """测试检查包是否存在"""
        # 初始状态应该不存在
        self.assertFalse(self.package.check_package_exists())
        
        # 创建空文件
        self.package.package_path.touch()
        self.assertTrue(self.package.check_package_exists())
    
    @patch('time.sleep')
    @patch('random.uniform')
    @patch('random.choice')
    def test_download_with_nodejs(self, mock_choice, mock_uniform, mock_sleep):
        """测试下载功能"""
        # 设置mock
        mock_uniform.return_value = 0.5
        mock_choice.return_value = "测试特朗普名言"
        
        # 执行下载
        result = self.package.download_with_nodejs()
        
        # 验证结果
        self.assertTrue(result)
        self.assertTrue(self.package.package_path.exists())
        self.assertTrue(self.package.downloaded)
        
        # 验证文件大小
        file_size = self.package.package_path.stat().st_size
        self.assertEqual(file_size, self.package.package_size)


class TestTrumpTrafficTax(unittest.TestCase):
    """测试特朗普流量税"""
    
    def setUp(self):
        self.tax_calculator = TrumpTrafficTax()
    
    def test_calculate_tax(self):
        """测试税收计算"""
        # 测试基础税
        tax = self.tax_calculator.calculate_tax()
        self.assertGreaterEqual(tax, 0.10)
        self.assertLessEqual(tax, 0.99)
    
    def test_apply_tax_to_speed(self):
        """测试应用税收到速度"""
        original_speed = 1000  # 1000 KB/s
        
        # 测试税后速度
        taxed_speed = self.tax_calculator.apply_tax_to_speed(original_speed)
        
        # 验证速度被降低
        self.assertLess(taxed_speed, original_speed)
        
        # 验证最低速度
        self.assertGreaterEqual(taxed_speed, 1.0)
    
    def test_get_tax_details(self):
        """测试获取税收详情"""
        details = self.tax_calculator.get_tax_details("192.168.1.1")
        
        # 验证返回字典包含必要的键
        expected_keys = [
            'trump_tax_rate',
            'detected_country',
            'original_speed',
            'taxed_speed',
            'speed_reduction',
            'maga_contribution',
            'effective_date',
            'executive_order',
        ]
        
        for key in expected_keys:
            self.assertIn(key, details)


class TestTrumpPolicySimulator(unittest.TestCase):
    """测试特朗普政策模拟器"""
    
    def setUp(self):
        self.policy_simulator = TrumpPolicySimulator()
    
    def test_apply_policies_to_package(self):
        """测试应用政策到包"""
        result = self.policy_simulator.apply_policies_to_package("test-package", "china")
        
        # 验证返回字典包含必要的键
        expected_keys = [
            'package',
            'country',
            'allowed',
            'tariff_applied',
            'speed_multiplier',
            'delay_ms',
            'messages',
            'executive_orders',
        ]
        
        for key in expected_keys:
            self.assertIn(key, result)
    
    def test_toggle_policy(self):
        """测试切换政策状态"""
        # 获取初始状态
        initial_state = self.policy_simulator.policies["tariff_policy"]["active"]
        
        # 切换状态
        new_state = self.policy_simulator.toggle_policy("tariff_policy")
        
        # 验证状态已切换
        self.assertNotEqual(initial_state, new_state)
        
        # 再次切换应该恢复原状
        final_state = self.policy_simulator.toggle_policy("tariff_policy")
        self.assertEqual(initial_state, final_state)
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        # 先处理一些包
        self.policy_simulator.apply_policies_to_package("pkg1", "china")
        self.policy_simulator.apply_policies_to_package("pkg2", "usa")
        
        stats = self.policy_simulator.get_statistics()
        
        # 验证统计信息
        self.assertIn("total_packages_processed", stats)
        self.assertIn("blocked_packages", stats)
        self.assertIn("block_rate", stats)
        self.assertIn("maga_score", stats)


class TestMAGAPackageManager(unittest.TestCase):
    """测试MAGA包管理器"""
    
    def setUp(self):
        # 使用临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建配置目录
        self.config_dir = Path(self.temp_dir) / ".maga"
        self.config_dir.mkdir(exist_ok=True)
        
        # 创建CDN包文件
        cdn_file = self.config_dir / "cdn_traffic.pkg"
        cdn_file.touch()
        
        # 创建配置
        config = {
            "cdn_package_required": False,  # 测试时不需要CDN包
            "install_count": 0,
            "blocked_count": 0,
        }
        
        config_file = self.config_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f)
    
    @patch('maga_pm.package_manager.Path.home')
    def test_install_package(self, mock_home):
        """测试安装包"""
        # Mock home目录
        mock_home.return_value = Path(self.temp_dir)
        
        # 创建包管理器
        pm = MAGAPackageManager()
        
        # Mock下载模拟器
        with patch.object(pm.download_simulator, 'show_download_progress'):
            # 安装包
            result = pm.install("test-package")
            
            # 验证安装成功
            self.assertTrue(result)
            
            # 验证包列表已更新
            packages = pm._load_packages()
            self.assertIn("test-package", packages)
    
    @patch('maga_pm.package_manager.Path.home')
    def test_list_packages(self, mock_home):
        """测试列出包"""
        # Mock home目录
        mock_home.return_value = Path(self.temp_dir)
        
        # 创建包管理器并添加测试包
        pm = MAGAPackageManager()
        
        # 添加测试包到包列表
        packages = {
            "requests": {
                "version": "2.28.0",
                "country": "usa",
                "size_mb": 1.5,
                "install_time": "2024-01-01 12:00:00",
                "download_time": 150.0,
                "trump_tax_applied": True,
            }
        }
        
        packages_file = self.config_dir / "packages.json"
        with open(packages_file, 'w') as f:
            json.dump(packages, f)
        
        # 测试列出包（应该不抛出异常）
        try:
            pm.list_packages()
            success = True
        except:
            success = False
        
        self.assertTrue(success)


if __name__ == "__main__":
    unittest.main()