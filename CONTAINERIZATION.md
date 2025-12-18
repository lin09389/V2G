# V2G平台容器化部署指南

本指南将详细介绍如何使用Docker和Docker Compose对V2G平台进行容器化部署。

## 环境要求

- Docker 19.03或更高版本
- Docker Compose 1.25或更高版本

## 安装Docker和Docker Compose

### Windows系统
1. 下载并安装Docker Desktop for Windows：[https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. 安装完成后，启动Docker Desktop并确保Docker服务正在运行

### Linux系统
```bash
# 更新系统包
 sudo apt-get update

# 安装Docker
 sudo apt-get install -y docker.io

# 安装Docker Compose
 sudo apt-get install -y docker-compose

# 启动Docker服务
 sudo systemctl start docker
 sudo systemctl enable docker
```

## 容器化部署步骤

### 1. 构建并启动容器

在项目根目录下执行以下命令：

```bash
# 使用Docker Compose构建并启动所有服务
docker-compose up -d
```

### 2. 访问服务

- 前端服务：[http://localhost](http://localhost)
- 后端服务：[https://localhost:5000](https://localhost:5000)（使用自签名SSL证书）
- 健康检查接口：[https://localhost:5000/health](https://localhost:5000/health)

### 3. 查看容器状态

```bash
# 查看所有容器的运行状态
docker-compose ps

# 查看服务日志
docker-compose logs

# 查看特定服务的日志
docker-compose logs backend
```

## 容器化架构

### 后端服务（backend）
- 使用Python 3.11-slim作为基础镜像
- 运行Flask应用程序
- 内置自签名SSL证书生成
- 挂载数据卷用于持久化数据库和上传文件

### 前端服务（frontend）
- 使用Nginx Alpine作为基础镜像
- 托管静态HTML、CSS和JavaScript文件
- 反向代理配置（可选）

## 自定义配置

### 环境变量

可以通过修改`.env`文件或在`docker-compose.yml`中设置环境变量来自定义配置：

```bash
# 示例：创建.env文件
cat > .env <<EOF
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
FLASK_ENV=production
DEBUG=False
EOF
```

### 端口映射

如果需要修改服务的访问端口，可以在`docker-compose.yml`中调整端口映射：

```yaml
backend:
  ports:
    - "8080:5000"  # 将后端服务映射到主机的8080端口

frontend:
  ports:
    - "8081:80"  # 将前端服务映射到主机的8081端口
```

## 数据持久化

### 数据库
后端服务使用SQLite数据库，数据文件通过Docker卷挂载到主机：

```yaml
volumes:
  - ./backend/v2g.db:/app/v2g.db
```

### 上传文件
上传的文件也通过Docker卷持久化：

```yaml
volumes:
  - ./backend/uploads:/app/uploads
```

## 维护命令

### 停止服务
```bash
docker-compose down
```

### 重启服务
```bash
docker-compose restart
```

### 更新服务
```bash
# 停止并删除旧容器
docker-compose down

# 重新构建并启动服务
docker-compose up -d --build
```

## 注意事项

1. **自签名SSL证书**：默认使用自签名SSL证书，在生产环境中应替换为受信任的证书
2. **环境变量安全**：生产环境中应使用强随机密钥并避免在配置文件中硬编码敏感信息
3. **资源限制**：根据实际需求调整Docker容器的资源限制
4. **日志管理**：配置适当的日志轮转机制以防止日志文件过大

## 故障排除

### 容器启动失败
```bash
# 查看容器日志以了解失败原因
docker-compose logs backend
```

### 数据库连接问题
确保数据库文件有正确的权限，并且容器可以读写：

```bash
# 检查文件权限
ls -la ./backend/v2g.db

# 更改权限
chmod 666 ./backend/v2g.db
```

### SSL证书问题
如果遇到SSL证书错误，可以重新生成证书：

```bash
# 进入后端容器
docker exec -it v2g-backend bash

# 重新生成证书
python generate_ssl.py

# 重启后端服务
docker-compose restart backend
```