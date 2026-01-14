"""
URL cache for storing and checking failed URLs to avoid repeated failures.
Also includes content cache for storing successfully fetched webpage content.
"""

import json
import time
import logging
import hashlib
from typing import Dict, Optional, Set, Any, List
from urllib.parse import urlparse
from pathlib import Path
from dataclasses import dataclass, asdict
from threading import Lock, RLock
from collections import OrderedDict


logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entry in the URL cache."""
    url: str
    failure_count: int
    last_failure_time: float
    error_type: str
    
    def is_expired(self, ttl: int) -> bool:
        """Check if the cache entry has expired."""
        return (time.time() - self.last_failure_time) > ttl


class DomainCache:
    """
    Cache for tracking failed URLs to avoid repeated fetch attempts.
    
    Features:
    - Configurable TTL (time-to-live) for cache entries
    - Configurable failure threshold before URL is cached
    - Persistent storage to file (optional)
    - Thread-safe operations
    """
    
    def __init__(
        self,
        cache_file: Optional[str] = None,
        ttl: int = 86400,  # 24 hours default
        failure_threshold: int = 3,
        max_size: int = 10000,
    ):
        """
        Initialize URL cache.
        
        Args:
            cache_file: Path to cache file for persistence (None for memory-only)
            ttl: Time-to-live for cache entries in seconds (default: 24 hours)
            failure_threshold: Number of failures before caching URL (default: 3)
            max_size: Maximum number of entries in cache (default: 10000)
        """
        self.cache_file = cache_file
        self.ttl = ttl
        self.failure_threshold = failure_threshold
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        
        if cache_file:
            self._load_cache()
    
    def _load_cache(self) -> None:
        """Load cache from file."""
        if not self.cache_file or not Path(self.cache_file).exists():
            return
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for url, entry_dict in data.items():
                    self._cache[url] = CacheEntry(**entry_dict)
        except (IOError, PermissionError) as e:
            logger.warning(f"Failed to load cache from {self.cache_file}: {e}")
            self._cache = {}
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Cache file {self.cache_file} is corrupted: {e}")
            self._cache = {}
        except Exception as e:
            logger.error(f"Unexpected error loading cache: {e}")
            self._cache = {}
    
    def _save_cache(self) -> None:
        """Save cache to file."""
        if not self.cache_file:
            return
        
        try:
            # Clean expired entries before saving
            self._clean_expired()
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                data = {url: asdict(entry) for url, entry in self._cache.items()}
                json.dump(data, f, indent=2)
        except (IOError, PermissionError) as e:
            logger.warning(f"Failed to save cache to {self.cache_file}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving cache: {e}")
    
    def _clean_expired(self) -> None:
        """Remove expired entries from cache."""
        current_time = time.time()
        expired_urls = [
            url for url, entry in self._cache.items()
            if (current_time - entry.last_failure_time) > self.ttl
        ]
        for url in expired_urls:
            del self._cache[url]
    
    def _enforce_max_size(self) -> None:
        """Ensure cache doesn't exceed max size by removing oldest entries."""
        if len(self._cache) <= self.max_size:
            return
        
        # Sort by last failure time and remove oldest entries
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].last_failure_time
        )
        
        num_to_remove = len(self._cache) - self.max_size
        for url, _ in sorted_entries[:num_to_remove]:
            del self._cache[url]
    
    def should_skip(self, url: str) -> bool:
        """
        Check if URL should be skipped based on cached failures.
        
        Args:
            url: URL to check
        
        Returns:
            True if URL should be skipped, False otherwise
        """
        with self._lock:
            if url not in self._cache:
                return False
            
            entry = self._cache[url]
            
            # Check if entry has expired
            if entry.is_expired(self.ttl):
                del self._cache[url]
                return False
            
            # Check if failure count exceeds threshold
            return entry.failure_count >= self.failure_threshold
    
    def record_failure(
        self,
        url: str,
        error_type: str = "unknown"
    ) -> None:
        """
        Record a failure for a URL.
        
        Args:
            url: URL that failed
            error_type: Type of error (e.g., "404", "403", "timeout")
        """
        current_time = time.time()
        
        with self._lock:
            if url in self._cache:
                entry = self._cache[url]
                
                # Check if entry has expired
                if entry.is_expired(self.ttl):
                    # Reset entry
                    entry.failure_count = 1
                    entry.last_failure_time = current_time
                    entry.error_type = error_type
                else:
                    # Increment failure count
                    entry.failure_count += 1
                    entry.last_failure_time = current_time
                    entry.error_type = error_type
            else:
                # Create new entry
                self._cache[url] = CacheEntry(
                    url=url,
                    failure_count=1,
                    last_failure_time=current_time,
                    error_type=error_type
                )
            
            # Enforce max size
            self._enforce_max_size()
            
            # Save to file if configured
            if self.cache_file:
                self._save_cache()
    
    def record_success(self, url: str) -> None:
        """
        Record a success for a URL (removes it from cache).
        
        Args:
            url: URL that succeeded
        """
        with self._lock:
            if url in self._cache:
                del self._cache[url]
                
                # Save to file if configured
                if self.cache_file:
                    self._save_cache()
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            if self.cache_file:
                self._save_cache()
    
    def get_stats(self) -> Dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            return {
                "total_entries": len(self._cache),
                "urls": list(self._cache.keys()),
                "failure_counts": {
                    url: entry.failure_count
                    for url, entry in self._cache.items()
                }
            }


@dataclass
class ContentCacheEntry:
    """Entry in the content cache for successfully fetched webpages."""
    url: str
    html: Optional[str]
    content: Optional[str]
    timestamp: float
    final_url: Optional[str]
    metadata: Dict[str, Any]


class ContentCache:
    """
    High-performance LRU cache for storing successfully fetched webpage content.
    
    Features:
    - LRU (Least Recently Used) eviction policy
    - Configurable maximum size
    - Thread-safe operations with optimized concurrency using sharding
    - Stores both HTML and extracted content
    - Only caches successful fetches
    - Sharded design reduces lock contention for high-concurrency scenarios
    
    This is a short-term temporary cache for webpage content, NOT for failed domains.
    
    The cache uses sharding to minimize lock contention under high concurrency.
    URLs are distributed across multiple shards based on hash, so concurrent
    operations on different URLs can proceed in parallel without blocking.
    """
    
    def __init__(self, max_size: int = 500, num_shards: int = 16):
        """
        Initialize content cache.
        
        Args:
            max_size: Maximum number of entries to cache (default: 500)
                     Set to 0 to disable caching
            num_shards: Number of cache shards for concurrency (default: 16)
                       Higher values reduce lock contention but use more memory
        """
        self.max_size = max_size
        self.num_shards = num_shards
        
        # Create sharded caches for better concurrency
        # Each shard has its own lock and OrderedDict
        self._shards: List[Dict[str, Any]] = []
        for _ in range(num_shards):
            self._shards.append({
                'cache': OrderedDict(),
                'lock': RLock(),
                'max_size': max_size // num_shards + (max_size % num_shards > 0)
            })
    
    def _get_shard(self, url: str) -> Dict[str, Any]:
        """Get the shard for a given URL based on hash."""
        # Use hash to distribute URLs across shards
        url_hash = int(hashlib.md5(url.encode()).hexdigest(), 16)
        shard_index = url_hash % self.num_shards
        return self._shards[shard_index]
    
    def get(self, url: str) -> Optional[ContentCacheEntry]:
        """
        Get cached content for a URL.
        
        Args:
            url: URL to retrieve from cache
        
        Returns:
            ContentCacheEntry if found, None otherwise
        """
        if self.max_size == 0:
            return None
        
        shard = self._get_shard(url)
        with shard['lock']:
            cache = shard['cache']
            if url in cache:
                # Move to end to mark as recently used (LRU)
                cache.move_to_end(url)
                return cache[url]
            return None
    
    def put(
        self,
        url: str,
        html: Optional[str] = None,
        content: Optional[str] = None,
        final_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Store content in cache (only for successful fetches).
        
        Args:
            url: Original URL
            html: Raw HTML content
            content: Extracted content
            final_url: Final URL after redirects
            metadata: Additional metadata
        """
        if self.max_size == 0:
            return
        
        shard = self._get_shard(url)
        with shard['lock']:
            cache = shard['cache']
            
            # Create cache entry
            entry = ContentCacheEntry(
                url=url,
                html=html,
                content=content,
                timestamp=time.time(),
                final_url=final_url,
                metadata=metadata or {}
            )
            
            # If URL already exists, remove it first (will be re-added at end)
            if url in cache:
                del cache[url]
            
            # Add new entry at the end (most recent)
            cache[url] = entry
            
            # Enforce max size by removing oldest entries (from beginning)
            max_shard_size = shard['max_size']
            while len(cache) > max_shard_size:
                # Remove first item (oldest in LRU)
                cache.popitem(last=False)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        for shard in self._shards:
            with shard['lock']:
                shard['cache'].clear()
    
    def get_stats(self) -> Dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        all_urls = []
        all_timestamps = []
        total_entries = 0
        
        # Collect stats from all shards
        for shard in self._shards:
            with shard['lock']:
                cache = shard['cache']
                total_entries += len(cache)
                all_urls.extend(cache.keys())
                all_timestamps.extend(entry.timestamp for entry in cache.values())
        
        return {
            "total_entries": total_entries,
            "max_size": self.max_size,
            "num_shards": self.num_shards,
            "urls": all_urls,
            "oldest_timestamp": min(all_timestamps) if all_timestamps else None,
            "newest_timestamp": max(all_timestamps) if all_timestamps else None
        }
    
    def __len__(self) -> int:
        """Return number of cached entries."""
        total = 0
        for shard in self._shards:
            with shard['lock']:
                total += len(shard['cache'])
        return total
