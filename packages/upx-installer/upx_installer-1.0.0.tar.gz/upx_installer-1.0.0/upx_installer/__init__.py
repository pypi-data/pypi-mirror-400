"""
UPX Installer Package
自动安装UPX可执行文件到Windows系统
"""

__version__ = "1.0.0"
__author__ = "UPX Installer Team"

from .installer import install_upx, uninstall_upx, verify_installation

__all__ = ['install_upx', 'uninstall_upx', 'verify_installation']
