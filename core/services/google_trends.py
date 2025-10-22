from pytrends.request import TrendReq
import time
import random

def get_trending_keywords(niche, geo='KE', timeframe='now 7-d', retries=5):
    """
    Scrape trending data from Google Trends for a given niche (default: Kenya).
    """
    for attempt in range(retries):
        try:
            pytrends = TrendReq(hl='en-GB', tz=180)  # East Africa timezone
            pytrends.build_payload([niche], geo=geo, timeframe=timeframe)
            df = pytrends.interest_over_time()
            if df.empty:
                return []
            vals = df[niche].dropna()
            top = vals.nlargest(min(5, len(vals)))
            return [
                {'keyword': niche, 'date': str(idx.date()), 'score': float(v)}
                for idx, v in top.items()
            ]
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(random.randint(20, 40))
    return []
