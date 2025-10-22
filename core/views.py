from django.shortcuts import render
from .models import Trend, AdKeyword

def dashboard(request):
    return render(request, 'dashboard.html', {
        'trends': Trend.objects.order_by('-created_at')[:20],
        'keywords': AdKeyword.objects.order_by('-performance_score')[:20],
    })
