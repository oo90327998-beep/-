# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

简历星球 — AI 简历优化助手。上传 PDF 简历 → 本地 pymupdf 抽取文本 → 硅基流动 LLM 结构化解析 + 逐模块修改建议。附带风格转换、ATS 检测、求职信、面试辅导、语音识别等功能。

## 开发命令

```bash
# 后端
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd frontend && npm install && npm run dev

# Docker 部署
docker-compose up -d

# 本地一键部署
./deploy-local.sh        # Linux/macOS
.\deploy-local.ps1       # Windows

# 性能基准测试
cd backend && python performance_benchmark.py
```

## 架构

### 后端 (FastAPI + SQLite)

```
backend/app/
├── main.py              → FastAPI 工厂函数, CORS, 注册路由
├── api/
│   ├── resume_routes.py → 核心路由: /ocr, /suggestions, /transform, /ats/check,
│   │                       /cover-letter, /interview-coach, /career-*, /chat,
│   │                       /speech-recognize, /ws/speech
│   └── auth_routes.py   → /auth/register, /auth/login, /auth/logout, /auth/me
├── db/
│   ├── init_db.py       → 建表 (resume_records, resume_versions, experience_answers,
│   │                       ats_reports, users)
│   └── repo.py          → ResumeRepo: SQLite CRUD + dataclass (ResumeRecord,
│                           ResumeVersion, ATSReport, User)
└── services/
    ├── siliconflow_client.py → LLM 客户端。chat() 调用 /chat/completions,
    │                           带重试(3次)、超时(180s)。extract_json_object()
    │                           从 LLM 输出中提取/修复 JSON
    ├── resume_ocr.py    → PDF 文本抽取(pymupdf/fitz) + 图片抽取 + llm_extract_sections()
    ├── suggestions.py   → llm_generate_suggestions() 逐模块建议
    ├── advanced_features.py → 风格转换、ATS检测、求职信、面试辅导、职业推荐、
    │                           职涯规划、简历助手
    ├── performance_cache.py → ResultCache(LRU, max 200) + PerformanceMonitor
    └── xunfei_speech.py → 讯飞语音识别 (WebSocket, WAV→PCM 转换)
```

**数据流**: PDF上传 → `/ocr` → pymupdf抽取文本 → 硅基流动 LLM 结构化 sections → 存 SQLite → `/suggestions` → LLM 生成建议 → 存 SQLite

**配置**: `backend/config/siliconflow.json` (baseUrl, apiKey, model)，环境变量可覆盖（`SILICONFLOW_API_KEY`, `SILICONFLOW_BASE_URL`, `SILICONFLOW_MODEL`）。CORS 通过 `CORS_ALLOW_ORIGINS` 环境变量（默认 `*`）。

### 前端 (Vue 3 + TypeScript + Vite)

```
frontend/src/
├── App.vue              → 主壳: 导航栏、粒子背景、视图路由（upload/diff/ats/templates/career）
├── api/client.ts        → API 调用函数，base 路径 /api
├── types.ts             → 共享 TS 类型
└── components/
    ├── UploadView.vue        → 文件上传页
    ├── DiffView.vue          → 简历对比 + AI 建议展示（核心页面）
    ├── TemplateLibrary.vue   → 模板选择
    ├── CareerTools.vue       → 职业工具（求职信、面试辅导等）
    ├── VersionManager.vue    → ATS 检测 + 版本管理
    ├── ExperienceExcavator.vue → 经历挖掘
    └── LoginView.vue         → 登录/注册
```

Vite 开发代理 `/api` → `http://localhost:8000`。无测试框架配置。

### 数据库

SQLite (`backend/data/resume.db`)，路径可通过 `RESUME_DB_PATH` 环境变量覆盖。表: `resume_records`, `resume_versions`, `experience_answers`, `ats_reports`, `users`。首次启动自动建表。

### 认证

自实现 token 认证（`JWT_SECRET_KEY` 环境变量，默认随机生成）。token 为 `user_id:username:expire:signature` 格式，有效期 168 小时。支持 cookie + Bearer header。

## 关键约定

- Python 环境在项目根 `.venv/`
- `__pycache__/` 目录已被 git 追踪，应加到 `.gitignore`
- 配置文件中的 API key 已提交到 git（安全问题，需处理）
- PDF 文件限制 ≤ 20MB
- LLM 响应中的 JSON 可能格式不完整，`extract_json_object()` 会自动修复（补括号、去尾部逗号等）
