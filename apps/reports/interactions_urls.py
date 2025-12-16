"""
URLs pour Notifications & Interactions AJAX
Endpoint URL mapping pour likes, commentaires, notifications
"""
from django.urls import path
from apps.reports import interactions_views

app_name = 'interactions'

urlpatterns = [
    # ==================== NOTIFICATIONS ====================
    
    # Page principale notifications
    path('notifications/', interactions_views.notifications_view, name='notifications_list'),
    
    # API endpoints
    path('api/notifications/unread/', interactions_views.get_unread_count, name='get_unread_count'),
    path('api/notifications/<str:notification_id>/read/', interactions_views.mark_notification_read, name='mark_notification_read'),
    path('api/notifications/read-all/', interactions_views.mark_all_notifications_read, name='mark_all_read'),
    
    # ==================== LIKES ====================
    
    path('api/reports/<str:report_id>/like/', interactions_views.toggle_like, name='toggle_like'),
    path('api/reports/<str:report_id>/likes/', interactions_views.get_likes_data, name='get_likes_data'),
    
    # ==================== COMMENTAIRES ====================
    
    path('api/reports/<str:report_id>/comments/', interactions_views.get_comments, name='get_comments'),
    path('api/reports/<str:report_id>/comment/', interactions_views.add_comment, name='add_comment'),
]
