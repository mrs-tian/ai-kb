# Vue 管理后台 — API 对接清单

> Axios baseURL：`import.meta.env.VITE_API_BASE_URL`  
> 统一响应：`{ code, message, data }`，`code === 0` 为成功

---

## 1. 请求封装（request.ts）

```typescript
// 伪代码要点
axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
axios.interceptors.response.use(res => {
  if (res.data.code !== 0) {
    ElMessage.error(res.data.message)
    if (res.data.code === 40101) router.push('/login')
    return Promise.reject(res.data)
  }
  return res.data.data
})
```

---

## 2. 接口对接总表

| 页面/功能 | 方法 | 路径 | api 文件 |
|-----------|------|------|----------|
| 登录 | POST | `/api/admin/auth/login` | auth.ts |
| 当前用户 | GET | `/api/admin/auth/me` | auth.ts |
| 概览统计 | GET | `/api/admin/stats/overview` | stats.ts |
| 提问趋势 | GET | `/api/admin/stats/chat-trend` | stats.ts |
| 知识库列表 | GET | `/api/admin/kb` | kb.ts |
| 创建知识库 | POST | `/api/admin/kb` | kb.ts |
| 知识库详情 | GET | `/api/admin/kb/:id` | kb.ts |
| 更新知识库 | PUT | `/api/admin/kb/:id` | kb.ts |
| 删除知识库 | DELETE | `/api/admin/kb/:id` | kb.ts |
| 文档列表 | GET | `/api/admin/kb/:kbId/documents` | document.ts |
| 上传文档 | POST | `/api/admin/kb/:kbId/documents` | document.ts |
| 删除文档 | DELETE | `/api/admin/documents/:id` | document.ts |
| 重新解析 | POST | `/api/admin/documents/:id/reparse` | document.ts |
| 会话列表 | GET | `/api/admin/chats/sessions` | chat.ts |
| 会话消息 | GET | `/api/admin/chats/sessions/:id/messages` | chat.ts |
| 试问答 | POST | `/api/admin/chats/ask` | chat.ts |
| 系统设置 | GET | `/api/admin/settings` | stats.ts |

---

## 3. 各模块 TypeScript 类型（概要）

### 3.1 KnowledgeBase

```typescript
export interface KnowledgeBase {
  id: number
  name: string
  description?: string
  status: 'active' | 'disabled'
  is_public: boolean
  doc_count: number
  chunk_count: number
  created_at: string
  updated_at: string
}
```

### 3.2 Document

```typescript
export type DocumentStatus =
  | 'pending' | 'parsing' | 'embedding' | 'ready' | 'failed'

export interface Document {
  id: number
  kb_id: number
  filename: string
  file_ext: string
  file_size: number
  char_count: number
  status: DocumentStatus
  error_message?: string
  created_at: string
}
```

### 3.3 Chat

```typescript
export interface ChatSession {
  id: string
  kb_id: number
  kb_name?: string
  title?: string
  client_type?: string
  message_count?: number
  created_at: string
}

export interface ChatMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
  references_json?: Reference[]
  latency_ms?: number
  created_at: string
}

export interface Reference {
  doc_id: number
  doc_name: string
  chunk_id: number
  snippet: string
  score: number
}
```

---

## 4. 上传文档对接

```typescript
export function uploadDocument(kbId: number, file: File) {
  const form = new FormData()
  form.append('file', file)
  return request.post(`/api/admin/kb/${kbId}/documents`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  })
}
```

---

## 5. 试问答对接

**优先：** `POST /api/admin/chats/ask`

```typescript
export function askQuestion(data: {
  kb_id: number
  question: string
  session_id?: string
}) {
  return request.post('/api/admin/chats/ask', data)
}
```

**备选：** 直接调 C 端 `POST /api/public/chat`（无需 admin 专用接口时）

---

## 6. C 端公开接口（管理端仅调试时可调）

| 方法 | 路径 | 用途 |
|------|------|------|
| GET | `/api/public/kb` | 预览 C 端可见库 |
| POST | `/api/public/chat` | 与线上一致问答 |

完整说明：[`api-public.md`](../backend/api-public.md)

管理端 **正常业务流程不依赖** public API。

---

## 7. 环境变量

**`.env.development`**

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_APP_TITLE=智问知识库管理后台
```

**`.env.production`**

```env
VITE_API_BASE_URL=https://api.example.com
VITE_APP_TITLE=智问知识库管理后台
```

---

## 8. 联调顺序

1. 登录拿 token  
2. 创建知识库  
3. 上传 md 文档，轮询至 ready  
4. KbDetail 试问答  
5. ChatList 查看记录  
6. Dashboard 数字正确  

---

## 9. Mock 策略

文档阶段 **不使用 mock**。  
开发时后端未就绪可临时 `vite-plugin-mock`，定稿后删除。

---

## 10. 相关文档

- 管理端 API 详情：[`api-admin.md`](../backend/api-admin.md)
- 数据表：[`database.md`](../backend/database.md)
- 项目配置：[`config.md`](../docs/config.md)
