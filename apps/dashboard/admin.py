from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import DashboardStats, UserActivityLog, SystemNotification


@admin.register(DashboardStats)
class DashboardStatsAdmin(admin.ModelAdmin):
    """Admin for DashboardStats model"""
    list_display = ('date', 'total_reports', 'total_users', 'reports_created_today', 'reports_resolved_today')
    list_filter = ('date',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
    
    fieldsets = (
        (_('Date'), {
            'fields': ('date',)
        }),
        (_('Statistiques Rapports'), {
            'fields': ('total_reports', 'open_reports', 'in_progress_reports', 'resolved_reports', 'closed_reports')
        }),
        (_('Statistiques Utilisateurs'), {
            'fields': ('total_users', 'new_users', 'active_users')
        }),
        (_('Statistiques du Jour'), {
            'fields': ('reports_created_today', 'reports_resolved_today')
        }),
        (_('Distribution par Catégorie'), {
            'fields': ('category_infrastructure', 'category_environment', 'category_health', 'category_education', 'category_transport')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    """Admin for UserActivityLog model"""
    list_display = ('user', 'activity_type', 'ip_address', 'timestamp')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('user__email', 'description', 'ip_address')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'


@admin.register(SystemNotification)
class SystemNotificationAdmin(admin.ModelAdmin):
    """Admin for SystemNotification model"""
    list_display = ('title', 'notification_type', 'is_active', 'created_at')
    list_filter = ('notification_type', 'is_active', 'created_at')
    search_fields = ('title', 'message')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('target_users',)
