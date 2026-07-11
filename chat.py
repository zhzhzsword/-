"""
图书馆智能服务系统 - 对话式智能助手独立启动脚本
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.chat_agent import chat_interface

if __name__ == "__main__":
    chat_interface()