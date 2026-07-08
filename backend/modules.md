# 后端功能模块设计（Python / FastAPI）

> 目录：`backend/`（本仓库）  
> Python 3.11+ · FastAPI · SQLAlchemy · Pydantic v2

---

## 1. 目录结构

```text
backend/
├── app/
│   ├── main.py                 # FastAPI 入口、路由挂载、CORS
│   ├── core/
│   │   ├── config.py           # 读取 .env（pydantic-settings）
│   │   ├── security.py         # JWT、密码 hash
│   │   ├── deps.py             # 依赖注入：get_db, get_current_admin
│   │   └── exceptions.py       # 统一异常与 handler
│   ├── db/
│   │   ├── base.py             # declarative base
│   │   ├── session.py          # SessionLocal
│   │   └── init_db.py          # seed 管理员、Demo 数据
│   ├── models/                 # SQLAlchemy models
│   │   ├── admin_user.py
│   │   ├── knowledge_base.py
│   │   ├── document.py
│   │   ├── document_chunk.py
│   │   ├── chat_session.py
│   │   └── chat_message.py
│   ├── schemas/                # Pydantic 请求/响应
│   │   ├── auth.py
│   │   ├── kb.py
│   │   ├── document.py
│   │   ├── chat.py
│   │   └── common.py           # 统一响应 ApiResponse
│   ├── api/
│   │   ├── router.py           # 总路由
│   │   ├── admin/              # 管理端 /api/admin/*
│   │   │   ├── auth.py
│   │   │   ├── kb.py
│   │   │   ├── documents.py
│   │   │   ├── chats.py
│   │   │   └── stats.py
│   │   └── public/             # C 端 /api/public/*
│   │       ├── kb.py
│   │       └── chat.py
│   └── services/               # 业务逻辑
│       ├── auth_service.py
│       ├── kb_service.py
│       ├── document_service.py
│       ├── parser_service.py   # txt/md/pdf 解析
│       ├── chunk_service.py    # 分块
│       ├── embedding_service.py
│       ├── rag_service.py      # 检索 + prompt 组装
│       ├── llm_service.py      # DeepSeek 调用
│       ├── chat_service.py
│       └── storage_service.py  # local / oss 抽象
├── alembic/
├── uploads/                    # 本地存储（gitignore）
├── data/                       # SQLite 文件（gitignore）
├── seed/                       # 样例文档
├── tests/
├── requirements.txt
├── .env.example
└── alembic.ini
```

---

## 2. 模块职责

### 2.1 core — 核心基础设施

| 模块 | 职责 |
|------|------|
| config | 环境变量、常量 |
| security | JWT 签发/校验、bcrypt |
| deps | FastAPI Depends |
| exceptions | HTTP 4xx/5xx 统一格式 |

### 2.2 auth — 认证（管理端）

- 管理员登录
- Token 刷新（可选，Demo 可省略）
- 当前用户解析

### 2.3 kb — 知识库

- CRUD
- 启用/禁用、C 端可见开关
- 统计字段更新

### 2.4 document — 文档

-  multipart 上传
- 触发解析流水线
- 列表、删除、状态查询

### 2.5 parser — 文档解析

| 格式 | 库 |
|------|-----|
| txt | 内置 read |
| md | 内置 read |
| pdf | `pypdf` 或 `pdfplumber`（定稿选定） |

输出：纯文本 + char_count

### 2.6 chunk — 分块

- 按 `RAG_CHUNK_SIZE` / `RAG_CHUNK_OVERLAP` 切分
- 写入 `document_chunk`
- 更新 document.status

### 2.7 embedding — 向量化

- 调用 DeepSeek Embedding API
- 批量写入 chunk.embedding
- 失败标记 document.status = failed

### 2.8 rag — 检索增强

1. 用户 question → embedding
2. 与同 kb_id 下 chunk 做余弦相似度
3. 取 Top-K
4. 组装 Prompt（见下）

**降级：** Embedding 不可用时，用关键词匹配（LIKE / 简单 TF）

### 2.9 llm — 大模型

- OpenAI 兼容客户端调用 DeepSeek
- 支持 stream / non-stream
- 超时、重试（最多 2 次）

**Prompt 模板：**

```text
你是企业知识库助手。仅根据【参考资料】回答，资料不足请明确说明「知识库中未找到相关信息」，不要编造。

【参考资料】
{context}

【用户问题】
{question}
```

### 2.10 chat — 对话

- 创建/复用 session
- 保存 user / assistant 消息
- 返回 references

### 2.11 storage — 存储抽象

```python
class StorageBackend(Protocol):
    async def save(self, file: UploadFile, key: str) -> str: ...
    async def delete(self, key: str) -> None: ...
    async def read(self, key: str) -> bytes: ...
```

实现：`LocalStorageBackend`、`OSSStorageBackend`

---

## 3. 文档处理流水线

```text
上传 → pending
  → parsing（parser_service）
  → chunking（chunk_service）
  → embedding（embedding_service）
  → ready

任一步失败 → failed + error_message
```

Demo 阶段可 **同步执行**（上传接口内串行）；后续可改 BackgroundTasks / Celery。

---

## 4. 统一 API 响应格式

```json
{
  "code": 0,
  "message": "ok",
  "data": { }
}
```

错误：

```json
{
  "code": 40001,
  "message": "知识库不存在",
  "data": null
}
```

---

## 5. 依赖包（requirements.txt 预览）

```text
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
sqlalchemy>=2.0.0
alembic>=1.13.0
pydantic-settings>=2.0.0
python-jose[cryptography]
passlib[bcrypt]
python-multipart
httpx
pypdf                    # 或 pdfplumber
oss2                     # 生产 OSS 可选
```

---

## 6. 日志与监控

| 项 | 说明 |
|----|------|
| 日志 | structlog 或标准 logging，按 request_id |
| 健康检查 | `GET /health` |
| LLM 调用 | 记录 latency_ms 到 chat_message |

---

## 7. 模块与 Phase 对应

| 模块 | Phase |
|------|-------|
| core, db, auth | Phase 1 |
| kb, document, parser, chunk, storage | Phase 2 |
| embedding, rag, llm, chat, public API | Phase 3 |

---

## 8. 待定项

| 项 | 建议 |
|----|------|
| PDF 库 | pypdf（轻）/ pdfplumber（表格好） |
| 异步 ORM | Demo 同步 Session 即可 |
| 向量检索 | 应用层 numpy 余弦 |
