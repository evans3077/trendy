# core/scrapers/master_scraper.py
from .google_trends_scraper import GoogleTrendsScraper
from .amazon_scraper import AmazonScraper
# from .twitter_scraper import TwitterScraper
# from .reddit_scraper import RedditScraper
from .news_scraper import NewsScraper
from .marketplace_scraper import MarketplaceScraper 
from .ai_marketplace_scraper import AIMarketplaceScraper

class MasterScraper:
    def __init__(self):
        self.scrapers = {
            'google_trends': GoogleTrendsScraper(),
            'amazon': AmazonScraper(),
            # 'twitter': TwitterScraper(),
            # 'reddit': RedditScraper(),
            'news': NewsScraper(),
            'ai_marketplace': AIMarketplaceScraper(),  
        }
    
    # In core/scrapers/master_scraper.py - update the news scraper usage
    def scrape_all_sources(self, niche, active_sources=None):
        """Scrape all active sources for a niche"""
        if active_sources is None:
            active_sources = ['news', 'ai_marketplace']  
        
        all_data = []
        
        for source_name in active_sources:
            if source_name in self.scrapers:
                print(f"Scraping {source_name} for {niche}...")
                
                try:
                    if source_name == 'news':
                        # Use enhanced news scraping
                        data = self.scrapers[source_name].scrape_with_fallback(niche, limit=15)
                    else:
                        data = self.scrapers[source_name].scrape(niche)
                    
                    all_data.extend(data)
                    
                    print(f"✅ {source_name}: Found {len(data)} items")
                    
                except Exception as e:
                    print(f"❌ {source_name} failed: {e}")
        
        return all_data


    def scrape_multiple_niches(self, niches, active_sources=None):
        """Scrape multiple niches"""
        all_niche_data = {}
        
        for niche in niches:
            print(f"\n🎯 Scraping niche: {niche}")
            niche_data = self.scrape_all_sources(niche, active_sources)
            all_niche_data[niche] = niche_data
        
        return all_niche_data




    def __init__(self):
        self.scrapers = {
            'news': NewsScraper(),
            'ai_marketplace': AIMarketplaceScraper(),  # NEW AI Scraper
            'google_trends': GoogleTrendsScraper(),
        }
    
    def scrape_all_sources(self, niche, active_sources=None):
        if active_sources is None:
            active_sources = ['news', 'ai_marketplace']  # Focus on working sources
        
        all_data = []
        
        for source_name in active_sources:
            if source_name in self.scrapers:
                print(f"Scraping {source_name} for {niche}...")
                
                try:
                    data = self.scrapers[source_name].scrape(niche)
                    all_data.extend(data)
                    print(f"✅ {source_name}: Found {len(data)} items")
                    
                except Exception as e:
                    print(f"❌ {source_name} failed: {e}")
        
        return all_data