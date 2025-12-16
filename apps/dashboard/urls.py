"""
Dashboard URLs - Admin & Statistics
"""
from django.urls import path
from . import views


app_name = 'dashboard'

urlpatterns = [
    # Web Views
    path('', views.dashboard_view, name='index'),
    path('reports/', views.reports_dashboard_view, name='reports'),
    path('users/', views.users_dashboard_view, name='users'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('activity/', views.activity_log_view, name='activity'),
    path('notifications/', views.notifications_view, name='notifications'),
    
    # API
    path('api/stats/', views.StatsAPIView.as_view(), name='api_stats'),
    path('api/chart-data/', views.ChartDataAPIView.as_view(), name='api_chart_data'),
    path('api/recent-reports/', views.RecentReportsAPIView.as_view(), name='api_recent_reports'),
    path('api/user-activity/', views.UserActivityAPIView.as_view(), name='api_user_activity'),
]
