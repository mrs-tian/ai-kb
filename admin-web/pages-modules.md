# Vue 管理后台 — 页面与功能模块

> 目录：`admin-web/`  
> Vue 3 + Vite + TypeScript + Element Plus + Pinia + Vue Router

---

## 1. 路由结构

| 路径 | 页面 | 菜单 | 说明 |
|------|------|------|------|
| `/login` | Login | 否 | 登录 |
| `/` | Layout | — | 重定向 `/dashboard` |
| `/dashboard` | Dashboard | 仪表盘 | 统计概览 |
| `/kb` | KbList | 知识库 | 列表 |
| `/kb/:id` | KbDetail | — | 详情 + 文档管理 |
| `/chats` | ChatList | 对话记录 | 会话列表 |
| `/chats/:sessionId` | ChatDetail | — | 消息明细 |
| `/settings` | Settings | 系统设置 | 只读配置展示 |

---

## 2. 布局 Layout

```text
┌──────────────────────────────────────────────────┐
│ Logo  智问知识库                    admin ▼ 退出   │
├──────────┬───────────────────────────────────────┤
│ 仪表盘    │                                       │
│ 知识库    │           <router-view />             │
│ 对话记录  │                                       │
│ 系统设置  │                                       │
└──────────┴───────────────────────────────────────┘
```

- 侧边栏可折叠
- 未登录访问除 `/login` 外路由 → 跳转登录

---

## 3. 功能模块明细

### 3.1 登录 Login

| 项 | 说明 |
|----|------|
| 表单 | 用户名、密码 |
| 校验 | 必填 |
| 成功 | 存 token（localStorage）→ `/dashboard` |
| API | `POST /api/admin/auth/login` |

### 3.2 仪表盘 Dashboard

| 区块 | 内容 |
|------|------|
| 统计卡片 ×4 | 知识库数、文档数、分块数、累计问答 |
| 折线图 | 近 7 日提问趋势 |
| 快捷入口 | 「新建知识库」「查看对话」 |

**API：**

- `GET /api/admin/stats/overview`
- `GET /api/admin/stats/chat-trend?days=7`

### 3.3 知识库列表 KbList

| 功能 | 说明 |
|------|------|
| 表格 | 名称、描述、文档数、状态、C端可见、创建时间 |
| 搜索 | 名称 keyword |
| 操作 | 新建、编辑、进入详情、删除（二次确认） |
| 新建/编辑 | Dialog 表单 |

**API：**

- `GET /api/admin/kb`
- `POST /api/admin/kb`
- `PUT /api/admin/kb/{id}`
- `DELETE /api/admin/kb/{id}`

### 3.4 知识库详情 KbDetail

| 区块 | 说明 |
|------|------|
| 基本信息 | 名称、描述、状态、是否公开（可编辑保存） |
| 文档表格 | 文件名、大小、状态、字符数、上传时间 |
| 上传 | el-upload drag，支持 txt/md/pdf |
| 状态 | pending/parsing/ready/failed 标签色 |
| 失败 | 展示 error_message，可「重新解析」 |
| 试问答 | 底部折叠 Panel：输入问题 → 调 admin ask 或 public chat |

**API：**

- `GET /api/admin/kb/{id}`
- `PUT /api/admin/kb/{id}`
- `GET /api/admin/kb/{id}/documents`
- `POST /api/admin/kb/{id}/documents`
- `DELETE /api/admin/documents/{id}`
- `POST /api/admin/documents/{id}/reparse`（可选）

**上传后轮询：** 每 3s 刷新文档列表直到 status=ready/failed（最多 2 分钟）

### 3.5 对话记录 ChatList

| 功能 | 说明 |
|------|------|
| 表格 | 会话标题、知识库、来源(h5/mp)、消息数、时间 |
| 筛选 | kb_id 下拉、keyword |
| 操作 | 查看详情 |

**API：** `GET /api/admin/chats/sessions`

### 3.6 对话详情 ChatDetail

| 功能 | 说明 |
|------|------|
| 消息列表 | 左右气泡 user / assistant |
| 引用 | assistant 下折叠展示 references |
| 元信息 | latency_ms、时间 |

**API：** `GET /api/admin/chats/sessions/{id}/messages`

### 3.7 系统设置 Settings

| 展示项 | 说明 |
|--------|------|
| LLM 模型 | 只读 |
| Embedding 模型 | 只读 |
| RAG Top K | 只读或可编辑（若后端支持） |
| 存储类型 | local / oss |
| DeepSeek | 已配置 / 未配置 |

**API：** `GET /api/admin/settings`

> API Key 不在前端展示；提示「请在服务器 .env 配置」

---

## 4. 前端目录结构

```text
admin-web/
├── src/
│   ├── api/
│   │   ├── request.ts        # axios 封装、token、错误处理
│   │   ├── auth.ts
│   │   ├── kb.ts
│   │   ├── document.ts
│   │   ├── chat.ts
│   │   └── stats.ts
│   ├── stores/
│   │   └── user.ts
│   ├── router/
│   │   └── index.ts
│   ├── layouts/
│   │   └── MainLayout.vue
│   ├── views/
│   │   ├── login/LoginView.vue
│   │   ├── dashboard/DashboardView.vue
│   │   ├── kb/KbListView.vue
│   │   ├── kb/KbDetailView.vue
│   │   ├── chat/ChatListView.vue
│   │   ├── chat/ChatDetailView.vue
│   │   └── settings/SettingsView.vue
│   ├── components/
│   │   ├── StatCard.vue
│   │   └── ChatBubble.vue
│   ├── types/
│   │   └── index.ts
│   ├── utils/
│   └── main.ts
├── .env.development
├── .env.production
└── vite.config.ts
```

---

## 5. 状态与交互规范

| 项 | 规范 |
|----|------|
| 加载 | 表格 v-loading |
| 空态 | el-empty |
| 删除 | MessageBox 确认 |
| 错误 | ElMessage 展示 message |
| Token 过期 | 401 → 清 token → `/login` |

---

## 6. 与数据表关系（只读理解）

| 页面 | 主要数据 |
|------|----------|
| KbList / KbDetail | knowledge_base, document |
| ChatList / ChatDetail | chat_session, chat_message |
| Dashboard | 聚合 |

详细表结构见 [`database.md`](../backend/database.md)

---

## 7. 不做（Demo 范围外）

- 多管理员 / 角色权限
- 在线修改 DeepSeek Key
- 文档在线编辑
- 国际化

---

## 8. UI 参考

- 主色：Element Plus 默认蓝或 `#409EFF`
- 表格 + Dialog 为主，不做复杂动效
- 知识库详情「试问答」便于录屏演示

---

## 9. 待定项

| 项 | 建议 |
|----|------|
| 图表库 | ECharts 或 vue-echarts |
| 试问答入口 | KbDetail 页内嵌 |
