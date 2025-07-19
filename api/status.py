#!/usr/bin/env python3
"""
状态查询API端点 - Vercel Serverless Function
"""

from flask import Flask, jsonify

app = Flask(__name__)

# 这需要和 process.py 共享状态，但在无服务器环境中这很困难
# 简化版本，返回基本状态
@app.route('/')
def get_status():
    """获取处理状态"""
    # 在真实的无服务器环境中，我们需要使用外部存储（如Redis）来共享状态
    # 这里返回一个简化的响应
    return jsonify({
        'running': False,
        'progress': 0,
        'message': 'Status endpoint ready',
        'output': [],
        'error': None,
        'session_id': None,
        'result_files': []
    })