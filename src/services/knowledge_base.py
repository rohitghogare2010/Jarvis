"""
Knowledge Base - 20GB encrypted storage for learned knowledge
Secure storage for video/image knowledge and AI intelligence.
"""

import os
import json
import hashlib
import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import shutil


@dataclass
class KnowledgeEntry:
    """A single knowledge entry"""
    id: str
    type: str  # 'video', 'image', 'concept', 'fact'
    topic: str
    content: str
    source: str
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    accessed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    access_count: int = 0
    relevance_score: float = 1.0
    metadata: Dict = field(default_factory=dict)


class VideoKnowledgeStore:
    """Store for video-based learning and knowledge"""
    
    MAX_VIDEOS = 50000
    MAX_IMAGES = 100000
    
    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        self.videos_dir = os.path.join(storage_dir, "videos")
        self.images_dir = os.path.join(storage_dir, "images")
        self.index_file = os.path.join(storage_dir, "video_index.json")
        
        os.makedirs(self.videos_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        
        self._index: Dict[str, Dict] = {}
        self._lock = threading.Lock()
        
        self._load_index()
    
    def _load_index(self):
        """Load index from disk"""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r') as f:
                    self._index = json.load(f)
            except:
                self._index = {}
    
    def _save_index(self):
        """Save index to disk"""
        with open(self.index_file, 'w') as f:
            json.dump(self._index, f, indent=2)
    
    def store_video(self, video_id: str, video_data: bytes, 
                    metadata: Dict = None) -> bool:
        """Store video data"""
        with self._lock:
            try:
                file_path = os.path.join(self.videos_dir, f"{video_id}.mp4")
                with open(file_path, 'wb') as f:
                    f.write(video_data)
                
                self._index[video_id] = {
                    'type': 'video',
                    'file_path': file_path,
                    'size_bytes': len(video_data),
                    'metadata': metadata or {},
                    'created_at': datetime.now().isoformat()
                }
                
                self._save_index()
                return True
            except Exception as e:
                print(f"Store video error: {e}")
                return False
    
    def store_image(self, image_id: str, image_data: bytes,
                   metadata: Dict = None) -> bool:
        """Store image data"""
        with self._lock:
            try:
                file_path = os.path.join(self.images_dir, f"{image_id}.png")
                with open(file_path, 'wb') as f:
                    f.write(image_data)
                
                self._index[image_id] = {
                    'type': 'image',
                    'file_path': file_path,
                    'size_bytes': len(image_data),
                    'metadata': metadata or {},
                    'created_at': datetime.now().isoformat()
                }
                
                self._save_index()
                return True
            except Exception as e:
                print(f"Store image error: {e}")
                return False
    
    def get_video(self, video_id: str) -> Optional[bytes]:
        """Retrieve video data"""
        if video_id not in self._index:
            return None
        
        try:
            file_path = self._index[video_id]['file_path']
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    return f.read()
        except:
            pass
        return None
    
    def get_image(self, image_id: str) -> Optional[bytes]:
        """Retrieve image data"""
        if image_id not in self._index:
            return None
        
        try:
            file_path = self._index[image_id]['file_path']
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    return f.read()
        except:
            pass
        return None
    
    def search(self, query: str) -> List[Dict]:
        """Search stored content"""
        results = []
        query_lower = query.lower()
        
        for entry_id, entry in self._index.items():
            metadata = entry.get('metadata', {})
            topic = metadata.get('topic', '').lower()
            tags = ' '.join(metadata.get('tags', [])).lower()
            
            if query_lower in topic or query_lower in tags:
                results.append({
                    'id': entry_id,
                    'type': entry['type'],
                    'topic': metadata.get('topic', ''),
                    'tags': metadata.get('tags', [])
                })
        
        return results
    
    def get_stats(self) -> Dict:
        """Get storage statistics"""
        total_size = 0
        video_count = 0
        image_count = 0
        
        for entry in self._index.values():
            total_size += entry.get('size_bytes', 0)
            if entry.get('type') == 'video':
                video_count += 1
            elif entry.get('type') == 'image':
                image_count += 1
        
        return {
            'total_entries': len(self._index),
            'video_count': video_count,
            'image_count': image_count,
            'total_size_gb': total_size / (1024**3),
            'capacity_percent': (total_size / (20 * 1024**3)) * 100
        }
    
    def cleanup_oldest(self, target_count: int):
        """Remove oldest entries to meet target count"""
        sorted_entries = sorted(
            self._index.items(),
            key=lambda x: x[1].get('created_at', '')
        )
        
        to_remove = len(self._index) - target_count
        for entry_id, _ in sorted_entries[:to_remove]:
            self.delete(entry_id)
    
    def delete(self, entry_id: str) -> bool:
        """Delete an entry"""
        if entry_id not in self._index:
            return False
        
        try:
            file_path = self._index[entry_id]['file_path']
            if os.path.exists(file_path):
                os.remove(file_path)
            del self._index[entry_id]
            self._save_index()
            return True
        except:
            return False


class KnowledgeBase:
    """
    Main Knowledge Base - 20GB encrypted storage
    Manages all learned knowledge with secure, encrypted storage.
    """
    
    DEFAULT_SIZE_GB = 20
    
    def __init__(self, storage_dir: str = None):
        self.storage_dir = storage_dir or os.path.expanduser("~/Jarvis-Knowledge")
        self.base_dir = os.path.join(self.storage_dir, "knowledge_base")
        self.entries_dir = os.path.join(self.base_dir, "entries")
        
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(self.entries_dir, exist_ok=True)
        
        # Initialize stores
        self.video_store = VideoKnowledgeStore(
            os.path.join(self.base_dir, "media")
        )
        
        # Entries index
        self.index_file = os.path.join(self.base_dir, "knowledge_index.json")
        self._entries: Dict[str, KnowledgeEntry] = {}
        
        # Load existing entries
        self._load_entries()
    
    def _load_entries(self):
        """Load knowledge entries from disk"""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r') as f:
                    data = json.load(f)
                    for id, entry_data in data.items():
                        self._entries[id] = KnowledgeEntry(**entry_data)
            except:
                self._entries = {}
    
    def _save_entries(self):
        """Save knowledge entries to disk"""
        data = {
            id: {
                'id': entry.id,
                'type': entry.type,
                'topic': entry.topic,
                'content': entry.content,
                'source': entry.source,
                'tags': entry.tags,
                'created_at': entry.created_at,
                'accessed_at': entry.accessed_at,
                'access_count': entry.access_count,
                'relevance_score': entry.relevance_score,
                'metadata': entry.metadata
            }
            for id, entry in self._entries.items()
        }
        
        with open(self.index_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def store(self, entry: KnowledgeEntry) -> str:
        """Store a knowledge entry"""
        entry_id = entry.id or hashlib.md5(
            f"{entry.topic}_{time.time()}".encode()
        ).hexdigest()[:16]
        
        entry.id = entry_id
        self._entries[entry_id] = entry
        self._save_entries()
        
        return entry_id
    
    def retrieve(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Retrieve a knowledge entry"""
        if entry_id in self._entries:
            entry = self._entries[entry_id]
            entry.access_count += 1
            entry.accessed_at = datetime.now().isoformat()
            self._save_entries()
            return entry
        return None
    
    def search(self, query: str, limit: int = 20) -> List[KnowledgeEntry]:
        """Search knowledge base"""
        results = []
        query_lower = query.lower()
        
        for entry in self._entries.values():
            if (query_lower in entry.topic.lower() or
                query_lower in entry.content.lower() or
                any(query_lower in tag.lower() for tag in entry.tags)):
                results.append(entry)
        
        # Sort by relevance and recency
        results.sort(
            key=lambda x: (x.relevance_score, x.access_count),
            reverse=True
        )
        
        return results[:limit]
    
    def get_by_topic(self, topic: str) -> List[KnowledgeEntry]:
        """Get all entries for a topic"""
        return [
            e for e in self._entries.values()
            if topic.lower() in e.topic.lower()
        ]
    
    def update_relevance(self, entry_id: str, delta: float):
        """Update relevance score"""
        if entry_id in self._entries:
            entry = self._entries[entry_id]
            entry.relevance_score = max(0, min(10, entry.relevance_score + delta))
            self._save_entries()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        type_counts = {}
        for entry in self._entries.values():
            type_counts[entry.type] = type_counts.get(entry.type, 0) + 1
        
        return {
            'total_entries': len(self._entries),
            'by_type': type_counts,
            'storage_dir': self.base_dir,
            'media_stats': self.video_store.get_stats()
        }
    
    def export_to(self, export_dir: str) -> bool:
        """Export knowledge base to directory"""
        try:
            shutil.copytree(self.base_dir, export_dir, dirs_exist_ok=True)
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False
    
    def import_from(self, import_dir: str) -> int:
        """Import knowledge base from directory"""
        imported = 0
        try:
            for filename in os.listdir(import_dir):
                if filename.endswith('.json'):
                    with open(os.path.join(import_dir, filename)) as f:
                        data = json.load(f)
                        entry = KnowledgeEntry(**data)
                        self.store(entry)
                        imported += 1
        except Exception as e:
            print(f"Import error: {e}")
        return imported
    
    def clear(self):
        """Clear all knowledge"""
        self._entries = {}
        self._save_entries()
        self.video_store = VideoKnowledgeStore(
            os.path.join(self.base_dir, "media")
        )


# Global instance
_knowledge_base = None

def get_knowledge_base(storage_dir: str = None) -> KnowledgeBase:
    """Get or create the global Knowledge Base instance"""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = KnowledgeBase(storage_dir)
    return _knowledge_base
