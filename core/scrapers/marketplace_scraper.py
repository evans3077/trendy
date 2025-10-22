# core/scrapers/marketplace_scraper.py
from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime

class MarketplaceScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        # Enhanced headers to mimic real browsers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Marketplace configurations
        self.marketplaces = {
            # International
            'amazon': {
                'base_url': 'https://www.amazon.com/s?k={query}',
                'selectors': {
                    'products': '[data-component-type="s-search-result"]',
                    'title': 'h2 a span',
                    'price': '.a-price .a-offscreen',
                    'rating': '.a-icon-alt',
                    'reviews': '.a-size-base.s-underline-text',
                    'link': 'h2 a'
                }
            },
            'walmart': {
                'base_url': 'https://www.walmart.com/search/?q={query}',
                'selectors': {
                    'products': '[data-item-id]',
                    'title': '[data-automation-id="product-title"]',
                    'price': '[data-automation-id="product-price"]',
                    'rating': '.w_iUH7',
                    'reviews': '.w_iUH7 + span',
                    'link': 'a[data-automation-id="product-title"]'
                }
            },
            'alibaba': {
                'base_url': 'https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText={query}',
                'selectors': {
                    'products': '.organic-offer-wrapper',
                    'title': '.elements-title-normal__content',
                    'price': '.elements-offer-price-normal__price',
                    'rating': '.seb-supplier-review-gallery-test__score',
                    'reviews': '.seb-supplier-review-gallery-test__review-count',
                    'link': '.organic-gallery-offer__img-wrapper a'
                }
            },
            
            # African Marketplaces
            'jumia': {
                'base_url': 'https://www.jumia.co.ke/catalog/?q={query}',
                'selectors': {
                    'products': '.prd',
                    'title': '.name',
                    'price': '.prc',
                    'rating': '.rev',
                    'reviews': '.stars._s',
                    'link': '.core'
                }
            },
            'kilimall': {
                'base_url': 'https://www.kilimall.co.ke/new/commoditysearch?q={query}',
                'selectors': {
                    'products': '.list-good-item',
                    'title': '.title',
                    'price': '.price',
                    'rating': '.score',
                    'reviews': '.comments',
                    'link': '.good-title'
                }
            },
            'konga': {
                'base_url': 'https://www.konga.com/catalogsearch/result/?q={query}',
                'selectors': {
                    'products': '.product-card',
                    'title': '.name',
                    'price': '.price',
                    'rating': '.rating',
                    'reviews': '.count',
                    'link': '.product-link'
                }
            },
            
            # Kenyan Local
            'masoko': {
                'base_url': 'https://masoko.com/catalogsearch/result/?q={query}',
                'selectors': {
                    'products': '.product-item',
                    'title': '.product-item-link',
                    'price': '.price',
                    'rating': '.rating-result',
                    'reviews': '.review-count',
                    'link': '.product-item-photo'
                }
            },
            
            # Additional International
            'ebay': {
                'base_url': 'https://www.ebay.com/sch/i.html?_nkw={query}',
                'selectors': {
                    'products': '.s-item',
                    'title': '.s-item__title',
                    'price': '.s-item__price',
                    'rating': '.x-star-rating',
                    'reviews': '.s-item__reviews',
                    'link': '.s-item__link'
                }
            },
            'aliExpress': {
                'base_url': 'https://www.aliexpress.com/wholesale?SearchText={query}',
                'selectors': {
                    'products': '.product-container',
                    'title': '.item-title',
                    'price': '.price-current',
                    'rating': '.rating-value',
                    'reviews': '.rating-num',
                    'link': '.item-title'
                }
            },
            'target': {
                'base_url': 'https://www.target.com/s?searchTerm={query}',
                'selectors': {
                    'products': '[data-test="product-details"]',
                    'title': '[data-test="product-title"]',
                    'price': '[data-test="product-price"]',
                    'rating': '[data-test="rating"]',
                    'reviews': '[data-test="rating-count"]',
                    'link': '[data-test="product-title"] a'
                }
            },
            'takealot': {
                'base_url': 'https://www.takealot.com/all?q={query}',
                'selectors': {
                    'products': '.product-anchor',
                    'title': '.product-title',
                    'price': '.price',
                    'rating': '.rating-stars',
                    'reviews': '.rating-count',
                    'link': '.product-anchor'
                }
            },
            'copia': {
                'base_url': 'https://www.copia.co.ke/catalogsearch/result/?q={query}',
                'selectors': {
                    'products': '.product-item',
                    'title': '.product-item-name',
                    'price': '.price',
                    'rating': '.rating',
                    'reviews': '.review-count',
                    'link': '.product-item-link'
                }
            }
        }
        
        # Enhanced niche mapping for marketplaces
        self.niche_categories = {
            'technology': [
                'laptop', 'smartphone', 'tablet', 'computer', 'phone', 'mobile',
                'electronics', 'gadget', 'tech', 'wireless', 'bluetooth', 'headphones',
                'camera', 'tv', 'television', 'monitor', 'printer', 'router',
                'smart watch', 'fitness tracker', 'earphones', 'speaker', 'charger',
                'power bank', 'cable', 'adapter', 'memory card', 'hard drive', 'ssd',
                'processor', 'ram', 'graphics card', 'motherboard'
            ],
            'solar energy': [
                'solar panel', 'solar battery', 'solar inverter', 'solar charger',
                'solar light', 'solar lamp', 'solar power', 'solar kit', 'solar system',
                'solar generator', 'solar water heater', 'solar fan', 'solar pump',
                'solar controller', 'solar module', 'photovoltaic', 'solar home system',
                'solar street light', 'solar garden light', 'solar security light'
            ],
            'mobile technology': [
                'smartphone', 'iphone', 'android phone', 'mobile phone', 'cell phone',
                '5g phone', '4g phone', 'smart phone', 'phone case', 'screen protector',
                'phone charger', 'mobile charger', 'power bank', 'phone holder',
                'phone stand', 'mobile accessory', 'earphones', 'wireless earbuds',
                'phone cable', 'phone adapter', 'mobile gadget'
            ],
            'agriculture': [
                'tractor', 'plough', 'harvester', 'irrigation', 'watering can',
                'garden tool', 'farming tool', 'agricultural equipment', 'seeds',
                'fertilizer', 'pesticide', 'herbicide', 'garden hose', 'sprinkler',
                'wheelbarrow', 'shovel', 'rake', 'hoe', 'pruner', 'lawn mower',
                'greenhouse', 'farming machine', 'agriculture tool'
            ],
            'home appliances': [
                'refrigerator', 'washing machine', 'microwave', 'oven', 'cooker',
                'blender', 'toaster', 'kettle', 'iron', 'vacuum cleaner', 'fan',
                'air conditioner', 'heater', 'water dispenser', 'food processor',
                'mixer', 'coffee maker', 'juicer', 'electric stove', 'dishwasher'
            ],
            'fashion': [
                'dress', 'shirt', 'trouser', 'jeans', 'shoes', 'sneakers', 'bag',
                'watch', 'jewelry', 'perfume', 'cosmetic', 'makeup', 'skincare',
                'handbag', 'backpack', 'wallet', 'belt', 'hat', 'cap', 'sunglasses',
                'jewelry', 'necklace', 'bracelet', 'earring', 'ring'
            ],
            'health beauty': [
                'vitamin', 'supplement', 'protein', 'fitness', 'gym equipment',
                'yoga mat', 'dumbbell', 'skincare', 'moisturizer', 'serum',
                'face mask', 'body lotion', 'hair care', 'shampoo', 'conditioner',
                'hair oil', 'perfume', 'deodorant', 'makeup', 'lipstick', 'mascara',
                'foundation', 'eyeshadow', 'nail polish'
            ],
            'sports outdoors': [
                'football', 'basketball', 'tennis', 'running shoes', 'sports wear',
                'fitness tracker', 'yoga mat', 'dumbbell', 'treadmill', 'bicycle',
                'camping gear', 'fishing rod', 'hiking boot', 'tent', 'sleeping bag',
                'backpack', 'water bottle', 'sports equipment'
            ],
            'baby kids': [
                'diaper', 'baby food', 'stroller', 'car seat', 'baby clothes',
                'toy', 'educational toy', 'baby carrier', 'baby bottle', 'pacifier',
                'baby monitor', 'crib', 'high chair', 'baby bath', 'baby skincare'
            ],
            'automotive': [
                'car accessory', 'tire', 'battery', 'oil', 'filter', 'tool kit',
                'car charger', 'phone holder', 'car seat cover', 'steering wheel cover',
                'car mat', 'wiper blade', 'headlight', 'brake pad', 'spark plug'
            ],
            'office supplies': [
                'laptop', 'printer', 'scanner', 'desk', 'chair', 'stationery',
                'pen', 'notebook', 'file', 'folder', 'staple', 'paper', 'envelope',
                'calculator', 'whiteboard', 'marker', 'organizer'
            ],
            'garden patio': [
                'gardening tool', 'lawn mower', 'plant pot', 'soil', 'fertilizer',
                'watering can', 'garden hose', 'sprinkler', 'outdoor furniture',
                'grill', 'bbq', 'patio set', 'garden light', 'plant seeds'
            ]
        }
    
    def scrape(self, niche, limit=15):
        """Scrape all marketplaces for a specific niche"""
        print(f"🛒 Scraping marketplaces for '{niche}'...")
        
        all_products = []
        successful_marketplaces = 0
        
        # Get search terms for this niche
        search_terms = self.get_search_terms(niche)
        
        for marketplace_name, config in self.marketplaces.items():
            if len(all_products) >= limit:
                break
                
            try:
                products = self.scrape_marketplace(marketplace_name, search_terms, 
                                                 limit - len(all_products))
                if products:
                    all_products.extend(products)
                    successful_marketplaces += 1
                    print(f"  ✅ {marketplace_name}: {len(products)} products")
                else:
                    print(f"  ❌ {marketplace_name}: 0 products")
                
                # Respectful delay
                time.sleep(1)
                
            except Exception as e:
                print(f"  💥 {marketplace_name}: Error - {e}")
                continue
        
        print(f"📦 Total: {len(all_products)} products from {successful_marketplaces} marketplaces")
        return all_products[:limit]
    
    def get_search_terms(self, niche):
        """Get relevant search terms for a niche"""
        niche_lower = niche.lower()
        
        # Find matching niche and return its categories
        for niche_key, categories in self.niche_categories.items():
            if niche_key in niche_lower or niche_lower in niche_key:
                return categories[:3]  # Return top 3 categories
        
        # Default to niche name if no match
        return [niche_lower]
    
    def scrape_marketplace(self, marketplace_name, search_terms, limit):
        """Scrape a specific marketplace"""
        config = self.marketplaces[marketplace_name]
        products = []
        
        for search_term in search_terms:
            if len(products) >= limit:
                break
                
            try:
                url = config['base_url'].format(query=search_term.replace(' ', '+'))
                response = self.make_request(url)
                
                if not response:
                    continue
                
                # Check for blocking
                if self.is_blocked(response, marketplace_name):
                    print(f"    ⚠️ {marketplace_name}: Blocked, using mock data")
                    return self.get_mock_products(marketplace_name, search_terms, limit)
                
                soup = BeautifulSoup(response.content, 'html.parser')
                marketplace_products = self.parse_products(soup, config['selectors'], 
                                                         marketplace_name, search_term)
                
                products.extend(marketplace_products)
                
            except Exception as e:
                print(f"    💥 {marketplace_name} search failed for '{search_term}': {e}")
                continue
        
        return products[:limit]
    
    def parse_products(self, soup, selectors, marketplace_name, search_term):
        """Parse products from marketplace HTML"""
        products = []
        
        product_elements = soup.select(selectors['products'])
        
        for element in product_elements:
            try:
                product_data = self.extract_product_data(element, selectors, marketplace_name)
                if product_data:
                    product_data['search_term'] = search_term
                    product_data['marketplace'] = marketplace_name
                    products.append(product_data)
            except Exception as e:
                continue
        
        return products
    
    def extract_product_data(self, element, selectors, marketplace_name):
        """Extract individual product data"""
        try:
            # Title
            title_elem = element.select_one(selectors['title'])
            title = title_elem.get_text(strip=True) if title_elem else None
            
            if not title or len(title) < 3:
                return None
            
            # Price
            price_elem = element.select_one(selectors['price'])
            price = price_elem.get_text(strip=True) if price_elem else 'Price not available'
            
            # Rating
            rating_elem = element.select_one(selectors['rating'])
            rating = rating_elem.get_text(strip=True) if rating_elem else 'No rating'
            
            # Reviews
            reviews_elem = element.select_one(selectors['reviews'])
            reviews = reviews_elem.get_text(strip=True) if reviews_elem else 'No reviews'
            
            # Link
            link_elem = element.select_one(selectors['link'])
            link = link_elem.get('href') if link_elem else None
            if link and not link.startswith('http'):
                link = self.make_absolute_url(link, marketplace_name)
            
            return {
                'title': title,
                'price': price,
                'rating': rating,
                'reviews': reviews,
                'link': link,
                'marketplace': marketplace_name,
                'timestamp': datetime.now().isoformat(),
                'source': 'marketplace'
            }
            
        except Exception as e:
            return None
    
    def make_absolute_url(self, relative_url, marketplace_name):
        """Convert relative URL to absolute"""
        base_urls = {
            'amazon': 'https://www.amazon.com',
            'walmart': 'https://www.walmart.com',
            'alibaba': 'https://www.alibaba.com',
            'jumia': 'https://www.jumia.co.ke',
            'kilimall': 'https://www.kilimall.co.ke',
            'konga': 'https://www.konga.com',
            'masoko': 'https://masoko.com',
            'ebay': 'https://www.ebay.com',
            'aliExpress': 'https://www.aliexpress.com',
            'target': 'https://www.target.com',
            'takealot': 'https://www.takealot.com',
            'copia': 'https://www.copia.co.ke'
        }
        
        base_url = base_urls.get(marketplace_name, '')
        if relative_url.startswith('/'):
            return base_url + relative_url
        return relative_url
    
    def is_blocked(self, response, marketplace_name):
        """Check if we're being blocked"""
        text = response.text.lower()
        block_indicators = ['captcha', 'robot', 'access denied', 'blocked', 'security check']
        return any(indicator in text for indicator in block_indicators)
    
    def get_mock_products(self, marketplace_name, search_terms, limit):
        """Return mock products when scraping is blocked"""
        mock_products = []
        
        for search_term in search_terms[:2]:
            for i in range(2):  # 2 mock products per search term
                mock_products.append({
                    'title': f'Popular {search_term} on {marketplace_name}',
                    'price': '$' + str(round(20 + i * 30, 2)),
                    'rating': f'{4.0 + i * 0.3} out of 5',
                    'reviews': f'{50 + i * 30} reviews',
                    'link': f'https://{marketplace_name}.com/product/{search_term.replace(" ", "-")}',
                    'marketplace': marketplace_name,
                    'search_term': search_term,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'marketplace_mock'
                })
        
        return mock_products[:limit]