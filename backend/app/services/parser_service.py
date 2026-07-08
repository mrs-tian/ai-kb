from pathlib import Path

from pypdf import PdfReader

ALLOWED_EXTENSIONS = {"txt", "md", "pdf"}


def parse_file_content(path: Path, file_ext: str) -> tuple[str, int]:
    ext = file_ext.lower().lstrip(".")
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件格式: {ext}")

    if ext == "pdf":
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages).strip()
    else:
        raw = path.read_bytes()
        text = _decode_text(raw)

    return text, len(text)


def parse_bytes_content(content: bytes, file_ext: str) -> tuple[str, int]:
    ext = file_ext.lower().lstrip(".")
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件格式: {ext}")

    if ext == "pdf":
        from io import BytesIO

        reader = PdfReader(BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages).strip()
    else:
        text = _decode_text(content)

    return text, len(text)


def _decode_text(raw: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gbk"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")
