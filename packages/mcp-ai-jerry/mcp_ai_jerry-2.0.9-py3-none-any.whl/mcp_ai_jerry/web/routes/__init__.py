#!/usr/bin/env python3
"""
Web UI 路由模组
==============

提供 Web UI 的路由设置和处理。
"""

from .main_routes import setup_routes
from .auth_routes import router as auth_router, is_licensed, check_and_verify


__all__ = ["setup_routes", "auth_router", "is_licensed", "check_and_verify"]
