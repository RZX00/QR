#!/usr/bin/env python3
"""
Vercel 入口点文件
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

# 这是 Vercel 需要的标准入口点
def handler(request):
    return app