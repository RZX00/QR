# QR处理器 Docker 部署指南

本指南将帮助您使用Docker和反向代理部署QR码处理应用。

## 📋 系统要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 2GB 可用内存
- 至少 5GB 可用磁盘空间

## 🚀 快速部署

### Windows 用户

1. **确保Docker Desktop已安装并运行**
2. **打开命令提示符或PowerShell，进入项目目录**
3. **运行部署脚本**：
   ```cmd
   deploy.bat start
   ```

### Linux/macOS 用户

1. **确保Docker和Docker Compose已安装**
2. **打开终端，进入项目目录**
3. **给脚本执行权限**：
   ```bash
   chmod +x deploy.sh
   ```
4. **运行部署脚本**：
   ```bash
   ./deploy.sh start
   ```

## 📁 项目结构

部署后的项目结构：
```
QR/
├── api/                    # Flask应用
├── public/                 # 前端静态文件
├── image/                  # 输入图片目录
├── qr_output/             # 输出结果目录
├── nginx/                 # Nginx配置
│   ├── nginx.conf         # 主配置文件
│   ├── conf.d/            # 站点配置
│   └── ssl/               # SSL证书目录
├── Dockerfile             # Docker镜像构建文件
├── docker-compose.yml     # 容器编排配置
├── deploy.sh              # Linux/macOS部署脚本
├── deploy.bat             # Windows部署脚本
└── requirements.txt       # Python依赖
```

## 🔧 手动部署步骤

如果您不想使用自动化脚本，可以按以下步骤手动部署：

### 1. 构建并启动服务

```bash
# 创建必要目录
mkdir -p image qr_output nginx/ssl

# 构建并启动所有服务
docker-compose up -d --build
```

### 2. 验证部署

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 3. 访问应用

- **主页**: http://localhost
- **API状态**: http://localhost/api/status
- **健康检查**: http://localhost/health

## 🛠️ 管理命令

### 使用部署脚本

```bash
# 启动服务
./deploy.sh start

# 停止服务
./deploy.sh stop

# 重启服务
./deploy.sh restart

# 查看日志
./deploy.sh logs

# 查看状态
./deploy.sh status

# 清理资源
./deploy.sh cleanup
```

### 使用Docker Compose

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重新构建并启动
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 查看服务状态
docker-compose ps
```

## 🌐 配置域名和HTTPS

### 1. 配置域名

编辑 `nginx/conf.d/qr-processor.conf`，将 `server_name localhost;` 改为您的域名：

```nginx
server_name your-domain.com;
```

### 2. 配置HTTPS（可选）

1. **获取SSL证书**（推荐使用Let's Encrypt）
2. **将证书文件放入** `nginx/ssl/` 目录
3. **取消注释HTTPS配置**在 `nginx/conf.d/qr-processor.conf` 中
4. **重启服务**：
   ```bash
   docker-compose restart nginx
   ```

## 📊 监控和维护

### 查看资源使用情况

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
docker system df
```

### 备份数据

```bash
# 备份处理结果
tar -czf qr_backup_$(date +%Y%m%d).tar.gz qr_output/

# 备份配置文件
tar -czf config_backup_$(date +%Y%m%d).tar.gz nginx/ docker-compose.yml
```

### 更新应用

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build
```

## 🔍 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查看端口使用情况
   netstat -tulpn | grep :80
   
   # 修改docker-compose.yml中的端口映射
   ports:
     - "8080:80"  # 改为其他端口
   ```

2. **内存不足**
   ```bash
   # 增加Docker内存限制
   # 在docker-compose.yml中添加：
   deploy:
     resources:
       limits:
         memory: 1G
   ```

3. **权限问题**
   ```bash
   # 修复目录权限
   sudo chown -R $USER:$USER image/ qr_output/
   chmod -R 755 image/ qr_output/
   ```

### 查看详细日志

```bash
# 查看特定服务日志
docker-compose logs qr-app
docker-compose logs nginx

# 实时查看日志
docker-compose logs -f --tail=100
```

## 🔒 安全建议

1. **更改默认端口**（如果暴露到公网）
2. **配置防火墙规则**
3. **定期更新Docker镜像**
4. **使用HTTPS**（生产环境必须）
5. **限制文件上传大小**
6. **配置访问日志监控**

## 📞 技术支持

如果遇到问题，请：

1. 查看日志文件
2. 检查系统资源
3. 验证网络连接
4. 确认配置文件语法

---

**部署完成后，您的QR码处理应用将通过 http://localhost 访问！**