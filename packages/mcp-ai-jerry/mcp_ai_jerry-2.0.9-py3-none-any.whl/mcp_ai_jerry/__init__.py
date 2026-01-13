#!/usr/bin/env python3
"""
MCP AI Jerry
============

智能交互反馈 MCP 服务器，提供 Web UI 和桌面应用双重界面支持。

特色：
- Web UI 介面支援
- 桌面应用程序
- 智慧环境检测
- 命令执行功能
- 图片上传支援
- 现代化深色主题
"""

__version__ = "2.0.6"
__author__ = "Jerry"
__email__ = "jerry@example.com"

import os

from .server import main as run_server

# 导入新的 Web UI 模组
from .web import WebUIManager, get_web_ui_manager, launch_web_feedback_ui, stop_web_ui


# 保持向后兼容性
feedback_ui = None

# 主要导出介面
__all__ = [
    "WebUIManager",
    "__author__",
    "__version__",
    "feedback_ui",
    "get_web_ui_manager",
    "launch_web_feedback_ui",
    "run_server",
    "stop_web_ui",
]


def main():
    """主要入口点，用于 uvx 执行"""
    from .__main__ import main as cli_main

    return cli_main()
