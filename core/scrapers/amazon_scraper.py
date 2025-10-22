# core/scrapers/amazon_scraper.py 
from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import random
import time

class AmazonScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        # Better headers to mimic real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })
    
    def scrape(self, niche, limit=5):
        """Scrape Amazon with better anti-bot handling"""
        try:
            search_term = niche.replace(' ', '+')
            url = f"https://www.amazon.com/s?k={search_term}"
            
            print(f"    Trying Amazon search: {niche}")
            response = self.make_request(url)
            
            if not response:
                print("    Amazon: Request failed")
                return []
            
            # Check if we got blocked
            if "captcha" in response.text.lower() or "robot" in response.text.lower():
                print("    Amazon: Blocked by CAPTCHA")
                return self.get_mock_amazon_data(niche, limit)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Try multiple selectors for product elements
            selectors = [
                '[data-component-type="s-search-result"]',
                '.s-result-item',
                '.s-main-slot .s-result-item'
            ]
            
            for selector in selectors:
                product_elements = soup.select(selector)
                if product_elements:
                    break
            
            for element in product_elements[:limit]:
                product_data = self.extract_product_data(element)
                if product_data:
                    products.append(product_data)
            
            # If no products found, return mock data for testing
            if not products:
                print("    Amazon: No products found, using mock data")
                return self.get_mock_amazon_data(niche, limit)
            
            print(f"    Amazon: Found {len(products)} products")
            return products
            
        except Exception as e:
            print(f"    Amazon scraping failed: {e}")
            return self.get_mock_amazon_data(niche, limit)
    
    def get_mock_amazon_data(self, niche, limit):
        """Return mock Amazon data for testing"""
        mock_products = [
            {
                'title': f'Popular {niche} product with great reviews',
                'price': '$99.99',
                'ratings': '4.5',
                'review_count': '1250',
                'source': 'amazon_mock',
                'timestamp': '2025-10-22T13:40:00'
            },
            {
                'title': f'Best selling {niche} item 2025',
                'price': '$149.99', 
                'ratings': '4.3',
                'review_count': '890',
                'source': 'amazon_mock',
                'timestamp': '2025-10-22T13:40:00'
            }
        ]
        return mock_products[:limit]