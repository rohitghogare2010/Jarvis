"""
Jarvis Storage Module
50GB encrypted storage management with automatic organization
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger('JarvisStorage')


class EncryptedStorage:
    """Encrypted file storage with 50GB capacity"""
    
    def __init__(self, storage_path: str = './storage', encrypted: bool = True):
        self.storage_path = Path(storage_path)
        self.encrypted = encrypted
        self.max_storage = 50 * 1024 * 1024 * 1024  # 50GB
        self.index_file = self.storage_path / '.index.json'
        self.index = self.load_index()
        
        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)
        (self.storage_path / '.encrypted').mkdir(exist_ok=True)
        
    def load_index(self) -> Dict[str, Any]:
        """Load file index"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading index: {e}")
        return {'files': {}, 'metadata': {'created': datetime.now().isoformat()}}
    
    def save_index(self):
        """Save file index"""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def get_storage_usage(self) -> Dict[str, Any]:
        """Get storage usage statistics"""
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(self.storage_path):
            if '.index.json' in files:
                continue
            for file in files:
                file_path = Path(root) / file
                try:
                    total_size += file_path.stat().st_size
                    file_count += 1
                except OSError:
                    continue
        
        return {
            'total': self.max_storage,
            'used': total_size,
            'free': self.max_storage - total_size,
            'used_percent': (total_size / self.max_storage) * 100,
            'file_count': file_count
        }
    
    def store_file(self, source_path: str, category: str = 'general') -> Optional[str]:
        """Store a file in encrypted storage"""
        source = Path(source_path)
        if not source.exists():
            logger.error(f"Source file not found: {source_path}")
            return None
        
        file_hash = self.calculate_hash(source)
        file_ext = source.suffix
        
        # Generate encrypted filename
        encrypted_name = f"{file_hash[:16]}{file_ext}"
        dest_path = self.storage_path / '.encrypted' / encrypted_name
        
        try:
            # Copy file
            with open(source, 'rb') as src, open(dest_path, 'wb') as dst:
                if self.encrypted:
                    # Simple XOR encryption (in production, use proper encryption)
                    key = file_hash.encode()
                    while True:
                        chunk = src.read(8192)
                        if not chunk:
                            break
                        encrypted_chunk = bytes(a ^ b for a, b in zip(chunk, key * (len(chunk) // len(key) + 1)))
                        dst.write(encrypted_chunk)
                else:
                    dst.write(src.read())
            
            # Update index
            file_id = str(len(self.index['files']))
            self.index['files'][file_id] = {
                'original_name': source.name,
                'encrypted_name': encrypted_name,
                'hash': file_hash,
                'size': source.stat().st_size,
                'category': category,
                'created': datetime.now().isoformat(),
                'path': str(dest_path)
            }
            self.save_index()
            
            logger.info(f"File stored: {source.name} -> {encrypted_name}")
            return file_id
            
        except Exception as e:
            logger.error(f"Error storing file: {e}")
            return None
    
    def retrieve_file(self, file_id: str, dest_path: str = './') -> bool:
        """Retrieve and decrypt a file from storage"""
        if file_id not in self.index['files']:
            logger.error(f"File not found in index: {file_id}")
            return False
        
        file_info = self.index['files'][file_id]
        source_path = Path(file_info['path'])
        dest = Path(dest_path) / file_info['original_name']
        
        if not source_path.exists():
            logger.error(f"Encrypted file not found: {source_path}")
            return False
        
        try:
            with open(source_path, 'rb') as src, open(dest, 'wb') as dst:
                if self.encrypted:
                    key = file_info['hash'].encode()
                    with open(source_path, 'rb') as enc:
                        while True:
                            chunk = enc.read(8192)
                            if not chunk:
                                break
                            decrypted_chunk = bytes(a ^ b for a, b in zip(chunk, key * (len(chunk) // len(key) + 1)))
                            dst.write(decrypted_chunk)
                else:
                    dst.write(src.read())
            
            logger.info(f"File retrieved: {file_info['original_name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error retrieving file: {e}")
            return False
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file from storage"""
        if file_id not in self.index['files']:
            return False
        
        file_info = self.index['files'][file_id]
        file_path = Path(file_info['path'])
        
        try:
            if file_path.exists():
                file_path.unlink()
            del self.index['files'][file_id]
            self.save_index()
            logger.info(f"File deleted: {file_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def list_files(self, category: str = None) -> List[Dict[str, Any]]:
        """List files in storage"""
        if category:
            return [f for f in self.index['files'].values() if f['category'] == category]
        return list(self.index['files'].values())
    
    def search_files(self, query: str) -> List[Dict[str, Any]]:
        """Search files by name"""
        query = query.lower()
        return [
            f for f in self.index['files'].values()
            if query in f['original_name'].lower()
        ]


class MediaStorage(EncryptedStorage):
    """Specialized storage for videos and images (20GB encrypted)"""
    
    def __init__(self, storage_path: str = './media_storage'):
        super().__init__(storage_path, encrypted=True)
        self.max_storage = 20 * 1024 * 1024 * 1024  # 20GB


# Export classes
__all__ = ['EncryptedStorage', 'MediaStorage']