#!/bin/bash

# 服务器部署脚本 - 适用于1Panel环境
# 在/opt/1panel/apps/QR目录下运行此脚本

echo "开始部署QR处理器项目..."

# 创建必要的目录
echo "创建必要的目录结构..."
mkdir -p qr_output
mkdir -p nginx/ssl
mkdir -p image

# 设置目录权限
echo "设置目录权限..."
chmod 755 qr_output
chmod 755 nginx/ssl
chmod 755 image
chmod 755 nginx/conf.d

# 检查Docker和Docker Compose是否可用
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装或不可用"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "错误: Docker Compose未安装或不可用"
    exit 1
fi

# 停止并删除现有容器（如果存在）
echo "停止现有容器..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true

# 构建并启动服务
echo "构建并启动服务..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d --build
else
    docker compose up -d --build
fi

# 检查服务状态
echo "检查服务状态..."
sleep 10

if command -v docker-compose &> /dev/null; then
    docker-compose ps
else
    docker compose ps
fi

# 检查健康状态
echo "等待服务启动完成..."
sleep 30

echo "检查应用健康状态..."
if curl -f http://localhost:8080/api/health 2>/dev/null; then
    echo "✅ 应用部署成功！"
    echo "访问地址: http://your-server-ip:8080"
    echo "HTTPS访问: https://your-server-ip:8443 (需配置SSL证书)"
else
    echo "⚠️  应用可能还在启动中，请稍后检查"
    echo "可以使用以下命令查看日志:"
    if command -v docker-compose &> /dev/null; then
        echo "docker-compose logs -f"
    else
        echo "docker compose logs -f"
    fi
    echo "或者通过Dockge面板查看容器状态和日志"
fi

echo "部署脚本执行完成！"