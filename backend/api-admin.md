# 管理端 API 接口文档

> Base URL：`http://127.0.0.1:8000`（本地）  
> 前缀：`/api/admin`  
> 认证：除登录外均需 Header `Authorization: Bearer <token>`

---

## 通用说明

### 请求头

```http
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### 分页参数（列表接口）

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| page | int | 1 | 页码 |
| page_size | int | 20 | 每页条数，最大 100 |

### 分页响应

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "items": [],
    "total": 0,
    "page": 1,
    "page_size": 20
  }
}
```

---

## 1. 认证 Auth

### 1.1 登录

`POST /api/admin/auth/login`

**Body:**

```json
{
  "username": "admin",
  "password": "demo123456"
}
```

**Response data:**

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 1.2 当前用户信息

`GET /api/admin/auth/me`

**Response data:**

```json
{
  "id": 1,
  "username": "admin",
  "nickname": "管理员"
}
```

### 1.3 退出（可选）

`POST /api/admin/auth/logout`

Demo 可仅前端清除 token。

---

## 2. 仪表盘 Stats

### 2.1 概览统计

`GET /api/admin/stats/overview`

**Response data:**

```json
{
  "kb_count": 2,
  "document_count": 8,
  "chunk_count": 156,
  "chat_count": 42,
  "today_chat_count": 5
}
```

### 2.2 近 7 日提问趋势

`GET /api/admin/stats/chat-trend?days=7`

**Response data:**

```json
{
  "items": [
    { "date": "2026-06-27", "count": 3 },
    { "date": "2026-06-28", "count": 8 }
  ]
}
```

---

## 3. 知识库 Knowledge Base

### 3.1 列表

`GET /api/admin/kb?page=1&page_size=20&keyword=`

**Response item:**

```json
{
  "id": 1,
  "name": "产品使用手册",
  "description": "对外产品文档",
  "status": "active",
  "is_public": true,
  "doc_count": 3,
  "chunk_count": 48,
  "created_at": "2026-06-01T10:00:00",
  "updated_at": "2026-06-01T10:00:00"
}
```

### 3.2 创建

`POST /api/admin/kb`

**Body:**

```json
{
  "name": "产品使用手册",
  "description": "可选描述",
  "is_public": true
}
```

### 3.3 详情

`GET /api/admin/kb/{id}`

### 3.4 更新

`PUT /api/admin/kb/{id}`

**Body:**

```json
{
  "name": "新名称",
  "description": "描述",
  "status": "active",
  "is_public": true
}
```

### 3.5 删除

`DELETE /api/admin/kb/{id}`

级联删除文档、分块、会话。

---

## 4. 文档 Documents

### 4.1 某知识库下的文档列表

`GET /api/admin/kb/{kb_id}/documents?page=1&page_size=20`

**Response item:**

```json
{
  "id": 1,
  "kb_id": 1,
  "filename": "常见问题.md",
  "file_ext": "md",
  "file_size": 4096,
  "char_count": 3200,
  "status": "ready",
  "error_message": null,
  "created_at": "2026-06-01T10:05:00"
}
```

### 4.2 上传文档

`POST /api/admin/kb/{kb_id}/documents`

**Content-Type:** `multipart/form-data`

| 字段 | 类型 | 说明 |
|------|------|------|
| file | File | txt / md / pdf |

**Response data:** 文档对象（status 可能为 pending，随后变 ready）

### 4.3 文档详情

`GET /api/admin/documents/{id}`

### 4.4 删除文档

`DELETE /api/admin/documents/{id}`

### 4.5 重新解析（可选）

`POST /api/admin/documents/{id}/reparse`

失败或更新文件后可触发。

---

## 5. 对话记录 Chats

### 5.1 会话列表

`GET /api/admin/chats/sessions?page=1&page_size=20&kb_id=&keyword=`

**Response item:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "kb_id": 1,
  "kb_name": "产品使用手册",
  "title": "如何重置密码？",
  "client_type": "h5",
  "message_count": 2,
  "created_at": "2026-06-01T11:00:00"
}
```

### 5.2 会话消息明细

`GET /api/admin/chats/sessions/{session_id}/messages`

**Response data:**

```json
{
  "session": { "id": "...", "kb_id": 1, "title": "..." },
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "如何重置密码？",
      "references_json": null,
      "created_at": "..."
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "您可以在设置-账号安全中...",
      "references_json": [{ "doc_name": "常见问题.md", "snippet": "..." }],
      "latency_ms": 1200,
      "created_at": "..."
    }
  ]
}
```

### 5.3 管理端试问答（可选，方便后台调试）

`POST /api/admin/chats/ask`

**Body:**

```json
{
  "kb_id": 1,
  "question": "如何重置密码？",
  "session_id": null
}
```

**Response:** 同 C 端问答结构（见 [`api-public.md`](./api-public.md)）

---

## 6. 系统设置 Settings

### 6.1 获取配置（脱敏）

`GET /api/admin/settings`

**Response data:**

```json
{
  "llm_model": "deepseek-chat",
  "embedding_model": "deepseek-embed",
  "rag_top_k": 5,
  "deepseek_configured": true,
  "storage_type": "local"
}
```

> API Key 不返回，仅返回是否已配置。

### 6.2 更新 RAG 参数（可选）

`PUT /api/admin/settings/rag`

**Body:**

```json
{
  "rag_top_k": 5,
  "rag_chunk_size": 500
}
```

Demo 可只做展示，不允许在线改 Key（Key 仅 `.env`）。

---

## 7. 健康检查（无需 admin 前缀）

`GET /health`

```json
{ "status": "ok", "version": "0.1.0" }
```

---

## 8. 错误码

| code | 说明 |
|------|------|
| 0 | 成功 |
| 40101 | 未登录或 token 无效 |
| 40301 | 无权限 |
| 40401 | 资源不存在 |
| 40001 | 参数错误 |
| 40002 | 文件格式不支持 |
| 40003 | 文件过大 |
| 50001 | 服务器内部错误 |
| 50002 | LLM 调用失败 |
| 50003 | 文档解析失败 |

---

## 9. 与数据表对应

| API 模块 | 主要表 |
|----------|--------|
| Auth | admin_user |
| KB | knowledge_base |
| Documents | document, document_chunk |
| Chats | chat_session, chat_message |
| Stats | 聚合查询 |

---

## 10. OpenAPI

开发环境自动生成：`http://127.0.0.1:8000/docs`
