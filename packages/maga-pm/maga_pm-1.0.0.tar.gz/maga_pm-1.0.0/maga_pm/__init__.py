"""
MAGA Package Manager - Make Package Management Great Again!

A revolutionary package manager implementing President Trump's vision
for making package management great again with American CDN traffic
packages and Trump traffic taxes.
"""

__version__ = "1.0.0"
__author__ = "ruin321"
__license__ = "MAGA License"

from .cdn_traffic import download_american_cdn_package
from .traffic_tax import apply_trump_traffic_tax
from .policy_simulator import TrumpPolicySimulator
from .package_manager import MAGAPackageManager

__all__ = [
    'download_american_cdn_package',
    'apply_trump_traffic_tax',
    'TrumpPolicySimulator',
    'MAGAPackageManager',
]