from django.db import models

class Niche(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class DataSource(models.Model):
    name = models.CharField(max_length=120)
    url = models.URLField(blank=True)
    data_type = models.CharField(max_length=50, default='web')
    def __str__(self):
        return self.name

class Trend(models.Model):
    niche = models.ForeignKey(Niche, on_delete=models.CASCADE)
    keywords = models.JSONField(default=list)
    sentiment = models.FloatField(default=0.0)
    score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

class AdKeyword(models.Model):
    trend = models.ForeignKey(Trend, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=200)
    performance_score = models.FloatField(default=0.0)
