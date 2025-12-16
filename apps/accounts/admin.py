from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, LoginHistory


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Custom admin for User model"""
    list_display = ('email', 'username', 'role', 'is_verified', 'created_at')
    list_filter = ('role', 'is_verified', 'is_staff', 'created_at')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    readonly_fields = ('id', 'created_at', 'updated_at', 'last_login_ip')
    fieldsets = (
        (_('Information personnelle'), {
            'fields': ('id', 'email', 'username', 'first_name', 'last_name', 'phone', 'avatar', 'bio')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'role')
        }),
        (_('Sécurité'), {
            'fields': ('is_verified', 'failed_login_attempts', 'account_locked_until', 'two_factor_enabled', 'last_login_ip')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    ordering = ('-created_at',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile model"""
    list_display = ('user', 'department', 'organization', 'reputation_score')
    list_filter = ('department', 'created_at')
    search_fields = ('user__email', 'organization')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    """Admin for LoginHistory model"""
    list_display = ('user', 'ip_address', 'success', 'timestamp')
    list_filter = ('success', 'timestamp')
    search_fields = ('user__email', 'ip_address')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
