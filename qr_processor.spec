
# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

# 收集pyzbar的数据文件和动态库
pyzbar_datas = collect_data_files('pyzbar')
pyzbar_binaries = collect_dynamic_libs('pyzbar')

a = Analysis(
    ['api/index.py'],
    pathex=[],
    binaries=pyzbar_binaries,
    datas=[
        ('public', 'public'),
        ('requirements.txt', '.'),
    ] + pyzbar_datas,
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
