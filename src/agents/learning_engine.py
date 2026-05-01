"""
Learning Engine - Continuous intelligence gathering from multiple sources
Learns from GitHub repos, coding books, web search, app stores.
"""

import os
import re
import json
import time
import hashlib
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote_plus


class LearningSource(Enum):
    """Sources of learning data"""
    GITHUB = "github"
    WEB = "web"
    BOOKS = "books"
    APPSTORE = "appstore"
    DOCUMENTATION = "documentation"
    VIDEO = "video"
    UNKNOWN = "unknown"


@dataclass
class LearnedKnowledge:
    """Represents a piece of learned knowledge"""
    source: str
    source_type: LearningSource
    topic: str
    content: str
    url: Optional[str] = None
    timestamp: Optional[str] = None
    relevance_score: float = 1.0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> dict:
        return asdict(self)


class GitHubLearner:
    """Learns from public GitHub repositories"""
    
    GITHUB_API = "https://api.github.com"
    
    def __init__(self, token: str = None):
        self.token = token
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        if token:
            self.headers['Authorization'] = f'token {token}'
    
    def search_repos(self, query: str, language: str = None, 
                    max_results: int = 10) -> List[Dict]:
        """Search GitHub repositories"""
        search_query = query
        if language:
            search_query += f" language:{language}"
        
        url = f"{self.GITHUB_API}/search/repositories"
        params = {
            'q': search_query,
            'per_page': max_results,
            'sort': 'stars',
            'order': 'desc'
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            repos = []
            for repo in data.get('items', []):
                repos.append({
                    'name': repo['full_name'],
                    'description': repo.get('description', ''),
                    'stars': repo['stargazers_count'],
                    'language': repo.get('language', ''),
                    'url': repo['html_url'],
                    'clone_url': repo['clone_url'],
                    'readme': None
                })
            
            return repos
        except Exception as e:
            print(f"GitHub search error: {e}")
            return []
    
    def get_readme(self, owner: str, repo: str) -> Optional[str]:
        """Get repository README content"""
        url = f"{self.GITHUB_API}/repos/{owner}/{repo}/readme"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            import base64
            content = base64.b64decode(data['content']).decode('utf-8')
            return content
        except Exception as e:
            print(f"README fetch error: {e}")
            return None
    
    def get_file_content(self, owner: str, repo: str, path: str) -> Optional[str]:
        """Get content of a file from repository"""
        url = f"{self.GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('encoding') == 'base64':
                import base64
                content = base64.b64decode(data['content']).decode('utf-8')
                return content
        except Exception as e:
            print(f"File fetch error: {e}")
            return None
    
    def learn_from_repo(self, repo_url: str) -> Dict[str, Any]:
        """Learn comprehensive information from a repository"""
        result = {
            'success': False,
            'repo': repo_url,
            'knowledge': [],
            'readme': '',
            'language': '',
            'topics': []
        }
        
        # Parse repo URL
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) >= 2:
            owner, repo = path_parts[0], path_parts[1]
            
            # Get repo info
            url = f"{self.GITHUB_API}/repos/{owner}/{repo}"
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    result['language'] = data.get('language', '')
                    result['topics'] = data.get('topics', [])
                    result['success'] = True
            except:
                pass
            
            # Get README
            result['readme'] = self.get_readme(owner, repo) or ''
        
        return result
    
    def get_trending_repos(self, language: str = None, 
                          since: str = 'daily') -> List[Dict]:
        """Get trending repositories"""
        url = f"https://github.com/trending"
        if language:
            url += f"/{language}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            repos = []
            articles = soup.find_all('article', class_='Box-row')
            
            for article in articles[:10]:
                link = article.find('h2', class_='h3')
                if link:
                    repo_name = link.find('a').get_text().strip()
                    desc_elem = article.find('p')
                    description = desc_elem.get_text().strip() if desc_elem else ''
                    
                    repos.append({
                        'name': repo_name,
                        'description': description,
                        'url': f"https://github.com/{repo_name}"
                    })
            
            return repos
        except Exception as e:
            print(f"Trending fetch error: {e}")
            return []


class BookLearner:
    """Learns from free programming books and documentation"""
    
    POPULAR_BOOKS = {
        'python': [
            'https://automatetheboringstuff.com/',
            'https://docs.python.org/3/tutorial/',
            'https://realpython.com/',
        ],
        'javascript': [
            'https://developer.mozilla.org/en-US/docs/Web/JavaScript',
            'https://javascript.info/',
            'https://eloquentjavascript.net/',
        ],
        'react': [
            'https://react.dev/',
            'https://www.freecodecamp.org/learn/',
        ],
        'ai_ml': [
            'https://spacy.io/usage/spacy-101',
            'https://pytorch.org/tutorials/',
            'https://tensorflow.org/tutorials/',
        ]
    }
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def get_free_books(self, topic: str) -> List[Dict]:
        """Get list of free books for a topic"""
        topic_lower = topic.lower()
        
        matching_books = []
        for topic_key, urls in self.POPULAR_BOOKS.items():
            if topic_key in topic_lower or topic_lower in topic_key:
                for url in urls:
                    matching_books.append({
                        'title': topic_key.title(),
                        'url': url,
                        'type': 'documentation'
                    })
        
        return matching_books
    
    def scrape_book_content(self, url: str, max_pages: int = 5) -> str:
        """Scrape content from a book/tutorial site"""
        content_parts = []
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for elem in soup(["script", "style", "nav", "header", "footer"]):
                elem.decompose()
            
            # Get main content
            main = soup.find('main') or soup.find('article') or soup.find('body')
            if main:
                text = main.get_text(separator='\n', strip=True)
                content_parts.append(text[:5000])  # Limit content
            
        except Exception as e:
            print(f"Book scrape error: {e}")
        
        return '\n\n'.join(content_parts)
    
    def learn_concept(self, concept: str) -> Dict[str, Any]:
        """Learn about a specific programming concept"""
        search_urls = [
            f"https://www.google.com/search?q={quote_plus(concept + ' tutorial')}",
            f"https://stackoverflow.com/search?q={quote_plus(concept)}"
        ]
        
        result = {
            'concept': concept,
            'sources': [],
            'summary': ''
        }
        
        return result


class WebScraper:
    """General web scraping for learning"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_text(self, url: str) -> str:
        """Scrape text content from a URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for elem in soup(["script", "style"]):
                elem.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text[:10000]  # Limit to 10k chars
        except Exception as e:
            return f"Error: {e}"
    
    def extract_code_snippets(self, url: str) -> List[str]:
        """Extract code snippets from a webpage"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            code_blocks = []
            for code in soup.find_all(['code', 'pre']):
                code_text = code.get_text(strip=True)
                if len(code_text) > 20:  # Filter out short snippets
                    code_blocks.append(code_text)
            
            return code_blocks
        except:
            return []


class WebFinder:
    """Search and find information from the web"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search the web"""
        try:
            # Use DuckDuckGo HTML
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            response = requests.get(url, headers=self.headers, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for i, result in enumerate(soup.find_all('div', class_='result')):
                if i >= num_results:
                    break
                
                title_tag = result.find('a', class_='result__a')
                snippet_tag = result.find('a', class_='result__snippet')
                
                if title_tag:
                    results.append({
                        'title': title_tag.get_text(),
                        'link': title_tag['href'],
                        'snippet': snippet_tag.get_text() if snippet_tag else ''
                    })
            
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def search_code(self, query: str) -> List[Dict]:
        """Search for code examples"""
        code_queries = [
            f"{query} code example github",
            f"{query} stackoverflow",
            f"{query} site:github.com"
        ]
        
        all_results = []
        for q in code_queries:
            results = self.search(q, num_results=3)
            all_results.extend(results)
        
        return all_results[:10]


class AppStoreLearner:
    """Learns intelligence from app stores"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search_apps(self, query: str, store: str = 'google') -> List[Dict]:
        """Search app stores for intelligence"""
        # Simplified - would need API keys in production
        return [{
            'name': query,
            'store': store,
            'intelligence': f'App insights for {query}'
        }]
    
    def get_app_metadata(self, app_id: str) -> Dict:
        """Get app metadata"""
        return {
            'app_id': app_id,
            'metadata': {
                'category': 'development',
                'features': ['AI-powered'],
                'compatibility': 'Windows 10+'
            }
        }


class LearningEngine:
    """
    Main Learning Engine - Coordinates all learning operations
    Gathers intelligence from multiple sources continuously.
    """
    
    def __init__(self, storage_dir: str = None):
        self.storage_dir = storage_dir or os.path.expanduser("~/Jarvis-Learning")
        self.knowledge_dir = os.path.join(self.storage_dir, "knowledge")
        self.cache_dir = os.path.join(self.storage_dir, "cache")
        
        os.makedirs(self.knowledge_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize learners
        self.github_learner = GitHubLearner()
        self.book_learner = BookLearner()
        self.web_scraper = WebScraper()
        self.web_finder = WebFinder()
        self.appstore_learner = AppStoreLearner()
        
        # Knowledge storage
        self.knowledge_base: Dict[str, LearnedKnowledge] = {}
        self.learning_history: List[Dict] = []
        
        # Load existing knowledge
        self._load_knowledge()
    
    def _load_knowledge(self):
        """Load existing knowledge from disk"""
        knowledge_file = os.path.join(self.knowledge_dir, "knowledge_base.json")
        if os.path.exists(knowledge_file):
            try:
                with open(knowledge_file, 'r') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        self.knowledge_base[key] = LearnedKnowledge(**value)
            except:
                pass
    
    def _save_knowledge(self):
        """Save knowledge to disk"""
        knowledge_file = os.path.join(self.knowledge_dir, "knowledge_base.json")
        data = {k: v.to_dict() for k, v in self.knowledge_base.items()}
        with open(knowledge_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def learn_from_github(self, query: str, max_repos: int = 5) -> List[Dict]:
        """Learn from GitHub repositories"""
        repos = self.github_learner.search_repos(query, max_results=max_repos)
        
        learned = []
        for repo in repos:
            repo_info = self.github_learner.learn_from_repo(repo['url'])
            
            if repo_info['success']:
                knowledge = LearnedKnowledge(
                    source=repo['name'],
                    source_type=LearningSource.GITHUB,
                    topic=query,
                    content=repo_info['readme'],
                    url=repo['url'],
                    tags=[repo_info['language']] + repo_info['topics']
                )
                
                key = hashlib.md5(f"{repo['url']}_{query}".encode()).hexdigest()
                self.knowledge_base[key] = knowledge
                learned.append(repo_info)
        
        self._save_knowledge()
        self.learning_history.append({
            'timestamp': datetime.now().isoformat(),
            'source': 'github',
            'query': query,
            'learned_count': len(learned)
        })
        
        return learned
    
    def learn_from_web(self, url: str, topic: str = None) -> Dict[str, Any]:
        """Learn from a web page"""
        content = self.web_scraper.scrape_text(url)
        topic = topic or urlparse(url).netloc
        
        knowledge = LearnedKnowledge(
            source=urlparse(url).netloc,
            source_type=LearningSource.WEB,
            topic=topic,
            content=content[:5000],
            url=url,
            tags=['web', 'learned']
        )
        
        key = hashlib.md5(url.encode()).hexdigest()
        self.knowledge_base[key] = knowledge
        self._save_knowledge()
        
        return {
            'success': True,
            'topic': topic,
            'content_length': len(content),
            'url': url
        }
    
    def search_and_learn(self, query: str) -> Dict[str, Any]:
        """Search the web and learn from results"""
        results = self.web_finder.search(query)
        
        learned_count = 0
        for result in results:
            self.learn_from_web(result['link'], topic=result['title'])
            learned_count += 1
        
        self.learning_history.append({
            'timestamp': datetime.now().isoformat(),
            'source': 'web_search',
            'query': query,
            'learned_count': learned_count
        })
        
        return {
            'query': query,
            'results_found': len(results),
            'learned': learned_count,
            'search_results': results
        }
    
    def learn_concept(self, concept: str) -> LearnedKnowledge:
        """Learn about a specific concept from multiple sources"""
        # Search web
        web_results = self.web_finder.search(concept)
        
        # Search code examples
        code_results = self.web_finder.search_code(concept)
        
        # Get book resources
        book_resources = self.book_learner.get_free_books(concept)
        
        combined_content = f"Concept: {concept}\n\n"
        combined_content += f"Web Sources: {len(web_results)}\n"
        combined_content += f"Code Examples: {len(code_results)}\n"
        combined_content += f"Documentation: {len(book_resources)}\n"
        
        knowledge = LearnedKnowledge(
            source="learning_engine",
            source_type=LearningSource.DOCUMENTATION,
            topic=concept,
            content=combined_content,
            tags=['concept', 'learned']
        )
        
        key = hashlib.md5(concept.encode()).hexdigest()
        self.knowledge_base[key] = knowledge
        self._save_knowledge()
        
        return knowledge
    
    def get_knowledge(self, topic: str = None) -> List[LearnedKnowledge]:
        """Get learned knowledge, optionally filtered by topic"""
        if topic:
            return [
                k for k in self.knowledge_base.values()
                if topic.lower() in k.topic.lower() or 
                   topic.lower() in ' '.join(k.tags).lower()
            ]
        
        return list(self.knowledge_base.values())
    
    def get_recent_learning(self, limit: int = 10) -> List[Dict]:
        """Get recent learning history"""
        return self.learning_history[-limit:]
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        sources_count = {}
        for k in self.knowledge_base.values():
            source_type = k.source_type.value
            sources_count[source_type] = sources_count.get(source_type, 0) + 1
        
        return {
            'total_knowledge': len(self.knowledge_base),
            'sources_breakdown': sources_count,
            'learning_sessions': len(self.learning_history),
            'storage_dir': self.storage_dir,
            'knowledge_base_size': len(str(self.knowledge_base))
        }
    
    def continuous_learning(self, keywords: List[str], duration_minutes: int = 60):
        """Continuous learning session for a duration"""
        start_time = time.time()
        learned = 0
        
        while time.time() - start_time < duration_minutes * 60:
            for keyword in keywords:
                # Learn from GitHub
                self.learn_from_github(keyword, max_repos=3)
                learned += 1
                
                # Search and learn from web
                self.search_and_learn(keyword)
                learned += 1
                
                # Learn concept
                self.learn_concept(keyword)
                learned += 1
            
            # Sleep between cycles
            time.sleep(60)
        
        return {
            'duration_minutes': duration_minutes,
            'learned_items': learned,
            'keywords': keywords
        }


# Global instance
_learning_engine = None

def get_learning_engine(storage_dir: str = None) -> LearningEngine:
    """Get or create the global Learning Engine instance"""
    global _learning_engine
    if _learning_engine is None:
        _learning_engine = LearningEngine(storage_dir)
    return _learning_engine
