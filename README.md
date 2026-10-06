# NL2SQL Agent

> 基于 LangChain 构建的 NL2SQL 数据分析系统，支持自然语言转 SQL、数据查询与可视化。

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-v1+-green)](https://www.langchain.com/)
[![React](https://img.shields.io/badge/React-18+-61dafb)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688)](https://fastapi.tiangolo.com/)
[![Milvus](https://img.shields.io/badge/Milvus-v2.3+-blueviolet)](https://milvus.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ 特性

- 💬 **自然语言查询**：用大白话提问，自动生成 SQL 并执行
- 📊 **数据可视化**：自动生成图表，直观展示查询结果
- 🧠 **Schema 理解**：基于向量检索的表结构理解，支持复杂数据库
- 🔐 **安全可控**：SQL 白名单、权限控制、防止危险操作
- 🎨 **现代前端**：React + Vite + TailwindCSS 数据分析界面
- 🐳 **容器化部署**：Milvus + 后端 + 前端 Docker 编排

---

## 🏗️ 技术架构

```
┌──────────────────────────────────────────────────┐
│                    Frontend                      │
│            (React + Vite + ECharts)              │
│  ┌─────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ 对话界面 │ │ SQL 展示 │ │ 图表可视化       │  │
│  └─────────┘ └──────────┘ └──────────────────┘  │
└──────────────────────┬───────────────────────────┘
                       │
           ┌───────────▼────────────┐
           │       Backend          │
           │      (FastAPI)         │
           │  ┌──────────────────┐  │
           │  │  NL2SQL Agent    │  │  LangChain
           │  │  (SQL 生成)      │  │
           │  └──────────────────┘  │
           │  ┌──────────────────┐  │
           │  │ Schema 检索      │  │  Milvus
           │  │  (表结构理解)    │  │
           │  └──────────────────┘  │
           └────────────────────────┘
```

---

## 📁 项目结构

```
.
├── backend/                    # 后端服务
│   ├── app/
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── frontend/                   # 前端
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── milvus-deployment/          # Milvus 部署配置
├── app_jina_embedding_v4.py    # Embedding 服务
└── README.md
```

> 💡 **模型文件**：Embedding 模型权重位于 `../data/embedding-models/`（约 7GB）。

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- Milvus 向量数据库
- 大模型 API Key（如 GPT-4、Qwen 等）
- Embedding 模型

### 后端启动

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 填入 API Key、数据库连接、Milvus 地址等

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Milvus 启动

```bash
cd milvus-deployment
docker compose up -d
```

### 前端启动

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

访问 http://localhost:5173

---

## 📚 相关课程

- 📖 课程文档：[飞书知识库](https://scnxinvxtnbo.feishu.cn/wiki/JMLuwxuc6i5iUrkblYuc1b97ncd)
- 🎥 视频教程：[课程链接](#)（待补充）

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
