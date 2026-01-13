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
from .usa_colors import USAColors
from .i18n import i18n
from .real_pip_manager import real_pip

__all__ = [
    'download_american_cdn_package',
    'apply_trump_traffic_tax',
    'TrumpPolicySimulator',
    'MAGAPackageManager',
    'USAColors',
    'i18n',
    'real_pip',
]