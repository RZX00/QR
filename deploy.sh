#!/bin/bash

# QR处理器Docker部署脚本
# 使用方法: ./deploy.sh [start|stop|restart|logs|status]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目名称
PROJECT_NAME="qr-processor"

# 函数：打印彩色消息
print_message() {
    echo -e "${2}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# 函数：检查Docker和Docker Compose
check_requirements() {
    print_message "检查系统要求..." $BLUE
    
    if ! command -v docker &> /dev/null; then
        print_message "错误: Docker未安装" $RED
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_message "错误: Docker Compose未安装" $RED
        exit 1
    fi
    
    print_message "系统要求检查通过" $GREEN
}

# 函数：创建必要目录
create_directories() {
    print_message "创建必要目录..." $BLUE
    mkdir -p image qr_output nginx/ssl
    print_message "目录创建完成" $GREEN
}

# 函数：启动服务
start_services() {
    print_message "启动QR处理器服务..." $BLUE
    
    # 创建必要目录
    create_directories
    
    # 构建并启动服务
    docker-compose up -d --build
    
    # 等待服务启动
    print_message "等待服务启动..." $YELLOW
    sleep 10
    
    # 检查服务状态
    if docker-compose ps | grep -q "Up"; then
        print_message "服务启动成功!" $GREEN
        print_message "访问地址: http://localhost" $GREEN
        print_message "API状态: http://localhost/api/status" $GREEN
    else
        print_message "服务启动失败，请检查日志" $RED
        docker-compose logs
    fi
}

# 函数：停止服务
stop_services() {
    print_message "停止QR处理器服务..." $BLUE
    docker-compose down
    print_message "服务已停止" $GREEN
}

# 函数：重启服务
restart_services() {
    print_message "重启QR处理器服务..." $BLUE
    stop_services
    start_services
}

# 函数：查看日志
show_logs() {
    print_message "显示服务日志..." $BLUE
    docker-compose logs -f
}

# 函数：显示状态
show_status() {
    print_message "服务状态:" $BLUE
    docker-compose ps
    
    print_message "\n容器资源使用情况:" $BLUE
    docker stats --no-stream $(docker-compose ps -q) 2>/dev/null || true
}

# 函数：清理资源
cleanup() {
    print_message "清理Docker资源..." $BLUE
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_message "清理完成" $GREEN
}

# 函数：显示帮助
show_help() {
    echo "QR处理器Docker部署脚本"
    echo ""
    echo "使用方法: $0 [命令]"
    echo ""
    echo "可用命令:"
    echo "  start     启动服务"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  logs      查看日志"
    echo "  status    显示状态"
    echo "  cleanup   清理资源"
    echo "  help      显示帮助"
    echo ""
}

# 主逻辑
case "${1:-start}" in
    start)
        check_requirements
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        check_requirements
        restart_services
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_message "未知命令: $1" $RED
        show_help
        exit 1
        ;;
esac