"""
授权 API 客户端

与 Go 授权服务器通信，处理激活和验证请求
"""

import httpx
import logging
from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .device_fingerprint import DeviceFingerprint

logger = logging.getLogger(__name__)


class LicenseType(str, Enum):
    """授权类型（时间卡）"""
    MONTHLY = "monthly"      # 月卡 (31天)
    QUARTERLY = "quarterly"  # 季卡 (90天)
    HALFYEAR = "halfyear"    # 半年卡 (180天)
    YEARLY = "yearly"        # 年卡 (365天)


class ActivationResult(str, Enum):
    """激活结果"""
    SUCCESS = "success"
    INVALID_CODE = "invalid_code"
    ALREADY_USED = "already_used"
    MAX_DEVICES = "max_devices"
    EXPIRED = "expired"
    NETWORK_ERROR = "network_error"
    SERVER_ERROR = "server_error"


@dataclass
class LicenseInfo:
    """授权信息"""
    license_key: str
    activation_code: str
    device_id: str
    expires_at: Optional[datetime]
    is_valid: bool
    license_type: str = "standard"  # 授权类型: standard, monthly, yearly, lifetime
    device_count: int = 1  # 已绑定设备数
    max_devices: int = 2   # 最大设备数
    
    def days_remaining(self) -> int:
        """剩余天数"""
        if not self.expires_at:
            return 9999  # 永久有效
        # 确保时区一致性
        now = datetime.now()
        expires = self.expires_at
        # 如果 expires_at 有时区信息，转换为无时区
        if expires.tzinfo is not None:
            expires = expires.replace(tzinfo=None)
        delta = expires - now
        return max(0, delta.days)
    
    def get_type_display(self) -> str:
        """获取授权类型显示名称"""
        type_names = {
            "standard": "标准版",
            "monthly": "月卡",
            "quarterly": "季卡",
            "halfyear": "半年卡",
            "yearly": "年卡",
            "lifetime": "终身",
        }
        return type_names.get(self.license_type, self.license_type)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "license_key": self.license_key,
            "activation_code": self.activation_code,
            "device_id": self.device_id,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_valid": self.is_valid,
            "license_type": self.license_type,
            "device_count": self.device_count,
            "max_devices": self.max_devices,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "LicenseInfo":
        """从字典创建"""
        expires_at = None
        if data.get("expires_at"):
            try:
                expires_at = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
            except:
                pass
        
        return cls(
            license_key=data.get("license_key", ""),
            activation_code=data.get("activation_code", ""),
            device_id=data.get("device_id", ""),
            expires_at=expires_at,
            is_valid=data.get("valid", True),
            license_type=data.get("license_type", "standard"),
            device_count=data.get("device_count", 1),
            max_devices=data.get("max_devices", 2),
        )


class AuthAPIClient:
    """授权 API 客户端 - 连接 Go 服务"""
    
    # Go 授权服务器地址
    DEFAULT_SERVER_URL = "http://47.93.143.37:8000"
    
    def __init__(self, server_url: Optional[str] = None, timeout: float = 30.0):
        """
        初始化 API 客户端
        
        Args:
            server_url: 授权服务器地址
            timeout: 请求超时时间（秒）
        """
        self.server_url = server_url or self.DEFAULT_SERVER_URL
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """获取 HTTP 客户端"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={
                    "User-Agent": "MCP-AI-Jerry/1.0",
                    "Content-Type": "application/json",
                }
            )
        return self._client
    
    async def close(self) -> None:
        """关闭客户端"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def activate(self, activation_code: str) -> tuple[ActivationResult, Optional[LicenseInfo]]:
        """
        激活设备
        
        Args:
            activation_code: 激活码
            
        Returns:
            (激活结果, 授权信息)
        """
        device_info = DeviceFingerprint.get_device_info()
        device_id = device_info["fingerprint"]
        
        try:
            client = await self._get_client()
            response = await client.post(
                f"{self.server_url}/api/v1/activate",
                json={
                    "activation_code": activation_code.strip().upper(),
                    "device_id": device_id,
                    "device_info": str(device_info),
                }
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get("success"):
                license_info = LicenseInfo(
                    license_key=data.get("license_key", ""),
                    activation_code=activation_code.strip().upper(),
                    device_id=device_id,
                    expires_at=datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00")) if data.get("expires_at") else None,
                    is_valid=True,
                    license_type=data.get("license_type", "standard"),
                    device_count=data.get("device_count", 1),
                    max_devices=data.get("max_devices", 2),
                )
                logger.info(f"激活成功: {license_info.license_key}")
                return ActivationResult.SUCCESS, license_info
            
            # 解析错误
            error = data.get("error", "").lower()
            if "not found" in error:
                return ActivationResult.INVALID_CODE, None
            elif "exhausted" in error or "max" in error:
                return ActivationResult.MAX_DEVICES, None
            elif "expired" in error:
                return ActivationResult.EXPIRED, None
            elif "already" in error:
                # 设备已激活，返回现有信息
                license_info = LicenseInfo(
                    license_key=data.get("license_key", ""),
                    activation_code=activation_code.strip().upper(),
                    device_id=device_id,
                    expires_at=datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00")) if data.get("expires_at") else None,
                    is_valid=True,
                    license_type=data.get("license_type", "standard"),
                    device_count=data.get("device_count", 1),
                    max_devices=data.get("max_devices", 2),
                )
                return ActivationResult.SUCCESS, license_info
            
            return ActivationResult.INVALID_CODE, None
                
        except httpx.TimeoutException:
            logger.error("请求超时")
            return ActivationResult.NETWORK_ERROR, None
        except httpx.RequestError as e:
            logger.error(f"网络错误: {e}")
            return ActivationResult.NETWORK_ERROR, None
        except Exception as e:
            logger.error(f"激活失败: {e}")
            return ActivationResult.SERVER_ERROR, None
    
    async def verify(self, license_key: str) -> tuple[bool, Optional[LicenseInfo]]:
        """
        验证授权状态
        
        Args:
            license_key: 授权密钥
            
        Returns:
            (是否有效, 授权信息)
        """
        device_id = DeviceFingerprint.get_fingerprint()
        
        try:
            client = await self._get_client()
            response = await client.post(
                f"{self.server_url}/api/v1/verify",
                json={
                    "license_key": license_key,
                    "device_id": device_id,
                }
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get("valid"):
                license_info = LicenseInfo(
                    license_key=license_key,
                    activation_code="",
                    device_id=device_id,
                    expires_at=datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00")) if data.get("expires_at") else None,
                    is_valid=True,
                    license_type=data.get("license_type", "standard"),
                    device_count=data.get("device_count", 1),
                    max_devices=data.get("max_devices", 2),
                )
                return True, license_info
            
            return False, None
            
        except Exception as e:
            logger.error(f"验证失败: {e}")
            return False, None
    
    async def deactivate(self, license_key: str, reason: str = "") -> tuple[bool, Optional[str]]:
        """
        解绑当前设备
        
        Args:
            license_key: 授权密钥
            reason: 解绑原因
            
        Returns:
            (是否成功, 错误消息或None)
        """
        device_id = DeviceFingerprint.get_fingerprint()
        
        try:
            client = await self._get_client()
            response = await client.post(
                f"{self.server_url}/api/v1/deactivate",
                json={
                    "license_key": license_key,
                    "device_id": device_id,
                    "reason": reason or "User requested deactivation",
                }
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get("success"):
                return True, None
            
            return False, data.get("error", "解绑失败")
            
        except Exception as e:
            logger.error(f"解绑失败: {e}")
            return False, f"网络错误: {str(e)}"
