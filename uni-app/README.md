# uni-app — 移动端（H5 + 微信小程序）

> Vue 3 · uni-app · 对接 `/api/public/*`

C 端 AI 知识库问答：选知识库 → 对话 → 展示引用来源。

---

## 状态

**Phase 6 已完成基础开发**：知识库列表、AI 对话、引用展示、H5 / 小程序构建脚本。

---

## 页面

| 页面 | 路径 | 说明 |
|------|------|------|
| 知识库列表 | `pages/index/index` | 公开知识库列表 |
| AI 对话 | `pages/chat/chat` | 非流式问答 + 引用来源 |

详见 [`pages-modules.md`](./pages-modules.md)、[`api-integration.md`](./api-integration.md)。

---

## 启动

```bash
cd uni-app
npm install

# H5 开发（端口 5174，代理 /api → 127.0.0.1:8000）
npm run dev:h5

# 微信小程序开发
npm run dev:mp-weixin
```

**前置：** 本地后端 `uvicorn` 已启动；管理端 `admin` 账号已在「AI 配置」填写 API Key（C 端复用该 Key）。

---

## 构建

```bash
npm run build:h5          # 输出 dist/build/h5
npm run build:mp-weixin   # 输出 dist/build/mp-weixin
```

---

## 相关文档

- C 端 API：[`backend/api-public.md`](../backend/api-public.md)
- 项目配置：[`docs/config.md`](../docs/config.md)
