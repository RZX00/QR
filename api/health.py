#!/usr/bin/env python3
"""
健康检查API端点 - Vercel Serverless Function
"""

from flask import Flask, jsonify

try:
    from pyzbar import pyzbar
    import qrcode
    import cv2
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

app = Flask(__name__)

@app.route('/')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'dependencies': DEPENDENCIES_AVAILABLE,
        'version': '1.0.0',
        'runtime': 'Vercel Serverless Function'
    })