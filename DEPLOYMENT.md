# Resume Studio AI 简历优化助手 - 一键部署指南

## 项目概述
AI 简历优化助手是一个基于 Vue + FastAPI + SQLite + 硅基流动的智能简历处理系统。系统通过本地 PDF 文本提取和 AI 分析，提供简历结构化解析、优化建议、风格转换等功能。

## 快速开始

### 方法一：本地一键部署（推荐 - 无需 Docker）

#### Windows 用户
1. 确保已安装：
   - Python 3.8+（已安装）
   - Node.js 16+（已安装）
   - 推荐使用 VSCode 或 PyCharm 等开发工具

2. 打开 PowerShell，进入项目目录：
   ```powershell
   cd C:\Users\zzz\Desktop\resume_2
   ```

3. 运行一键部署脚本：
   ```powershell
   # 启动服务
   .\deploy-local.ps1
   
   # 或者带参数运行
   .\deploy-local.ps1 -Help      # 查看帮助
   .\deploy-local.ps1 -Stop      # 停止服务
   .\deploy-local.ps1 -Logs      # 查看日志
   .\deploy-local.ps1 -Build     # 重新构建并启动
   ```

#### Linux/macOS 用户
1. 确保已安装：
   - Python 3.8+
   - Node.js 16+
   - 确保脚本有执行权限

2. 打开终端，进入项目目录：
   ```bash
   cd ~/Desktop/resume_2
   ```

3. 运行一键部署脚本：
   ```bash
   # 添加执行权限（首次运行）
   chmod +x deploy-local.sh
   
   # 启动服务
   ./deploy-local.sh
   
   # 停止服务
   ./deploy-local.sh stop
   ```

### 方法二：Docker 容器化部署

#### 前置条件
1. 安装 Docker Desktop（Windows/Mac）或 Docker Engine（Linux）
2. 确保 Docker 已启动

#### Windows 用户（PowerShell）
```powershell
# 进入项目目录
cd C:\Users\zzz\Desktop\resume_2

# 启动服务
.\deploy.ps1

# 常用命令
.\deploy.ps1 -Build     # 重新构建并启动
.\deploy.ps1 -Stop      # 停止服务
.\deploy.ps1 -Logs      # 查看日志
.\deploy.ps1 -Help      # 查看帮助
```

#### Linux/macOS 用户
```bash
# 进入项目目录
cd ~/Desktop/resume_2

# 添加执行权限（首次运行）
chmod +x deploy.sh

# 启动服务
./deploy.sh

# 常用命令
./deploy.sh build       # 重新构建并启动
./deploy.sh stop        # 停止服务
./deploy.sh logs        # 查看日志
./deploy.sh -h          # 查看帮助
```

## 访问服务

部署成功后，可以访问以下地址：

- **前端应用**：http://localhost（Docker 部署）或 http://localhost:5173（本地部署）
- **后端 API**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs

## 项目结构

```
resume_2/
├── backend/                    # 后端服务（FastAPI）
│   ├── app/
│   │   ├── api/               # API 路由
│   │   ├── db/                # 数据库相关
│   │   ├── services/          # 业务服务
│   │   └── main.py            # 应用入口
│   ├── config/                # 配置文件
│   │   └── siliconflow.json   # 硅基流动配置
│   ├── data/                  # 数据存储目录
│   ├── Dockerfile             # Docker 镜像配置
│   ├── requirements.txt       # Python 依赖
│   └── README.md             # 后端文档
├── frontend/                  # 前端服务（Vue 3 + TypeScript）
│   ├── src/
│   │   ├── api/              # API 客户端
│   │   ├── components/       # Vue 组件
│   │   └── types/           # TypeScript 类型定义
│   ├── Dockerfile            # Docker 镜像配置
│   ├── nginx.conf           # Nginx 配置
│   ├── package.json         # Node.js 依赖
│   ├── vite.config.ts       # Vite 配置
│   └── README.md           # 前端文档
├── deploy.ps1              # Windows Docker 部署脚本
├── deploy.sh               # Linux/macOS Docker 部署脚本
├── deploy-local.ps1       # Windows 本地部署脚本
├── deploy-local.sh        # Linux/macOS 本地部署脚本
├── docker-compose.yml     # Docker Compose 配置
└── README.md             # 项目主文档
```

## 配置说明

### AI 模型配置
项目使用硅基流动（Silicon Flow）作为 AI 服务提供商。配置文件位于 `backend/config/siliconflow.json`：

```json
{
  "baseUrl": "https://api.siliconflow.cn/v1",
  "apiKey": "sk-tomaiyhwyxzbyqggzxolrvyncbimsnybadvgptajczmpaoip",
  "model": "deepseek-ai/DeepSeek-V3.2"
}
```

如需更换模型或 API Key，请修改此配置文件。

### 数据库配置
- 使用 SQLite 作为数据库
- 数据库文件位置：`backend/data/resume.db`
- 数据库会自动在首次启动时创建

## 功能测试

部署完成后，您可以通过以下方式测试系统：

### 1. 测试后端 API
```bash
# 使用 curl 测试 API 健康状态
curl http://localhost:8000/api/resumes

# 或直接在浏览器访问 API 文档
# http://localhost:8000/docs
```

### 2. 测试前端应用
1. 访问 http://localhost（Docker）或 http://localhost:5173（本地）
2. 上传 PDF 简历文件进行测试
3. 系统将自动解析简历并生成优化建议

## 故障排除

### 常见问题

#### 1. Docker 部署失败
**问题**：`docker compose` 命令不存在
**解决**：
- 安装 Docker Desktop（Windows/Mac）
- Linux 用户：`sudo apt install docker-compose`

#### 2. Python 依赖安装失败
**问题**：pip 安装超时或失败
**解决**：
```bash
# 使用国内镜像源
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 3. Node.js 依赖安装失败
**问题**：npm install 失败
**解决**：
```bash
# 使用淘宝镜像
npm config set registry https://registry.npmmirror.com
npm install
```

#### 4. 端口冲突
**问题**：端口 80、8000 或 5173 已被占用
**解决**：
- 修改 `docker-compose.yml` 中的端口映射
- 或者停止占用端口的程序

### 日志查看

#### Docker 部署
```bash
# 查看所有容器日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

#### 本地部署
- Windows：查看 PowerShell 窗口输出
- Linux/macOS：查看终端输出

## 高级配置

### 自定义端口
修改 `docker-compose.yml` 文件中的端口映射：
```yaml
services:
  backend:
    ports:
      - "8888:8000"  # 将外部端口改为 8888
  frontend:
    ports:
      - "8080:80"    # 将外部端口改为 8080
```

### 生产环境部署
对于生产环境，建议：

1. **启用 HTTPS**：配置 Nginx SSL 证书
2. **数据持久化**：确保数据库文件定期备份
3. **API Key 保护**：使用环境变量存储 API Key
4. **监控**：设置应用性能监控

### 环境变量配置
可以在 `.env` 文件中配置环境变量：
```
CORS_ALLOW_ORIGINS=http://localhost:5173,http://localhost:3000
DATABASE_PATH=/app/data/resume.db
```

## 开发说明

### 后端开发
```bash
cd backend
# 安装依赖
python -m pip install -r requirements.txt
# 启动开发服务器
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发
```bash
cd frontend
# 安装依赖
npm install
# 启动开发服务器
npm run dev
```

### 代码检查
```bash
# 后端代码检查
cd backend
python -m pylint app/
python -m mypy app/

# 前端代码检查
cd frontend
npm run lint
```

## 系统要求

### 最低要求
- CPU：2 核以上
- 内存：4GB 以上
- 存储：2GB 可用空间
- 网络：可访问硅基流动 API

### 推荐配置
- CPU：4 核以上
- 内存：8GB 以上
- 存储：10GB 可用空间
- 网络：稳定的互联网连接

## 安全注意事项

1. **API Key 保护**：不要将配置文件提交到公共仓库
2. **文件上传限制**：系统限制上传文件大小不超过 20MB
3. **输入验证**：系统会对上传的文件进行格式验证
4. **SQL 注入防护**：使用参数化查询防止 SQL 注入

## 支持与反馈

如果在部署过程中遇到问题，请：

1. 查看日志文件获取详细错误信息
2. 检查端口占用情况
3. 确保网络连接正常
4. 验证依赖包安装是否正确

欢迎提交问题到项目仓库，我们将尽快处理。

---
*最后更新：2026年4月13日*
*版本：1.0.0*