#!/usr/bin/env python3
"""
QR处理器项目 - EXE打包脚本
使用PyInstaller将Flask应用打包成独立的exe文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print("✓ PyInstaller 已安装")
        return True
    except ImportError:
        print("✗ PyInstaller 未安装")
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装 PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller 安装成功")
        return True
    except subprocess.CalledProcessError:
        print("✗ PyInstaller 安装失败")
        return False

def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['api/index.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('public', 'public'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'cv2',
        'numpy',
        'PIL',
        'pyzbar',
        'qrcode',
        'flask',
        'werkzeug',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='QR-Processor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('qr_processor.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✓ 已创建 qr_processor.spec 文件")

def create_launcher_script():
    """创建启动脚本"""
    launcher_content = '''
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
        print("\n服务已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        input("按回车键退出...")
'''
    
    with open('launcher.py', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    print("✓ 已创建 launcher.py 启动脚本")

def build_exe():
    """构建exe文件"""
    print("正在构建 EXE 文件...")
    try:
        # 使用spec文件构建
        subprocess.check_call(["pyinstaller", "--clean", "qr_processor.spec"])
        print("✓ EXE 文件构建成功")
        
        # 检查输出文件
        exe_path = Path("dist/QR-Processor.exe")
        if exe_path.exists():
            print(f"✓ EXE 文件位置: {exe_path.absolute()}")
            print(f"✓ 文件大小: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
        else:
            print("✗ 未找到生成的 EXE 文件")
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 构建失败: {e}")
        return False

def create_batch_file():
    """创建Windows批处理文件"""
    batch_content = '''@echo off
chcp 65001 >nul
echo ================================================
echo           QR码处理器 - 一键打包工具
echo ================================================
echo.
echo 正在检查环境...
python build_exe.py
echo.
echo 打包完成！
echo EXE文件位置: dist\\QR-Processor.exe
echo.
pause
'''
    
    with open('打包成EXE.bat', 'w', encoding='utf-8') as f:
        f.write(batch_content)
    print("✓ 已创建 打包成EXE.bat 批处理文件")

def main():
    """主函数"""
    print("="*60)
    print("           QR处理器项目 - EXE打包工具")
    print("="*60)
    
    # 检查当前目录
    if not Path("api/index.py").exists():
        print("✗ 错误: 请在项目根目录运行此脚本")
        return False
    
    # 检查并安装PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            return False
    
    # 创建必要文件
    create_spec_file()
    create_launcher_script()
    create_batch_file()
    
    # 构建exe
    if build_exe():
        print("\n" + "="*60)
        print("                   打包成功！")
        print("="*60)
        print("EXE文件位置: dist/QR-Processor.exe")
        print("双击即可运行QR码处理器")
        print("="*60)
        return True
    else:
        print("\n" + "="*60)
        print("                   打包失败！")
        print("="*60)
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        input("\n按回车键退出...")