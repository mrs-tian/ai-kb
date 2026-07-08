from dataclasses import dataclass

AI_PROVIDERS: dict[str, dict[str, str]] = {
    "deepseek": {
        "label": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "llm_model": "deepseek-chat",
        "embedding_model": "deepseek-embed",
    },
    "qwen": {
        "label": "通义千问",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "llm_model": "qwen-plus",
        "embedding_model": "text-embedding-v3",
    },
}


@dataclass
class AiCredentials:
    provider: str
    api_key: str
    base_url: str
    llm_model: str
    embedding_model: str


def get_provider_config(provider: str) -> dict[str, str]:
    if provider not in AI_PROVIDERS:
        raise ValueError(f"不支持的 AI 提供商: {provider}")
    return AI_PROVIDERS[provider]
