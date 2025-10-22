
# core/models.py
from django.db import models

class Niche(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class DataSource(models.Model):
    SOURCE_CHOICES = [
        ('google_trends', 'Google Trends'),
        ('amazon', 'Amazon Products'),
        ('twitter', 'Twitter Trends'),
        ('reddit', 'Reddit'),
        ('news', 'News'),
        ('youtube', 'YouTube'),
    ]
    
    name = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    niche = models.ForeignKey(Niche, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(default=dict)  # API keys, URLs, etc.
    
    def __str__(self):
        return f"{self.get_name_display()} - {self.niche.name if self.niche else 'Global'}"

class ScrapedData(models.Model):
    source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    niche = models.ForeignKey(Niche, on_delete=models.CASCADE)
    raw_data = models.JSONField()
    cleaned_data = models.JSONField(blank=True, null=True)
    keywords = models.JSONField(default=list)
    sentiment = models.FloatField(default=0.0)
    engagement_score = models.FloatField(default=0.0)  # Likes, shares, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['niche', 'created_at']),
            models.Index(fields=['source', 'created_at']),
        ]

class Trend(models.Model):
    niche = models.ForeignKey(Niche, on_delete=models.CASCADE)
    keywords = models.JSONField(default=list)
    sentiment = models.FloatField(default=0.0)
    score = models.FloatField(default=0.0)
    source = models.CharField(max_length=50, default='multiple')
    created_at = models.DateTimeField(auto_now_add=True)

class AdKeyword(models.Model):
    trend = models.ForeignKey(Trend, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=200)
    performance_score = models.FloatField(default=0.0)
    source = models.CharField(max_length=50)