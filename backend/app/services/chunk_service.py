def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    normalized = text.strip()
    if not normalized:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size 必须大于 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap 无效")

    chunks: list[str] = []
    start = 0
    text_len = len(normalized)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= text_len:
            break
        start = end - overlap

    return chunks


def estimate_token_count(text: str) -> int:
    return max(1, len(text) // 4) if text else 0
