# uni-app — 移动端（H5 + 微信小程序）

> Vue 3 · uni-app · 对接生产 API `https://un.easytransfer.top`

C 端：宣传首页（免登录）→ 登录 → 知识库问答。

---

## 页面

| 页面 | 路径 | 说明 |
|------|------|------|
| 宣传首页 | `pages/home/home` | 动效介绍页，无需登录 |
| 登录 | `pages/login/login` | 后台 `admin_user` 账号 |
| 知识库列表 | `pages/kb/list` | 需登录 |
| AI 对话 | `pages/chat/chat` | 需登录，非流式问答 + 引用 |

详见 [`pages-modules.md`](./pages-modules.md)、[`api-integration.md`](./api-integration.md)。

---

## 启动

```bash
cd uni-app
npm install
npm run dev:h5    # http://127.0.0.1:5174
```

**API：** 生产 H5 部署于 `https://www.easytransfer.top`，API 同域 `/api`。

**登录：** 与管理后台相同账号（如 `admin` / `demo123456`）。问答使用**当前登录用户**在后台配置的 AI Key。

---

## 构建

```bash
npm run build:h5
npm run build:mp-weixin
```

---

## 相关文档

- C 端 API：[`backend/api-public.md`](../backend/api-public.md)
- 项目配置：[`docs/config.md`](../docs/config.md)
