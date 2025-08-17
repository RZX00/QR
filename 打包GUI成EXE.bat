@echo off
chcp 65001 >nul
echo ================================================
echo        QR码处理器GUI - 一键打包工具
echo ================================================
echo.
echo 正在检查环境...
python build_gui_exe.py
echo.
echo 打包完成！
echo EXE文件位置: dist\QR-Processor-GUI.exe
echo.
pause
