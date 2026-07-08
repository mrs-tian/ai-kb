import json
import logging
from collections.abc import Iterator
from typing import Any

import httpx

from app.core.ai_providers import AiCredentials
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """你是企业知识库助手。仅根据【参考资料】回答，资料不足请明确说明「知识库中未找到相关信息」，不要编造。

【参考资料】
{context}

【用户问题】
{question}"""


def build_messages(question: str, context: str) -> list[dict[str, str]]:
    return [
        {
            "role": "user",
            "content": PROMPT_TEMPLATE.format(
                context=context or "（无相关资料）",
                question=question,
            ),
        }
    ]


def _chat_url(credentials: AiCredentials) -> str:
    return f"{credentials.base_url.rstrip('/')}/v1/chat/completions"


def _headers(credentials: AiCredentials) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {credentials.api_key}",
        "Content-Type": "application/json",
    }


def _require_credentials(credentials: AiCredentials | None) -> AiCredentials:
    if not credentials or not credentials.api_key.strip():
        raise AppException(50002, "请先在系统设置中配置 AI 模型 API Key", 503)
    return credentials


def chat_completion(
    question: str,
    context: str,
    *,
    credentials: AiCredentials | None,
) -> tuple[str, str]:
    creds = _require_credentials(credentials)
    payload = {
        "model": creds.llm_model,
        "messages": build_messages(question, context),
        "stream": False,
    }

    last_error: Exception | None = None
    for _ in range(3):
        try:
            with httpx.Client(timeout=90.0) as client:
                response = client.post(
                    _chat_url(creds), json=payload, headers=_headers(creds)
                )
                if response.status_code >= 400:
                    raise AppException(50002, "AI 服务暂时不可用，请稍后重试", 503)
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                model = data.get("model", creds.llm_model)
                return content.strip(), model
        except AppException:
            raise
        except Exception as exc:
            last_error = exc
            logger.warning("LLM request failed: %s", exc)

    raise AppException(50002, "AI 服务暂时不可用，请稍后重试", 503) from last_error


def stream_chat_completion(
    question: str,
    context: str,
    *,
    credentials: AiCredentials | None,
) -> Iterator[str]:
    creds = _require_credentials(credentials)
    payload = {
        "model": creds.llm_model,
        "messages": build_messages(question, context),
        "stream": True,
    }

    try:
        with httpx.Client(timeout=90.0) as client:
            with client.stream(
                "POST",
                _chat_url(creds),
                json=payload,
                headers=_headers(creds),
            ) as response:
                if response.status_code >= 400:
                    raise AppException(50002, "AI 服务暂时不可用，请稍后重试", 503)
                for line in response.iter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    chunk = _parse_stream_chunk(data_str)
                    if chunk:
                        yield chunk
    except AppException:
        raise
    except Exception as exc:
        logger.warning("LLM stream failed: %s", exc)
        raise AppException(50002, "AI 服务暂时不可用，请稍后重试", 503) from exc


def _parse_stream_chunk(data_str: str) -> str | None:
    try:
        payload: dict[str, Any] = json.loads(data_str)
        delta = payload["choices"][0].get("delta", {})
        content = delta.get("content")
        return content if content else None
    except (json.JSONDecodeError, KeyError, IndexError):
        return None
