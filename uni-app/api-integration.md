# uni-app API 对接说明

## 基址配置

| 环境 | 文件 | `VITE_API_BASE_URL` |
|------|------|---------------------|
| 开发 H5 | `.env.development` | 空（走 Vite 代理 `/api`） |
| 生产 H5 | `.env.production` | `https://un.easytransfer.top` |
| 小程序 | 同生产 | 需在微信后台配置该域名 |

开发代理见 `vite.config.ts`：`5174` → `8000`。

---

## 封装

`src/api/request.ts` 统一：

- 前缀：`API_BASE_URL + path`
- 响应：校验 `{ code, message, data }`，`code !== 0` 时 toast 报错
- 请求头：`X-Client-Type`（h5 / mp-weixin）

---

## 接口清单

| 方法 | 路径 | 用途 |
|------|------|------|
| GET | `/api/public/kb` | 首页知识库列表 |
| GET | `/api/public/kb/{id}` | 知识库详情（可选） |
| POST | `/api/public/chat` | 非流式问答 |
| GET | `/api/public/chat/sessions/{id}/messages` | 恢复会话历史 |

### 问答请求体

```json
{
  "kb_id": 1,
  "question": "如何重置密码？",
  "session_id": "可选，续聊"
}
```

### 问答响应

```json
{
  "session_id": "...",
  "answer": "...",
  "references": [{ "doc_name": "...", "snippet": "...", "score": 0.89 }],
  "latency_ms": 1200
}
```

---

## C 端 AI Key 说明

C 端用户不登录，后端使用环境变量 `PUBLIC_AI_USERNAME`（默认 `admin`）对应管理员账号在「AI 配置」中填写的 API Key。

**上线前请确保 admin 已配置 DeepSeek / 千问 Key。**

---

## 小程序上线 checklist

- [ ] 微信公众平台配置 request 合法域名：`https://un.easytransfer.top`
- [ ] `manifest.json` → `mp-weixin.appid` 填入小程序 AppID
- [ ] `npm run build:mp-weixin` 后用微信开发者工具上传
