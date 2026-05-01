"""
Jarvis Core - Central Intelligence Layer for RS AI / JARVIS OS
Controls all AI operations, command routing, and system intelligence.
"""

import json
import os
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class IntentType(Enum):
    """Types of intents the AI can handle"""
    CHAT = "chat"
    CODE = "code"
    IMAGE = "image"
    VIDEO = "video"
    LEARN = "learn"
    SEARCH = "search"
    OS_CONTROL = "os_control"
    PROJECT = "project"
    VOICE = "voice"
    UNKNOWN = "unknown"


@dataclass
class ConversationContext:
    """Maintains conversation context and history"""
    session_id: str
    created_at: datetime
    last_updated: datetime
    user_preferences: Dict[str, Any]
    conversation_history: List[Dict[str, str]]
    active_tasks: List[Dict[str, Any]]
    learned_facts: Dict[str, str]
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_updated'] = self.last_updated.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ConversationContext':
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)


class IntentClassifier:
    """Classifies user intents from natural language"""
    
    # Keyword patterns for intent detection
    INTENT_PATTERNS = {
        IntentType.CODE: [
            'code', 'write', 'create', 'function', 'class', 'python', 'javascript',
            'java', 'c++', 'rust', 'go', 'programming', 'debug', 'fix', 'error',
            'script', 'variable', 'import', 'export', 'compile', 'build', 'execute',
            'vscode', 'file', 'directory', 'folder'
        ],
        IntentType.IMAGE: [
            'image', 'picture', 'photo', 'generate', 'create', 'draw', 'art',
            'render', 'stable diffusion', 'sd', '8k', '16k', 'upscale', 'resolution',
            'realistic', 'anime', 'supernatural', 'movie', 'style', 'character',
            'city', 'architecture', 'portrait', 'landscape'
        ],
        IntentType.VIDEO: [
            'video', 'movie', 'film', 'clip', 'animation', 'animate', 'generate',
            'create', 'cinematic', 'scene', 'frame', 'duration', 'stable video',
            'svd', 'youtube', 'tiktok', 'reel', 'short'
        ],
        IntentType.LEARN: [
            'learn', 'teach', 'study', 'research', 'search', 'find', 'github',
            'repository', 'book', 'documentation', 'wiki', 'scrape', 'crawl',
            'knowledge', 'understand', 'explain', 'how does', 'what is'
        ],
        IntentType.SEARCH: [
            'search', 'find', 'lookup', 'google', 'duckduckgo', 'bing', 'web',
            'internet', 'online', 'query', 'browse'
        ],
        IntentType.OS_CONTROL: [
            'open', 'close', 'start', 'stop', 'run', 'execute', 'command',
            'system', 'windows', 'folder', 'file', 'app', 'application',
            'autostart', 'registry', 'background', 'tray'
        ],
        IntentType.PROJECT: [
            'project', 'app', 'website', 'webapp', 'desktop', 'application',
            'build', 'create', 'scaffold', 'template', 'framework', 'react',
            'vue', 'angular', 'django', 'flask', 'electron', 'nextjs'
        ],
        IntentType.VOICE: [
            'speak', 'talk', 'voice', 'audio', 'speech', 'say', ' pronounce',
            'listen', 'hear', 'microphone', 'record', 'transcribe'
        ]
    }
    
    @classmethod
    def classify(cls, text: str) -> IntentType:
        """Classify intent from text input"""
        text_lower = text.lower()
        
        # Count keyword matches for each intent
        intent_scores = {}
        for intent_type, patterns in cls.INTENT_PATTERNS.items():
            score = sum(1 for pattern in patterns if pattern in text_lower)
            if score > 0:
                intent_scores[intent_type] = score
        
        if not intent_scores:
            return IntentType.CHAT
        
        # Return the intent with highest score
        return max(intent_scores, key=intent_scores.get)


class CommandRouter:
    """Routes commands to appropriate agents"""
    
    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents
        self.classifier = IntentClassifier()
    
    def route(self, text: str, context: ConversationContext) -> Dict[str, Any]:
        """Route a command to the appropriate agent"""
        intent = self.classifier.classify(text)
        
        routing_map = {
            IntentType.CODE: 'coding_agent',
            IntentType.IMAGE: 'image_generator',
            IntentType.VIDEO: 'video_generator',
            IntentType.LEARN: 'learning_engine',
            IntentType.SEARCH: 'web_finder',
            IntentType.OS_CONTROL: 'os_control',
            IntentType.PROJECT: 'project_builder',
            IntentType.VOICE: 'voice_io',
            IntentType.CHAT: 'ollama'
        }
        
        agent_name = routing_map.get(intent, 'ollama')
        
        return {
            'intent': intent.value,
            'agent': agent_name,
            'text': text,
            'context': context
        }


class JarvisCore:
    """
    Central Intelligence Layer for JARVIS OS
    Coordinates all AI operations and provides unified interface.
    """
    
    def __init__(self, cache_dir: str = None):
        self.cache_dir = cache_dir or os.path.expanduser("~/Jarvis-Cache")
        self.context_dir = os.path.join(self.cache_dir, "contexts")
        os.makedirs(self.context_dir, exist_ok=True)
        
        # Initialize components
        self.contexts: Dict[str, ConversationContext] = {}
        self.knowledge_base: Dict[str, Any] = {}
        self.learning_history: List[Dict] = []
        
        # Initialize agents registry
        self.agents: Dict[str, Any] = {}
        
        # Performance metrics
        self.metrics = {
            'requests_processed': 0,
            'images_generated': 0,
            'videos_generated': 0,
            'code_files_created': 0,
            'knowledge_acquired': 0,
            'uptime_start': time.time()
        }
    
    def register_agent(self, name: str, agent: Any):
        """Register an AI agent with the core"""
        self.agents[name] = agent
    
    def create_session(self, user_id: str = "default") -> str:
        """Create a new conversation session"""
        session_id = hashlib.md5(f"{user_id}_{time.time()}".encode()).hexdigest()[:12]
        
        context = ConversationContext(
            session_id=session_id,
            created_at=datetime.now(),
            last_updated=datetime.now(),
            user_preferences={},
            conversation_history=[],
            active_tasks=[],
            learned_facts={}
        )
        
        self.contexts[session_id] = context
        self.save_context(session_id)
        
        return session_id
    
    def get_context(self, session_id: str) -> Optional[ConversationContext]:
        """Get conversation context by session ID"""
        return self.contexts.get(session_id)
    
    def update_context(self, session_id: str, **kwargs):
        """Update conversation context"""
        context = self.contexts.get(session_id)
        if context:
            for key, value in kwargs.items():
                if hasattr(context, key):
                    setattr(context, key, value)
            context.last_updated = datetime.now()
            self.save_context(session_id)
    
    def add_to_history(self, session_id: str, role: str, content: str):
        """Add a message to conversation history"""
        context = self.contexts.get(session_id)
        if context:
            context.conversation_history.append({
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat()
            })
            context.last_updated = datetime.now()
            self.save_context(session_id)
    
    def learn_fact(self, session_id: str, fact_key: str, fact_value: str):
        """Store a learned fact"""
        context = self.contexts.get(session_id)
        if context:
            context.learned_facts[fact_key] = fact_value
            self.metrics['knowledge_acquired'] += 1
            self.save_context(session_id)
    
    def get_learning_context(self, session_id: str) -> str:
        """Build context string from learned facts for AI prompts"""
        context = self.contexts.get(session_id)
        if not context or not context.learned_facts:
            return ""
        
        facts_text = "\nKnown facts:\n"
        for key, value in context.learned_facts.items():
            facts_text += f"- {key}: {value}\n"
        
        return facts_text
    
    def process(self, text: str, session_id: str = None, images: List = None) -> Dict[str, Any]:
        """Process user input and route to appropriate agent"""
        self.metrics['requests_processed'] += 1
        
        # Create session if not provided
        if not session_id:
            session_id = self.create_session()
        
        # Get or create context
        context = self.get_context(session_id)
        if not context:
            session_id = self.create_session()
            context = self.get_context(session_id)
        
        # Add user message to history
        self.add_to_history(session_id, 'user', text)
        
        # Classify intent
        intent = IntentClassifier.classify(text)
        
        # Build response
        response = {
            'session_id': session_id,
            'intent': intent.value,
            'text': text,
            'context': context,
            'success': True,
            'timestamp': datetime.now().isoformat()
        }
        
        return response
    
    def save_context(self, session_id: str):
        """Save context to disk"""
        context = self.contexts.get(session_id)
        if context:
            path = os.path.join(self.context_dir, f"{session_id}.json")
            with open(path, 'w') as f:
                json.dump(context.to_dict(), f, indent=2)
    
    def load_context(self, session_id: str) -> Optional[ConversationContext]:
        """Load context from disk"""
        path = os.path.join(self.context_dir, f"{session_id}.json")
        if os.path.exists(path):
            with open(path, 'r') as f:
                return ConversationContext.from_dict(json.load(f))
        return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        metrics = self.metrics.copy()
        metrics['uptime_seconds'] = time.time() - metrics['uptime_start']
        metrics['active_sessions'] = len(self.contexts)
        metrics['knowledge_base_size'] = len(self.knowledge_base)
        return metrics
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'status': 'online',
            'version': '2.0.0',
            'name': 'JARVIS OS',
            'uptime': self.get_metrics()['uptime_seconds'],
            'agents_registered': list(self.agents.keys()),
            'active_sessions': len(self.contexts),
            'knowledge_entries': self.metrics['knowledge_acquired'],
            'cache_dir': self.cache_dir
        }


class MemoryManager:
    """Manages encrypted memory and knowledge storage"""
    
    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        self.memory_file = os.path.join(storage_dir, "memory.enc")
        os.makedirs(storage_dir, exist_ok=True)
        self.memory: Dict[str, Any] = {}
        self.load_memory()
    
    def load_memory(self):
        """Load memory from encrypted storage"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    self.memory = json.load(f)
            except:
                self.memory = {}
    
    def save_memory(self):
        """Save memory to encrypted storage"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def store(self, key: str, value: Any):
        """Store a memory item"""
        self.memory[key] = {
            'value': value,
            'timestamp': time.time(),
            'access_count': 0
        }
        self.save_memory()
    
    def recall(self, key: str) -> Optional[Any]:
        """Recall a memory item"""
        if key in self.memory:
            self.memory[key]['access_count'] += 1
            self.save_memory()
            return self.memory[key]['value']
        return None
    
    def forget(self, key: str):
        """Forget a memory item"""
        if key in self.memory:
            del self.memory[key]
            self.save_memory()
    
    def get_recent(self, limit: int = 10) -> List[Dict]:
        """Get recently accessed memories"""
        sorted_memory = sorted(
            self.memory.items(),
            key=lambda x: x[1]['timestamp'],
            reverse=True
        )
        return [{'key': k, 'value': v['value']} for k, v in sorted_memory[:limit]]


# Global instance
_jarvis_core = None

def get_jarvis_core(cache_dir: str = None) -> JarvisCore:
    """Get or create the global Jarvis Core instance"""
    global _jarvis_core
    if _jarvis_core is None:
        _jarvis_core = JarvisCore(cache_dir)
    return _jarvis_core
