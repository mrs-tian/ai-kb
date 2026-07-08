import math
import re
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.ai_providers import AiCredentials
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import create_embedding
from app.services.kb_service import get_kb_or_404


@dataclass
class RetrievedChunk:
    chunk: DocumentChunk
    document: Document
    score: float


def _tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[\u4e00-\u9fff]|\w+", text.lower())
    return {token for token in tokens if token}


def keyword_score(question: str, content: str) -> float:
    question_tokens = _tokenize(question)
    if not question_tokens:
        return 0.0
    content_tokens = _tokenize(content)
    overlap = len(question_tokens & content_tokens)
    bonus = sum(1 for token in question_tokens if token in content)
    return (overlap + bonus * 0.5) / len(question_tokens)


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    if len(vector_a) != len(vector_b) or not vector_a:
        return 0.0
    dot = sum(a * b for a, b in zip(vector_a, vector_b, strict=True))
    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def retrieve_chunks(
    db: Session,
    kb_id: int,
    question: str,
    *,
    credentials: AiCredentials | None = None,
) -> list[RetrievedChunk]:
    get_kb_or_404(db, kb_id)
    settings = get_settings()

    rows = db.execute(
        select(DocumentChunk, Document)
        .join(Document, Document.id == DocumentChunk.doc_id)
        .where(
            DocumentChunk.kb_id == kb_id,
            Document.status == "ready",
        )
    ).all()

    if not rows:
        return []

    query_embedding = create_embedding(question, credentials=credentials)
    scored: list[RetrievedChunk] = []

    for chunk, document in rows:
        if query_embedding and chunk.embedding:
            score = cosine_similarity(query_embedding, chunk.embedding)
        else:
            score = keyword_score(question, chunk.content)
        scored.append(RetrievedChunk(chunk=chunk, document=document, score=score))

    scored.sort(key=lambda item: item.score, reverse=True)
    return scored[: settings.rag_top_k]


def build_context(retrieved: list[RetrievedChunk]) -> str:
    settings = get_settings()
    parts: list[str] = []
    total_chars = 0

    for index, item in enumerate(retrieved, start=1):
        snippet = item.chunk.content.strip()
        if not snippet:
            continue
        block = f"[{index}] 来源：{item.document.filename}\n{snippet}"
        if total_chars + len(block) > settings.rag_max_context_chars:
            remaining = settings.rag_max_context_chars - total_chars
            if remaining <= 0:
                break
            block = block[:remaining]
        parts.append(block)
        total_chars += len(block)
        if total_chars >= settings.rag_max_context_chars:
            break

    return "\n\n".join(parts)


def build_references(retrieved: list[RetrievedChunk]) -> list[dict]:
    references: list[dict] = []
    for item in retrieved:
        snippet = item.chunk.content.strip()
        if len(snippet) > 120:
            snippet = snippet[:120] + "..."
        references.append(
            {
                "doc_id": item.document.id,
                "doc_name": item.document.filename,
                "chunk_id": item.chunk.id,
                "snippet": snippet,
                "score": round(item.score, 2),
            }
        )
    return references
