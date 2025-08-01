FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p /app/image /app/qr_output

# 设置权限
RUN chmod -R 755 /app

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=api/index.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# 启动命令
CMD ["python", "api/index.py"]