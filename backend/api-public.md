# C 端公开 API 接口文档

> 前缀：`/api/public`  
> **需管理员 JWT 登录**（与 `/api/admin/auth/login` 共用账号）  
> 供 uni-app / H5 调用

---

## 1. 安全策略

| 措施 | 说明 |
|------|------|
| 认证 | Header `Authorization: Bearer <token>`，后台 `admin_user` 账号 |
| 限流 | 每 IP 每分钟 `PUBLIC_RATE_LIMIT` 次（见 config.md） |
| 可见范围 | 仅 `is_public=true` 且 `status=active` 的知识库 |
| AI Key | 使用**当前登录用户**已配置的 API Key（非 `PUBLIC_AI_USERNAME`） |
| 会话 | 客户端传 `session_id` 续聊；不传则新建 |

---

## 2. 知识库

### 2.1 公开知识库列表

`GET /api/public/kb`

**Query:** 无

**Response data:**

```json
{
  "items": [
    {
      "id": 1,
      "name": "产品使用手册",
      "description": "产品介绍与常见问题"
    }
  ]
}
```

> 不返回文档列表、内部统计。

### 2.2 知识库简要信息

`GET /api/public/kb/{id}`

**Response data:**

```json
{
  "id": 1,
  "name": "产品使用手册",
  "description": "产品介绍与常见问题",
  "doc_count": 3
}
```

若不存在或未公开：`40401`

---

## 3. 对话 Chat

### 3.1 问答（非流式，小程序优先）

`POST /api/public/chat`

**Body:**

```json
{
  "kb_id": 1,
  "question": "如何重置密码？",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| kb_id | 是 | 知识库 ID |
| question | 是 | 用户问题，1～2000 字 |
| session_id | 否 | 续聊；空则新建会话 |

**Response data:**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "answer": "您可以在「设置 - 账号安全」中选择重置密码...",
  "references": [
    {
      "doc_id": 2,
      "doc_name": "常见问题.md",
      "chunk_id": 15,
      "snippet": "重置密码：进入设置页...",
      "score": 0.89
    }
  ],
  "latency_ms": 1350
}
```

**错误示例：**

```json
{
  "code": 50002,
  "message": "AI 服务暂时不可用，请稍后重试",
  "data": null
}
```

### 3.2 问答（流式 SSE，H5 用）

`POST /api/public/chat/stream`

**Body:** 同 3.1

**Response:** `Content-Type: text/event-stream`

```
event: session
data: {"session_id":"550e8400-..."}

event: delta
data: {"content":"您可以在"}

event: delta
data: {"content":"设置页"}

event: references
data: {"references":[...]}

event: done
data: {"latency_ms":1350}
```

**说明：**

- 微信小程序不支持标准 SSE 时，**只用 3.1 非流式**
- H5 可先显示 loading，流式逐字展示

### 3.3 获取会话历史（可选）

`GET /api/public/chat/sessions/{session_id}/messages`

**用途：** H5 刷新后恢复对话

**Response data:**

```json
{
  "session_id": "...",
  "kb_id": 1,
  "messages": [
    { "role": "user", "content": "...", "created_at": "..." },
    { "role": "assistant", "content": "...", "references": [], "created_at": "..." }
  ]
}
```

**安全：** Demo 仅凭 session_id 查询（uuid 不可猜测）；生产可加签名或短期 token。

---

## 4. 客户端类型标识

请求头（可选）：

```http
X-Client-Type: h5 | mp-weixin
```

写入 `chat_session.client_type`，便于后台统计。

---

## 5. uni-app 对接要点（后续）

| 端 | 接口 | 备注 |
|----|------|------|
| H5 | `/chat/stream` 或 `/chat` | 流式体验更好 |
| 微信小程序 | `/chat` 非流式 | 域名需配置 request 合法域名 |
| 两者 | `/kb` 列表 | 首页展示 |

**合法域名：** 上线小程序前，微信公众平台配置 `https://api.example.com`

---

## 6. 调用示例

### curl — 列表

```bash
curl http://127.0.0.1:8000/api/public/kb
```

### curl — 问答

```bash
curl -X POST http://127.0.0.1:8000/api/public/chat \
  -H "Content-Type: application/json" \
  -d '{"kb_id":1,"question":"如何重置密码？"}'
```

---

## 7. 与管理端 API 边界

| 能力 | 管理端 `/api/admin` | C 端 `/api/public` |
|------|---------------------|---------------------|
| 知识库 CRUD | ✅ | ❌ 只读列表 |
| 文档上传 | ✅ | ❌ |
| 问答 | 可选调试接口 | ✅ |
| 对话记录 | 全部 | 仅当前 session_id |
| 统计 | ✅ | ❌ |

---

## 8. 待定项

| 项 | 建议 | 确认 |
|----|------|------|
| C 端是否要 API Key | Demo 不要 | ☐ |
| session 保留天数 | 90 天定时清理 | ☐ |
| 单次 question 长度 | 2000 字 | ☐ |
