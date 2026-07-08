from fastapi import APIRouter

from app.api.admin import auth, chats, documents, kb, logs, stats, users
from app.api.public import chat as public_chat
from app.api.public import kb as public_kb

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/admin/auth", tags=["admin-auth"])
api_router.include_router(kb.router, tags=["admin-kb"])
api_router.include_router(documents.router, tags=["admin-documents"])
api_router.include_router(chats.router, tags=["admin-chats"])
api_router.include_router(stats.router, tags=["admin-stats"])
api_router.include_router(users.router, tags=["admin-users"])
api_router.include_router(logs.router, tags=["admin-logs"])
api_router.include_router(public_kb.router)
api_router.include_router(public_chat.router)
