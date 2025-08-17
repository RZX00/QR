# 1Panel 服务器部署指南

本指南详细说明如何在1Panel（阿里云）服务器上部署QR处理器项目。

## 前置条件

- 已安装1Panel管理面板
- 服务器已安装Docker和Docker Compose
- 项目文件已上传到服务器的 `/opt/1panel/apps/QR` 目录

## 部署步骤

### 1. 连接服务器并进入项目目录

```bash
cd /opt/1panel/apps/QR
```

### 2. 运行部署脚本

```bash
# 给脚本执行权限
chmod +x server-deploy.sh

# 运行部署脚本
./server-deploy.sh
```

### 3. 手动部署（可选）

如果自动脚本失败，可以手动执行以下步骤：

```bash
# 创建必要目录
mkdir -p qr_output nginx/ssl image

# 设置权限
chmod 755 qr_output nginx/ssl image nginx/conf.d

# 构建并启动服务
docker compose up -d --build

# 或者使用旧版本命令
docker-compose up -d --build
```

## 1Panel 容器配置

如果您更喜欢通过1Panel界面创建容器，请参考以下配置：

### 应用容器 (qr-app)

**基本信息：**
- 容器名称: `qr-processor`
- 镜像: 需要先构建镜像或使用 `docker compose`

**端口配置：**
- 容器端口: 5000
- 主机端口: 5000

**挂载配置：**
- `/opt/1panel/apps/QR/image` → `/app/image`
- `/opt/1panel/apps/QR/qr_output` → `/app/qr_output`

**环境变量：**
- `FLASK_ENV=production`
- `PYTHONPATH=/app`

### Nginx 容器 (qr-nginx)

**基本信息：**
- 容器名称: `qr-nginx`
- 镜像: `nginx:alpine`

**端口配置：**
- 容器端口: 80 → 主机端口: 80
- 容器端口: 443 → 主机端口: 443

**挂载配置：**
- `/opt/1panel/apps/QR/nginx/nginx.conf` → `/etc/nginx/nginx.conf`
- `/opt/1panel/apps/QR/nginx/conf.d` → `/etc/nginx/conf.d`

**依赖关系：**
- 依赖于 `qr-processor` 容器

## 验证部署

### 1. 检查容器状态

```bash
docker compose ps
```

### 2. 查看日志

```bash
# 查看所有服务日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f qr-app
docker compose logs -f nginx
```

### 3. 测试应用

```bash
# 测试健康检查端点
curl http://localhost/api/health

# 或者通过浏览器访问
# http://your-server-ip
```

## 常见问题解决

### 1. 权限问题

如果遇到权限问题，确保目录权限正确：

```bash
sudo chown -R 1000:1000 /opt/1panel/apps/QR/qr_output
sudo chown -R 1000:1000 /opt/1panel/apps/QR/image
```

### 2. 端口冲突

如果80端口被占用，可以修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8080:80"  # 改为8080端口
  - "8443:443"
```

### 3. 容器无法启动

检查Docker服务状态：

```bash
sudo systemctl status docker
sudo systemctl start docker
```

### 4. 网络问题

确保防火墙允许相应端口：

```bash
# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload

# Ubuntu/Debian
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

## 更新部署

当需要更新应用时：

```bash
# 停止服务
docker compose down

# 重新构建并启动
docker compose up -d --build
```

## 备份和恢复

### 备份数据

```bash
# 备份处理的图片和二维码
tar -czf qr_backup_$(date +%Y%m%d).tar.gz qr_output/ image/
```

### 恢复数据

```bash
# 解压备份文件
tar -xzf qr_backup_YYYYMMDD.tar.gz
```

## 监控和维护

### 查看资源使用情况

```bash
docker stats
```

### 清理未使用的镜像

```bash
docker system prune -f
```

### 查看容器详细信息

```bash
docker inspect qr-processor
docker inspect qr-nginx
```

---

**注意事项：**
- 确保服务器有足够的磁盘空间存储图片文件
- 定期备份 `qr_output` 和 `image` 目录
- 监控容器资源使用情况，必要时调整资源限制
- 如果使用HTTPS，需要配置SSL证书到 `nginx/ssl` 目录