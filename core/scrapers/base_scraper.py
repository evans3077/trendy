# core/scrapers/base_scraper.py
import abc
import requests
import time
from datetime import datetime
from typing import List, Dict, Any

class BaseScraper(abc.ABC):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    @abc.abstractmethod
    def scrape(self, niche: str, **kwargs) -> List[Dict[str, Any]]:
        """Main scraping method to be implemented by each scraper"""
        pass
    
    def make_request(self, url, method='GET', **kwargs):
        """Safe request method with error handling"""
        try:
            response = self.session.request(method, url, timeout=10, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Request failed for {url}: {e}")
            return None
    
    def rate_limit(self, delay=1):
        """Respect rate limiting"""
        time.sleep(delay)