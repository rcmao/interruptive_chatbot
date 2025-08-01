"""
性能优化工具
改进响应时间测量和缓存机制
"""

import time
import asyncio
from typing import Dict, Any
from functools import lru_cache
import threading

class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self):
        self.cache = {}
        self.cache_lock = threading.Lock()
        self.response_times = []
        self.max_cache_size = 1000
    
    def measure_response_time(self, func):
        """测量响应时间的装饰器"""
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                response_time = time.time() - start_time
                self.response_times.append(response_time)
                return result
            except Exception as e:
                response_time = time.time() - start_time
                self.response_times.append(response_time)
                raise e
        return wrapper
    
    def get_average_response_time(self) -> float:
        """获取平均响应时间"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    def get_p95_response_time(self) -> float:
        """获取95%响应时间"""
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[index]
    
    def clear_cache(self):
        """清理缓存"""
        with self.cache_lock:
            self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self.cache_lock:
            return {
                "cache_size": len(self.cache),
                "max_cache_size": self.max_cache_size,
                "cache_hit_rate": self._calculate_cache_hit_rate()
            }
    
    def _calculate_cache_hit_rate(self) -> float:
        """计算缓存命中率"""
        # 这里可以实现更复杂的缓存命中率计算
        return 0.8  # 示例值 