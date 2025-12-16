"""
Dashboard Views - Admin & Statistics
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.db.models import Count, Q
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
import json

from apps.reports.models import Report, ReportComment, ReportHistory
from apps.accounts.decorators import admin_or_moderator_required
from .models import DashboardStats, UserActivityLog, SystemNotification


User = get_user_model()


@login_required
@admin_or_moderator_required
def dashboard_view(request):
    """Main dashboard view with key metrics"""
    # Get stats for the current date
    today = timezone.now().date()
    stats, created = DashboardStats.objects.get_or_create(date=today)
    
    # Calculate current stats
    stats.total_reports = Report.objects.count()
    stats.open_reports = Report.objects.filter(status='open').count()
    stats.in_progress_reports = Report.objects.filter(status='in_progress').count()
    stats.resolved_reports = Report.objects.filter(status='resolved').count()
    stats.closed_reports = Report.objects.filter(status='closed').count()
    
    stats.total_users = User.objects.count()
    stats.new_users = User.objects.filter(
        created_at__date=today
    ).count()
    stats.active_users = User.objects.filter(
        last_login__date=today
    ).count()
    
    stats.reports_created_today = Report.objects.filter(
        created_at__date=today
    ).count()
    stats.reports_resolved_today = Report.objects.filter(
        resolved_at__date=today
    ).count()
    
    # Category distribution
    stats.category_infrastructure = Report.objects.filter(category='infrastructure').count()
    stats.category_environment = Report.objects.filter(category='environment').count()
    stats.category_health = Report.objects.filter(category='health').count()
    stats.category_education = Report.objects.filter(category='education').count()
    stats.category_transport = Report.objects.filter(category='transport').count()
    
    stats.save()
    
    # Recent reports
    recent_reports = Report.objects.select_related('author').order_by('-created_at')[:5]
    
    # Pending reports for assignment
    pending_reports = Report.objects.filter(
        assigned_to__isnull=True,
        status__in=['open', 'in_progress']
    ).count()
    
    context = {
        'stats': stats,
        'recent_reports': recent_reports,
        'pending_reports': pending_reports,
    }
    
    return render(request, 'dashboard/index.html', context)


@login_required
@admin_or_moderator_required
def reports_dashboard_view(request):
    """Reports management dashboard"""
    reports = Report.objects.select_related('author', 'assigned_to').all()
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        reports = reports.filter(status=status_filter)
    
    # Group by status for stats
    status_stats = {
        'open': Report.objects.filter(status='open').count(),
        'in_progress': Report.objects.filter(status='in_progress').count(),
        'resolved': Report.objects.filter(status='resolved').count(),
        'closed': Report.objects.filter(status='closed').count(),
        'rejected': Report.objects.filter(status='rejected').count(),
    }
    
    context = {
        'reports': reports[:20],  # Limit to 20 for display
        'status_stats': status_stats,
        'status_filter': status_filter,
        'total_reports': Report.objects.count(),
    }
    
    return render(request, 'dashboard/reports.html', context)


@login_required
@admin_or_moderator_required
def users_dashboard_view(request):
    """Users management dashboard"""
    users = User.objects.all().order_by('-created_at')
    
    # User stats
    user_stats = {
        'total': User.objects.count(),
        'admin': User.objects.filter(role='admin').count(),
        'moderator': User.objects.filter(role='moderator').count(),
        'users': User.objects.filter(role='user').count(),
        'verified': User.objects.filter(is_verified=True).count(),
    }
    
    context = {
        'users': users[:20],
        'user_stats': user_stats,
        'total_users': user_stats['total'],
    }
    
    return render(request, 'dashboard/users.html', context)


@login_required
@admin_or_moderator_required
def statistics_view(request):
    """Advanced statistics and analytics"""
    # Get last 30 days of stats
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    stats_data = DashboardStats.objects.filter(
        date__gte=thirty_days_ago
    ).order_by('date')
    
    # Reports trend
    reports_per_day = []
    for stat in stats_data:
        reports_per_day.append({
            'date': stat.date.strftime('%Y-%m-%d'),
            'count': stat.reports_created_today
        })
    
    # Category distribution
    categories = {
        'Infrastructure': Report.objects.filter(category='infrastructure').count(),
        'Environnement': Report.objects.filter(category='environment').count(),
        'Santé': Report.objects.filter(category='health').count(),
        'Éducation': Report.objects.filter(category='education').count(),
        'Transports': Report.objects.filter(category='transport').count(),
    }
    
    # Status distribution
    statuses = {
        'Ouvert': Report.objects.filter(status='open').count(),
        'En cours': Report.objects.filter(status='in_progress').count(),
        'Résolu': Report.objects.filter(status='resolved').count(),
        'Fermé': Report.objects.filter(status='closed').count(),
    }
    
    # Priority distribution
    priorities = {
        'Basse': Report.objects.filter(priority='low').count(),
        'Moyenne': Report.objects.filter(priority='medium').count(),
        'Élevée': Report.objects.filter(priority='high').count(),
        'Critique': Report.objects.filter(priority='critical').count(),
    }
    
    context = {
        'reports_per_day': json.dumps(reports_per_day),
        'categories': json.dumps(categories),
        'statuses': json.dumps(statuses),
        'priorities': json.dumps(priorities),
    }
    
    return render(request, 'dashboard/statistics.html', context)


@login_required
@admin_or_moderator_required
def activity_log_view(request):
    """View user activity logs"""
    activities = UserActivityLog.objects.select_related('user').order_by('-timestamp')[:100]
    
    # Activity type distribution
    activity_types = UserActivityLog.objects.values('activity_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'activities': activities,
        'activity_types': activity_types,
    }
    
    return render(request, 'dashboard/activity.html', context)


@login_required
@admin_or_moderator_required
def notifications_view(request):
    """System notifications management"""
    notifications = SystemNotification.objects.filter(is_active=True).order_by('-created_at')
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'dashboard/notifications.html', context)


# ======================== API Views ========================

class StatsAPIView(generics.GenericAPIView):
    """API endpoint for dashboard statistics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_admin():
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        today = timezone.now().date()
        stats, _ = DashboardStats.objects.get_or_create(date=today)
        
        return Response({
            'status': 'success',
            'stats': {
                'total_reports': Report.objects.count(),
                'open_reports': Report.objects.filter(status='open').count(),
                'in_progress_reports': Report.objects.filter(status='in_progress').count(),
                'resolved_reports': Report.objects.filter(status='resolved').count(),
                'total_users': User.objects.count(),
                'new_users_today': User.objects.filter(created_at__date=today).count(),
                'reports_created_today': Report.objects.filter(created_at__date=today).count(),
                'reports_resolved_today': Report.objects.filter(resolved_at__date=today).count(),
            }
        })


class ChartDataAPIView(generics.GenericAPIView):
    """API endpoint for chart data"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_admin():
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Category distribution
        category_data = {
            'Infrastructure': Report.objects.filter(category='infrastructure').count(),
            'Environnement': Report.objects.filter(category='environment').count(),
            'Santé': Report.objects.filter(category='health').count(),
            'Éducation': Report.objects.filter(category='education').count(),
            'Transports': Report.objects.filter(category='transport').count(),
        }
        
        # Status distribution
        status_data = {
            'Ouvert': Report.objects.filter(status='open').count(),
            'En cours': Report.objects.filter(status='in_progress').count(),
            'Résolu': Report.objects.filter(status='resolved').count(),
            'Fermé': Report.objects.filter(status='closed').count(),
        }
        
        return Response({
            'status': 'success',
            'categories': category_data,
            'statuses': status_data,
        })


class RecentReportsAPIView(generics.ListAPIView):
    """API endpoint for recent reports"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_admin():
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reports = Report.objects.select_related('author').order_by('-created_at')[:10]
        
        data = [{
            'id': str(r.id),
            'title': r.title,
            'author': r.author.email,
            'status': r.status,
            'priority': r.priority,
            'created_at': r.created_at.isoformat(),
        } for r in reports]
        
        return Response({
            'status': 'success',
            'count': len(data),
            'reports': data
        })


class UserActivityAPIView(generics.ListAPIView):
    """API endpoint for user activity"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_admin():
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        activities = UserActivityLog.objects.select_related('user').order_by('-timestamp')[:20]
        
        data = [{
            'user': a.user.email,
            'activity': a.get_activity_type_display(),
            'timestamp': a.timestamp.isoformat(),
            'ip_address': a.ip_address,
        } for a in activities]
        
        return Response({
            'status': 'success',
            'count': len(data),
            'activities': data
        })

