#!/usr/bin/env python3
"""
Performance Optimization Module for Claude Code

Features:
- Advanced caching with TTL and LRU eviction
- Connection pooling for MCP servers
- Async batch processing
- Memory-efficient data structures
- Lazy loading and streaming
- Result memoization
"""

import asyncio
import functools
import hashlib
import json
import time
from collections import OrderedDict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from pathlib import Path
import aiofiles
import aiohttp
from loguru import logger

T = TypeVar('T')


class LRUCache:
    """Thread-safe LRU cache with TTL support"""
    
    def __init__(self, max_size: int = 128, ttl: timedelta = timedelta(hours=1)):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[str, datetime] = {}
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self._lock:
            if key not in self.cache:
                return None
            
            # Check TTL
            if datetime.now() - self.timestamps[key] > self.ttl:
                del self.cache[key]
                del self.timestamps[key]
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
    
    async def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        async with self._lock:
            # Remove oldest if at capacity
            if len(self.cache) >= self.max_size and key not in self.cache:
                oldest = next(iter(self.cache))
                del self.cache[oldest]
                del self.timestamps[oldest]
            
            self.cache[key] = value
            self.timestamps[key] = datetime.now()
            self.cache.move_to_end(key)
    
    async def clear(self) -> None:
        """Clear all cache entries"""
        async with self._lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl": str(self.ttl),
            "oldest": min(self.timestamps.values()) if self.timestamps else None,
            "newest": max(self.timestamps.values()) if self.timestamps else None
        }


class PersistentCache:
    """Disk-based persistent cache with async I/O"""
    
    def __init__(self, cache_dir: Path = Path(".claude_cache")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.cache_dir / "index.json"
        self.index: Dict[str, Dict] = {}
        self._lock = asyncio.Lock()
        asyncio.create_task(self._load_index())
    
    async def _load_index(self):
        """Load cache index from disk"""
        if self.index_file.exists():
            try:
                async with aiofiles.open(self.index_file, 'r') as f:
                    content = await f.read()
                    self.index = json.loads(content)
            except Exception as e:
                logger.warning(f"Failed to load cache index: {e}")
                self.index = {}
    
    async def _save_index(self):
        """Save cache index to disk"""
        try:
            async with aiofiles.open(self.index_file, 'w') as f:
                await f.write(json.dumps(self.index, indent=2))
        except Exception as e:
            logger.warning(f"Failed to save cache index: {e}")
    
    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for key"""
        hash_key = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.json"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from persistent cache"""
        async with self._lock:
            if key not in self.index:
                return None
            
            # Check expiry
            meta = self.index[key]
            if datetime.fromisoformat(meta['expires']) < datetime.now():
                await self.delete(key)
                return None
            
            cache_file = self._get_cache_file(key)
            if not cache_file.exists():
                return None
            
            try:
                async with aiofiles.open(cache_file, 'r') as f:
                    content = await f.read()
                    return json.loads(content)
            except Exception as e:
                logger.warning(f"Failed to load cache entry: {e}")
                return None
    
    async def set(self, key: str, value: Any, ttl: timedelta = timedelta(hours=24)) -> None:
        """Set value in persistent cache"""
        async with self._lock:
            cache_file = self._get_cache_file(key)
            
            try:
                # Write data (JSON)
                async with aiofiles.open(cache_file, 'w') as f:
                    await f.write(json.dumps(value))
                
                # Update index
                self.index[key] = {
                    "created": datetime.now().isoformat(),
                    "expires": (datetime.now() + ttl).isoformat(),
                    "size": cache_file.stat().st_size
                }
                await self._save_index()
                
            except Exception as e:
                logger.warning(f"Failed to save cache entry: {e}")
    
    async def delete(self, key: str) -> None:
        """Delete entry from cache"""
        if key in self.index:
            cache_file = self._get_cache_file(key)
            if cache_file.exists():
                cache_file.unlink()
            del self.index[key]
            await self._save_index()
    
    async def cleanup(self) -> int:
        """Remove expired entries"""
        expired = []
        now = datetime.now()
        
        for key, meta in self.index.items():
            if datetime.fromisoformat(meta['expires']) < now:
                expired.append(key)
        
        for key in expired:
            await self.delete(key)
        
        return len(expired)


class ConnectionPool:
    """Connection pool for MCP servers"""
    
    def __init__(self, max_connections: int = 10, timeout: int = 30):
        self.max_connections = max_connections
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.sessions: Dict[str, aiohttp.ClientSession] = {}
        self.connectors: Dict[str, aiohttp.TCPConnector] = {}
        self._lock = asyncio.Lock()
    
    async def get_session(self, server_id: str, base_url: str) -> aiohttp.ClientSession:
        """Get or create session for server"""
        async with self._lock:
            if server_id not in self.sessions:
                connector = aiohttp.TCPConnector(
                    limit=self.max_connections,
                    limit_per_host=self.max_connections,
                    ttl_dns_cache=300
                )
                self.connectors[server_id] = connector
                
                self.sessions[server_id] = aiohttp.ClientSession(
                    base_url=base_url,
                    connector=connector,
                    timeout=self.timeout,
                    headers={"User-Agent": "Claude-Code/2.0"}
                )
            
            return self.sessions[server_id]
    
    async def close_all(self):
        """Close all sessions"""
        for session in self.sessions.values():
            await session.close()
        self.sessions.clear()
        self.connectors.clear()


class AsyncBatchProcessor:
    """Process multiple items in parallel batches"""
    
    def __init__(self, batch_size: int = 10, max_workers: int = 5):
        self.batch_size = batch_size
        self.semaphore = asyncio.Semaphore(max_workers)
    
    async def process(self, 
                      items: List[T],
                      processor: Callable[[T], asyncio.Coroutine],
                      progress_callback: Optional[Callable[[int, int], None]] = None) -> List[Any]:
        """Process items in batches"""
        results = []
        total = len(items)
        
        for i in range(0, total, self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_results = await self._process_batch(batch, processor)
            results.extend(batch_results)
            
            if progress_callback:
                progress_callback(min(i + self.batch_size, total), total)
        
        return results
    
    async def _process_batch(self, batch: List[T], processor: Callable) -> List[Any]:
        """Process a single batch"""
        tasks = []
        for item in batch:
            task = self._process_with_semaphore(processor, item)
            tasks.append(task)
        
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_with_semaphore(self, processor: Callable, item: T) -> Any:
        """Process item with semaphore limit"""
        async with self.semaphore:
            try:
                return await processor(item)
            except Exception as e:
                logger.error(f"Batch processing error: {e}")
                return None


def async_memoize(ttl: timedelta = timedelta(minutes=5)):
    """Decorator for async function memoization"""
    cache = LRUCache(ttl=ttl)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{repr(args)}:{repr(kwargs)}"
            
            # Check cache
            result = await cache.get(key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            await cache.set(key, result)
            return result
        
        wrapper.cache = cache  # Expose cache for management
        return wrapper
    
    return decorator


class StreamProcessor:
    """Process large data streams efficiently"""
    
    def __init__(self, chunk_size: int = 1024):
        self.chunk_size = chunk_size
    
    async def process_file(self,
                          file_path: Path,
                          processor: Callable[[bytes], Any]) -> AsyncIterator[Any]:
        """Process file in chunks"""
        async with aiofiles.open(file_path, 'rb') as f:
            while True:
                chunk = await f.read(self.chunk_size)
                if not chunk:
                    break
                yield processor(chunk)
    
    async def process_stream(self,
                            stream: asyncio.StreamReader,
                            processor: Callable[[bytes], Any]) -> AsyncIterator[Any]:
        """Process stream in chunks"""
        while True:
            chunk = await stream.read(self.chunk_size)
            if not chunk:
                break
            yield processor(chunk)


class ResourceMonitor:
    """Monitor and optimize resource usage"""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics: Dict[str, List[float]] = {
            "memory": [],
            "cpu": [],
            "io": []
        }
    
    async def record_metric(self, metric_type: str, value: float):
        """Record a metric value"""
        if metric_type not in self.metrics:
            self.metrics[metric_type] = []
        self.metrics[metric_type].append(value)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get resource usage statistics"""
        import psutil
        
        process = psutil.Process()
        
        return {
            "uptime": time.time() - self.start_time,
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "cpu_percent": process.cpu_percent(),
            "num_threads": process.num_threads(),
            "open_files": len(process.open_files()),
            "connections": len(process.connections()),
            "metrics": {
                k: {
                    "count": len(v),
                    "avg": sum(v) / len(v) if v else 0,
                    "min": min(v) if v else 0,
                    "max": max(v) if v else 0
                }
                for k, v in self.metrics.items()
            }
        }


class LazyLoader:
    """Lazy loading for expensive resources"""
    
    def __init__(self, loader: Callable[[], Any]):
        self.loader = loader
        self._value = None
        self._loaded = False
        self._lock = asyncio.Lock()
    
    async def get(self) -> Any:
        """Get the lazily loaded value"""
        if not self._loaded:
            async with self._lock:
                if not self._loaded:
                    if asyncio.iscoroutinefunction(self.loader):
                        self._value = await self.loader()
                    else:
                        self._value = self.loader()
                    self._loaded = True
        return self._value
    
    def reset(self):
        """Reset the lazy loader"""
        self._loaded = False
        self._value = None


class OptimizedMCPClient:
    """Optimized MCP client with caching and pooling"""
    
    def __init__(self, server_config: Dict[str, Any]):
        self.config = server_config
        self.cache = LRUCache(max_size=256)
        self.pool = ConnectionPool()
        self.batch_processor = AsyncBatchProcessor()
        self.monitor = ResourceMonitor()
    
    @async_memoize(ttl=timedelta(minutes=10))
    async def list_tools(self) -> List[Dict]:
        """List available tools with caching"""
        session = await self.pool.get_session(
            self.config['name'],
            self.config['url']
        )
        
        async with session.post('/tools/list') as response:
            return await response.json()
    
    async def batch_execute(self, requests: List[Dict]) -> List[Any]:
        """Execute multiple requests in parallel"""
        async def execute_single(request):
            return await self.execute(request['method'], request.get('params'))
        
        return await self.batch_processor.process(requests, execute_single)
    
    async def execute(self, method: str, params: Optional[Dict] = None) -> Any:
        """Execute method with caching"""
        # Check cache for read operations
        if method.startswith('get_') or method.startswith('list_'):
            cache_key = f"{method}:{json.dumps(params or {}, sort_keys=True)}"
            cached = await self.cache.get(cache_key)
            if cached:
                await self.monitor.record_metric("cache_hit", 1)
                return cached
        
        # Execute request
        session = await self.pool.get_session(
            self.config['name'],
            self.config['url']
        )
        
        payload = {
            "jsonrpc": "2.0",
            "id": str(time.time()),
            "method": method,
            "params": params or {}
        }
        
        start = time.time()
        async with session.post('/execute', json=payload) as response:
            result = await response.json()
            elapsed = time.time() - start
            
            await self.monitor.record_metric("request_time", elapsed)
            
            # Cache result for read operations
            if method.startswith('get_') or method.startswith('list_'):
                await self.cache.set(cache_key, result)
            
            return result


# Singleton instances
_memory_cache = LRUCache(max_size=512)
_disk_cache = PersistentCache()
_connection_pool = ConnectionPool()


async def get_memory_cache() -> LRUCache:
    """Get singleton memory cache"""
    return _memory_cache


async def get_disk_cache() -> PersistentCache:
    """Get singleton disk cache"""
    return _disk_cache


async def get_connection_pool() -> ConnectionPool:
    """Get singleton connection pool"""
    return _connection_pool


async def cleanup():
    """Cleanup all resources"""
    await _memory_cache.clear()
    await _disk_cache.cleanup()
    await _connection_pool.close_all()


# Example usage
async def example_usage():
    """Example of performance optimization features"""
    
    # Use memoized function
    @async_memoize(ttl=timedelta(seconds=30))
    async def expensive_operation(param: str) -> str:
        await asyncio.sleep(2)  # Simulate expensive operation
        return f"Result for {param}"
    
    # First call takes 2 seconds
    result1 = await expensive_operation("test")
    
    # Second call returns immediately from cache
    result2 = await expensive_operation("test")
    
    # Batch processing
    processor = AsyncBatchProcessor(batch_size=5)
    items = list(range(100))
    
    async def process_item(item: int) -> int:
        await asyncio.sleep(0.1)
        return item * 2
    
    results = await processor.process(items, process_item)
    
    # Use optimized MCP client
    client = OptimizedMCPClient({
        "name": "test-server",
        "url": "http://localhost:8000"
    })
    
    # Batch execute multiple requests
    requests = [
        {"method": "get_user", "params": {"id": i}}
        for i in range(10)
    ]
    batch_results = await client.batch_execute(requests)
    
    # Get resource stats
    monitor = ResourceMonitor()
    stats = monitor.get_stats()
    print(f"Resource usage: {stats}")
    
    # Cleanup
    await cleanup()


if __name__ == "__main__":
    asyncio.run(example_usage())