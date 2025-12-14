"""
Web crawler module for extracting website content
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import time
import config
from utils import is_valid_url, clean_text

class WebsiteCrawler:
    """Crawls websites and extracts content using BFS"""
    
    def __init__(self, base_url, max_depth=None, max_pages=None):
        self.base_url = base_url
        self.max_depth = max_depth or config.MAX_CRAWL_DEPTH
        self.max_pages = max_pages or config.MAX_PAGES
        self.visited = set()
        self.domain = urlparse(base_url).netloc
        
    def extract_content(self, soup):
        """Extract clean text content from HTML"""
        # Remove unwanted elements
        for element in soup(config.SKIP_ELEMENTS):
            element.decompose()
        
        # Get title
        title = soup.title.string.strip() if soup.title and soup.title.string else "Untitled"
        
        # Get headings
        headings = []
        for tag in ['h1', 'h2', 'h3']:
            for h in soup.find_all(tag):
                text = h.get_text().strip()
                if text and len(text) > 3:
                    headings.append(text)
        
        # Get main text
        text = soup.get_text(separator=' ', strip=True)
        text = clean_text(text)
        
        return {
            'title': title,
            'headings': headings[:10],
            'content': text[:50000]  # Limit content length
        }
    
    def crawl(self, progress_callback=None):
        """Crawl website using BFS algorithm"""
        queue = deque([(self.base_url, 0)])
        pages_content = []
        
        while queue and len(pages_content) < self.max_pages:
            url, depth = queue.popleft()
            
            if url in self.visited or depth > self.max_depth:
                continue
            
            try:
                if progress_callback:
                    progress_callback(f"📄 Page {len(pages_content)+1}/{self.max_pages}: {url[:60]}...")
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=config.CRAWL_TIMEOUT)
                response.raise_for_status()
                
                # Only process HTML
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' not in content_type:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                content = self.extract_content(soup)
                
                # Only store pages with substantial content
                if len(content['content']) > 200:
                    pages_content.append({
                        'url': url,
                        'depth': depth,
                        **content
                    })
                
                self.visited.add(url)
                
                # Find links for next level
                if depth < self.max_depth and len(pages_content) < self.max_pages:
                    for link in soup.find_all('a', href=True)[:50]:
                        next_url = urljoin(url, link['href'])
                        next_url = next_url.split('#')[0]  # Remove fragments
                        
                        if is_valid_url(next_url, self.domain) and next_url not in self.visited:
                            queue.append((next_url, depth + 1))
                
                time.sleep(config.CRAWL_DELAY)
                
            except Exception as e:
                if progress_callback:
                    progress_callback(f"⚠️ Skipped: {url[:40]}... ({str(e)[:30]})")
                continue
        
        return pages_content