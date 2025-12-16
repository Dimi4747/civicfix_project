"""
Advanced Admin and Moderator Views - User Management, Report Management, Moderation
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q, Count
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
import json
from datetime import timedelta

from apps.reports.models import Report, ReportComment
from apps.accounts.decorators import admin_required, admin_or_moderator_required
from apps.accounts.models import UserProfile
from .models import AuditLog, AdminNotification
from .utils import log_admin_action, get_client_ip


User = get_user_model()


# ================== ADMIN USER MANAGEMENT ==================

@login_required
@admin_required
def users_list_view(request):
    """List all users with filtering and search"""
    users = User.objects.all().order_by('-created_at')
    
    # Search
    query = request.GET.get('q', '')
    if query:
        users = users.filter(
            Q(email__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        )
    
    # Filter by role
    role = request.GET.get('role', '')
    if role:
        users = users.filter(role=role)
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    elif status_filter == 'locked':
        users = users.filter(account_locked_until__isnull=False, account_locked_until__gt=timezone.now())
    
    # Pagination
    paginator = Paginator(users, 20)
    page = request.GET.get('page', 1)
    try:
        users_page = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        users_page = paginator.page(1)
    
    context = {
        'users': users_page,
        'paginator': paginator,
        'query': query,
        'role': role,
        'status_filter': status_filter,
        'total_count': paginator.count,
    }
    return render(request, 'dashboard/admin/users_list.html', context)


@login_required
@admin_required
def user_detail_view(request, user_id):
    """View user details and manage"""
    user = get_object_or_404(User, id=user_id)
    user_profile = user.userprofile if hasattr(user, 'userprofile') else None
    
    # Get user's activity
    reports = user.reports_authored.all().order_by('-created_at')[:5]
    login_history = user.login_history.all().order_by('-timestamp')[:10]
    audit_logs = AuditLog.objects.filter(
        Q(actor=user) | Q(target_user=user)
    ).order_by('-created_at')[:10]
    
    context = {
        'user': user,
        'user_profile': user_profile,
        'reports': reports,
        'login_history': login_history,
        'audit_logs': audit_logs,
        'total_reports': user.reports_authored.count(),
        'total_comments': user.reportcomment_set.count(),
    }
    return render(request, 'dashboard/admin/user_detail.html', context)


@login_required
@admin_required
def user_edit_view(request, user_id):
    """Edit user details"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Update user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        old_role = user.role
        new_role = request.POST.get('role', user.role)
        
        # Log role change
        if old_role != new_role:
            log_admin_action(
                request.user,
                'role_changed',
                f"Rôle changé de {old_role} à {new_role}",
                target_user=user,
                old_value=old_role,
                new_value=new_role,
                ip_address=get_client_ip(request)
            )
        
        user.role = new_role
        user.save()
        
        messages.success(request, f"Utilisateur {user.email} mis à jour avec succès.")
        log_admin_action(
            request.user,
            'user_modified',
            f"Utilisateur {user.email} modifié",
            target_user=user,
            ip_address=get_client_ip(request)
        )
        return redirect('user-detail', user_id=user.id)
    
    context = {'user': user}
    return render(request, 'dashboard/admin/user_edit.html', context)


@login_required
@admin_required
@require_http_methods(["POST"])
def user_toggle_status_view(request, user_id):
    """Enable/Disable user account"""
    user = get_object_or_404(User, id=user_id)
    
    if user == request.user:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
        return redirect('user-detail', user_id=user.id)
    
    old_status = user.is_active
    user.is_active = not user.is_active
    user.save()
    
    action = 'user_activated' if user.is_active else 'user_deactivated'
    log_admin_action(
        request.user,
        action,
        f"Compte {user.email} {'activé' if user.is_active else 'désactivé'}",
        target_user=user,
        ip_address=get_client_ip(request)
    )
    
    status_msg = "activé" if user.is_active else "désactivé"
    messages.success(request, f"Compte de {user.email} {status_msg}.")
    return redirect('user-detail', user_id=user.id)


@login_required
@admin_required
@require_http_methods(["POST"])
def user_delete_view(request, user_id):
    """Delete user account"""
    user = get_object_or_404(User, id=user_id)
    
    if user == request.user:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect('user-detail', user_id=user.id)
    
    email = user.email
    log_admin_action(
        request.user,
        'user_deleted',
        f"Utilisateur {email} supprimé",
        target_user=user,
        ip_address=get_client_ip(request)
    )
    
    user.delete()
    messages.success(request, f"Utilisateur {email} supprimé avec succès.")
    return redirect('dashboard:users-list')


@login_required
@admin_required
@require_http_methods(["POST"])
def user_unlock_view(request, user_id):
    """Unlock locked user account"""
    user = get_object_or_404(User, id=user_id)
    
    user.account_locked_until = None
    user.failed_login_attempts = 0
    user.save()
    
    log_admin_action(
        request.user,
        'user_modified',
        f"Compte de {user.email} déverrouillé",
        target_user=user,
        ip_address=get_client_ip(request)
    )
    
    messages.success(request, f"Compte de {user.email} déverrouillé.")
    return redirect('user-detail', user_id=user.id)


# ================== ADMIN REPORT MANAGEMENT ==================

@login_required
@admin_required
def reports_admin_view(request):
    """Manage all reports as admin"""
    reports = Report.objects.all().order_by('-created_at')
    
    # Filters
    status = request.GET.get('status', '')
    if status:
        reports = reports.filter(status=status)
    
    priority = request.GET.get('priority', '')
    if priority:
        reports = reports.filter(priority=priority)
    
    search = request.GET.get('q', '')
    if search:
        reports = reports.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(reports, 25)
    page = request.GET.get('page', 1)
    try:
        reports_page = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        reports_page = paginator.page(1)
    
    context = {
        'reports': reports_page,
        'status': status,
        'priority': priority,
        'search': search,
        'STATUS_CHOICES': Report.STATUS_CHOICES,
        'PRIORITY_CHOICES': Report.PRIORITY_CHOICES,
    }
    return render(request, 'dashboard/admin/reports_admin.html', context)


@login_required
@admin_required
def report_manage_view(request, report_id):
    """Admin interface to manage a specific report"""
    report = get_object_or_404(Report, id=report_id)
    
    if request.method == 'POST':
        with transaction.atomic():
            # Update report details
            old_title = report.title
            new_title = request.POST.get('title', report.title)
            if old_title != new_title:
                log_admin_action(
                    request.user,
                    'report_modified',
                    f"Titre du rapport changé",
                    target_report=report,
                    old_value=old_title,
                    new_value=new_title,
                    ip_address=get_client_ip(request)
                )
            report.title = new_title
            
            old_description = report.description
            new_description = request.POST.get('description', report.description)
            if old_description != new_description:
                log_admin_action(
                    request.user,
                    'report_modified',
                    f"Description du rapport changée",
                    target_report=report,
                    old_value=old_description[:100],
                    new_value=new_description[:100],
                    ip_address=get_client_ip(request)
                )
            report.description = new_description
            
            # Status change
            old_status = report.status
            new_status = request.POST.get('status', report.status)
            if old_status != new_status:
                report.status = new_status
                if new_status == 'resolved':
                    report.resolved_at = timezone.now()
                log_admin_action(
                    request.user,
                    'report_status_changed',
                    f"Statut changé de {old_status} à {new_status}",
                    target_report=report,
                    old_value=old_status,
                    new_value=new_status,
                    ip_address=get_client_ip(request)
                )
            
            # Category & Priority
            report.category = request.POST.get('category', report.category)
            report.priority = request.POST.get('priority', report.priority)
            
            # Assignment
            assigned_to_id = request.POST.get('assigned_to', '')
            if assigned_to_id:
                assigned_user = User.objects.get(id=assigned_to_id)
                if report.assigned_to != assigned_user:
                    log_admin_action(
                        request.user,
                        'report_assigned',
                        f"Rapport assigné à {assigned_user.email}",
                        target_report=report,
                        ip_address=get_client_ip(request)
                    )
                report.assigned_to = assigned_user
            
            # Internal notes
            internal_note = request.POST.get('internal_note', '')
            if internal_note:
                report.internal_notes = (report.internal_notes or '') + f"\n[{request.user.email} - {timezone.now().strftime('%d/%m/%Y %H:%M')}]\n{internal_note}\n"
                log_admin_action(
                    request.user,
                    'internal_note_added',
                    f"Note interne ajoutée au rapport",
                    target_report=report,
                    ip_address=get_client_ip(request)
                )
            
            report.save()
        
        messages.success(request, "Rapport mis à jour avec succès.")
        return redirect('dashboard:report-manage', report_id=report.id)
    
    # Get moderators for assignment
    moderators = User.objects.filter(role__in=['admin', 'moderator']).exclude(id=report.author_id)
    
    context = {
        'report': report,
        'moderators': moderators,
        'STATUS_CHOICES': Report.STATUS_CHOICES,
        'PRIORITY_CHOICES': Report.PRIORITY_CHOICES,
        'CATEGORY_CHOICES': Report.CATEGORY_CHOICES,
    }
    return render(request, 'dashboard/admin/report_manage.html', context)


@login_required
@admin_required
@require_http_methods(["POST"])
def report_delete_view(request, report_id):
    """Delete a report"""
    report = get_object_or_404(Report, id=report_id)
    
    report_title = report.title
    log_admin_action(
        request.user,
        'report_deleted',
        f"Rapport '{report_title}' supprimé",
        target_report=report,
        ip_address=get_client_ip(request)
    )
    
    report.delete()
    messages.success(request, f"Rapport '{report_title}' supprimé avec succès.")
    return redirect('dashboard:reports-admin')


# ================== MODERATOR INTERFACE ==================

@login_required
@admin_or_moderator_required
def moderator_queue_view(request):
    """Moderator view - Reports assigned to them"""
    user = request.user
    
    # Get assigned reports
    reports = Report.objects.filter(
        assigned_to=user
    ).order_by('-priority', '-created_at')
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        reports = reports.filter(status=status)
    
    # Pagination
    paginator = Paginator(reports, 15)
    page = request.GET.get('page', 1)
    try:
        reports_page = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        reports_page = paginator.page(1)
    
    stats = {
        'total': Report.objects.filter(assigned_to=user).count(),
        'open': Report.objects.filter(assigned_to=user, status='open').count(),
        'in_progress': Report.objects.filter(assigned_to=user, status='in_progress').count(),
        'resolved': Report.objects.filter(assigned_to=user, status='resolved').count(),
    }
    
    context = {
        'reports': reports_page,
        'stats': stats,
        'status': status,
        'STATUS_CHOICES': Report.STATUS_CHOICES,
    }
    return render(request, 'dashboard/moderator/queue.html', context)


@login_required
@admin_or_moderator_required
def moderate_report_view(request, report_id):
    """Moderator interface to moderate a specific report"""
    report = get_object_or_404(Report, id=report_id)
    
    # Check if moderator has access
    if report.assigned_to != request.user and not request.user.is_admin():
        return HttpResponseForbidden("Vous n'avez pas accès à ce rapport.")
    
    if request.method == 'POST':
        with transaction.atomic():
            # Update status
            old_status = report.status
            new_status = request.POST.get('status', report.status)
            if old_status != new_status:
                report.status = new_status
                if new_status == 'resolved':
                    report.resolved_at = timezone.now()
                
                log_admin_action(
                    request.user,
                    'report_status_changed',
                    f"Statut changé de {old_status} à {new_status}",
                    target_report=report,
                    old_value=old_status,
                    new_value=new_status,
                    ip_address=get_client_ip(request)
                )
            
            # Add resolution notes
            resolution_note = request.POST.get('resolution_notes', '')
            if resolution_note:
                report.resolution_notes = (report.resolution_notes or '') + f"\n[{request.user.email} - {timezone.now().strftime('%d/%m/%Y %H:%M')}]\n{resolution_note}\n"
                log_admin_action(
                    request.user,
                    'resolution_note_added',
                    f"Note de résolution ajoutée",
                    target_report=report,
                    ip_address=get_client_ip(request)
                )
            
            # Add internal comment
            internal_comment = request.POST.get('internal_comment', '')
            if internal_comment:
                report.internal_notes = (report.internal_notes or '') + f"\n[{request.user.email} - {timezone.now().strftime('%d/%m/%Y %H:%M')}]\n{internal_comment}\n"
                log_admin_action(
                    request.user,
                    'internal_note_added',
                    f"Commentaire interne ajouté",
                    target_report=report,
                    ip_address=get_client_ip(request)
                )
            
            report.save()
        
        messages.success(request, "Rapport modéré avec succès.")
        return redirect('moderate-report', report_id=report.id)
    
    # Get report comments
    comments = report.reportcomment_set.all().order_by('-created_at')
    
    context = {
        'report': report,
        'comments': comments,
        'STATUS_CHOICES': Report.STATUS_CHOICES,
    }
    return render(request, 'dashboard/moderator/moderate_report.html', context)


# ================== AUDIT & ACTIVITY LOG ==================

@login_required
@admin_required
def audit_log_view(request):
    """View audit logs"""
    logs = AuditLog.objects.all().order_by('-created_at')
    
    # Filter by action
    action = request.GET.get('action', '')
    if action:
        logs = logs.filter(action=action)
    
    # Filter by actor
    actor_id = request.GET.get('actor_id', '')
    if actor_id:
        logs = logs.filter(actor_id=actor_id)
    
    # Filter by date range
    date_from = request.GET.get('date_from', '')
    if date_from:
        logs = logs.filter(created_at__date__gte=date_from)
    
    # Pagination
    paginator = Paginator(logs, 50)
    page = request.GET.get('page', 1)
    try:
        logs_page = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        logs_page = paginator.page(1)
    
    context = {
        'logs': logs_page,
        'action': action,
        'actor_id': actor_id,
        'date_from': date_from,
        'ACTION_CHOICES': AuditLog.ACTION_CHOICES,
        'admins': User.objects.filter(role__in=['admin', 'moderator']),
    }
    return render(request, 'dashboard/audit_log.html', context)


@login_required
@admin_or_moderator_required
def admin_notifications_view(request):
    """View admin/moderator notifications"""
    notifications = AdminNotification.objects.filter(recipient=request.user).order_by('-created_at')
    
    # Mark as read if requested
    if request.GET.get('mark_read') == 'all':
        notifications.filter(is_read=False).update(is_read=True, read_at=timezone.now())
        messages.success(request, "Toutes les notifications marquées comme lues.")
        return redirect('admin-notifications')
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page = request.GET.get('page', 1)
    try:
        notifications_page = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        notifications_page = paginator.page(1)
    
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications_page,
        'unread_count': unread_count,
    }
    return render(request, 'dashboard/admin_notifications.html', context)
