"""
本地授权管理器

管理授权状态的本地缓存和验证
"""

import hashlib
import hmac
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from .device_fingerprint import DeviceFingerprint
from .api_client import AuthAPIClient, LicenseInfo, ActivationResult

logger = logging.getLogger(__name__)


@dataclass
class CachedLicense:
    """缓存的授权信息"""
    license_info: LicenseInfo
    cached_at: datetime
    last_verified: datetime
    
    def to_dict(self) -> dict:
        return {
            "license_info": self.license_info.to_dict(),
            "cached_at": self.cached_at.isoformat(),
            "last_verified": self.last_verified.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CachedLicense":
        return cls(
            license_info=LicenseInfo.from_dict(data["license_info"]),
            cached_at=datetime.fromisoformat(data["cached_at"]),
            last_verified=datetime.fromisoformat(data["last_verified"]),
        )


class LicenseManager:
    """授权管理器"""
    
    # 离线宽限期（小时）- 设为0表示不允许离线使用
    OFFLINE_GRACE_PERIOD_HOURS = 0
    
    # 验证间隔（小时）- 每24小时验证一次
    VERIFY_INTERVAL_HOURS = 24
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        初始化授权管理器
        
        Args:
            cache_dir: 缓存目录，默认为用户目录下的 .mcp-ai-jerry
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".mcp-ai-jerry"
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.license_file = self.cache_dir / "license.json"
        
        self._cached_license: Optional[CachedLicense] = None
        self._api_client: Optional[AuthAPIClient] = None
        
        # 加载缓存
        self._load_cache()
    
    def _get_sign_key(self) -> bytes:
        """
        动态生成签名密钥 - 每个设备+每个授权唯一
        
        使用设备指纹 + 服务器下发的 license_key 组合生成密钥，
        这样即使攻击者获得源码也无法伪造其他设备的签名。
        """
        device_fp = DeviceFingerprint.get_fingerprint()
        
        # 如果有缓存的授权信息，使用 license_key 作为服务器盐值
        # 这样每个授权的签名密钥都不同
        if self._cached_license and self._cached_license.license_info.license_key:
            server_component = self._cached_license.license_info.license_key
        else:
            # 没有授权时使用设备指纹的哈希作为临时组件
            server_component = hashlib.sha256(device_fp.encode()).hexdigest()[:32]
        
        # 使用 PBKDF2 派生强密钥，增加破解难度
        key = hashlib.pbkdf2_hmac(
            'sha256',
            device_fp.encode(),
            server_component.encode(),
            100000  # 迭代次数
        )
        return key
    
    def _generate_signature(self, data: dict) -> str:
        """为缓存数据生成签名"""
        # 移除签名字段后计算
        data_copy = {k: v for k, v in data.items() if k != '_signature'}
        data_str = json.dumps(data_copy, sort_keys=True, ensure_ascii=False)
        signature = hmac.new(
            self._get_sign_key(),
            data_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _verify_signature(self, data: dict) -> bool:
        """验证缓存数据的签名"""
        stored_signature = data.get('_signature')
        if not stored_signature:
            logger.warning("缓存文件缺少签名，可能被篡改")
            return False
        
        expected_signature = self._generate_signature(data)
        if not hmac.compare_digest(stored_signature, expected_signature):
            logger.warning("缓存文件签名验证失败，可能被篡改")
            return False
        
        return True
    
    def _load_cache(self) -> None:
        """从文件加载缓存的授权信息"""
        if not self.license_file.exists():
            return
        
        try:
            with open(self.license_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 先临时加载 license_info 用于生成正确的签名密钥
            # 这样 _get_sign_key() 可以使用 license_key 而不是临时组件
            try:
                temp_license = CachedLicense.from_dict(data)
                self._cached_license = temp_license  # 临时设置，用于签名密钥生成
            except Exception as e:
                logger.warning(f"授权缓存格式错误: {e}")
                self._cached_license = None
                return
            
            # 现在验证签名（使用正确的签名密钥）
            if not self._verify_signature(data):
                logger.warning("授权缓存签名验证失败，清除缓存")
                self._cached_license = None
                self._clear_cache()
                return
            
            logger.debug("授权缓存加载成功")
            
        except Exception as e:
            logger.warning(f"授权缓存加载失败: {e}")
            self._cached_license = None
    
    def _save_cache(self, cached_license: CachedLicense) -> None:
        """保存授权信息到缓存"""
        try:
            data = cached_license.to_dict()
            # 添加签名
            data['_signature'] = self._generate_signature(data)
            
            with open(self.license_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self._cached_license = cached_license
            logger.debug("授权缓存保存成功")
            
        except Exception as e:
            logger.error(f"授权缓存保存失败: {e}")
    
    def _clear_cache(self) -> None:
        """清除授权缓存"""
        if self.license_file.exists():
            self.license_file.unlink()
        self._cached_license = None
        logger.info("授权缓存已清除")
    
    def _get_api_client(self) -> AuthAPIClient:
        """获取 API 客户端"""
        if self._api_client is None:
            self._api_client = AuthAPIClient()
        return self._api_client
    
    def is_licensed(self) -> bool:
        """
        检查是否已授权（快速本地检查）
        
        Returns:
            是否有有效授权
        """
        if not self._cached_license:
            return False
        
        license_info = self._cached_license.license_info
        
        # 检查是否过期
        if license_info.expires_at:
            expires = license_info.expires_at
            # 确保时区一致性
            if expires.tzinfo is not None:
                expires = expires.replace(tzinfo=None)
            if datetime.now() > expires:
                logger.info("授权已过期")
                return False
        
        # 检查是否需要在线验证（不允许离线使用）
        if self.OFFLINE_GRACE_PERIOD_HOURS == 0:
            # 离线宽限期为0，每次都需要验证
            last_verified = self._cached_license.last_verified
            verify_deadline = last_verified + timedelta(hours=self.VERIFY_INTERVAL_HOURS)
            
            if datetime.now() > verify_deadline:
                logger.warning("需要在线验证授权状态")
                return False
        
        return True
    
    def needs_online_verify(self) -> bool:
        """
        检查是否需要在线验证
        
        使用随机抖动(jitter)来分散验证请求，避免大量设备同时请求
        
        Returns:
            是否需要在线验证
        """
        if not self._cached_license:
            return True
        
        last_verified = self._cached_license.last_verified
        
        # 添加随机抖动：±2小时，避免所有设备同时验证
        import random
        jitter_hours = random.uniform(-2, 2)
        verify_deadline = last_verified + timedelta(hours=self.VERIFY_INTERVAL_HOURS + jitter_hours)
        
        return datetime.now() > verify_deadline
    
    async def activate(self, activation_code: str) -> tuple[ActivationResult, Optional[str]]:
        """
        激活授权
        
        Args:
            activation_code: 激活码
            
        Returns:
            (激活结果, 错误消息或成功消息)
        """
        api_client = self._get_api_client()
        
        try:
            result, license_info = await api_client.activate(activation_code)
            
            if result == ActivationResult.SUCCESS and license_info:
                # 保存授权信息
                cached = CachedLicense(
                    license_info=license_info,
                    cached_at=datetime.now(),
                    last_verified=datetime.now(),
                )
                self._save_cache(cached)
                
                days = license_info.days_remaining()
                return result, f"激活成功！剩余 {days} 天"
            
            # 错误消息映射
            error_messages = {
                ActivationResult.INVALID_CODE: "激活码无效",
                ActivationResult.ALREADY_USED: "激活码已被使用",
                ActivationResult.MAX_DEVICES: "已达到最大设备数限制（2台）",
                ActivationResult.EXPIRED: "激活码已过期",
                ActivationResult.NETWORK_ERROR: "网络连接失败，请检查网络",
                ActivationResult.SERVER_ERROR: "服务器错误，请稍后重试",
            }
            
            return result, error_messages.get(result, "激活失败")
            
        finally:
            await api_client.close()
    
    async def verify_online(self) -> bool:
        """
        在线验证授权状态
        
        Returns:
            授权是否有效
        """
        if not self._cached_license:
            return False
        
        api_client = self._get_api_client()
        
        try:
            license_key = self._cached_license.license_info.license_key
            is_valid, license_info = await api_client.verify(license_key)
            
            if is_valid and license_info:
                # 合并信息，保留 activation_code（verify 不返回它）
                license_info.activation_code = self._cached_license.license_info.activation_code
                # 如果 verify 没有返回 license_type，保留原来的
                if not license_info.license_type or license_info.license_type == "standard":
                    if self._cached_license.license_info.license_type:
                        license_info.license_type = self._cached_license.license_info.license_type
                
                # 更新缓存
                cached = CachedLicense(
                    license_info=license_info,
                    cached_at=self._cached_license.cached_at,
                    last_verified=datetime.now(),
                )
                self._save_cache(cached)
                return True
            
            # 授权无效，清除缓存
            self._clear_cache()
            return False
            
        except Exception as e:
            logger.error(f"在线验证失败: {e}")
            # 网络错误时保持现有状态（在宽限期内）
            return self.is_licensed()
        finally:
            await api_client.close()
    
    async def deactivate(self) -> tuple[bool, Optional[str]]:
        """
        解绑当前设备
        
        Returns:
            (是否成功, 错误消息或None)
        """
        if not self._cached_license:
            return True, None
        
        api_client = self._get_api_client()
        
        try:
            license_key = self._cached_license.license_info.license_key
            success, error_message = await api_client.deactivate(license_key)
            
            if success:
                self._clear_cache()
                return True, None
            
            return False, error_message
            
        finally:
            await api_client.close()
    
    def get_license_info(self) -> Optional[LicenseInfo]:
        """获取当前授权信息"""
        if self._cached_license:
            return self._cached_license.license_info
        return None
    
    def get_status_display(self) -> dict:
        """
        获取授权状态显示信息
        
        Returns:
            状态信息字典
        """
        if not self._cached_license:
            return {
                "status": "未激活",
                "type": "-",
                "expires": None,
                "devices": "-",
            }
        
        license_info = self._cached_license.license_info
        days = license_info.days_remaining()
        
        return {
            "status": "已激活" if self.is_licensed() else "已过期",
            "type": license_info.get_type_display(),
            "expires": f"{days} 天" if days < 9999 else "永久",
            "devices": "已绑定",
        }
