# core/admin.py
from django.contrib import admin
from .models import Niche, DataSource, ScrapedData, Trend, AdKeyword

@admin.register(Niche)
class NicheAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']

@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'niche', 'is_active']
    list_filter = ['name', 'is_active']

@admin.register(ScrapedData)
class ScrapedDataAdmin(admin.ModelAdmin):
    list_display = ['niche', 'source', 'sentiment', 'created_at']
    list_filter = ['source', 'niche', 'created_at']
    readonly_fields = ['created_at']

@admin.register(Trend)
class TrendAdmin(admin.ModelAdmin):
    list_display = ['niche', 'keywords_preview', 'sentiment', 'score', 'source', 'created_at']
    list_filter = ['niche', 'source', 'created_at']
    
    def keywords_preview(self, obj):
        return ', '.join(obj.keywords[:3]) if obj.keywords else 'None'
    keywords_preview.short_description = 'Keywords'

@admin.register(AdKeyword)
class AdKeywordAdmin(admin.ModelAdmin):
    list_display = ['keyword', 'trend', 'performance_score', 'source']
    list_filter = ['source', 'trend__niche']
    search_fields = ['keyword']