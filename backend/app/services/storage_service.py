from pathlib import Path
from typing import Protocol
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import Settings, get_settings
from app.core.exceptions import AppException


class StorageBackend(Protocol):
    async def save(self, file: UploadFile, key: str) -> str: ...

    async def delete(self, key: str) -> None: ...

    def read_bytes(self, key: str) -> bytes: ...

    def absolute_path(self, key: str) -> Path: ...


class LocalStorageBackend:
    def __init__(self, upload_dir: str) -> None:
        self.root = Path(upload_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    async def save(self, file: UploadFile, key: str) -> str:
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        content = await file.read()
        path.write_bytes(content)
        return key

    async def delete(self, key: str) -> None:
        path = self.root / key
        if path.exists():
            path.unlink()

    def read_bytes(self, key: str) -> bytes:
        path = self.root / key
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {key}")
        return path.read_bytes()

    def absolute_path(self, key: str) -> Path:
        return self.root / key


def build_storage_key(kb_id: int, filename: str) -> str:
    safe_name = Path(filename).name
    return f"{kb_id}/{uuid4().hex}_{safe_name}"


def get_storage_backend(settings: Settings | None = None) -> StorageBackend:
    settings = settings or get_settings()
    if settings.storage_type == "local":
        return LocalStorageBackend(settings.upload_dir)
    raise AppException(50001, "OSS 存储尚未实现，请将 STORAGE_TYPE 设为 local", 501)
