"""
授权相关路由

处理激活、验证、解绑等请求
"""

import logging
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from ...auth import LicenseManager, DeviceFingerprint

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["auth"])

# 模板目录
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# 全局授权管理器实例
_license_manager: LicenseManager | None = None


def get_license_manager() -> LicenseManager:
    """获取授权管理器实例"""
    global _license_manager
    if _license_manager is None:
        _license_manager = LicenseManager()
    return _license_manager


@router.get("/activation", response_class=HTMLResponse)
async def activation_page(request: Request):
    """激活页面"""
    return templates.TemplateResponse("activation.html", {"request": request})


@router.get("/device-info")
async def get_device_info():
    """获取设备信息"""
    device_info = DeviceFingerprint.get_device_info()
    return JSONResponse(device_info)


@router.get("/license-status")
async def get_license_status():
    """获取授权状态（始终从服务器获取最新数据）"""
    manager = get_license_manager()
    
    # 如果有缓存的授权，先在线验证以获取最新的 device_count 等信息
    if manager._cached_license:
        try:
            await manager.verify_online()
        except Exception as e:
            logger.warning(f"在线验证失败，使用缓存数据: {e}")
    
    is_licensed = manager.is_licensed()
    license_info = manager.get_license_info()
    status = manager.get_status_display()
    
    return JSONResponse({
        "is_licensed": is_licensed,
        "license": license_info.to_dict() if license_info else None,
        "status": status,
    })


@router.post("/activate")
async def activate_license(request: Request):
    """激活授权"""
    try:
        data = await request.json()
        activation_code = data.get("activation_code", "").strip()
        
        if not activation_code:
            return JSONResponse({
                "success": False,
                "message": "请输入激活码"
            }, status_code=400)
        
        manager = get_license_manager()
        result, message = await manager.activate(activation_code)
        
        from ...auth.api_client import ActivationResult
        
        logger.info(f"激活结果: {result}, 消息: {message}")
        
        if result == ActivationResult.SUCCESS:
            license_info = manager.get_license_info()
            return JSONResponse({
                "success": True,
                "message": message,
                "license": license_info.to_dict() if license_info else None,
            })
        
        return JSONResponse({
            "success": False,
            "message": message,
        }, status_code=400)
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"激活失败: {e}\n{error_trace}")
        return JSONResponse({
            "success": False,
            "message": f"激活失败: {str(e)}"
        }, status_code=500)


@router.post("/deactivate")
async def deactivate_license():
    """解绑设备"""
    try:
        manager = get_license_manager()
        success, error_message = await manager.deactivate()
        
        if success:
            return JSONResponse({
                "success": True,
                "message": "设备已解绑"
            })
        
        # 返回详细的错误信息，同时使用 error 和 message 字段保证兼容性
        return JSONResponse({
            "success": False,
            "error": error_message or "解绑失败",
            "message": error_message or "解绑失败"
        }, status_code=400)
        
    except Exception as e:
        logger.error(f"解绑失败: {e}")
        return JSONResponse({
            "success": False,
            "error": f"解绑失败: {str(e)}",
            "message": f"解绑失败: {str(e)}"
        }, status_code=500)


@router.post("/verify")
async def verify_license():
    """在线验证授权"""
    try:
        manager = get_license_manager()
        is_valid = await manager.verify_online()
        
        return JSONResponse({
            "is_valid": is_valid,
            "status": manager.get_status_display(),
        })
        
    except Exception as e:
        logger.error(f"验证失败: {e}")
        return JSONResponse({
            "is_valid": False,
            "message": "验证失败"
        }, status_code=500)


def is_licensed() -> bool:
    """
    快速检查是否已授权
    
    供其他模块调用
    """
    return get_license_manager().is_licensed()


async def check_and_verify() -> bool:
    """
    检查授权状态，必要时在线验证
    
    强制在线验证模式：每次调用都会尝试在线验证
    
    Returns:
        是否有有效授权
    """
    manager = get_license_manager()
    
    # 没有缓存的授权信息，直接返回 False
    if not manager._cached_license:
        return False
    
    # 检查授权是否已过期（硬性检查）
    license_info = manager._cached_license.license_info
    if license_info.expires_at:
        from datetime import datetime
        expires = license_info.expires_at
        if expires.tzinfo is not None:
            expires = expires.replace(tzinfo=None)
        if datetime.now() > expires:
            return False
    
    # 始终尝试在线验证
    if manager.needs_online_verify():
        return await manager.verify_online()
    
    # 在验证间隔内，返回本地缓存状态
    return True
