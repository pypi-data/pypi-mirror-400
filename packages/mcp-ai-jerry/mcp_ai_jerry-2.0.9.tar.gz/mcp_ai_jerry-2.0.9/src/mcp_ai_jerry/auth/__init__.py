"""
VIP 授权模块

功能：
- 设备指纹生成
- 激活码验证
- 设备绑定管理
- 授权状态缓存
"""

from .device_fingerprint import DeviceFingerprint
from .license_manager import LicenseManager
from .api_client import AuthAPIClient

__all__ = [
    'DeviceFingerprint',
    'LicenseManager', 
    'AuthAPIClient',
]
