#!/usr/bin/env python3
"""
QR码处理工具 - Vercel部署版本
支持原有前端界面的API接口
"""

import os
import sys
import tempfile
import shutil
import uuid
import json
import time
import mimetypes
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import threading
import subprocess
import cv2
import numpy as np
from PIL import Image

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from pyzbar import pyzbar
    import qrcode
    import qrcode.image.svg
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# 支持的图片格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif', 'webp'}

# 全局变量存储处理状态
processing_status = {
    'running': False,
    'progress': 0,
    'message': 'Ready',
    'output': [],
    'error': None,
    'session_id': None,
    'result_files': []
}

# 存储会话数据
sessions = {}

class VercelQRProcessor:
    """适用于Vercel的QR码处理器"""
    
    def __init__(self, margin_ratio=0.05, min_size=50, white_threshold=240, tolerance=15):
        self.margin_ratio = margin_ratio
        self.min_size = min_size
        self.white_threshold = white_threshold
        self.tolerance = tolerance
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        
        # 模拟处理器基础目录
        self.base_dir = Path("/tmp")
        self.temp_dir = self.base_dir / 'temp_uploads'
        self.output_dir = self.base_dir / 'web_output'
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    def allowed_file(self, filename):
        """检查文件扩展名是否允许"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def create_session(self):
        """创建新的处理会话"""
        session_id = str(uuid.uuid4())
        session_dir = self.temp_dir / session_id
        session_dir.mkdir(exist_ok=True)
        
        sessions[session_id] = {
            'upload_dir': session_dir,
            'output_dir': self.output_dir / session_id,
            'files': [],
            'created_at': time.time()
        }
        
        sessions[session_id]['output_dir'].mkdir(exist_ok=True)
        return session_id
    
    def save_uploaded_files(self, files, session_id):
        """保存上传的文件"""
        if session_id not in sessions:
            raise ValueError('Invalid session ID')
        
        session = sessions[session_id]
        saved_files = []
        
        for file in files:
            if file and self.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # 添加时间戳避免文件名冲突
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{int(time.time())}{ext}"
                
                file_path = session['upload_dir'] / filename
                file.save(str(file_path))
                
                saved_files.append({
                    'name': filename,
                    'original_name': file.filename,
                    'path': str(file_path),
                    'size': file_path.stat().st_size
                })
        
        session['files'].extend(saved_files)
        return saved_files
    
    def process_files(self, session_id, options):
        """处理上传的文件"""
        global processing_status
        
        if session_id not in sessions:
            processing_status['error'] = 'Invalid session ID'
            return
        
        session = sessions[session_id]
        
        try:
            processing_status['running'] = True
            processing_status['progress'] = 0
            processing_status['message'] = 'Starting processing...'
            processing_status['output'] = []
            processing_status['error'] = None
            processing_status['session_id'] = session_id
            processing_status['result_files'] = []
            
            # 模拟处理过程
            processing_status['progress'] = 10
            processing_status['message'] = 'Loading images...'
            
            # 处理每个文件
            for file_info in session['files']:
                file_path = Path(file_info['path'])
                if file_path.exists():
                    processing_status['message'] = f'Processing {file_info["original_name"]}...'
                    
                    # 读取并处理图像
                    image = cv2.imread(str(file_path))
                    if image is not None:
                        # 检测QR码
                        qr_codes = self._detect_qr_codes(image)
                        
                        if qr_codes:
                            processing_status['output'].append(f'Found {len(qr_codes)} QR code(s) in {file_info["original_name"]}')
                            
                            # 处理每个QR码
                            for i, qr_code in enumerate(qr_codes):
                                qr_image = self._extract_qr_region(image, qr_code)
                                
                                # 保存基础QR码
                                base_name = f"{file_path.stem}_qr_{i+1}"
                                qr_output_path = session['output_dir'] / 'qr_codes'
                                qr_output_path.mkdir(exist_ok=True)
                                
                                qr_file_path = qr_output_path / f"{base_name}.png"
                                cv2.imwrite(str(qr_file_path), qr_image)
                                
                                # 处理选项
                                if options.get('transparent'):
                                    transparent_dir = session['output_dir'] / 'transparent_codes'
                                    transparent_dir.mkdir(exist_ok=True)
                                    
                                    pil_image = Image.fromarray(cv2.cvtColor(qr_image, cv2.COLOR_BGR2RGB))
                                    transparent_image = self._create_transparent_version(pil_image)
                                    transparent_path = transparent_dir / f"{base_name}_transparent.png"
                                    transparent_image.save(str(transparent_path))
                                
                                if options.get('invert'):
                                    inverted_dir = session['output_dir'] / 'inverted_codes'
                                    inverted_dir.mkdir(exist_ok=True)
                                    
                                    inverted_image = 255 - qr_image
                                    inverted_path = inverted_dir / f"{base_name}_inverted.png"
                                    cv2.imwrite(str(inverted_path), inverted_image)
                                
                                if options.get('svg'):
                                    svg_dir = session['output_dir'] / 'svg_codes'
                                    svg_dir.mkdir(exist_ok=True)
                                    
                                    svg_data = self._create_svg_version(qr_code.data.decode('utf-8'))
                                    svg_path = svg_dir / f"{base_name}.svg"
                                    with open(str(svg_path), 'w') as f:
                                        f.write(svg_data)
                        else:
                            processing_status['output'].append(f'No QR codes found in {file_info["original_name"]}')
                    
                    processing_status['progress'] = min(90, processing_status['progress'] + 20)
            
            processing_status['progress'] = 95
            processing_status['message'] = 'Processing completed, scanning results...'
            
            # 扫描结果文件
            result_files = self.scan_result_files(session['output_dir'])
            processing_status['result_files'] = result_files
            
            processing_status['progress'] = 100
            processing_status['message'] = 'Processing completed successfully!'
            
        except Exception as e:
            processing_status['error'] = f'Processing error: {str(e)}'
            processing_status['output'].append(f'Error: {str(e)}')
        finally:
            processing_status['running'] = False
    
    def _detect_qr_codes(self, image):
        """检测图片中的QR码"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        qr_codes = pyzbar.decode(gray)
        return qr_codes
    
    def _extract_qr_region(self, image, qr_code):
        """提取QR码区域"""
        x, y, w, h = qr_code.rect
        
        # 添加边距
        margin_x = int(w * self.margin_ratio)
        margin_y = int(h * self.margin_ratio)
        
        # 计算扩展后的边界
        start_x = max(0, x - margin_x)
        start_y = max(0, y - margin_y)
        end_x = min(image.shape[1], x + w + margin_x)
        end_y = min(image.shape[0], y + h + margin_y)
        
        # 提取区域
        qr_region = image[start_y:end_y, start_x:end_x]
        return qr_region
    
    def _create_transparent_version(self, image):
        """创建透明背景版本"""
        # 转换为RGBA模式
        rgba_img = image.convert('RGBA')
        data = np.array(rgba_img)
        
        # 将白色背景设为透明
        white_mask = (data[:, :, 0] >= self.white_threshold) & \
                     (data[:, :, 1] >= self.white_threshold) & \
                     (data[:, :, 2] >= self.white_threshold)
        
        data[white_mask] = [255, 255, 255, 0]  # 设为透明
        
        return Image.fromarray(data, 'RGBA')
    
    def _create_svg_version(self, qr_data):
        """创建SVG版本"""
        # 创建QR码对象
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # 生成SVG
        factory = qrcode.image.svg.SvgPathImage
        svg_img = qr.make_image(image_factory=factory)
        
        # 获取SVG字符串
        import io
        svg_buffer = io.BytesIO()
        svg_img.save(svg_buffer)
        svg_data = svg_buffer.getvalue().decode('utf-8')
        
        return svg_data
    
    def scan_result_files(self, output_dir):
        """扫描输出目录中的结果文件"""
        result_files = []
        
        try:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(output_dir)
                    
                    # 确定文件类型
                    file_type = 'unknown'
                    if file.lower().endswith('.svg'):
                        file_type = 'svg'
                    elif file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        file_type = 'image'
                    
                    # 将Windows路径分隔符转换为URL路径分隔符
                    url_path = str(relative_path).replace('\\', '/')
                    
                    result_files.append({
                        'name': file,
                        'path': url_path,
                        'full_path': str(file_path),
                        'size': self.format_file_size(file_path.stat().st_size),
                        'type': file_type
                    })
        except Exception as e:
            print(f"Error scanning result files: {e}")
        
        return result_files
    
    def format_file_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def cleanup_old_sessions(self, max_age_hours=24):
        """清理旧的会话数据"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        sessions_to_remove = []
        for session_id, session in sessions.items():
            if current_time - session['created_at'] > max_age_seconds:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            try:
                session = sessions[session_id]
                if session['upload_dir'].exists():
                    shutil.rmtree(session['upload_dir'])
                if session['output_dir'].exists():
                    shutil.rmtree(session['output_dir'])
                del sessions[session_id]
            except Exception as e:
                print(f"Error cleaning up session {session_id}: {e}")

# 初始化处理器
processor = VercelQRProcessor()

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """处理文件上传"""
    try:
        # 创建新会话
        session_id = processor.create_session()
        
        # 获取上传的文件
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({'error': 'No files selected'}), 400
        
        # 保存文件
        saved_files = processor.save_uploaded_files(files, session_id)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'files': saved_files,
            'message': f'Successfully uploaded {len(saved_files)} files'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process', methods=['POST'])
def process_files():
    """处理文件"""
    try:
        if not DEPENDENCIES_AVAILABLE:
            return jsonify({'error': 'Missing required dependencies'}), 500
        
        # 检查是否有文件上传
        files = request.files.getlist('files')
        options_json = request.form.get('options', '{}')
        options = json.loads(options_json)
        
        if not files or all(f.filename == '' for f in files):
            return jsonify({'error': 'No files uploaded'}), 400
        
        # 创建新会话并保存文件
        session_id = processor.create_session()
        saved_files = processor.save_uploaded_files(files, session_id)
        
        if not saved_files:
            return jsonify({'error': 'No valid image files uploaded'}), 400
        
        # 在后台线程中开始处理
        thread = threading.Thread(
            target=processor.process_files,
            args=(session_id, options)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Processing started successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def get_status():
    """获取处理状态"""
    return jsonify(processing_status)

@app.route('/api/results')
def get_results():
    """获取处理结果"""
    return jsonify({
        'files': processing_status.get('result_files', [])
    })

@app.route('/api/preview/<session_id>/<path:file_path>')
def preview_file(session_id, file_path):
    """预览文件"""
    try:
        if session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        session = sessions[session_id]
        full_path = session['output_dir'] / file_path
        
        if not full_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        # 确定MIME类型
        mime_type, _ = mimetypes.guess_type(str(full_path))
        if mime_type is None:
            mime_type = 'application/octet-stream'
        
        return send_file(
            str(full_path),
            mimetype=mime_type
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download')
def download_file():
    """下载文件"""
    try:
        file_path = request.args.get('file')
        session_id = request.args.get('session_id')
        
        if not file_path:
            return jsonify({'error': 'No file specified'}), 400
        
        if not session_id:
            session_id = processing_status.get('session_id')
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        session = sessions[session_id]
        full_path = session['output_dir'] / file_path
        
        if not full_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        # 确定MIME类型
        mime_type, _ = mimetypes.guess_type(str(full_path))
        if mime_type is None:
            mime_type = 'application/octet-stream'
        
        return send_file(
            str(full_path),
            as_attachment=True,
            download_name=full_path.name,
            mimetype=mime_type
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup_sessions():
    """清理旧会话"""
    try:
        processor.cleanup_old_sessions()
        return jsonify({'success': True, 'message': 'Cleanup completed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'dependencies': DEPENDENCIES_AVAILABLE,
        'version': '1.0.0'
    })

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 100MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# Vercel需要的主要处理函数
def handler(event, context):
    return app(event, context)

if __name__ == '__main__':
    app.run(debug=True)