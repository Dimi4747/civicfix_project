"""
Notifications & Interactions Views - AJAX/HTMX Endpoints
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
import json

from apps.accounts.models import Notification, User
from apps.reports.models import Report, Like, ReportComment


# ==================== NOTIFICATIONS ====================

@login_required
def notifications_view(request):
    """Page principale des notifications"""
    notifications = Notification.objects.filter(recipient=request.user).select_related('actor', 'report')
    
    # Marquer les notifications comme lues au chargement de la page
    unread = notifications.filter(is_read=False)
    unread.update(is_read=True, read_at=timezone.now())
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Stats
    total_unread = Notification.objects.filter(recipient=request.user, is_read=False).count()
    
    context = {
        'page_obj': page_obj,
        'total_unread': total_unread,
    }
    
    return render(request, 'notifications/list.html', context)


@login_required
@require_http_methods(["GET"])
def get_unread_count(request):
    """API: Obtenir le nombre de notifications non lues"""
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({'unread_count': count})


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """API: Marquer une notification comme lue"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.mark_as_read()
    
    return JsonResponse({
        'status': 'success',
        'message': 'Notification marquée comme lue'
    })


@login_required
@require_http_methods(["POST"])
def mark_all_notifications_read(request):
    """API: Marquer TOUTES les notifications comme lues"""
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True, read_at=timezone.now())
    
    return JsonResponse({
        'status': 'success',
        'message': 'Toutes les notifications marquées comme lues'
    })


# ==================== LIKES ====================

@login_required
@require_http_methods(["POST"])
def toggle_like(request, report_id):
    """API AJAX: Toggle like sur un rapport (style réseaux sociaux)"""
    try:
        report = get_object_or_404(Report, id=report_id)
        
        # Toggle like
        liked, like_obj = Like.toggle_like(report, request.user)
        
        # Créer notification si nouveau like
        if liked:
            Notification.create_notification(
                recipient=report.author,
                actor=request.user,
                notification_type='like',
                content=f"{request.user.get_full_name()} a aimé votre rapport: \"{report.title}\"",
                report=report
            )
        
        # Retourner nombre de likes
        like_count = report.likes.count()
        
        return JsonResponse({
            'status': 'success',
            'liked': liked,
            'like_count': like_count,
            'message': 'Like ajouté' if liked else 'Like supprimé'
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["GET"])
def get_likes_data(request, report_id):
    """API: Obtenir les données de likes d'un rapport"""
    report = get_object_or_404(Report, id=report_id)
    
    is_liked = report.likes.filter(user=request.user).exists()
    like_count = report.likes.count()
    
    return JsonResponse({
        'status': 'success',
        'is_liked': is_liked,
        'like_count': like_count
    })


# ==================== COMMENTAIRES DYNAMIQUES ====================

@login_required
@require_http_methods(["GET"])
def get_comments(request, report_id):
    """API AJAX: Charger les commentaires d'un rapport"""
    try:
        report = get_object_or_404(Report, id=report_id)
        comments = report.comments.select_related('author').order_by('-created_at')
        
        # Sérialiser les commentaires
        comments_data = []
        for comment in comments:
            comments_data.append({
                'id': str(comment.id),
                'author': {
                    'id': str(comment.author.id),
                    'name': comment.author.get_full_name(),
                    'email': comment.author.email,
                    'role': comment.author.get_role_display(),
                    'initials': (comment.author.first_name[0] + comment.author.last_name[0]).upper() if comment.author.first_name and comment.author.last_name else 'U',
                },
                'content': comment.content,
                'is_internal': comment.is_internal,
                'created_at': comment.created_at.strftime('%d %b %Y à %H:%M'),
                'created_at_relative': _get_relative_time(comment.created_at),
            })
        
        return JsonResponse({
            'status': 'success',
            'count': len(comments_data),
            'comments': comments_data
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def add_comment(request, report_id):
    """API AJAX: Ajouter un commentaire sans rechargement"""
    try:
        report = get_object_or_404(Report, id=report_id)
        
        content = request.POST.get('content', '').strip()
        is_internal = request.POST.get('is_internal', 'false').lower() == 'true'
        
        if not content:
            return JsonResponse({
                'status': 'error',
                'message': 'Le commentaire ne peut pas être vide'
            }, status=400)
        
        # Vérifier permissions pour commentaire interne
        if is_internal and not (request.user.is_staff or request.user.is_admin()):
            return JsonResponse({
                'status': 'error',
                'message': 'Vous n\'avez pas les permissions pour ajouter un commentaire interne'
            }, status=403)
        
        # Créer le commentaire
        comment = ReportComment.objects.create(
            report=report,
            author=request.user,
            content=content,
            is_internal=is_internal
        )
        
        # Mettre à jour le compteur
        report.comments_count = report.comments.count()
        report.save(update_fields=['comments_count'])
        
        # Créer notification
        Notification.create_notification(
            recipient=report.author,
            actor=request.user,
            notification_type='comment',
            content=f"{request.user.get_full_name()} a commenté: \"{report.title}\"",
            report=report
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Commentaire ajouté',
            'comment': {
                'id': str(comment.id),
                'author': {
                    'name': comment.author.get_full_name(),
                    'role': comment.author.get_role_display(),
                },
                'content': comment.content,
                'created_at_relative': 'à l\'instant',
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


# ==================== UTILITAIRES ====================

def _get_relative_time(dt):
    """Convertir datetime en temps relatif (il y a 2h, etc.)"""
    now = timezone.now()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "à l'instant"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"il y a {minutes}m"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"il y a {hours}h"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"il y a {days}j"
    else:
        weeks = int(seconds / 604800)
        return f"il y a {weeks}w"
