# core/scrapers/twitter_scraper.py
from .base_scraper import BaseScraper
import tweepy
import os, datetime

class TwitterScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        # You'll need to set these as environment variables
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.client = self.authenticate()
    
    def authenticate(self):
        """Authenticate with Twitter API"""
        if not self.api_key or not self.api_secret:
            print("Twitter API credentials not found")
            return None
        
        try:
            client = tweepy.Client(bearer_token=self.api_key)
            return client
        except Exception as e:
            print(f"Twitter authentication failed: {e}")
            return None
    
    def scrape(self, niche, limit=10):
        """Scrape Twitter for trending topics in niche"""
        if not self.client:
            return []
        
        try:
            # Search for tweets in the niche
            query = f"{niche} -is:retweet"  # Exclude retweets
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=limit,
                tweet_fields=['created_at', 'public_metrics']
            )
            
            trends = []
            if tweets.data:
                for tweet in tweets.data:
                    trends.append({
                        'text': tweet.text,
                        'engagement': tweet.public_metrics['like_count'] + tweet.public_metrics['retweet_count'],
                        'created_at': tweet.created_at.isoformat(),
                        'source': 'twitter',
                        'niche': niche
                    })
            
            return trends
            
        except Exception as e:
            print(f"Twitter scraping failed for {niche}: {e}")
            return []