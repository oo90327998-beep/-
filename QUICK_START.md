# Resume Studio AI 简历优化助手 - 快速开始

## 🚀 一键部署（最简单的方法）

### Windows 用户
1. 打开 PowerShell 或命令提示符
2. 导航到项目目录：
   ```powershell
   cd C:\Users\zzz\Desktop\resume_2
   ```
3. 运行一键部署脚本：
   ```powershell
   .\deploy.ps1
   ```
4. 如果不想使用 Docker，使用本地部署脚本：
   ```powershell
   .\deploy-local.ps1
   ```

### Linux/macOS 用户
1. 打开终端
2. 导航到项目目录：
   ```bash
   cd ~/Desktop/resume_2
   ```
3. 运行一键部署脚本：
   ```bash
   # 首次运行需要添加执行权限
   chmod +x deploy.sh deploy-local.sh
   
   # 使用 Docker 部署
   ./deploy.sh
   
   # 或者使用本地部署
   ./deploy-local.sh
   ```

## 🌐 访问应用

部署成功后，访问以下地址：

- **前端应用**：http://localhost（Docker）或 http://localhost:5173（本地）
- **API 文档**：http://localhost:8000/docs

## 🛠️ 常用命令

### Docker 部署
```bash
# 启动服务
./deploy.sh

# 重新构建并启动
./deploy.sh build

# 停止服务
./deploy.sh stop

# 查看日志
./deploy.sh logs
```

### 本地部署
```bash
# 启动服务
./deploy-local.sh

# 停止服务
./deploy-local.sh stop
```

## 📁 项目结构概览

```
resume_2/
├── backend/           # 后端服务 (Python + FastAPI)
├── frontend/          # 前端应用 (Vue 3 + TypeScript)
├── docker-compose.yml # Docker 容器编排
├── deploy.sh         # Linux/macOS 部署脚本
├── deploy.ps1        # Windows 部署脚本
└── README.md         # 项目说明
```

## 🧪 测试系统

1. 访问 http://localhost 或 http://localhost:5173
2. 点击"上传简历"按钮
3. 选择一个 PDF 简历文件
4. 查看 AI 生成的解析结果和建议

## 🔧 依赖检查

确保以下组件已安装：

### Docker 部署
- ✅ Docker Desktop (Windows/Mac) 或 Docker Engine (Linux)

### 本地部署
- ✅ Python 3.8+ (已安装：Python 3.13.12)
- ✅ Node.js 16+ (已安装：v24.14.0)

## 🆘 遇到问题？

### 常见问题

1. **端口冲突**：
   - 检查 80、8000、5173 端口是否被占用
   - 修改 `docker-compose.yml` 中的端口映射

2. **Docker 未安装**：
   - 下载 Docker Desktop：https://www.docker.com/products/docker-desktop

3. **依赖安装失败**：
   ```bash
   # Python
   python -m pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   
   # Node.js
   npm config set registry https://registry.npmmirror.com
   npm install
   ```

### 查看日志
```bash
# Docker 部署
docker-compose logs -f

# 本地部署
# 查看启动脚本的终端输出
```

## 📞 帮助

- 详细部署说明：查看 `DEPLOYMENT.md`
- 项目介绍：查看 `README.md`
- 后端文档：查看 `backend/README.md`
- 前端文档：查看 `frontend/README.md`

---

**✨ 现在可以开始使用 AI 简历优化助手了！**