# run_scraping.py - Run the actual Celery task
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trendy_project.settings')
django.setup()

from core.tasks import run_multi_source_scraping

print("🚀 Starting scraping task...")
result = run_multi_source_scraping.delay()

print(f"✅ Task started!")
print(f"📋 Task ID: {result.id}")
print("🔍 Check Celery worker terminal for progress...")
print("💡 Make sure Celery is running: celery -A trendy_project worker --pool=solo")