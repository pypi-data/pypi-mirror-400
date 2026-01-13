#!/usr/bin/env python3
"""
回馈结果资料模型

定义回馈收集的资料结构，用于 Web UI 与后端的资料传输。
"""

from typing import TypedDict


class FeedbackResult(TypedDict):
    """回馈结果的型别定义"""

    command_logs: str
    interactive_feedback: str
    images: list[dict]
