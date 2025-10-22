from celery import shared_task
from .models import Niche, Trend, AdKeyword
from .services.google_trends import get_trending_keywords
from .services.ml_services import extract_keywords, analyze_sentiment
from .services.kenya_news import scrape_kenya_news

@shared_task
def run_scraping_and_analysis():
    for niche in Niche.objects.all():
        # Try Google Trends first
        trends = get_trending_keywords(niche.name, geo='KE')
        if not trends:
            print(f"No Google Trends data for {niche.name} — using Kenyan news instead.")
            headlines = scrape_kenya_news()
            for title in headlines:
                kws = extract_keywords(title)
                s, c = analyze_sentiment(title)
                trend_obj = Trend.objects.create(
                    niche=niche, keywords=kws, sentiment=s, score=1.0
                )
                for kw in kws:
                    AdKeyword.objects.create(
                        trend=trend_obj, keyword=kw, performance_score=s * 1.0
                    )
        else:
            for t in trends:
                kws = extract_keywords(t['keyword'])
                s = analyze_sentiment(t['keyword'])
                score = float(t['score'])
                trend_obj = Trend.objects.create(
                    niche=niche, keywords=kws, sentiment=s, score=score
                )
                for kw in kws:
                    AdKeyword.objects.create(
                        trend=trend_obj, keyword=kw, performance_score=s * score
                    )
    return True
