# 执行顺序与阶段规划

> **文档定稿 + 你明确通知后** 才进入编码。  
> 项目配置入口：[`docs/config.md`](../docs/config.md)

---

## 阶段总览

```
Phase 0  文档定稿 ◄── 当前
Phase 1  backend：骨架 + 数据库 + 认证
Phase 2  backend：知识库 + 文档 + 分块
Phase 3  backend：RAG + 对话 + C 端 API
Phase 4  admin-web：全页面
Phase 5  联调 + 部署
Phase 6  uni-app（后续）
Phase 7  小程序体验版（可选）
```

---

## Phase 0：文档定稿

| 序号 | 审阅文件 |
|------|----------|
| 0.1 | `docs/config.md` |
| 0.2 | `backend/database.md` |
| 0.3 | `backend/modules.md` |
| 0.4 | `backend/api-admin.md` |
| 0.5 | `backend/api-public.md` |
| 0.6 | `admin-web/pages-modules.md`、`admin-web/api-integration.md` |
| 0.7 | 你通知「进入开发」 |

---

## Phase 1：backend 骨架 + 认证

| 任务 | 文档 |
|------|------|
| 初始化 `backend/` FastAPI | `backend/modules.md` |
| 模型 + Alembic | `backend/database.md` |
| JWT 登录 | `backend/api-admin.md` § Auth |
| CORS、统一响应 | `docs/config.md` |

**验收：** uvicorn 启动；可登录拿 token。

---

## Phase 2：知识库 + 文档

| 任务 | 文档 |
|------|------|
| 知识库 CRUD | `backend/api-admin.md` |
| 上传 + 解析 txt/md/pdf | `backend/modules.md` |
| 分块入库 | `backend/database.md` |

**验收：** 上传文档 → status `ready` → chunk 有数据。

---

## Phase 3：RAG + 对话

| 任务 | 文档 |
|------|------|
| Embedding + 检索 | `backend/modules.md` |
| 管理端对话记录 | `backend/api-admin.md` |
| C 端公开 API | `backend/api-public.md` |

**验收：** 问答带 references；C 端无需 admin token。

---

## Phase 4：admin-web

| 任务 | 文档 |
|------|------|
| 路由、布局、各页面 | `admin-web/pages-modules.md` |
| API 对接 | `admin-web/api-integration.md` |

**验收：** 登录 → 建库 → 上传 → 试问答 → 看记录。

---

## Phase 5～7

- **Phase 5：** 预置样例、部署、录屏  
- **Phase 6：** 补充 `uni-app/` 文档与代码  
- **Phase 7：** 小程序体验版  

---

## 待定项

| 项 | 建议 |
|----|------|
| 数据库 | Demo 用 SQLite |
| OSS | 开发 local，生产 OSS |
| C 端 | 免登录 + IP 限流 |
| PDF | pypdf 或 pdfplumber |

---

## 建议工时（6～8h/周）

Phase 1～2 各 1 周；Phase 3～4 各 1～2 周；Phase 5 约 0.5 周。
