# core/scrapers/reddit_scraper.py
from .base_scraper import BaseScraper
import praw, os 

class RedditScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.reddit = self.authenticate()
    
    def authenticate(self):
        """Authenticate with Reddit API"""
        try:
            reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent="trendy_scraper_v1.0"
            )
            return reddit
        except Exception as e:
            print(f"Reddit authentication failed: {e}")
            return None
    
    def scrape(self, niche, limit=10, subreddit='all'):
        """Scrape Reddit for trending posts in niche"""
        if not self.reddit:
            return []
        
        try:
            trends = []
            
            # Search for posts in the niche
            for submission in self.reddit.subreddit(subreddit).search(niche, limit=limit):
                trends.append({
                    'title': submission.title,
                    'score': submission.score,
                    'upvote_ratio': submission.upvote_ratio,
                    'num_comments': submission.num_comments,
                    'created_utc': submission.created_utc,
                    'url': submission.url,
                    'source': 'reddit',
                    'niche': niche,
                    'subreddit': subreddit
                })
            
            return trends
            
        except Exception as e:
            print(f"Reddit scraping failed for {niche}: {e}")
            return []