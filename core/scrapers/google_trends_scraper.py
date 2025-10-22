# core/scrapers/google_trends_scraper.py
from .base_scraper import BaseScraper
from pytrends.request import TrendReq
import time, datetime 

class GoogleTrendsScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
    
    def scrape(self, niche, geo='KE', timeframe='now 7-d'):
        """Scrape Google Trends for a specific niche"""
        try:
            # Build payload
            self.pytrends.build_payload(
                [niche], 
                cat=0, 
                timeframe=timeframe, 
                geo=geo, 
                gprop=''
            )
            
            # Get related queries
            related_queries = self.pytrends.related_queries()
            rising_queries = related_queries[niche]['rising']
            
            trends = []
            if rising_queries is not None:
                for _, row in rising_queries.head(10).iterrows():
                    trends.append({
                        'keyword': row['query'],
                        'score': int(row['value']),
                        'type': 'rising',
                        'source': 'google_trends',
                        'niche': niche,
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Get interest over time
            interest_over_time = self.pytrends.interest_over_time()
            if not interest_over_time.empty:
                current_interest = interest_over_time[niche].iloc[-1]
                trends.append({
                    'keyword': niche,
                    'score': int(current_interest),
                    'type': 'interest',
                    'source': 'google_trends',
                    'niche': niche,
                    'timestamp': datetime.now().isoformat()
                })
            
            return trends
            
        except Exception as e:
            print(f"Google Trends scraping failed for {niche}: {e}")
            return []