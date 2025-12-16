"""
Dashboard URLs - Admin & Statistics
"""
from django.urls import path
from . import views
from . import admin_views


app_name = 'dashboard'

urlpatterns = [
    # Main Dashboard
    path('', views.dashboard_view, name='index'),
    path('reports/', views.reports_dashboard_view, name='reports'),
    path('users/', views.users_dashboard_view, name='users'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('activity/', views.activity_log_view, name='activity'),
    path('notifications/', views.notifications_view, name='notifications'),
    
    # Admin - User Management
    path('admin/users/', admin_views.users_list_view, name='users-list'),
    path('admin/users/<str:user_id>/', admin_views.user_detail_view, name='user-detail'),
    path('admin/users/<str:user_id>/edit/', admin_views.user_edit_view, name='user-edit'),
    path('admin/users/<str:user_id>/toggle-status/', admin_views.user_toggle_status_view, name='user-toggle-status'),
    path('admin/users/<str:user_id>/unlock/', admin_views.user_unlock_view, name='user-unlock'),
    path('admin/users/<str:user_id>/delete/', admin_views.user_delete_view, name='user-delete'),
    
    # Admin - Report Management
    path('admin/reports/', admin_views.reports_admin_view, name='reports-admin'),
    path('admin/reports/<str:report_id>/manage/', admin_views.report_manage_view, name='report-manage'),
    path('admin/reports/<str:report_id>/delete/', admin_views.report_delete_view, name='report-delete'),
    
    # Moderator - Moderation Queue
    path('moderator/queue/', admin_views.moderator_queue_view, name='moderator-queue'),
    path('moderator/reports/<str:report_id>/', admin_views.moderate_report_view, name='moderate-report'),
    
    # Audit & Notifications
    path('audit-log/', admin_views.audit_log_view, name='audit-log'),
    path('admin-notifications/', admin_views.admin_notifications_view, name='admin-notifications'),
    
    # API
    path('api/stats/', views.StatsAPIView.as_view(), name='api_stats'),
    path('api/chart-data/', views.ChartDataAPIView.as_view(), name='api_chart_data'),
    path('api/recent-reports/', views.RecentReportsAPIView.as_view(), name='api_recent_reports'),
    path('api/user-activity/', views.UserActivityAPIView.as_view(), name='api_user_activity'),
]
