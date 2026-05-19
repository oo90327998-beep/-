# AI 简历优化助手（演示：Vue + FastAPI + SQLite + 硅基流动）

学员上传简历 PDF -> 后端用本地 pymupdf 抽取文本 -> 用硅基流动模型对文本做结构化解析（sections）并生成逐模块修改建议。

## 关键模块说明（模型与 OCR）
本项目把“简历理解”拆成两步：先把 PDF 里的文字读出来（OCR/抽取在本地完成），再让模型基于文本进行结构化解析和生成建议。

### 硅基流动模型（LLM）
用到的硅基流动模型在 `backend/config/siliconflow.json` 中配置：
- `model`: `Qwen2.5-72B-Instruct`（该文件里第 4 行）

它在项目里主要承担两类“AI 文本处理”（都通过 `backend/app/services/siliconflow_client.py` 的 `chat()` 调用 `/chat/completions`）：

1. **结构化解析（生成 sections）**
   - 位置：`backend/app/services/resume_ocr.py` 的 `llm_extract_sections()`
   - 作用：把本地抽取到的简历文本，按“基本信息/教育/实习/项目/技能/证书/自我评价”等模块结构化成 JSON
   - 返回：`sections: [{ name, content }, ...]`

2. **逐模块修改建议（issues / recommendations / rewrite_example）**
   - 位置：`backend/app/services/suggestions.py` 的 `llm_generate_suggestions()`
   - 作用：把“简历完整文本 + 上一步的 sections”一起喂给模型，让它为每个模块输出
     - `issues`：当前模块常见问题（最多 3-5 条）
     - `recommendations`：具体怎么改（最多 3-5 条）
     - `rewrite_example`：改写示例
   - 另外还会输出整份简历的 `overall_summary`

补充一句：本项目不把 OCR/文本抽取交给硅基流动完成；PDF 转文本由本地 `pymupdf`（fitz）负责。硅基流动只负责理解与生成（sections 和逐模块建议）。

### 本地 `pymupdf`（fitz）
是一个本地的 Python 库，不走硅基流动 API。

作用：在后端把用户上传的 PDF 抽取为可读文本，让后续大模型能“读懂”。

对应代码：
- 文件：`backend/app/services/resume_ocr.py`
- 函数：`extract_text_from_pdf_bytes()`（内部通过 `fitz.open(...)` 打开 PDF）
- 逻辑：遍历每一页 `page.get_text("text")` 把页面文字抽取出来，再拼成一段总文本返回

课堂提醒：
- 对“文字型 PDF”（PDF 本身包含文字）效果最好
- 若用户上传的是“扫描件 PDF”（图片，没有真实文本层），`page.get_text()` 可能提取不到文字；这时你需要再补“视觉 OCR”方案（例如接入视觉 OCR，再替换抽取文本这一步）

## 后端
见 `backend/README.md`

## 前端
见 `frontend/README.md`

## 🚀 一键部署

### 快速开始
项目提供多种部署方式，选择最适合你的方案：

#### 最简单的方法
- **Windows 用户**：双击 `start.bat`
- **Linux/macOS 用户**：运行 `./start.sh`

#### Docker 部署（推荐）
```bash
# Windows
.\deploy.ps1

# Linux/macOS
chmod +x deploy.sh
./deploy.sh
```

#### 本地部署（无需 Docker）
```bash
# Windows
.\deploy-local.ps1

# Linux/macOS
chmod +x deploy-local.sh
./deploy-local.sh
```

### 访问应用
- **前端应用**：http://localhost（Docker）或 http://localhost:5173（本地）
- **API 文档**：http://localhost:8000/docs

### 详细文档
- [部署指南](DEPLOYMENT.md) - 完整的部署说明
- [快速开始](QUICK_START.md) - 简化版快速入门

## 🛠️ 系统要求

### 最小要求
- **内存**：4GB
- **存储空间**：2GB
- **操作系统**：Windows 10+ / macOS 10.15+ / Ubuntu 18.04+

### 依赖项
- **Docker 部署**：Docker 20.10+
- **本地部署**：Python 3.8+，Node.js 16+

## 📞 帮助与支持

如果在部署或使用过程中遇到问题：

1. 查看 `DEPLOYMENT.md` 中的故障排除章节
2. 检查日志文件：
   ```bash
   # Docker 部署
   docker-compose logs -f
   ```
3. 确保网络连接正常，能访问硅基流动 API
4. 验证依赖包是否正确安装

## 🔧 开发

### 后端开发
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发
```bash
cd frontend
npm install
npm run dev
```

## 📄 许可证

本项目仅供学习使用。