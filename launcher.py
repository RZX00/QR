
#!/usr/bin/env python3
"""
QR处理器 - 启动脚本
"""

import os
import sys
import webbrowser
import threading
import time
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# 设置环境变量
os.environ['FLASK_ENV'] = 'production'
os.environ['HOST'] = '127.0.0.1'
os.environ['PORT'] = '5000'

def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    print("="*50)
    print("    QR码处理器 - 正在启动...")
    print("="*50)
    print("服务地址: http://127.0.0.1:5000")
    print("按 Ctrl+C 停止服务")
    print("="*50)
    
    # 在后台线程中打开浏览器
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # 导入并启动Flask应用
        from api.index import app
        app.run(debug=False, host='127.0.0.1', port=5000)
    except KeyboardInterrupt:
        print("
服务已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        input("按回车键退出...")
