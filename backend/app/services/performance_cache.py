import hashlib
import time
from typing import Any, Dict, Optional
from functools import lru_cache
import json


class PerformanceMonitor:
    def __init__(self):
        self.metrics: Dict[str, list] = {}
    
    def record(self, operation: str, duration: float):
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(duration)
        if len(self.metrics[operation]) > 100:
            self.metrics[operation] = self.metrics[operation][-100:]
    
    def get_stats(self, operation: str) -> Dict[str, float]:
        if operation not in self.metrics or not self.metrics[operation]:
            return {"avg": 0, "min": 0, "max": 0, "count": 0}
        
        values = self.metrics[operation]
        return {
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "count": len(values),
        }


class ResultCache:
    def __init__(self, max_size: int = 100):
        self.cache: Dict[str, Any] = {}
        self.max_size = max_size
        self.access_times: Dict[str, float] = {}
    
    def _hash_content(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()
    
    def _hash_text(self, text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def get_ocr_result(self, pdf_bytes: bytes) -> Optional[Dict[str, Any]]:
        key = f"ocr_{self._hash_content(pdf_bytes)}"
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
    
    def set_ocr_result(self, pdf_bytes: bytes, result: Dict[str, Any]):
        key = f"ocr_{self._hash_content(pdf_bytes)}"
        self._evict_if_needed()
        self.cache[key] = result
        self.access_times[key] = time.time()
    
    def get_sections_result(self, text: str) -> Optional[Any]:
        key = f"sections_{self._hash_text(text)}"
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
    
    def set_sections_result(self, text: str, result: Any):
        key = f"sections_{self._hash_text(text)}"
        self._evict_if_needed()
        self.cache[key] = result
        self.access_times[key] = time.time()
    
    def get_suggestions_result(self, text: str, style_type: str, target_job: str) -> Optional[Any]:
        key = f"suggestions_{self._hash_text(text + style_type + target_job)}"
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
    
    def set_suggestions_result(self, text: str, style_type: str, target_job: str, result: Any):
        key = f"suggestions_{self._hash_text(text + style_type + target_job)}"
        self._evict_if_needed()
        self.cache[key] = result
        self.access_times[key] = time.time()
    
    def _evict_if_needed(self):
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times, key=self.access_times.get)
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
    
    def clear(self):
        self.cache.clear()
        self.access_times.clear()


performance_monitor = PerformanceMonitor()
result_cache = ResultCache(max_size=200)


def timed_operation(operation_name: str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                performance_monitor.record(operation_name, duration)
        return wrapper
    return decorator
