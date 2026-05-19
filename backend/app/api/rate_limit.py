"""Simple in-memory rate limiter for FastAPI."""
import time
import asyncio
from collections import defaultdict
from typing import Callable

from fastapi import Request, HTTPException


class RateLimiter:
    def __init__(self, requests: int = 10, window: int = 60):
        self.requests = requests
        self.window = window
        self._store: dict[str, list[float]] = defaultdict(list)

    def _clean(self, key: str, now: float) -> None:
        cutoff = now - self.window
        self._store[key] = [t for t in self._store[key] if t > cutoff]

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        self._clean(key, now)
        if len(self._store[key]) >= self.requests:
            return False
        self._store[key].append(now)
        return True


_llm_limiter = RateLimiter(requests=5, window=60)
_ocr_limiter = RateLimiter(requests=3, window=60)
_general_limiter = RateLimiter(requests=30, window=60)


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def rate_limit_llm(request: Request):
    """Rate limit for expensive LLM endpoints (chat, suggestions, cover-letter, etc.)"""
    key = f"llm:{get_client_ip(request)}"
    if not _llm_limiter.is_allowed(key):
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后重试")


async def rate_limit_ocr(request: Request):
    """Stricter rate limit for OCR (most expensive)"""
    key = f"ocr:{get_client_ip(request)}"
    if not _ocr_limiter.is_allowed(key):
        raise HTTPException(status_code=429, detail="上传过于频繁，请稍后重试")


async def rate_limit_general(request: Request):
    """General rate limit for all endpoints"""
    key = f"gen:{get_client_ip(request)}"
    if not _general_limiter.is_allowed(key):
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后重试")
