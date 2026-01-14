#!/usr/bin/env python3
"""
MCP Shouji
==================================

跨平台交互式反馈与命令执行工具。

作者: f
特点: 提供自动化辅助开发中的反馈收集功能。

特色：
- Web UI 介面支援
- 智慧環境檢測
- 命令執行功能
- 圖片上傳支援
- 現代化深色主題
- 重構的模組化架構
"""

__version__ = "2.6.0"
__author__ = "f"
__email__ = "f@gamil.com"

import os

from .server import main as run_server

# 導入新的 Web UI 模組
from .web import WebUIManager, get_web_ui_manager, launch_web_feedback_ui, stop_web_ui


# 保持向後兼容性
feedback_ui = None

# 主要導出介面
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
    """主要入口點，用於 uvx 執行"""
    from .__main__ import main as cli_main

    return cli_main()
