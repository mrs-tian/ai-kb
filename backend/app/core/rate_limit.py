import logging
import math
import re
import time
from collections import defaultdict

from app.core.config import get_settings
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)

_buckets: dict[str, list[float]] = defaultdict(list)


def check_public_rate_limit(client_ip: str) -> None:
    settings = get_settings()
    window_seconds = 60
    now = time.time()
    bucket = _buckets[client_ip]
    bucket[:] = [timestamp for timestamp in bucket if now - timestamp < window_seconds]
    if len(bucket) >= settings.public_rate_limit:
        raise AppException(42901, "请求过于频繁，请稍后再试", 429)
    bucket.append(now)
