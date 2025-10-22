# core/tasks.py
from celery import shared_task
from .models import Niche, ScrapedData, Trend, AdKeyword, DataSource
from .scrapers.master_scraper import MasterScraper
from .services.ml_services import extract_keywords, analyze_sentiment
from datetime import datetime
import json

@shared_task
def run_multi_source_scraping():
    """Run scraping from all sources for all niches"""
    niches = Niche.objects.all()
    master_scraper = MasterScraper()
    
    print(f"Starting multi-source scraping for {niches.count()} niches")
    
    for niche in niches:
        try:
            print(f"\n🔍 Processing niche: {niche.name}")
            
            # Scrape all sources
            scraped_data = master_scraper.scrape_all_sources(niche.name)
            
            # Save raw data
            for data_item in scraped_data:
                scraped_record = ScrapedData.objects.create(
                    niche=niche,
                    source=DataSource.objects.get_or_create(
                        name=data_item.get('source', 'unknown'),
                        defaults={'is_active': True}
                    )[0],
                    raw_data=data_item,
                    cleaned_data=clean_data(data_item)
                )
                
                # Extract keywords and sentiment
                text = extract_text_from_data(data_item)
                if text:
                    keywords = extract_keywords(text)
                    sentiment = analyze_sentiment(text)
                    
                    scraped_record.keywords = keywords
                    scraped_record.sentiment = sentiment
                    scraped_record.save()
                    
                    # Create trend if significant
                    if len(keywords) > 0 and sentiment > 0.1:
                        create_trend_from_scraped_data(niche, keywords, sentiment, data_item)
            
            print(f"✅ Completed {niche.name}: {len(scraped_data)} items")
            
        except Exception as e:
            print(f"❌ Failed {niche.name}: {e}")
    
    return f"Scraping completed for {niches.count()} niches"

def extract_text_from_data(data_item):
    """Extract text content from various data formats"""
    if 'title' in data_item:
        return data_item['title']
    elif 'text' in data_item:
        return data_item['text']
    elif 'keyword' in data_item:
        return data_item['keyword']
    return ""

def clean_data(data_item):
    """Clean and standardize scraped data"""
    cleaned = {k: v for k, v in data_item.items() if not k.startswith('_')}
    return cleaned

def create_trend_from_scraped_data(niche, keywords, sentiment, source_data):
    """Create Trend record from scraped data"""
    # Calculate score based on source and engagement
    score = calculate_trend_score(source_data)
    
    trend = Trend.objects.create(
        niche=niche,
        keywords=keywords,
        sentiment=sentiment,
        score=score,
        source=source_data.get('source', 'multiple')
    )
    
    # Create ad keywords
    for keyword in keywords[:5]:  # Limit to top 5 keywords
        AdKeyword.objects.create(
            trend=trend,
            keyword=keyword,
            performance_score=sentiment * score,
            source=source_data.get('source', 'unknown')
        )
    
    return trend

def calculate_trend_score(source_data):
    """Calculate trend score based on source-specific metrics"""
    source = source_data.get('source', '')
    score = 1.0  # Default score
    
    if source == 'google_trends':
        score = source_data.get('score', 50) / 100  # Normalize
    elif source == 'twitter':
        engagement = source_data.get('engagement', 0)
        score = min(engagement / 1000, 1.0)  # Cap at 1.0
    elif source == 'reddit':
        score = source_data.get('score', 0) / 1000  # Normalize
    elif source == 'amazon':
        review_count = source_data.get('review_count', '0')
        try:
            reviews = int(review_count.replace(',', ''))
            score = min(reviews / 1000, 1.0)
        except:
            score = 0.1
    
    return score

# Keep your existing task for backward compatibility
@shared_task
def run_scraping_and_analysis():
    """Legacy task - now uses multi-source approach"""
    return run_multi_source_scraping()