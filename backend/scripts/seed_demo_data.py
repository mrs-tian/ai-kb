"""填充 Demo 展示用 mock 数据。用法: uv run python scripts/seed_demo_data.py"""

from __future__ import annotations

import random
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete, select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.admin_user import AdminUser
from app.models.api_request_log import ApiRequestLog
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.knowledge_base import KnowledgeBase

random.seed(20260707)

KB_DATA = [
    ("产品使用手册", "面向终端用户的产品功能说明与常见问题", True),
    ("员工入职指南", "HR 入职流程、考勤制度与福利政策", True),
    ("API 接口文档", "内部 REST API 规范与鉴权说明", False),
    ("销售话术库", "销售团队客户沟通标准话术与案例", True),
    ("技术架构白皮书", "系统架构、部署方案与运维规范", False),
    ("客户服务 FAQ", "客服团队高频问题标准答复", True),
    ("财务报销制度", "差旅、采购、报销审批流程", False),
    ("安全合规手册", "数据安全、隐私合规与审计要求", True),
]

DOC_TEMPLATES = [
    ("快速入门.md", "md", 8200),
    ("功能详解.pdf", "pdf", 24500),
    ("常见问题.txt", "txt", 5600),
    ("更新日志.md", "md", 3200),
    ("操作视频脚本.txt", "txt", 4800),
    ("管理员指南.pdf", "pdf", 18600),
]

CHAT_QUESTIONS = [
    "如何重置密码？",
    "产品支持哪些文件格式上传？",
    "API 鉴权方式是什么？",
    "报销流程需要哪些材料？",
    "新员工入职第一天要做什么？",
    "如何导出对话记录？",
    "知识库文档大小限制是多少？",
    "DeepSeek 和千问有什么区别？",
    "接口限流策略是怎样的？",
    "如何设置知识库为公开？",
    "向量检索的原理是什么？",
    "文档解析失败怎么处理？",
    "支持私有化部署吗？",
    "客服 SLA 响应时间是多久？",
    "数据存储在哪里？",
]

CHAT_ANSWERS = [
    "根据知识库资料，您可以在「个人设置」页面点击「修改密码」完成重置，需验证原密码。",
    "当前支持 txt、md、pdf 三种格式，单文件最大 20MB，上传后系统会自动解析并分块入库。",
    "管理端 API 使用 JWT Bearer Token 鉴权，C 端公开接口采用 IP 限流，无需登录。",
    "报销需提交：发票原件、费用明细表、审批单，差旅额外附行程单，详见财务制度第三章。",
    "入职首日需完成：工位领取、账号开通、安全培训、签署劳动合同四件事项。",
    "管理员可在「对话记录」页面按会话查看完整问答，支持按知识库筛选。",
    "单文件上限 20MB，建议 PDF 控制在 10MB 以内以获得更好的解析速度。",
    "DeepSeek 性价比高，千问在中文场景表现稳定，两者均兼容 OpenAI 接口格式。",
    "C 端默认 30 次/分钟/IP，管理端无硬性限流，建议生产环境配置 Nginx 限速。",
    "编辑知识库时将「是否公开」设为是即可，公开后 C 端用户无需登录即可问答。",
]

API_PATHS = [
    ("/api/admin/auth/login", "POST"),
    ("/api/admin/auth/me", "GET"),
    ("/api/admin/kb", "GET"),
    ("/api/admin/kb", "POST"),
    ("/api/admin/stats/overview", "GET"),
    ("/api/admin/stats/chat-trend", "GET"),
    ("/api/admin/chats/ask", "POST"),
    ("/api/admin/chats/sessions", "GET"),
    ("/api/public/chat", "POST"),
    ("/api/admin/logs", "GET"),
    ("/api/admin/users", "GET"),
    ("/api/admin/auth/ai-config", "GET"),
]

USERS = [
    ("zhangsan", "张三", "user"),
    ("lisi", "李四", "user"),
    ("wangwu", "王五", "admin"),
]


def _rand_time(days_ago: int, hour_range: tuple[int, int] = (8, 22)) -> datetime:
    base = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(
        days=days_ago
    )
    hour = random.randint(*hour_range)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return base.replace(hour=hour, minute=minute, second=second)


def _chunk_content(topic: str, index: int) -> str:
    paragraphs = [
        f"【{topic}】第 {index + 1} 节：本章节介绍核心概念与操作流程。",
        "在实际使用中，建议先阅读快速入门文档，再按需查阅详细说明。",
        "如遇问题，可联系技术支持或在知识库中搜索相关关键词。",
        "系统支持全文检索与语义检索两种模式，语义检索基于向量相似度计算。",
    ]
    return "\n".join(random.sample(paragraphs, k=random.randint(2, 4)))


def seed_demo_data() -> None:
    db = SessionLocal()
    try:
        print("清理旧 mock 数据...")
        db.execute(delete(ApiRequestLog))
        db.execute(delete(ChatMessage))
        db.execute(delete(ChatSession))
        db.execute(delete(DocumentChunk))
        db.execute(delete(Document))
        db.execute(delete(KnowledgeBase))
        db.execute(
            delete(AdminUser).where(AdminUser.username.notin_(["admin"]))
        )
        db.commit()

        print("创建用户...")
        for username, nickname, role in USERS:
            db.add(
                AdminUser(
                    username=username,
                    password_hash=hash_password("demo123456"),
                    nickname=nickname,
                    role=role,
                    is_active=True,
                )
            )
        db.commit()
        users = list(db.scalars(select(AdminUser)).all())
        user_map = {u.username: u for u in users}

        print("创建知识库与文档...")
        kb_ids: list[int] = []
        total_docs = 0
        total_chunks = 0

        for name, desc, is_public in KB_DATA:
            kb = KnowledgeBase(
                name=name,
                description=desc,
                status="active",
                is_public=is_public,
                doc_count=0,
                chunk_count=0,
                created_at=_rand_time(random.randint(15, 45)),
            )
            db.add(kb)
            db.flush()
            kb_ids.append(kb.id)

            doc_count = random.randint(2, 4)
            kb_doc_count = 0
            kb_chunk_count = 0

            for i in range(doc_count):
                tpl = DOC_TEMPLATES[(total_docs + i) % len(DOC_TEMPLATES)]
                filename, ext, char_count = tpl
                doc = Document(
                    kb_id=kb.id,
                    filename=f"{name[:4]}_{filename}",
                    file_ext=ext,
                    file_size=char_count * 2,
                    storage_type="local",
                    storage_path=f"mock/{kb.id}/{filename}",
                    char_count=char_count,
                    status="ready",
                    created_at=_rand_time(random.randint(5, 30)),
                )
                db.add(doc)
                db.flush()
                kb_doc_count += 1
                total_docs += 1

                chunk_num = random.randint(4, 12)
                for ci in range(chunk_num):
                    content = _chunk_content(name, ci)
                    token_count = max(1, len(content) // 4)
                    chunk = DocumentChunk(
                        kb_id=kb.id,
                        doc_id=doc.id,
                        chunk_index=ci,
                        content=content,
                        token_count=token_count,
                        embedding=[random.uniform(-1, 1) for _ in range(8)],
                        created_at=doc.created_at + timedelta(minutes=ci),
                    )
                    db.add(chunk)
                    kb_chunk_count += 1
                    total_chunks += 1

            kb.doc_count = kb_doc_count
            kb.chunk_count = kb_chunk_count

        db.commit()
        print(f"  知识库 {len(kb_ids)} 个，文档 {total_docs} 个，分块 {total_chunks} 个")

        print("创建对话记录...")
        session_count = 0
        message_pairs = 0
        for day in range(7):
            daily_sessions = random.randint(4, 12)
            for _ in range(daily_sessions):
                kb_id = random.choice(kb_ids)
                q_idx = random.randint(0, len(CHAT_QUESTIONS) - 1)
                question = CHAT_QUESTIONS[q_idx]
                answer = CHAT_ANSWERS[q_idx % len(CHAT_ANSWERS)]
                session_time = _rand_time(day)

                session = ChatSession(
                    id=str(uuid.uuid4()),
                    kb_id=kb_id,
                    title=question[:64],
                    client_type=random.choice(["admin", "h5", "web", None]),
                    client_ip=f"192.168.1.{random.randint(10, 200)}",
                    created_at=session_time,
                )
                db.add(session)
                db.flush()
                session_count += 1

                latency = random.randint(800, 4500)
                user_msg = ChatMessage(
                    session_id=session.id,
                    role="user",
                    content=question,
                    created_at=session_time,
                )
                assistant_msg = ChatMessage(
                    session_id=session.id,
                    role="assistant",
                    content=answer
                    + f"\n\n（引用自知识库 #{kb_id}，相关度 {random.uniform(0.75, 0.98):.2f}）",
                    references_json=[
                        {
                            "doc_id": random.randint(1, total_docs),
                            "doc_name": "参考文档.pdf",
                            "chunk_id": random.randint(1, total_chunks),
                            "snippet": answer[:80],
                            "score": round(random.uniform(0.7, 0.95), 2),
                        }
                    ],
                    model=random.choice(["deepseek-chat", "qwen-plus"]),
                    latency_ms=latency,
                    created_at=session_time + timedelta(seconds=random.randint(2, 8)),
                )
                db.add(user_msg)
                db.add(assistant_msg)
                message_pairs += 1

        db.commit()
        print(f"  会话 {session_count} 个，问答 {message_pairs} 对")

        print("创建接口日志...")
        log_count = 0
        usernames = [None, "admin", "zhangsan", "lisi", None, "admin", None]
        for day in range(7):
            daily_logs = random.randint(60, 120)
            for _ in range(daily_logs):
                path, method = random.choice(API_PATHS)
                is_auth = random.random() > 0.25
                username = random.choice(usernames) if is_auth else None
                fail = random.random() < 0.045
                status = random.choice([401, 403, 422, 500]) if fail else random.choice(
                    [200, 200, 200, 201]
                )
                duration = random.randint(12, 2800)
                created = _rand_time(day)

                response = (
                    '{"code":40101,"message":"未登录或 token 无效","data":null}'
                    if status == 401
                    else '{"code":0,"message":"ok","data":{}}'
                )

                db.add(
                    ApiRequestLog(
                        method=method,
                        path=path,
                        query_string="page=1&page_size=20" if "?" not in path else None,
                        status_code=status,
                        response_body=response,
                        user_id=user_map[username].id if username and username in user_map else None,
                        username=username,
                        client_ip=f"10.0.{random.randint(0, 5)}.{random.randint(1, 254)}",
                        duration_ms=duration,
                        is_authenticated=is_auth and status != 401,
                        created_at=created,
                    )
                )
                log_count += 1

        db.commit()
        print(f"  接口日志 {log_count} 条")
        print("Mock 数据填充完成！")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
