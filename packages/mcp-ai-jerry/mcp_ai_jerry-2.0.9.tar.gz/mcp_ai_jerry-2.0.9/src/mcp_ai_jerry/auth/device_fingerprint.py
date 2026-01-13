"""
设备指纹生成模块

生成唯一的设备标识符，用于设备绑定验证
"""

import hashlib
import platform
import subprocess
import uuid
import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DeviceFingerprint:
    """设备指纹生成器"""
    
    _cached_fingerprint: Optional[str] = None
    # 持久化指纹文件路径
    _fingerprint_file = Path.home() / ".mcp-ai-jerry" / ".device_id"
    
    @classmethod
    def get_fingerprint(cls) -> str:
        """
        获取设备指纹
        
        优先使用持久化的指纹，确保跨进程一致性。
        如果没有持久化指纹，则基于硬件信息生成并保存。
        
        Returns:
            设备指纹 (32位十六进制字符串)
        """
        if cls._cached_fingerprint:
            return cls._cached_fingerprint
        
        # 尝试从文件加载已有指纹
        fingerprint = cls._load_fingerprint()
        if fingerprint:
            cls._cached_fingerprint = fingerprint
            return fingerprint
        
        try:
            # 生成新的稳定指纹
            fingerprint = cls._generate_stable_fingerprint()
            
            # 保存到文件
            cls._save_fingerprint(fingerprint)
            cls._cached_fingerprint = fingerprint
            
            logger.debug(f"设备指纹生成成功: {fingerprint[:8]}...")
            return fingerprint
            
        except Exception as e:
            logger.error(f"设备指纹生成失败: {e}")
            # 使用备用方案
            return cls._get_fallback_fingerprint()
    
    @classmethod
    def _load_fingerprint(cls) -> Optional[str]:
        """从文件加载已保存的指纹"""
        try:
            if cls._fingerprint_file.exists():
                fingerprint = cls._fingerprint_file.read_text().strip()
                if len(fingerprint) == 32:
                    logger.debug(f"从文件加载设备指纹: {fingerprint[:8]}...")
                    return fingerprint
        except Exception as e:
            logger.warning(f"加载设备指纹失败: {e}")
        return None
    
    @classmethod
    def _save_fingerprint(cls, fingerprint: str) -> None:
        """保存指纹到文件"""
        try:
            cls._fingerprint_file.parent.mkdir(parents=True, exist_ok=True)
            cls._fingerprint_file.write_text(fingerprint)
            # 设置文件权限为仅用户可读写
            cls._fingerprint_file.chmod(0o600)
            logger.debug("设备指纹已保存到文件")
        except Exception as e:
            logger.warning(f"保存设备指纹失败: {e}")
    
    @classmethod
    def _generate_stable_fingerprint(cls) -> str:
        """生成稳定的设备指纹"""
        # 收集稳定的设备信息
        info_parts = [
            cls._get_machine_id(),
            platform.system(),
            platform.machine(),
            platform.processor(),
            platform.node(),
        ]
        
        # 组合并哈希
        combined = "|".join(str(p) for p in info_parts if p)
        fingerprint = hashlib.sha256(combined.encode()).hexdigest()[:32]
        
        return fingerprint
    
    @classmethod
    def _get_machine_id(cls) -> str:
        """获取机器ID - 使用更稳定的方法"""
        system = platform.system()
        
        try:
            if system == "Darwin":  # macOS
                # 使用 IOPlatformSerialNumber 或 hardware UUID
                result = subprocess.run(
                    ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    import re
                    # 查找 IOPlatformUUID
                    match = re.search(r'"IOPlatformUUID"\s*=\s*"([^"]+)"', result.stdout)
                    if match:
                        return match.group(1)
            
            elif system == "Linux":
                # 尝试读取 machine-id
                for path in ["/etc/machine-id", "/var/lib/dbus/machine-id"]:
                    try:
                        with open(path, 'r') as f:
                            machine_id = f.read().strip()
                            if machine_id:
                                return machine_id
                    except FileNotFoundError:
                        continue
            
            elif system == "Windows":
                # 使用 wmic 获取主板序列号
                result = subprocess.run(
                    ["wmic", "baseboard", "get", "serialnumber"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        return lines[1].strip()
        
        except Exception as e:
            logger.debug(f"获取系统特定机器ID失败: {e}")
        
        # 回退到 uuid.getnode()，但这不够稳定
        try:
            mac = uuid.getnode()
            return str(mac)
        except Exception:
            return ""
    
    @classmethod
    def _get_fallback_fingerprint(cls) -> str:
        """备用指纹生成方案"""
        try:
            # 使用用户目录和系统信息
            fallback_info = f"{os.path.expanduser('~')}|{platform.system()}|{platform.node()}"
            return hashlib.sha256(fallback_info.encode()).hexdigest()[:32]
        except Exception:
            # 最后的备用方案
            return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:32]
    
    @classmethod
    def get_device_info(cls) -> dict:
        """
        获取设备信息摘要
        
        Returns:
            包含设备信息的字典
        """
        return {
            "fingerprint": cls.get_fingerprint(),
            "os": platform.system(),
            "os_version": platform.version(),
            "machine": platform.machine(),
            "hostname": platform.node()[:20],  # 截断防止泄露过多信息
            "python_version": platform.python_version(),
        }
    
    @classmethod
    def reset_cache(cls) -> None:
        """重置缓存的指纹（用于测试）"""
        cls._cached_fingerprint = None
