"""
CivicFix Project - Main URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


urlpatterns = [
    # Admin Interface
    path('admin/', admin.site.urls),
    
    # Authentication & Accounts
    path('accounts/', include('apps.accounts.urls')),
    
    # Reports & Issues
    path('reports/', include('apps.reports.urls')),
    
    # Interactions (Likes, Comments, Notifications)
    path('', include('apps.reports.interactions_urls')),
    
    # Dashboard & Analytics
    path('dashboard/', include('apps.dashboard.urls')),
    
    # API Root
    path('api-auth/', include('rest_framework.urls')),
    
    # Home Page
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

