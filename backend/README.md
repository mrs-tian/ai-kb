# backend — AI 知识库后端

> Python 3.11+ · FastAPI · SQLAlchemy · RAG（DeepSeek）

提供管理端 API（`/api/admin`）与 C 端公开 API（`/api/public`）。

---

## 职责

- 知识库与文档管理、解析分块
- Embedding + 向量检索 + LLM 问答
- 对话会话持久化
- JWT 管理员认证

---

## 本目录文档

| 文件 | 说明 |
|------|------|
| [database.md](./database.md) | 数据表设计 |
| [modules.md](./modules.md) | 代码结构、模块职责、RAG 流水线 |
| [api-admin.md](./api-admin.md) | 管理端接口 |
| [api-public.md](./api-public.md) | C 端公开接口（uni-app / H5） |

---

## 环境与启动

环境变量、DeepSeek、OSS 见 [`docs/config.md`](../docs/config.md)。

### 本地 Python（uv + .venv）

本机用 **uv** 切换 Python 版本；系统默认 `python` 为 3.6，需用 uv 创建虚拟环境：

```powershell
cd D:\ai-kb-demo\backend
uv venv --python 3.11
.\.venv\Scripts\activate
uv pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

完整说明（版本列表、切换命令、备选方案）见 [`docs/config.md` → 本地 Python 环境](../docs/config.md#本地-python-环境windows)。

本地 API 文档：`http://127.0.0.1:8000/docs`

---

## 开发阶段

见 [`docs/execution-plan.md`](../docs/execution-plan.md) Phase 1～3。

---

## 代码目录（规划）

代码将实现在本目录下，结构见 [modules.md](./modules.md)。
