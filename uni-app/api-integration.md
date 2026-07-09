# uni-app API 对接说明

## 基址配置

| 环境 | 文件 | `VITE_API_BASE_URL` |
|------|------|---------------------|
| 开发 H5 | `.env.development` | `https://un.easytransfer.top` |
| 生产 H5 | `.env.production` | `https://un.easytransfer.top` |
| 小程序 | 同生产 | 需在微信后台配置该域名 |

本地 H5 开发（`5174`）直连生产 API，生产环境 CORS 需包含 `http://localhost:5174` 与 `http://127.0.0.1:5174`。

---

## 封装

`src/api/request.ts`：

- 前缀：`API_BASE_URL + path`
- 响应：校验 `{ code, message, data }`
- 请求头：`Authorization: Bearer`（除登录外）、`X-Client-Type`
- `40101`：清 token 并跳转登录

`src/api/auth.ts`：登录 `/api/admin/auth/login`、当前用户 `/api/admin/auth/me`

---

## 接口清单

| 方法 | 路径 | 认证 | 用途 |
|------|------|------|------|
| POST | `/api/admin/auth/login` | 否 | 登录 |
| GET | `/api/admin/auth/me` | 是 | 当前用户 |
| GET | `/api/public/kb` | 是 | 知识库列表 |
| POST | `/api/public/chat` | 是 | 非流式问答 |
| GET | `/api/public/chat/sessions/{id}/messages` | 是 | 会话历史 |

---

## AI Key 说明

登录后问答使用**当前登录用户**在管理后台「AI 配置」中保存的 Key（每人独立）。未配置 Key 的用户问答会提示先在系统设置中配置。

---

## 小程序 checklist

- [ ] 微信公众平台 request 合法域名：`https://un.easytransfer.top`
- [ ] `manifest.json` → `mp-weixin.appid`
- [ ] `npm run build:mp-weixin`
