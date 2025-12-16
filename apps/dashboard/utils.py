"""
Dashboard Utilities - Helper functions for admin/moderator operations
"""
from .models import AuditLog, AdminNotification
from django.contrib.auth import get_user_model

User = get_user_model()


def log_admin_action(actor, action, description, target_user=None, target_report=None,
                     old_value=None, new_value=None, ip_address=None, user_agent=None):
    """
    Log an admin or moderator action for audit trail
    
    Args:
        actor: User performing the action
        action: Action code (from AuditLog.ACTION_CHOICES)
        description: Human-readable description of the action
        target_user: User being acted upon (optional)
        target_report: Report being acted upon (optional)
        old_value: Previous value (for change tracking)
        new_value: New value (for change tracking)
        ip_address: Client IP address
        user_agent: Client user agent
    """
    return AuditLog.log_action(
        actor=actor,
        action=action,
        description=description,
        target_user=target_user,
        target_report=target_report,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
        user_agent=user_agent
    )


def notify_admin(title, message, notification_type, recipient=None, related_report=None, related_user=None):
    """
    Send notification to admin/moderator
    
    Args:
        title: Notification title
        message: Notification message
        notification_type: Type of notification
        recipient: Specific user to notify (optional, defaults to all admins)
        related_report: Related report (optional)
        related_user: Related user (optional)
    """
    recipients = [recipient] if recipient else User.objects.filter(role__in=['admin', 'moderator'])
    
    for user in recipients:
        AdminNotification.objects.create(
            recipient=user,
            notification_type=notification_type,
            title=title,
            message=message,
            related_report=related_report,
            related_user=related_user
        )


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """
    Get client user agent from request
    """
    return request.META.get('HTTP_USER_AGENT', '')


def ban_user(user, reason, admin):
    """
    Ban a user from the platform
    """
    user.is_active = False
    user.save()
    
    log_admin_action(
        actor=admin,
        action='user_deactivated',
        description=f"Utilisateur banni. Raison: {reason}",
        target_user=user
    )
    
    notify_admin(
        title="Utilisateur banni",
        message=f"L'utilisateur {user.email} a été banni.\nRaison: {reason}",
        notification_type='system_alert',
        related_user=user
    )


def promote_user_to_moderator(user, admin):
    """
    Promote a regular user to moderator
    """
    old_role = user.role
    user.role = 'moderator'
    user.save()
    
    log_admin_action(
        actor=admin,
        action='role_changed',
        description=f"Utilisateur promu modérateur",
        target_user=user,
        old_value=old_role,
        new_value='moderator'
    )


def demote_moderator_to_user(user, admin):
    """
    Demote a moderator back to regular user
    """
    old_role = user.role
    user.role = 'user'
    user.save()
    
    log_admin_action(
        actor=admin,
        action='role_changed',
        description=f"Modérateur rétrogradé en utilisateur",
        target_user=user,
        old_value=old_role,
        new_value='user'
    )


def get_admin_stats():
    """
    Get key statistics for admin dashboard
    """
    from apps.reports.models import Report
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    last_7_days = timezone.now() - timedelta(days=7)
    
    return {
        'total_users': User.objects.count(),
        'total_admins': User.objects.filter(role='admin').count(),
        'total_moderators': User.objects.filter(role='moderator').count(),
        'inactive_users': User.objects.filter(is_active=False).count(),
        'locked_users': User.objects.filter(
            account_locked_until__isnull=False,
            account_locked_until__gt=timezone.now()
        ).count(),
        
        'total_reports': Report.objects.count(),
        'open_reports': Report.objects.filter(status='open').count(),
        'in_progress': Report.objects.filter(status='in_progress').count(),
        'resolved_reports': Report.objects.filter(status='resolved').count(),
        'pending_reports': Report.objects.filter(status__in=['open', 'in_progress']).count(),
        
        'today_reports': Report.objects.filter(created_at__date=today).count(),
        'today_resolved': Report.objects.filter(resolved_at__date=today).count(),
        'week_reports': Report.objects.filter(created_at__gte=last_7_days).count(),
        
        'recent_audit_logs': AuditLog.objects.all()[:10],
    }
