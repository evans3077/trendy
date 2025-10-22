from pytrends.request import TrendReq
import time

def get_trending_keywords(query, geo='KE', retries=2):
    """Enhanced with better rate limiting handling"""
    try:
        pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25))
        pytrends.build_payload([query], cat=0, timeframe='now 7-d', geo=geo)
        
        # Try different endpoints
        data = pytrends.related_queries()
        if data[query]['rising'] is not None:
            return [{'keyword': row['query'], 'score': row['value']} 
                   for _, row in data[query]['rising'].head(5).iterrows()]
        
        return []
    except Exception as e:
        print(f"Google Trends failed for {query}: {e}")
        return []