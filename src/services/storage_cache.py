"""
Storage Cache - 50GB LRU cache with encryption
High-performance caching system with automatic cleanup.
"""

import os
import json
import time
import hashlib
import shutil
import threading
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import gzip
import pickle


class CacheStrategy(Enum):
    """Cache replacement strategies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live


@dataclass
class CacheEntry:
    """Represents a single cache entry"""
    key: str
    value: Any
    size_bytes: int
    created_at: float
    last_accessed: float
    access_count: int = 0
    hits: int = 0
    metadata: Dict = field(default_factory=dict)
    
    def is_expired(self, ttl_seconds: float = None) -> bool:
        """Check if entry has expired"""
        if ttl_seconds is None:
            return False
        return (time.time() - self.last_accessed) > ttl_seconds


class StorageCache:
    """
    High-performance 50GB LRU Cache with encryption
    Provides intelligent caching with automatic cleanup and compression.
    """
    
    DEFAULT_MAX_SIZE_GB = 50
    DEFAULT_MAX_ITEMS = 100000
    CLEANUP_THRESHOLD = 0.9  # Start cleanup at 90% capacity
    
    def __init__(self, cache_dir: str = None, max_size_gb: float = None):
        self.cache_dir = cache_dir or os.path.expanduser("~/Jarvis-Cache/storage")
        self.max_size_bytes = int((max_size_gb or self.DEFAULT_MAX_SIZE_GB) * 1024 * 1024 * 1024)
        self.max_items = self.DEFAULT_MAX_ITEMS
        
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Index file for fast lookups
        self.index_file = os.path.join(self.cache_dir, "cache_index.json")
        self.stats_file = os.path.join(self.cache_dir, "cache_stats.json")
        
        # In-memory cache index
        self._cache_index: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        
        # Statistics
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'bytes_written': 0,
            'bytes_read': 0,
            'start_time': time.time()
        }
        
        # Load existing index
        self._load_index()
    
    def _load_index(self):
        """Load cache index from disk"""
        try:
            if os.path.exists(self.index_file):
                with open(self.index_file, 'r') as f:
                    data = json.load(f)
                    for key, entry_data in data.items():
                        self._cache_index[key] = CacheEntry(**entry_data)
        except Exception as e:
            print(f"Index load error: {e}")
            self._cache_index = {}
    
    def _save_index(self):
        """Save cache index to disk"""
        try:
            data = {
                key: {
                    'key': entry.key,
                    'size_bytes': entry.size_bytes,
                    'created_at': entry.created_at,
                    'last_accessed': entry.last_accessed,
                    'access_count': entry.access_count,
                    'hits': entry.hits,
                    'metadata': entry.metadata
                }
                for key, entry in self._cache_index.items()
            }
            with open(self.index_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Index save error: {e}")
    
    def _get_file_path(self, key: str) -> str:
        """Get file path for a cache key"""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.cache")
    
    def _calculate_size(self) -> int:
        """Calculate current cache size"""
        total = 0
        for entry in self._cache_index.values():
            total += entry.size_bytes
        return total
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value with compression"""
        try:
            data = pickle.dumps(value)
            compressed = gzip.compress(data)
            return compressed
        except:
            return pickle.dumps(value)
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value with decompression"""
        try:
            decompressed = gzip.decompress(data)
            return pickle.loads(decompressed)
        except:
            return pickle.loads(data)
    
    def _evict_lru(self, needed_bytes: int):
        """Evict least recently used entries"""
        if not self._cache_index:
            return
        
        # Sort by last accessed time (oldest first)
        sorted_entries = sorted(
            self._cache_index.items(),
            key=lambda x: x[1].last_accessed
        )
        
        freed_bytes = 0
        to_remove = []
        
        for key, entry in sorted_entries:
            if freed_bytes >= needed_bytes:
                break
            
            to_remove.append(key)
            freed_bytes += entry.size_bytes
            self._stats['evictions'] += 1
        
        # Remove entries
        for key in to_remove:
            self.delete(key)
    
    def _evict_lfu(self, needed_bytes: int):
        """Evict least frequently used entries"""
        if not self._cache_index:
            return
        
        sorted_entries = sorted(
            self._cache_index.items(),
            key=lambda x: x[1].hits
        )
        
        freed_bytes = 0
        to_remove = []
        
        for key, entry in sorted_entries:
            if freed_bytes >= needed_bytes:
                break
            
            to_remove.append(key)
            freed_bytes += entry.size_bytes
            self._stats['evictions'] += 1
        
        for key in to_remove:
            self.delete(key)
    
    def _auto_cleanup(self):
        """Automatically clean up cache if needed"""
        current_size = self._calculate_size()
        threshold = self.max_size_bytes * self.CLEANUP_THRESHOLD
        
        if current_size > threshold:
            needed = current_size - (self.max_size_bytes * 0.7)  # Target 70%
            self._evict_lru(int(needed))
    
    def set(self, key: str, value: Any, ttl_seconds: float = None, 
            metadata: Dict = None) -> bool:
        """Store a value in cache"""
        with self._lock:
            try:
                # Serialize value
                serialized = self._serialize(value)
                size = len(serialized)
                
                # Check if we need to make space
                current_size = self._calculate_size()
                if current_size + size > self.max_size_bytes:
                    self._auto_cleanup()
                
                # Create entry
                now = time.time()
                entry = CacheEntry(
                    key=key,
                    value=None,  # Don't store in memory
                    size_bytes=size,
                    created_at=now,
                    last_accessed=now,
                    access_count=0,
                    hits=0,
                    metadata=metadata or {}
                )
                
                # Write to disk
                file_path = self._get_file_path(key)
                with open(file_path, 'wb') as f:
                    f.write(serialized)
                
                # Update index
                self._cache_index[key] = entry
                self._stats['bytes_written'] += size
                
                # Save index periodically
                if len(self._cache_index) % 100 == 0:
                    self._save_index()
                
                return True
            except Exception as e:
                print(f"Cache set error: {e}")
                return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from cache"""
        with self._lock:
            if key not in self._cache_index:
                self._stats['misses'] += 1
                return default
            
            entry = self._cache_index[key]
            
            # Check TTL
            if entry.is_expired():
                self.delete(key)
                self._stats['misses'] += 1
                return default
            
            try:
                # Read from disk
                file_path = self._get_file_path(key)
                if not os.path.exists(file_path):
                    del self._cache_index[key]
                    self._stats['misses'] += 1
                    return default
                
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                # Deserialize
                value = self._deserialize(data)
                
                # Update access stats
                entry.last_accessed = time.time()
                entry.access_count += 1
                entry.hits += 1
                self._stats['bytes_read'] += len(data)
                self._stats['hits'] += 1
                
                return value
            except Exception as e:
                print(f"Cache get error: {e}")
                self._stats['misses'] += 1
                return default
    
    def delete(self, key: str) -> bool:
        """Delete a value from cache"""
        with self._lock:
            if key not in self._cache_index:
                return False
            
            try:
                file_path = self._get_file_path(key)
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                del self._cache_index[key]
                self._save_index()
                return True
            except Exception as e:
                print(f"Cache delete error: {e}")
                return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        return key in self._cache_index
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            for key in list(self._cache_index.keys()):
                self.delete(key)
            
            self._cache_index = {}
            self._save_index()
            self._save_stats()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        current_size = self._calculate_size()
        
        return {
            'current_size_bytes': current_size,
            'current_size_gb': current_size / (1024**3),
            'max_size_gb': self.max_size_bytes / (1024**3),
            'usage_percent': (current_size / self.max_size_bytes) * 100,
            'item_count': len(self._cache_index),
            'max_items': self.max_items,
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'hit_rate': (
                self._stats['hits'] / (self._stats['hits'] + self._stats['misses'])
                if (self._stats['hits'] + self._stats['misses']) > 0 else 0
            ),
            'evictions': self._stats['evictions'],
            'bytes_written': self._stats['bytes_written'],
            'bytes_read': self._stats['bytes_read'],
            'uptime_seconds': time.time() - self._stats['start_time']
        }
    
    def _save_stats(self):
        """Save statistics to disk"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self._stats, f, indent=2)
        except:
            pass
    
    def get_recent(self, limit: int = 20) -> List[Dict]:
        """Get recently accessed items"""
        sorted_entries = sorted(
            self._cache_index.items(),
            key=lambda x: x[1].last_accessed,
            reverse=True
        )
        
        return [
            {
                'key': key,
                'size_bytes': entry.size_bytes,
                'last_accessed': entry.last_accessed,
                'hits': entry.hits,
                'metadata': entry.metadata
            }
            for key, entry in sorted_entries[:limit]
        ]
    
    def get_least_used(self, limit: int = 20) -> List[Dict]:
        """Get least frequently used items"""
        sorted_entries = sorted(
            self._cache_index.items(),
            key=lambda x: x[1].hits
        )
        
        return [
            {
                'key': key,
                'size_bytes': entry.size_bytes,
                'hits': entry.hits,
                'access_count': entry.access_count
            }
            for key, entry in sorted_entries[:limit]
        ]
    
    def optimize(self):
        """Optimize cache by removing expired and low-value entries"""
        with self._lock:
            to_remove = []
            
            for key, entry in self._cache_index.items():
                if entry.is_expired():
                    to_remove.append(key)
                elif entry.hits == 0 and (time.time() - entry.created_at) > 86400:
                    to_remove.append(key)
            
            for key in to_remove:
                self.delete(key)
            
            return {
                'removed': len(to_remove),
                'remaining': len(self._cache_index)
            }
    
    def warm_up(self, keys: List[str]):
        """Pre-load items into cache"""
        with self._lock:
            loaded = 0
            for key in keys:
                if key not in self._cache_index:
                    file_path = self._get_file_path(key)
                    if os.path.exists(file_path):
                        # Just touch to update index
                        try:
                            stat = os.stat(file_path)
                            now = time.time()
                            self._cache_index[key] = CacheEntry(
                                key=key,
                                value=None,
                                size_bytes=stat.st_size,
                                created_at=stat.st_mtime,
                                last_accessed=now,
                                access_count=0,
                                hits=0
                            )
                            loaded += 1
                        except:
                            pass
            
            self._save_index()
            return loaded


class EncryptedStorage:
    """
    Encrypted storage for sensitive data
    Uses simple encryption (in production, use proper crypto library)
    """
    
    def __init__(self, storage_dir: str = None):
        self.storage_dir = storage_dir or os.path.expanduser("~/Jarvis-Cache/encrypted")
        os.makedirs(self.storage_dir, exist_ok=True)
        self._key = self._generate_key()
    
    def _generate_key(self) -> bytes:
        """Generate encryption key (simplified)"""
        import base64
        machine_id = hashlib.md5(os.environ.get('COMPUTERNAME', 'default').encode()).digest()
        return base64.b64encode(machine_id) * 2
    
    def _encrypt(self, data: bytes) -> bytes:
        """Simple XOR encryption"""
        key = self._key
        result = bytearray()
        for i, byte in enumerate(data):
            result.append(byte ^ key[i % len(key)])
        return bytes(result)
    
    def _decrypt(self, data: bytes) -> bytes:
        """Simple XOR decryption"""
        return self._encrypt(data)  # XOR is symmetric
    
    def save(self, key: str, data: Any) -> bool:
        """Save encrypted data"""
        try:
            file_path = os.path.join(self.storage_dir, f"{key}.enc")
            serialized = pickle.dumps(data)
            encrypted = self._encrypt(serialized)
            
            with open(file_path, 'wb') as f:
                f.write(encrypted)
            
            return True
        except Exception as e:
            print(f"Encrypted save error: {e}")
            return False
    
    def load(self, key: str, default: Any = None) -> Any:
        """Load encrypted data"""
        try:
            file_path = os.path.join(self.storage_dir, f"{key}.enc")
            if not os.path.exists(file_path):
                return default
            
            with open(file_path, 'rb') as f:
                encrypted = f.read()
            
            decrypted = self._decrypt(encrypted)
            return pickle.loads(decrypted)
        except Exception as e:
            print(f"Encrypted load error: {e}")
            return default
    
    def delete(self, key: str) -> bool:
        """Delete encrypted data"""
        try:
            file_path = os.path.join(self.storage_dir, f"{key}.enc")
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except:
            return False


# Global instances
_storage_cache = None
_encrypted_storage = None

def get_storage_cache(cache_dir: str = None, max_size_gb: float = None) -> StorageCache:
    """Get or create the global Storage Cache instance"""
    global _storage_cache
    if _storage_cache is None:
        _storage_cache = StorageCache(cache_dir, max_size_gb)
    return _storage_cache

def get_encrypted_storage(storage_dir: str = None) -> EncryptedStorage:
    """Get or create the global Encrypted Storage instance"""
    global _encrypted_storage
    if _encrypted_storage is None:
        _encrypted_storage = EncryptedStorage(storage_dir)
    return _encrypted_storage
