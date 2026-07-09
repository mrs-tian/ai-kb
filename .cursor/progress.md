# 项目进度

> **每次完成一个 Phase 或关键步骤后，请更新本文件。**  
> 新对话开始时 AI 应先读此文件再继续。

---

## 当前状态

| 项 | 值 |
|----|-----|
| **当前阶段** | Phase 6 — uni-app |
| **下一步** | Phase 7：小程序体验版（可选） |
| **最后更新** | 2026-07-09 |
| **编码状态** | uni-app H5/小程序页面已完成，对接 public API |

---

## 阶段 checklist

### Phase 0 — 文档定稿

- [x] 项目目录结构确定（docs / backend / admin-web / uni-app）
- [x] `docs/config.md` 项目配置
- [x] `docs/execution-plan.md` 执行计划
- [x] `backend/` 文档（database, modules, api-admin, api-public）
- [x] `admin-web/` 文档（pages-modules, api-integration）
- [x] `uni-app/README.md` 占位
- [x] `.cursor` 项目上下文与进度文件
- [x] 你审阅文档并确认定稿
- [x] 通知 AI「进入开发」

### Phase 1 — backend 骨架 + 认证

- [x] 初始化 `backend/` FastAPI 项目
- [x] SQLAlchemy 模型 + Alembic
- [x] 管理员 JWT 登录
- [x] CORS、统一响应、`GET /health`
- [x] **验收：** uvicorn 启动；Postman 登录成功

### Phase 2 — 知识库 + 文档

- [x] 知识库 CRUD
- [x] 文档上传（local / OSS 可配置）
- [x] txt / md / pdf 解析 + 分块
- [x] **验收：** 文档 status → ready，chunk 有数据

### Phase 3 — RAG + 对话 API

- [x] DeepSeek Embedding + 向量检索
- [x] LLM 问答 + references
- [x] 管理端对话记录 API
- [x] C 端 `/api/public/*`
- [x] SSE 流式 + 非流式 fallback
- [x] **验收：** C 端可问答且带引用

### Phase 4 — admin-web

- [x] Vue3 项目初始化
- [x] 登录、仪表盘、知识库、文档上传、对话记录、设置
- [x] **验收：** 全流程联调无 mock

### Phase 5 — 联调与部署

- [x] 预置 Demo 样例文档（seed_demo_data.py + 生产已填充）
- [x] 生产环境部署（un.easytransfer.top / systemd / Nginx / SSL）
- [ ] README 截图 / 录屏

### Phase 6 — uni-app

- [x] 补充 uni-app 文档（README / pages-modules / api-integration）
- [x] H5 + 小程序页面（宣传首页、登录、知识库、AI 对话）
- [x] 对接生产 API + JWT 登录，知识库功能需后台账号
- [x] H5 部署至 https://www.easytransfer.top
- [x] 单账号 AI 日消耗上限 1 元
- [x] **验收：** `npm run build:h5` 通过

### Phase 7 — 小程序体验版（可选）

- [ ] 备案 + 体验版发布

---

## 已完成里程碑（日志）

| 日期 | 内容 |
|------|------|
| 2026-07-03 | 确定产品方向：AI 知识库问答 + RAG Demo |
| 2026-07-03 | 文档初版（backend Python / admin-web Vue / uni-app 暂缓） |
| 2026-07-03 | 目录重组：docs 仅项目级；子项目文档归入各代码目录 |
| 2026-07-03 | 创建 `.cursor` 项目上下文与进度跟踪 |
| 2026-07-03 | Phase 1 任务 1：初始化 backend FastAPI 骨架（目录、config、main、requirements） |
| 2026-07-03 | Phase 1 任务 2：SQLAlchemy 模型、Alembic 初始迁移、默认管理员 seed |
| 2026-07-06 | Phase 1 任务 3～4：JWT 登录、CORS、统一响应、`GET /health`，本地接口验收通过 |
| 2026-07-06 | Phase 2：知识库 CRUD、文档上传/解析/分块、本地存储，验收 status=ready 且 chunk 有数据 |
| 2026-07-06 | Phase 3：RAG 检索、LLM 问答、管理端/C 端对话 API、SSE 流式，本地验收通过 |
| 2026-07-06 | Phase 4：admin-web 全页面（登录/仪表盘/知识库/文档/对话/设置），build 通过 |
| 2026-07-07 | 用户自填 AI Key（DeepSeek/千问）、接口请求日志、admin 角色权限、用户管理、登录页优化 |
| 2026-07-07 | Phase 5：部署至 un.easytransfer.top，SSH 免密，Demo 数据填充，SSL 证书 |
| 2026-07-07 | Phase 6：uni-app H5/小程序，public API 对接，C 端 AI fallback |

---

## 待定决策（定稿前确认）

| 项 | 建议 | 状态 |
|----|------|------|
| Demo 数据库 | SQLite | 待定 |
| PDF 解析库 | pypdf / pdfplumber | 待定 |
| C 端鉴权 | 免登录 + IP 限流 | 待定 |
| DeepSeek Embedding 模型名 | 开发前核实官方文档 | 待定 |

---

## 给 AI 的备注

- 私活作品集项目，开发者：9 年前端 Vue，后端用 Python + Cursor 辅助
- 不要提前写 uni-app 代码，除非 Phase 6
- 配置密钥只放 `.env`，不写进文档
- 仅在你明确说「进入开发 / 开始 Phase X」时写代码
