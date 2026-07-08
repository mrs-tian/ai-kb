# 数据表设计

> 数据库：SQLite（开发）/ MySQL（生产）  
> ORM：SQLAlchemy 2.x  
> 迁移：Alembic  
> 字符集（MySQL）：utf8mb4

---

## ER 关系概览

```
admin_user (1) ── manages ──> knowledge_base (1) ──< (N) document (1) ──< (N) document_chunk
                                    │
                                    └──< (N) chat_session (1) ──< (N) chat_message

system_config (KV 配置，可选)
```

---

## 1. admin_user — 管理员

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | 主键 |
| username | VARCHAR(64) | UNIQUE, NOT NULL | 登录名 |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt |
| nickname | VARCHAR(64) | NULL | 显示名 |
| is_active | BOOLEAN | DEFAULT true | 是否启用 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

**索引：** `username` UNIQUE

**Seed：** 首次启动创建默认管理员（见 [`docs/config.md`](../docs/config.md)）

---

## 2. knowledge_base — 知识库

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK | 主键 |
| name | VARCHAR(128) | NOT NULL | 名称 |
| description | TEXT | NULL | 描述 |
| status | VARCHAR(16) | NOT NULL | `active` / `disabled` |
| is_public | BOOLEAN | DEFAULT true | 是否对 C 端可见 |
| doc_count | INTEGER | DEFAULT 0 | 文档数（冗余统计） |
| chunk_count | INTEGER | DEFAULT 0 | 分块数（冗余） |
| created_at | DATETIME | NOT NULL | |
| updated_at | DATETIME | NOT NULL | |

**索引：**

- `idx_kb_status` (status)
- `idx_kb_public` (is_public, status)

---

## 3. document — 文档

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK | |
| kb_id | INTEGER | FK → knowledge_base.id | 所属知识库 |
| filename | VARCHAR(255) | NOT NULL | 原始文件名 |
| file_ext | VARCHAR(16) | NOT NULL | txt/md/pdf |
| file_size | INTEGER | NOT NULL | 字节 |
| storage_type | VARCHAR(16) | NOT NULL | `local` / `oss` |
| storage_path | VARCHAR(512) | NOT NULL | 相对路径或 OSS key |
| char_count | INTEGER | DEFAULT 0 | 解析后字符数 |
| status | VARCHAR(16) | NOT NULL | 见下表 |
| error_message | TEXT | NULL | 失败原因 |
| created_at | DATETIME | NOT NULL | |
| updated_at | DATETIME | NOT NULL | |

**status 枚举：**

| 值 | 说明 |
|----|------|
| pending | 已上传，待解析 |
| parsing | 解析中 |
| embedding | 向量化中 |
| ready | 可用 |
| failed | 失败 |

**索引：**

- `idx_doc_kb_id` (kb_id)
- `idx_doc_status` (status)

---

## 4. document_chunk — 文档分块（RAG）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK | |
| kb_id | INTEGER | FK | 冗余，便于检索 |
| doc_id | INTEGER | FK → document.id | |
| chunk_index | INTEGER | NOT NULL | 块序号，从 0 起 |
| content | TEXT | NOT NULL | 块文本 |
| token_count | INTEGER | DEFAULT 0 | 估算 token |
| embedding | JSON / TEXT | NULL | 向量数组 JSON；MySQL 可用 JSON |
| created_at | DATETIME | NOT NULL | |

**索引：**

- `idx_chunk_kb_id` (kb_id)
- `idx_chunk_doc_id` (doc_id)

**说明：** Demo 阶段向量检索可在应用层计算余弦相似度；数据量增大后可换 pgvector / Milvus（不在 MVP）。

---

## 5. chat_session — 对话会话

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | VARCHAR(36) | PK | UUID |
| kb_id | INTEGER | FK | 知识库 |
| title | VARCHAR(128) | NULL | 首问摘要 |
| client_type | VARCHAR(16) | NULL | `admin` / `h5` / `mp` |
| client_ip | VARCHAR(64) | NULL | C 端 IP |
| created_at | DATETIME | NOT NULL | |
| updated_at | DATETIME | NOT NULL | |

**索引：** `idx_session_kb_id` (kb_id), `idx_session_created` (created_at DESC)

---

## 6. chat_message — 对话消息

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK | |
| session_id | VARCHAR(36) | FK → chat_session.id | |
| role | VARCHAR(16) | NOT NULL | `user` / `assistant` |
| content | TEXT | NOT NULL | 消息正文 |
| references_json | JSON | NULL | 引用来源，见下方结构 |
| model | VARCHAR(64) | NULL | 使用的 LLM 模型 |
| latency_ms | INTEGER | NULL | 响应耗时 |
| created_at | DATETIME | NOT NULL | |

**references_json 结构：**

```json
[
  {
    "doc_id": 1,
    "doc_name": "产品手册.md",
    "chunk_id": 12,
    "snippet": "重置密码需进入设置页...",
    "score": 0.87
  }
]
```

**索引：** `idx_msg_session_id` (session_id)

---

## 7. system_config — 系统配置（可选）

| 字段 | 类型 | 说明 |
|------|------|------|
| key | VARCHAR(64) | PK |
| value | TEXT | JSON 或字符串 |
| updated_at | DATETIME | |

**用途：** 运行时覆盖部分配置（Demo 可仅用 `.env`，此表 Phase 4 设置页只读展示）

---

## 8. 统计字段维护

| 事件 | 更新 |
|------|------|
| 文档上传成功 | `knowledge_base.doc_count += 1` |
| 文档删除 | 递减；删除关联 chunk |
| 分块完成 | 更新 `chunk_count` |

---

## 9. 级联删除规则

| 操作 | 行为 |
|------|------|
| 删除 knowledge_base | 级联删除 document、document_chunk、chat_session、chat_message |
| 删除 document | 级联删除 document_chunk |

---

## 10. Demo 预置数据

**知识库：** `产品使用手册`

**样例文档（`backend/seed/`）：**

1. `01-功能介绍.md`
2. `02-常见问题.md`
3. `03-计费说明.md`

**建议首问测试：**

- 「如何重置密码？」
- 「支持上传哪些文件格式？」

---

## 11. 待定项（定稿确认）

| 项 | 建议 | 确认 |
|----|------|------|
| embedding 存储 | JSON 数组存 SQLite | ☐ |
| chat_session.id | UUID 字符串 | ☐ |
| 是否需 user 表（C 端用户） | Demo 不需要 | ☐ |
