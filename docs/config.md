# 智问 AI 知识库 — 项目配置

> 工作根目录：`D:\ai-kb-demo`  
> 真实 Key、密码写入各子项目 `.env`，勿提交 Git。

---

## 仓库结构

```text
ai-kb-demo/
├── docs/           # 项目级文档（本文件、执行计划）
├── backend/        # Python FastAPI 后端 → 见 backend/README.md
├── admin-web/      # Vue3 管理后台 → 见 admin-web/README.md
└── uni-app/        # C 端 H5 / 小程序 → 见 uni-app/README.md
```

---

## 环境地址


| 环境    | API                               | 管理后台                              | uni-app H5                          |
| ----- | --------------------------------- | --------------------------------- | ----------------------------------- |
| local | `http://127.0.0.1:8000`           | `http://localhost:5173`           | `http://127.0.0.1:5174`（开发，可直连生产 API） |
| prod  | `https://un.easytransfer.top/api` | `https://un.easytransfer.top`     | `https://www.easytransfer.top`      |


---

## 服务器（生产参考）


| 项    | 配置                              |
| ---- | ------------------------------- |
| 规格   | 2核4G 轻量服务器                      |
| 系统   | CentOS 7（实际运行环境）                |
| 反向代理 | Nginx                           |
| 进程管理 | systemd（`ai-kb-api.service`）    |
| 数据库  | SQLite（文件库，已随部署初始化并填充 Demo 数据） |


---

### 连接信息

| 项 | 值 |
|----|-----|
| 服务器 IP | `59.110.10.135` |
| SSH 用户 | `root` |
| SSH 端口 | **22**（8777 非 SSH，网站也不用 8777） |
| 域名 | https://un.easytransfer.top/（管理后台 + API） |
| H5 域名 | https://www.easytransfer.top/（uni-app C 端） |
| SSH 免密 | 本机 `~/.ssh/id_ed25519.pub` 已写入 `authorized_keys` |

### 生产服务器目录（代码 & 数据）

| 用途 | 服务器路径 |
|------|-----------|
| **项目根目录** | `/srv/ai-kb-demo/` |
| **后端代码** | `/srv/ai-kb-demo/backend/app/` |
| **后端虚拟环境** | `/srv/ai-kb-demo/backend/.venv/` |
| **后端环境变量** | `/srv/ai-kb-demo/backend/.env` |
| **数据库文件（SQLite）** | `/srv/ai-kb-demo/backend/data/app.db` |
| **上传文件目录** | `/srv/ai-kb-demo/backend/uploads/` |
| **管理后台静态页（Nginx root）** | `/srv/ai-kb-demo/www/` |
| **uni-app H5 静态页（Nginx root）** | `/srv/ai-kb-demo/h5/` |
| **Alembic 迁移脚本** | `/srv/ai-kb-demo/backend/alembic/` |
| **部署配置（Nginx/systemd）** | `/srv/ai-kb-demo/deploy/` |
| **Nginx 管理端站点** | `/etc/nginx/conf.d/ai-kb-demo.conf` |
| **Nginx H5 站点** | `/etc/nginx/conf.d/ai-kb-www.conf` |
| **systemd 服务单元** | `/etc/systemd/system/ai-kb-api.service` |
| **SSL 证书（管理端）** | `/etc/letsencrypt/live/un.easytransfer.top/` |
| **SSL 证书（H5）** | `/etc/letsencrypt/live/www.easytransfer.top/` |
| **后端监听（仅本机）** | `127.0.0.1:8001` |

> **H5 部署说明：** 本地 `npm run build:h5` 产物在 `uni-app/dist/build/h5/`，上传至服务器 `/srv/ai-kb-demo/h5/`。`www.easytransfer.top` 的 `/api/` 反代到 `127.0.0.1:8001`，与 `un.easytransfer.top` 共用同一后端与 SQLite 库。

> **数据库说明：** 生产环境使用 SQLite 单文件库，部署时执行 `alembic upgrade head` 建表，并通过 `scripts/seed_demo_data.py` 填充 Demo 数据。数据库与代码在同一台服务器，**不是**独立 MySQL 实例。若后续要切 MySQL，只需改 `.env` 中 `DATABASE_URL` 并重新迁移。

### 与其它项目隔离

| 域名 | 后端端口 | 目录 | 服务名 |
|------|---------|------|--------|
| `un.easytransfer.top` | 8001 | `/srv/ai-kb-demo/`（`www/` 管理端） | `ai-kb-api` |
| `www.easytransfer.top` | 8001（反代） | `/srv/ai-kb-demo/h5/`（uni-app H5） | `ai-kb-api` |
| `admin.easytransfer.top` | 8000 | `/srv/xt18/` | `xt18-api` |
| `ui.easytransfer.top` | 7001 | `/srv/stc-ui/` | `stc-ui-backend` |


---

## 数据库

```env
# 开发（本地）
DATABASE_URL=sqlite:///./data/app.db
# 文件：backend/data/app.db

# 生产（当前）
DATABASE_URL=sqlite:///./data/app.db
# 文件：/srv/ai-kb-demo/backend/data/app.db

# 可选：独立 MySQL
# DATABASE_URL=mysql+pymysql://user:pass@127.0.0.1:3306/ai_kb_demo?charset=utf8mb4
```

迁移：`alembic upgrade head`  
Demo 数据：`python scripts/seed_demo_data.py`（生产部署时已执行）

---



## OSS

```env
STORAGE_TYPE=local          # local | oss
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE_MB=20

OSS_ACCESS_KEY_ID=
OSS_ACCESS_KEY_SECRET=
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET=ai-kb-demo
OSS_PREFIX=documents/
```

开发用本地 `backend/uploads/`；生产可切 OSS。

---



## AI 模型（用户自行配置）

DeepSeek / 千问 API Key **不再写入** `.env`，由每位登录用户在管理端「AI 配置」页填写，服务端加密存储，保存后脱敏显示（中间星号）。

RAG 参数仍在 `.env`：

```env
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
RAG_TOP_K=5
RAG_MAX_CONTEXT_CHARS=4000
```

---



## 认证与安全

```env
JWT_SECRET=change-me-in-production
JWT_EXPIRE_MINUTES=1440
ADMIN_USERNAME=admin
ADMIN_PASSWORD=demo123456
PUBLIC_RATE_LIMIT=30
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

---



## 本地 Python 环境（Windows）

> 本机通过 **uv** 管理 Python 版本与虚拟环境；系统 PATH 里的 `python` 可能是旧版，**不要直接用于本项目**。



### 环境说明


| 项       | 说明                                                                   |
| ------- | -------------------------------------------------------------------- |
| 项目要求    | Python **3.11+**                                                     |
| 版本管理    | [uv](https://docs.astral.sh/uv/)（`C:\Users\admin\.local\bin\uv.exe`） |
| 系统默认    | `C:\python\python.exe` → Python 3.6.8，**不可用**                        |
| 已安装（uv） | 3.11.15、3.12.13（推荐用 **3.11**）                                        |
| 虚拟环境    | 各子项目独立 `.venv`，不提交 Git                                               |




### 查看 / 切换 Python 版本

```powershell
uv python list                 # 列出本机可用版本
uv python pin 3.11             # 可选：在当前目录固定 3.11（生成 .python-version）
uv venv --python 3.11          # 用指定版本创建 .venv
uv venv --python 3.12          # 或切换到 3.12
```

也可直接使用 uv 安装的 shim（已在 PATH 时）：

```powershell
python3.11 --version
python3.12 --version
```



### 前端 Node（参考）

管理端使用 **nvm**（`D:\nvm\nvm`）切换 Node 版本，与 Python 环境独立。

---



## 启动命令

**后端（推荐：uv + .venv）**

```powershell
cd D:\ai-kb-demo\backend
uv venv --python 3.11
.\.venv\Scripts\activate
uv pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> 若已存在 `.venv` 且版本正确，只需 `activate` 后执行 `uv pip install` / `uvicorn` 即可。  
> 更换 Python 版本时：删除 `.venv` 后重新 `uv venv --python 3.11`。

**后端（备选：已有 Python 3.11+ 在 PATH）**

```powershell
cd D:\ai-kb-demo\backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**管理后台**

```bash
cd D:\ai-kb-demo\admin-web
npm install && npm run dev
```

**uni-app（C 端 H5 / 小程序）**

```bash
cd D:\ai-kb-demo\uni-app
npm install
npm run dev:h5          # http://127.0.0.1:5174
npm run build:h5        # 产物 → uni-app/dist/build/h5/
npm run dev:mp-weixin   # 微信开发者工具打开 dist/dev/mp-weixin
```

> 生产 H5 访问 `https://www.easytransfer.top`，API 同域 `/api`（见 `uni-app/.env.production`）。  
> 知识库功能需登录后台账号；问答使用**当前登录用户**自配的 AI Key。

---



## 上线指令（摘要）

```powershell
# 本地一键部署（Windows）
powershell -ExecutionPolicy Bypass -File deploy/deploy.ps1
```

```bash
# 服务器上手动更新（已上传代码后）
SEED_DEMO=0 bash /srv/ai-kb-demo/deploy/setup_server.sh

# 仅更新 H5 静态页（本地 build 后）
# scp -r uni-app/dist/build/h5/* root@59.110.10.135:/srv/ai-kb-demo/h5/

# 健康检查
curl https://un.easytransfer.top/health
curl -I https://www.easytransfer.top/
systemctl status ai-kb-api
```

**隔离说明：** 管理端 Nginx 为 `un.easytransfer.top`，H5 为 `www.easytransfer.top`，后端均反代 **8001**；不修改 `admin.easytransfer.top`（xt18 / 8000）、`ui.easytransfer.top`（stc-ui / 7001）等既有配置。

---



## 小程序（后续）

- 个人主体 + ICP 备案 + 体验版扫码  
- H5 已部署：`https://www.easytransfer.top/`  
- 执行顺序见 [execution-plan.md](./execution-plan.md)

---



## 相关文档


| 文档                                       | 说明        |
| ---------------------------------------- | --------- |
| [execution-plan.md](./execution-plan.md) | 开发阶段与验收顺序 |


---



## 定稿检查

- [ ] 域名已确定
- [ ] 各用户已在「AI 配置」填写 DeepSeek 或千问 API Key
- [ ] 生产 JWT_SECRET 已更换
- [ ] 默认管理员密码已修改