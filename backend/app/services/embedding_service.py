import logging

import httpx

from app.core.ai_providers import AiCredentials

logger = logging.getLogger(__name__)


def create_embeddings(
    texts: list[str],
    *,
    credentials: AiCredentials | None,
) -> list[list[float]] | None:
    if not texts:
        return []
    if not credentials or not credentials.api_key.strip():
        return None

    url = f"{credentials.base_url.rstrip('/')}/v1/embeddings"
    payload = {
        "model": credentials.embedding_model,
        "input": texts,
    }
    headers = {
        "Authorization": f"Bearer {credentials.api_key}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, json=payload, headers=headers)
            if response.status_code >= 400:
                logger.warning(
                    "Embedding API failed: status=%s body=%s",
                    response.status_code,
                    response.text[:300],
                )
                return None
            data = response.json()
            items = data.get("data", [])
            if len(items) != len(texts):
                return None
            items.sort(key=lambda item: item.get("index", 0))
            return [item["embedding"] for item in items]
    except Exception as exc:
        logger.warning("Embedding API error: %s", exc)
        return None


def create_embedding(
    text: str,
    *,
    credentials: AiCredentials | None,
) -> list[float] | None:
    embeddings = create_embeddings([text], credentials=credentials)
    if embeddings is None:
        return None
    return embeddings[0]
