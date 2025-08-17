#!/usr/bin/env python3
"""
QR码处理工具 - Vercel一体化API
"""

import os
import tempfile
import uuid
import json
import time
import mimetypes
import base64
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from PIL import Image

try:
    from pyzbar import pyzbar
    import qrcode
    import qrcode.image.svg
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

app = Flask(__name__, static_folder='../public', static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# 支持的图片格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_qr_image(image_data, options):
    """处理单个图片的QR码"""
    results = []
    
    try:
        # 获取步骤顺序和激活步骤
        step_order = options.get('stepOrder', ['extract', 'transparent', 'svg', 'invert'])
        active_steps = options.get('activeSteps', ['extract'])
        
        print(f"处理步骤顺序: {step_order}")
        print(f"激活的步骤: {active_steps}")
        
        # 如果extract步骤未激活，直接返回空结果
        if 'extract' not in active_steps:
            print("extract步骤未激活，跳过QR码检测")
            return []
        
        # 解码base64图片
        if image_data.startswith('data:image'):
            # 移除data URL前缀
            header, data = image_data.split(',', 1)
            image_bytes = base64.b64decode(data)
        else:
            image_bytes = base64.b64decode(image_data)
        
        # 转换为numpy数组
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return []
        
        # 检测QR码
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        qr_codes = pyzbar.decode(gray)
        
        # 如果没有检测到QR码，尝试颜色反转后再次检测
        if not qr_codes:
            print("未检测到QR码，尝试颜色反转后重新检测...")
            inverted_gray = 255 - gray
            qr_codes = pyzbar.decode(inverted_gray)
            if qr_codes:
                print(f"颜色反转后成功检测到 {len(qr_codes)} 个QR码")
                # 使用反转后的图像作为处理基础
                image = cv2.cvtColor(inverted_gray, cv2.COLOR_GRAY2BGR)
            else:
                print("颜色反转后仍未检测到QR码")
                return []  # 如果没有检测到QR码，直接返回空结果
        
        for i, qr_code in enumerate(qr_codes):
            x, y, w, h = qr_code.rect
            
            # 添加5%边距
            margin_x = int(w * 0.05)
            margin_y = int(h * 0.05)
            
            start_x = max(0, x - margin_x)
            start_y = max(0, y - margin_y)
            end_x = min(image.shape[1], x + w + margin_x)
            end_y = min(image.shape[0], y + h + margin_y)
            
            # 提取QR码区域
            qr_region = image[start_y:end_y, start_x:end_x]
            qr_data = qr_code.data.decode('utf-8', errors='ignore')
            
            print(f"处理QR码 {i+1}: {qr_data[:50]}...")
            
            # 按照stepOrder的顺序处理每个步骤
            for step in step_order:
                if step not in active_steps:
                    print(f"跳过步骤 '{step}' (未激活)")
                    continue
                    
                print(f"执行步骤 '{step}'")
                    
                if step == 'extract':
                    # 基础QR码提取
                    _, buffer = cv2.imencode('.png', qr_region)
                    qr_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    results.append({
                        'name': f'qr_code_{i+1}.png',
                        'type': 'image',
                        'data': f'data:image/png;base64,{qr_base64}',
                        'qr_data': qr_data
                    })
                    
                elif step == 'transparent':
                    # 透明背景版本
                    try:
                        pil_image = Image.fromarray(cv2.cvtColor(qr_region, cv2.COLOR_BGR2RGB))
                        rgba_img = pil_image.convert('RGBA')
                        data = np.array(rgba_img)
                        
                        # 将白色背景设为透明
                        white_mask = (data[:, :, 0] >= 240) & (data[:, :, 1] >= 240) & (data[:, :, 2] >= 240)
                        data[white_mask] = [255, 255, 255, 0]
                        
                        transparent_img = Image.fromarray(data, 'RGBA')
                        import io
                        img_buffer = io.BytesIO()
                        transparent_img.save(img_buffer, format='PNG')
                        transparent_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                        
                        results.append({
                            'name': f'qr_code_{i+1}_transparent.png',
                            'type': 'image',
                            'data': f'data:image/png;base64,{transparent_base64}',
                            'qr_data': qr_data
                        })
                    except Exception as e:
                        print(f"透明背景处理错误: {e}")
                        
                elif step == 'svg':
                    # SVG版本
                    try:
                        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
                        qr.add_data(qr_data)
                        qr.make(fit=True)
                        
                        factory = qrcode.image.svg.SvgPathImage
                        svg_img = qr.make_image(image_factory=factory)
                        
                        import io
                        svg_buffer = io.BytesIO()
                        svg_img.save(svg_buffer)
                        svg_data = svg_buffer.getvalue().decode('utf-8')
                        
                        results.append({
                            'name': f'qr_code_{i+1}.svg',
                            'type': 'svg',
                            'data': svg_data,
                            'qr_data': qr_data
                        })
                    except Exception as e:
                        print(f"SVG处理错误: {e}")
                        
                elif step == 'invert':
                    # 反色版本
                    try:
                        inverted = 255 - qr_region
                        _, buffer = cv2.imencode('.png', inverted)
                        inverted_base64 = base64.b64encode(buffer).decode('utf-8')
                        
                        results.append({
                            'name': f'qr_code_{i+1}_inverted.png',
                            'type': 'image',
                            'data': f'data:image/png;base64,{inverted_base64}',
                            'qr_data': qr_data
                        })
                    except Exception as e:
                        print(f"颜色反转处理错误: {e}")
        
        return results
        
    except Exception as e:
        print(f"Processing error: {e}")
        return []

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/api')
def api_home():
    return jsonify({'message': 'QR Processor API', 'status': 'ready'})

@app.route('/api/process', methods=['POST'])
def process():
    """处理QR码 - 同步处理，立即返回结果"""
    try:
        if not DEPENDENCIES_AVAILABLE:
            return jsonify({'error': 'Missing dependencies'}), 500
        
        files = request.files.getlist('files')
        options_json = request.form.get('options', '{}')
        options = json.loads(options_json)
        
        if not files or all(f.filename == '' for f in files):
            return jsonify({'error': 'No files uploaded'}), 400
        
        all_results = []
        
        for file in files:
            if file and allowed_file(file.filename):
                # 读取文件内容
                file_content = file.read()
                file_base64 = base64.b64encode(file_content).decode('utf-8')
                
                # 处理图片
                results = process_qr_image(file_base64, options)
                all_results.extend(results)
        
        print(f"Processing completed. Found {len(all_results)} results:")  # 调试日志
        for i, result in enumerate(all_results):
            print(f"  Result {i+1}: {result.get('name', 'Unknown')} - {result.get('type', 'Unknown')}")  # 调试日志
        
        return jsonify({
            'success': True,
            'message': f'Found {len(all_results)} QR codes',
            'files': all_results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def status():
    return jsonify({
        'running': False,
        'progress': 100,
        'message': 'Ready',
        'dependencies': DEPENDENCIES_AVAILABLE
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'dependencies': DEPENDENCIES_AVAILABLE,
        'version': '2.0.0'
    })

@app.route('/api/results')
def results():
    return jsonify({'files': []})

@app.route('/api/download')
def download():
    return jsonify({'error': 'Use direct download from results'}), 404

@app.route('/api/preview/<path:path>')
def preview(path):
    return jsonify({'error': 'Use data URLs from results'}), 404

if __name__ == '__main__':
    # 从环境变量获取配置
    debug_mode = os.getenv('FLASK_ENV', 'production') == 'development'
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    app.run(debug=debug_mode, host=host, port=port)