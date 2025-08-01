@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM QR处理器Docker部署脚本 (Windows版本)
REM 使用方法: deploy.bat [start|stop|restart|logs|status]

set PROJECT_NAME=qr-processor
set COMMAND=%1
if "%COMMAND%"=="" set COMMAND=start

echo [%date% %time%] QR处理器Docker部署脚本
echo =====================================

REM 检查Docker是否安装
echo 检查系统要求...
docker --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker未安装或未启动
    echo 请先安装Docker Desktop并确保其正在运行
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker Compose未安装
    echo 请确保Docker Desktop包含Docker Compose
    pause
    exit /b 1
)

echo 系统要求检查通过
echo.

REM 根据命令执行相应操作
if "%COMMAND%"=="start" goto :start
if "%COMMAND%"=="stop" goto :stop
if "%COMMAND%"=="restart" goto :restart
if "%COMMAND%"=="logs" goto :logs
if "%COMMAND%"=="status" goto :status
if "%COMMAND%"=="cleanup" goto :cleanup
if "%COMMAND%"=="help" goto :help

echo 未知命令: %COMMAND%
goto :help

:start
echo 启动QR处理器服务...
echo.

REM 创建必要目录
if not exist "image" mkdir image
if not exist "qr_output" mkdir qr_output
if not exist "nginx\ssl" mkdir nginx\ssl

REM 构建并启动服务
docker-compose up -d --build
if errorlevel 1 (
    echo 服务启动失败
    pause
    exit /b 1
)

echo 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
docker-compose ps | findstr "Up" >nul
if errorlevel 1 (
    echo 服务启动失败，显示日志:
    docker-compose logs
    pause
    exit /b 1
) else (
    echo.
    echo ✓ 服务启动成功!
    echo ✓ 访问地址: http://localhost
    echo ✓ API状态: http://localhost/api/status
    echo ✓ 健康检查: http://localhost/health
)
goto :end

:stop
echo 停止QR处理器服务...
docker-compose down
echo 服务已停止
goto :end

:restart
echo 重启QR处理器服务...
call :stop
echo.
call :start
goto :end

:logs
echo 显示服务日志...
echo 按 Ctrl+C 退出日志查看
echo.
docker-compose logs -f
goto :end

:status
echo 服务状态:
echo ============
docker-compose ps
echo.
echo 容器资源使用情况:
echo ==================
for /f "tokens=*" %%i in ('docker-compose ps -q') do (
    docker stats --no-stream %%i 2>nul
)
goto :end

:cleanup
echo 清理Docker资源...
docker-compose down -v --remove-orphans
docker system prune -f
echo 清理完成
goto :end

:help
echo QR处理器Docker部署脚本
echo.
echo 使用方法: %0 [命令]
echo.
echo 可用命令:
echo   start     启动服务
echo   stop      停止服务
echo   restart   重启服务
echo   logs      查看日志
echo   status    显示状态
echo   cleanup   清理资源
echo   help      显示帮助
echo.
goto :end

:end
if "%COMMAND%"=="logs" goto :eof
echo.
echo 按任意键退出...
pause >nul