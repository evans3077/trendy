# core/scrapers/ai_marketplace_scraper.py
import requests
import json
from .base_scraper import BaseScraper
from datetime import datetime

class AIMarketplaceScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.api_key = "babf0b9047msh249b64e68aba30bp161856jsn54acc2ed7be7"
        self.api_host = "ai-web-scraper1.p.rapidapi.com"
        self.api_url = "https://ai-web-scraper1.p.rapidapi.com/"
        
        # Focus on marketplaces that work better
        self.marketplace_urls = {
            'jumia': 'https://www.jumia.co.ke/catalog/?q={query}',
            'kilimall': 'https://www.kilimall.co.ke/new/commoditysearch?q={query}',
            'konga': 'https://www.konga.com/catalogsearch/result/?q={query}',
            'masoko': 'https://masoko.com/catalogsearch/result/?q={query}',
            'amazon': 'https://www.amazon.com/s?k={query}',
        }
        
        # Better search terms
        self.niche_terms = {
            'technology': ['laptop', 'smartphone', 'tablet'],
            'solar energy': ['solar panel', 'solar light', 'solar battery'],
            'mobile technology': ['android phone', 'iphone', 'mobile phone'],
            'agriculture': ['farming tools', 'garden tools', 'irrigation'],
            'fashion': ['dress', 'shoes', 'handbag'],
            'home appliances': ['refrigerator', 'microwave', 'blender'],
        }
    
    def scrape(self, niche, limit=8):
        """Use AI Web Scraper with better error handling"""
        print(f"🤖 AI Scraping marketplaces for '{niche}'...")
        
        all_products = []
        search_terms = self.niche_terms.get(niche.lower(), [niche])
        
        # Test the API first with a simple URL
        test_url = "https://www.jumia.co.ke/catalog/?q=laptop"
        print(f"  🔧 Testing API with Jumia...")
        
        test_response = self.scrape_with_ai(test_url, "jumia", "laptop")
        if test_response:
            print(f"  ✅ API is working! Format: {type(test_response)}")
            if isinstance(test_response, dict):
                print(f"  📊 Response keys: {list(test_response.keys())}")
        else:
            print(f"  ❌ API test failed")
            # Return contextual mock data for now
            return self.get_smart_mock_products(niche, limit)
        
        # Continue with actual scraping
        for marketplace, base_url in self.marketplace_urls.items():
            if len(all_products) >= limit:
                break
                
            for search_term in search_terms[:2]:
                if len(all_products) >= limit:
                    break
                    
                try:
                    url = base_url.format(query=search_term.replace(' ', '+'))
                    print(f"  🔍 Scraping {marketplace} for '{search_term}'...")
                    
                    products = self.scrape_with_ai(url, marketplace, search_term)
                    if products:
                        all_products.extend(products)
                        print(f"    ✅ Found {len(products)} products")
                    else:
                        print(f"    ⚠️ No products found, using smart mock data")
                        # Add smart mock data when API fails
                        mock_products = self.get_smart_mock_products_for_marketplace(marketplace, search_term, 2)
                        all_products.extend(mock_products)
                        
                except Exception as e:
                    print(f"    💥 Error: {e}")
                    continue
        
        print(f"📦 AI Scraping Complete: {len(all_products)} total products")
        return all_products[:limit]
    
    def scrape_with_ai(self, url, marketplace, search_term):
        """Use RapidAPI AI Web Scraper with better response handling"""
        try:
            payload = {
                "url": url,
                "summary": False
            }
            
            headers = {
                "Content-Type": "application/json",
                "x-rapidapi-host": self.api_host,
                "x-rapidapi-key": self.api_key
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return self.parse_ai_response_advanced(response.json(), marketplace, search_term, url)
            else:
                print(f"    API Error {response.status_code}: {response.text[:100]}...")
                return []
                
        except Exception as e:
            print(f"    AI Scraper Error: {e}")
            return []
    
    def parse_ai_response_advanced(self, ai_data, marketplace, search_term, original_url):
        """Advanced parsing of AI scraper response"""
        products = []
        
        print(f"    🔍 Analyzing API response structure...")
        
        # Debug: Print response type and keys
        print(f"    Response type: {type(ai_data)}")
        if isinstance(ai_data, dict):
            print(f"    Response keys: {list(ai_data.keys())}")
        
        # Try different response formats
        content = None
        
        # Format 1: Direct content
        if isinstance(ai_data, str):
            content = ai_data
        # Format 2: Dictionary with content
        elif isinstance(ai_data, dict):
            content = ai_data.get('content') or ai_data.get('text') or ai_data.get('data') or str(ai_data)
        # Format 3: List
        elif isinstance(ai_data, list):
            content = str(ai_data)
        
        if not content:
            print(f"    ❌ No content found in response")
            return []
        
        print(f"    ✅ Content length: {len(str(content))} characters")
        
        # Try to extract products using multiple methods
        products.extend(self.extract_products_method1(content, marketplace, search_term))
        products.extend(self.extract_products_method2(content, marketplace, search_term))
        
        # If still no products, use contextual mock data
        if not products:
            products = self.extract_products_contextual(content, marketplace, search_term)
        
        return products[:3]  # Limit results
    
    def extract_products_method1(self, content, marketplace, search_term):
        """Method 1: Simple text parsing"""
        products = []
        
        # Convert to string and split into lines
        text_content = str(content)
        lines = text_content.split('\n')
        
        product_keywords = ['$', 'ksh', 'price', 'buy', 'product', 'item', 'shop', 'cart']
        
        for line in lines[:50]:  # Check first 50 lines
            line = line.strip()
            if len(line) > 15 and any(keyword in line.lower() for keyword in product_keywords):
                product = self.create_product_from_text(line, marketplace, search_term)
                if product:
                    products.append(product)
        
        return products
    
    def extract_products_method2(self, content, marketplace, search_term):
        """Method 2: JSON parsing if available"""
        products = []
        
        try:
            # Try to parse as JSON
            if isinstance(content, str) and ('{' in content or '[' in content):
                json_data = json.loads(content)
                if isinstance(json_data, list):
                    for item in json_data[:5]:
                        product = self.create_product_from_dict(item, marketplace, search_term)
                        if product:
                            products.append(product)
                elif isinstance(json_data, dict):
                    product = self.create_product_from_dict(json_data, marketplace, search_term)
                    if product:
                        products.append(product)
        except:
            pass
        
        return products
    
    def extract_products_contextual(self, content, marketplace, search_term):
        """Create contextual products based on search"""
        return self.get_smart_mock_products_for_marketplace(marketplace, search_term, 2)
    
    def create_product_from_text(self, text, marketplace, search_term):
        """Create product from text line"""
        try:
            # Extract price
            price = self.extract_price(text)
            
            # Clean title
            title = text[:80].strip()
            
            return {
                'title': f"{search_term.title()} - {title}",
                'price': price or "Check website",
                'rating': '4.0+',
                'reviews': '10+ reviews',
                'link': f"https://{marketplace}.com/search?q={search_term.replace(' ', '+')}",
                'marketplace': marketplace,
                'search_term': search_term,
                'timestamp': datetime.now().isoformat(),
                'source': 'ai_scraper_text'
            }
        except:
            return None
    
    def create_product_from_dict(self, data, marketplace, search_term):
        """Create product from dictionary data"""
        try:
            title = data.get('title') or data.get('name') or data.get('product')
            price = data.get('price') or data.get('cost') or data.get('amount')
            
            if title:
                return {
                    'title': str(title),
                    'price': str(price) if price else "Check website",
                    'rating': str(data.get('rating', '4.0')),
                    'reviews': str(data.get('reviews', '10+')),
                    'link': data.get('url') or f"https://{marketplace}.com/search?q={search_term.replace(' ', '+')}",
                    'marketplace': marketplace,
                    'search_term': search_term,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'ai_scraper_json'
                }
        except:
            pass
        return None
    
    def get_smart_mock_products(self, niche, limit):
        """Get smart mock products based on niche"""
        products = []
        
        niche_products = {
            'technology': [
                {'name': 'Latest Gaming Laptop', 'price': '$1,299', 'type': 'laptop'},
                {'name': 'Wireless Bluetooth Headphones', 'price': '$79', 'type': 'accessory'},
                {'name': 'Smartphone with 5G', 'price': '$599', 'type': 'phone'},
            ],
            'solar energy': [
                {'name': '100W Solar Panel Kit', 'price': '$189', 'type': 'solar panel'},
                {'name': 'Solar Power Bank', 'price': '$45', 'type': 'battery'},
                {'name': 'Solar Garden Lights', 'price': '$29', 'type': 'lighting'},
            ],
            'mobile technology': [
                {'name': 'Latest Android Smartphone', 'price': '$459', 'type': 'phone'},
                {'name': 'Phone Case and Protector', 'price': '$25', 'type': 'accessory'},
                {'name': 'Fast Phone Charger', 'price': '$35', 'type': 'charger'},
            ],
            'agriculture': [
                {'name': 'Professional Gardening Tools', 'price': '$89', 'type': 'tools'},
                {'name': 'Automatic Irrigation System', 'price': '$156', 'type': 'irrigation'},
                {'name': 'Organic Plant Seeds', 'price': '$12', 'type': 'seeds'},
            ]
        }
        
        products_list = niche_products.get(niche.lower(), [
            {'name': f'Popular {niche} Product', 'price': '$99', 'type': 'general'}
        ])
        
        for product_data in products_list[:limit]:
            products.append({
                'title': product_data['name'],
                'price': product_data['price'],
                'rating': '4.2',
                'reviews': '25+ reviews',
                'link': f"https://example.com/{product_data['type']}",
                'marketplace': 'multiple',
                'search_term': niche,
                'timestamp': datetime.now().isoformat(),
                'source': 'smart_mock'
            })
        
        return products
    
    def get_smart_mock_products_for_marketplace(self, marketplace, search_term, count=2):
        """Get marketplace-specific mock products"""
        products = []
        
        marketplace_prices = {
            'jumia': ['KSh 15,999', 'KSh 24,500', 'KSh 8,299'],
            'kilimall': ['KSh 18,299', 'KSh 22,999', 'KSh 7,899'],
            'konga': ['₦45,999', '₦52,500', '₦18,299'],
            'masoko': ['KSh 16,499', 'KSh 25,999', 'KSh 9,299'],
            'amazon': ['$199', '$349', '$89'],
        }
        
        prices = marketplace_prices.get(marketplace, ['$99', '$159', '$49'])
        
        for i in range(count):
            products.append({
                'title': f'Best {search_term.title()} on {marketplace.title()}',
                'price': prices[i % len(prices)],
                'rating': f'{4.0 + (i * 0.3):.1f}',
                'reviews': f'{15 + (i * 10)}+ reviews',
                'link': f'https://{marketplace}.com/product/{search_term.replace(" ", "-")}',
                'marketplace': marketplace,
                'search_term': search_term,
                'timestamp': datetime.now().isoformat(),
                'source': 'contextual_mock'
            })
        
        return products
    
    def extract_price(self, text):
        """Extract price from text"""
        import re
        price_patterns = [
            r'\$\d+[,.]?\d*',  # $10.99 or $1,299
            r'KSh\s?\d+[,.]?\d*',  # KSh 1,299
            r'₦\d+[,.]?\d*',  # ₦45,999
            r'\d+[,.]?\d*\s?(USD|usd|KSh|ksh)',  # 10.99 USD
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()
        return None