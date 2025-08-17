# Dockge 部署 QR 处理器项目指南

本指南详细说明如何通过 Dockge 在 1Panel 环境中部署 QR 处理器项目。

## 前置条件

- 已安装 1Panel 管理面板 <mcreference link="https://zhuanlan.zhihu.com/p/1910098607798976852?utm_source=chatgpt.com" index="0">0</mcreference>
- 已通过 1Panel 部署 Dockge 容器编排工具 <mcreference link="https://zhuanlan.zhihu.com/p/1910098607798976852?utm_source=chatgpt.com" index="0">0</mcreference>
- 项目文件已上传到服务器的 `/opt/1panel/apps/QR` 目录

## Dockge 部署步骤

### 1. 访问 Dockge 面板

通过 1Panel 应用商店安装 Dockge 后，访问 Dockge 管理界面。

### 2. 创建新的堆栈（Stack）

1. 在 Dockge 面板中点击 "创建堆栈" 或 "New Stack"
2. 设置堆栈名称：`qr-processor`
3. 设置工作目录：`/opt/1panel/apps/QR`

### 3. 配置 Docker Compose

将以下内容粘贴到 Dockge 的 compose 编辑器中：

```yaml
services:
  qr-app:
    build: .
    container_name: qr-processor
    restart: always
    volumes:
      - ./image:/app/image
      - ./qr_output:/app/qr_output
    environment:
      - FLASK_ENV=production
      - PYTHONPATH=/app
      - TZ=Asia/Shanghai
    networks:
      - qr-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    container_name: qr-nginx
    restart: always
    ports:
      - "8080:80"
      - "8443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./nginx/ssl:/etc/nginx/ssl
    environment:
      - TZ=Asia/Shanghai
    depends_on:
      - qr-app
    networks:
      - qr-network

networks:
  qr-network:
    driver: bridge

volumes:
  qr_data:
    driver: local
```

### 4. 部署前准备

在部署前，确保必要的目录结构存在：

```bash
# 通过 1Panel 终端或 SSH 连接服务器
cd /opt/1panel/apps/QR

# 创建必要目录
mkdir -p qr_output nginx/ssl image

# 设置权限
chmod 755 qr_output nginx/ssl image nginx/conf.d
```

### 5. 启动堆栈

1. 在 Dockge 中点击 "部署" 或 "Deploy" 按钮
2. 等待镜像构建和容器启动
3. 查看日志确认服务正常运行

## 配置说明

### 端口配置

- **HTTP 端口**: `8080` (避免与 1Panel 的 80 端口冲突)
- **HTTPS 端口**: `8443` (避免与 1Panel 的 443 端口冲突)
- **应用访问**: `http://your-server-ip:8080`

### 重启策略

- 使用 `restart: always` 确保容器在系统重启后自动启动 <mcreference link="https://zhuanlan.zhihu.com/p/1910098607798976852?utm_source=chatgpt.com" index="0">0</mcreference>

### 时区设置

- 添加 `TZ=Asia/Shanghai` 环境变量确保容器使用正确的时区 <mcreference link="https://zhuanlan.zhihu.com/p/1910098607798976852?utm_source=chatgpt.com" index="0">0</mcreference>

### 存储挂载

- `./image:/app/image` - 输入图片目录
- `./qr_output:/app/qr_output` - 输出二维码目录
- `./nginx/conf.d:/etc/nginx/conf.d` - Nginx 配置目录
- `./nginx/ssl:/etc/nginx/ssl` - SSL 证书目录

## Dockge 管理操作

### 查看容器状态

在 Dockge 面板中可以实时查看：
- 容器运行状态
- 资源使用情况
- 实时日志输出

### 更新部署

1. 修改 compose 配置
2. 点击 "重新部署" 按钮
3. Dockge 会自动处理容器的停止、重建和启动

### 扩展配置

如需要添加更多服务或修改配置：

1. 在 Dockge 中编辑 compose 文件
2. 添加新的服务定义
3. 重新部署堆栈

## 验证部署

### 1. 检查容器状态

在 Dockge 面板中查看所有容器是否正常运行。

### 2. 测试应用访问

```bash
# 测试健康检查端点
curl http://localhost:8080/api/health

# 或通过浏览器访问
# http://your-server-ip:8080
```

### 3. 查看日志

在 Dockge 面板中点击容器名称查看实时日志。

## 故障排除

### 端口冲突

如果 8080 端口被占用，可以修改为其他端口：

```yaml
ports:
  - "9080:80"  # 改为 9080 端口
  - "9443:443"
```

### 权限问题

```bash
# 确保目录权限正确
sudo chown -R 1000:1000 /opt/1panel/apps/QR/qr_output
sudo chown -R 1000:1000 /opt/1panel/apps/QR/image
```

### 构建失败

1. 检查 Dockerfile 是否存在
2. 确保 requirements.txt 文件完整
3. 查看构建日志中的错误信息

## 优势对比

### Dockge vs 传统 Docker Compose

- ✅ **可视化管理**: 通过 Web 界面管理容器 <mcreference link="https://zhuanlan.zhihu.com/p/1910098607798976852?utm_source=chatgpt.com" index="0">0</mcreference>
- ✅ **实时监控**: 容器状态和日志实时查看
- ✅ **简化操作**: 一键部署、更新、回滚
- ✅ **集成管理**: 与 1Panel 完美集成

### 适用场景

- 需要频繁更新部署的开发环境
- 多服务容器编排管理
- 团队协作的项目部署
- 需要可视化监控的生产环境

## 备份和恢复

### 导出堆栈配置

在 Dockge 中可以导出完整的 compose 配置文件，便于备份和迁移。

### 数据备份

```bash
# 备份应用数据
tar -czf qr_backup_$(date +%Y%m%d).tar.gz /opt/1panel/apps/QR/qr_output/ /opt/1panel/apps/QR/image/
```

---

**注意事项**：
- 确保 1Panel 和 Dockge 版本兼容 <mcreference link="https://zhuanlan.zhihu.com/p/1910098607798976852?utm_source=chatgpt.com" index="0">0</mcreference>
- 定期备份重要数据和配置
- 监控容器资源使用情况
- 及时更新镜像版本以获得安全补丁