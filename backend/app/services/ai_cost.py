"""AI 费用估算（与 stats_service 口径一致）。"""

LLM_COST_PER_1K = 0.002
EMBED_COST_PER_1K = 0.0002


def estimate_tokens_from_chars(char_count: int) -> int:
    return max(0, char_count // 4)


def estimate_tokens_from_text(text: str) -> int:
    return estimate_tokens_from_chars(len(text))


def estimate_cost(llm_tokens: int, embedding_tokens: int) -> float:
    cost = (llm_tokens / 1000) * LLM_COST_PER_1K + (embedding_tokens / 1000) * EMBED_COST_PER_1K
    return round(cost, 4)
