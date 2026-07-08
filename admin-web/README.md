# admin-web — 管理后台

> Vue 3 + Vite + TypeScript + Element Plus + Pinia

知识库管理、文档上传、对话记录查看、系统配置展示。

---

## 职责

- 管理员登录
- 知识库 CRUD、文档上传与状态查看
- 仪表盘统计、对话记录
- 知识库内试问答（调后端）

---

## 本目录文档

| 文件 | 说明 |
|------|------|
| [pages-modules.md](./pages-modules.md) | 路由、页面、功能模块 |
| [api-integration.md](./api-integration.md) | 后端 API 对接清单、TS 类型 |

---

## 环境与启动

```bash
cd admin-web
npm install
npm run dev
```

默认访问 `http://localhost:5173`，API 地址见 `.env.development`（`VITE_API_BASE_URL=http://127.0.0.1:8000`）。

**联调前请先启动后端：**

```bash
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

`VITE_API_BASE_URL` 等见 [`docs/config.md`](../docs/config.md)。

---

## 依赖后端

- 管理端 API：[`backend/api-admin.md`](../backend/api-admin.md)
- 数据模型：[`backend/database.md`](../backend/database.md)

---

## 开发阶段

见 [`docs/execution-plan.md`](../docs/execution-plan.md) Phase 4。
