# core/scrapers/news_scraper.py
from .base_scraper import BaseScraper
import feedparser
from bs4 import BeautifulSoup
import time
from datetime import datetime
import re

class NewsScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        # Expanded news sources - 20+ reliable feeds
        self.feeds = [
            # Kenyan News Sources
            "https://www.standardmedia.co.ke/rss/headlines.php",
            "https://www.standardmedia.co.ke/rss/kenya.php",
            "https://www.standardmedia.co.ke/rss/business.php",
            "https://www.standardmedia.co.ke/rss/technology.php",
            "https://nation.africa/kenya/rss",
            "https://www.the-star.co.ke/news/rss",
            "https://www.the-star.co.ke/business/rss",
            "https://www.businessdailyafrica.com/latest/rss",
            
            # African News
            "https://www.africanews.com/feed/rss",
            "https://allafrica.com/tools/headlines/africa/africa/index.rss",
            
            # International News with Africa Sections
            "https://feeds.bbci.co.uk/news/world/africa/rss.xml",
            "https://feeds.bbci.co.uk/news/business/rss.xml",
            "https://feeds.bbci.co.uk/news/technology/rss.xml",
            "https://rss.cnn.com/rss/edition_africa.rss",
            "https://rss.cnn.com/rss/edition_technology.rss",
            "https://feeds.reuters.com/reuters/AfricaLatestNews",
            "https://feeds.reuters.com/reuters/technologyNews",
            "https://feeds.reuters.com/reuters/businessNews",
            
            # Technology Focused
            "https://feeds.bbci.co.uk/news/technology/rss.xml",
            "https://rss.cnn.com/rss/edition_technology.rss", 
            "https://feeds.reuters.com/reuters/technologyNews",
            "https://www.techweez.com/feed/",
            "https://techcabal.com/feed/",
            
            # Business & Economy
            "https://feeds.bbci.co.uk/news/business/rss.xml",
            "https://rss.cnn.com/rss/money_news_international.rss",
            "https://feeds.reuters.com/reuters/businessNews",
            "https://www.bloomberg.com/africa/rss.xml",
            
            # Agriculture & Environment
            "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
            "https://www.fao.org/feeds/rss/africanews/en/",
            "https://www.agriculture.com/rss",
            
            # General News Aggregators
            "https://feeds.bbci.co.uk/news/rss.xml",
            "https://rss.cnn.com/rss/edition.rss",
            "https://feeds.reuters.com/reuters/topNews",
        ]
        
        # Enhanced niche keyword mapping for better accuracy
        self.niche_keywords = {
            'technology': [
                # Core tech terms
                'tech', 'technology', 'digital', 'ai', 'artificial intelligence', 'machine learning',
                'software', 'computer', 'internet', 'web', 'online', 'mobile', 'app', 'application',
                'data', 'cyber', 'cybersecurity', 'innovation', 'startup', 'programming', 'coding',
                'developer', 'IT', 'information technology', 'cloud', 'cloud computing', 'aws', 'azure',
                # Devices & hardware
                'smartphone', 'iphone', 'android', 'laptop', 'computer', 'device', 'gadget',
                '5g', 'wifi', 'wireless', 'bluetooth', 'processor', 'chip', 'semiconductor',
                # Companies & platforms
                'google', 'microsoft', 'apple', 'amazon', 'facebook', 'meta', 'twitter', 'x',
                'instagram', 'whatsapp', 'tiktok', 'netflix', 'youtube', 'spotify',
                # Specific technologies
                'blockchain', 'crypto', 'bitcoin', 'nft', 'metaverse', 'vr', 'ar', 'virtual reality',
                'iot', 'internet of things', 'robotics', 'drone', 'automation', 'api', 'algorithm',
                'database', 'server', 'network', 'bandwidth', 'streaming', 'download', 'upload',
                'ecommerce', 'digital marketing', 'social media', 'influencer', 'content creator'
            ],
            
            'solar energy': [
                # Core solar terms
                'solar', 'solar energy', 'solar power', 'solar panel', 'photovoltaic', 'pv',
                'renewable energy', 'clean energy', 'green energy', 'sustainable energy',
                'solar installation', 'solar system', 'solar farm', 'solar project',
                # Components
                'solar panel', 'solar cell', 'inverter', 'battery storage', 'solar battery',
                'charge controller', 'solar inverter', 'solar module',
                # Applications
                'solar heating', 'solar water heating', 'solar lighting', 'solar pump',
                'off-grid solar', 'on-grid solar', 'solar home system',
                # Industry terms
                'solar industry', 'solar market', 'solar investment', 'solar financing',
                'solar policy', 'solar tariff', 'net metering', 'feed-in tariff',
                # Companies & brands
                'tesla solar', 'sunpower', 'first solar', 'canadian solar', 'jinkosolar',
                'longi solar', 'trina solar', 'ja solar',
                # Related concepts
                'climate change', 'carbon emissions', 'energy transition', 'decarbonization',
                'energy efficiency', 'energy conservation', 'smart grid', 'microgrid'
            ],
            
            'mobile technology': [
                # Core mobile terms
                'mobile', 'smartphone', 'cell phone', 'mobile phone', 'handset', 'device',
                'android', 'iphone', 'ios', 'mobile os', 'mobile operating system',
                # Features & specs
                '5g', '4g', 'lte', 'wireless', 'cellular', 'mobile data', 'mobile network',
                'camera', 'display', 'screen', 'battery', 'processor', 'ram', 'storage',
                'biometric', 'fingerprint', 'face recognition', 'touchscreen',
                # Apps & services
                'mobile app', 'app store', 'play store', 'mobile game', 'mobile banking',
                'mobile payment', 'mobile wallet', 'm-pesa', 'mobile money',
                'streaming', 'mobile video', 'mobile music', 'podcast',
                # Companies
                'samsung', 'apple', 'huawei', 'xiaomi', 'oppo', 'vivo', 'nokia',
                'tecno', 'infinix', 'itel', 'oneplus', 'google pixel',
                # Trends
                'foldable phone', '5g phone', 'smartphone camera', 'mobile photography',
                'mobile gaming', 'esports mobile', 'mobile esports', 'cloud gaming'
            ],
            
            'agriculture': [
                # Core agriculture terms
                'agriculture', 'farming', 'farm', 'farmer', 'crop', 'livestock', 'harvest',
                'irrigation', 'fertilizer', 'pesticide', 'herbicide', 'soil', 'land',
                'agricultural', 'agribusiness', 'agri-tech', 'precision agriculture',
                # Crops
                'maize', 'corn', 'wheat', 'rice', 'beans', 'coffee', 'tea', 'sugarcane',
                'cotton', 'tobacco', 'horticulture', 'flowers', 'vegetables', 'fruits',
                'banana', 'avocado', 'mango', 'pineapple', 'citrus', 'potato', 'tomato',
                # Livestock
                'cattle', 'dairy', 'milk', 'beef', 'poultry', 'chicken', 'eggs', 'pork',
                'goat', 'sheep', 'fish farming', 'aquaculture', 'beekeeping', 'honey',
                # Technology in agriculture
                'agri-tech', 'digital farming', 'smart farming', 'drones in agriculture',
                'satellite farming', 'soil sensors', 'weather monitoring', 'crop monitoring',
                # Sustainability
                'organic farming', 'sustainable agriculture', 'climate-smart agriculture',
                'conservation agriculture', 'regenerative agriculture', 'soil conservation',
                # Markets & economy
                'food security', 'food prices', 'agricultural exports', 'farm inputs',
                'subsidy', 'agricultural policy', 'land reform', 'food production'
            ],
            
            'business': [
                # Core business terms
                'business', 'company', 'corporation', 'enterprise', 'firm', 'startup',
                'entrepreneur', 'entrepreneurship', 'investment', 'finance', 'economy',
                'market', 'trade', 'commerce', 'industry', 'sector', 'corporate',
                # Financial terms
                'profit', 'revenue', 'sales', 'income', 'loss', 'bankruptcy', 'merger',
                'acquisition', 'takeover', 'ipo', 'stock', 'share', 'dividend', 'bond',
                'currency', 'forex', 'exchange rate', 'inflation', 'deflation', 'recession',
                # Business operations
                'management', 'leadership', 'CEO', 'CFO', 'board', 'shareholder', 'stakeholder',
                'marketing', 'advertising', 'brand', 'customer', 'client', 'consumer',
                'supply chain', 'logistics', 'manufacturing', 'production', 'distribution',
                # Sectors
                'banking', 'insurance', 'real estate', 'construction', 'transport', 'tourism',
                'hospitality', 'retail', 'wholesale', 'ecommerce', 'export', 'import',
                # Kenyan business context
                'nairobi securities exchange', 'NSE', 'central bank of kenya', 'CBK',
                'kenya revenue authority', 'KRA', 'betting', 'sports betting', 'safaricom',
                'equity bank', 'kcb', 'cooperative bank'
            ]
        }
    
    def scrape(self, niche, limit=20):
        """Scrape all news sources with enhanced relevance filtering"""
        print(f"    📰 Scraping news for '{niche}' from {len(self.feeds)} sources...")
        
        all_articles = []
        successful_feeds = 0
        
        for feed_url in self.feeds:
            if len(all_articles) >= limit:
                break
                
            try:
                articles = self.parse_feed(feed_url, niche, limit - len(all_articles))
                if articles:
                    all_articles.extend(articles)
                    successful_feeds += 1
                    print(f"      ✅ {self.get_feed_name(feed_url)}: {len(articles)} relevant articles")
                else:
                    print(f"      ❌ {self.get_feed_name(feed_url)}: 0 relevant articles")
                
                # Respectful delay between requests
                time.sleep(0.5)
                
            except Exception as e:
                print(f"      💥 {self.get_feed_name(feed_url)}: Error - {e}")
                continue
        
        print(f"    📊 Total: {len(all_articles)} articles from {successful_feeds} sources")
        return all_articles[:limit]
    
    def parse_feed(self, feed_url, niche, limit):
        """Parse individual RSS feed with strict relevance checking"""
        try:
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                return []
            
            articles = []
            
            for entry in feed.entries[:limit * 2]:  # Check more entries for relevance
                try:
                    # Strict relevance checking
                    if self.is_highly_relevant(entry, niche):
                        articles.append({
                            'title': entry.title,
                            'link': entry.link,
                            'published': entry.get('published', ''),
                            'summary': entry.get('summary', entry.get('description', '')),
                            'source': 'news',
                            'niche': niche,
                            'feed_url': feed_url,
                            'feed_name': self.get_feed_name(feed_url),
                            'timestamp': datetime.now().isoformat(),
                            'relevance_score': self.calculate_relevance_score(entry, niche)
                        })
                except Exception as e:
                    continue
                
                if len(articles) >= limit:
                    break
            
            return articles
            
        except Exception as e:
            return []
    
    def is_highly_relevant(self, entry, niche):
        """Strict relevance checking using niche-specific keywords"""
        text = f"{entry.title} {entry.get('summary', '')}".lower()
        niche_lower = niche.lower()
        
        # Get keywords for this niche
        keywords = []
        for key, key_keywords in self.niche_keywords.items():
            if key in niche_lower or niche_lower in key:
                keywords.extend(key_keywords)
                break
        
        # If no specific niche match, use broad matching
        if not keywords:
            keywords = [niche_lower]
        
        # Count keyword matches
        matches = 0
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
                matches += 1
                if matches >= 2:  # Require at least 2 keyword matches
                    return True
        
        return matches >= 2
    
    def calculate_relevance_score(self, entry, niche):
        """Calculate how relevant an article is to the niche (0-100)"""
        text = f"{entry.title} {entry.get('summary', '')}".lower()
        niche_lower = niche.lower()
        
        # Get keywords for this niche
        keywords = []
        for key, key_keywords in self.niche_keywords.items():
            if key in niche_lower or niche_lower in key:
                keywords.extend(key_keywords)
                break
        
        if not keywords:
            keywords = [niche_lower]
        
        # Calculate score based on keyword matches
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += 5  # Base points for each keyword match
                # Bonus points for exact word matches
                if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
                    score += 10
        
        return min(score, 100)  # Cap at 100
    
    def get_feed_name(self, feed_url):
        """Extract feed name from URL for better logging"""
        domain = feed_url.split('//')[-1].split('/')[0]
        return domain.replace('www.', '').replace('.com', '').replace('.co.ke', '')
    
    def scrape_with_fallback(self, niche, limit=15):
        """Scrape with HTML fallback for feeds that don't work"""
        # First try RSS feeds
        articles = self.scrape(niche, limit)
        
        # If not enough articles, try direct website scraping
        if len(articles) < limit // 2:
            print(f"    🔄 Not enough RSS results, trying direct scraping...")
            fallback_articles = self.scrape_direct_websites(niche, limit - len(articles))
            articles.extend(fallback_articles)
        
        # Sort by relevance score and return
        articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return articles[:limit]
    
    def scrape_direct_websites(self, niche, limit):
        """Direct website scraping as fallback"""
        articles = []
        
        # Kenyan news websites
        websites = [
            {
                'url': 'https://www.nation.africa/kenya',
                'selectors': ['h3 a', 'h2 a', '.title a', '.headline a']
            },
            {
                'url': 'https://www.the-star.co.ke/news/',
                'selectors': ['.article-title', 'h4 a', 'h2 a']
            },
            {
                'url': 'https://www.businessdailyafrica.com/',
                'selectors': ['.story-link', 'h3 a', 'h2 a']
            }
        ]
        
        for site in websites:
            if len(articles) >= limit:
                break
                
            try:
                site_articles = self.scrape_website(site['url'], site['selectors'], niche, limit - len(articles))
                articles.extend(site_articles)
            except Exception as e:
                print(f"      💥 Direct scrape failed for {site['url']}: {e}")
        
        return articles
    
    def scrape_website(self, url, selectors, niche, limit):
        """Scrape a specific website for headlines"""
        try:
            response = self.make_request(url)
            if not response:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements[:limit * 2]:
                    title = element.get_text(strip=True)
                    link = element.get('href', '')
                    
                    if title and len(title) > 10 and self.is_highly_relevant({'title': title}, niche):
                        # Make absolute URL if relative
                        if link.startswith('/'):
                            link = url + link
                        
                        articles.append({
                            'title': title,
                            'link': link,
                            'published': '',
                            'summary': '',
                            'source': 'news_direct',
                            'niche': niche,
                            'feed_url': url,
                            'feed_name': url.split('//')[-1].split('/')[0],
                            'timestamp': datetime.now().isoformat(),
                            'relevance_score': self.calculate_relevance_score({'title': title}, niche)
                        })
                        
                        if len(articles) >= limit:
                            break
                
                if len(articles) >= limit:
                    break
            
            return articles
            
        except Exception as e:
            return []