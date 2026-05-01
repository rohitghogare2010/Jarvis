import requests
from bs4 import BeautifulSoup
import urllib.parse

class WebFinder:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def search(self, query, num_results=5):
        """
        Searches the web using DuckDuckGo (scraping for free use).
        """
        encoded_query = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for i, result in enumerate(soup.find_all('div', class_='result')):
                if i >= num_results:
                    break
                
                title_tag = result.find('a', class_='result__a')
                snippet_tag = result.find('a', class_='result__snippet')
                
                if title_tag:
                    title = title_tag.get_text()
                    link = title_tag['href']
                    snippet = snippet_tag.get_text() if snippet_tag else ""
                    
                    results.append({
                        'title': title,
                        'link': link,
                        'snippet': snippet
                    })
            
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def deep_search(self, query):
        """
        Finds results and scrapes the top one for full context.
        """
        results = self.search(query, num_results=3)
        if not results:
            return "No results found."
        
        # In a real app, you might want to return all results or 
        # let the user choose which one to scrape.
        return results
