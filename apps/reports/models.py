"""
Reports Models - Issue/Report Management System
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
import uuid


User = get_user_model()


class Report(models.Model):
    """Main Report/Issue model"""
    
    STATUS_CHOICES = (
        ('open', _('Ouvert')),
        ('in_progress', _('En cours')),
        ('resolved', _('Résolu')),
        ('closed', _('Fermé')),
        ('rejected', _('Rejeté')),
    )
    
    PRIORITY_CHOICES = (
        ('low', _('Basse')),
        ('medium', _('Moyenne')),
        ('high', _('Élevée')),
        ('critical', _('Critique')),
    )
    
    CATEGORY_CHOICES = (
        ('infrastructure', _('Infrastructure')),
        ('environment', _('Environnement')),
        ('health', _('Santé')),
        ('education', _('Éducation')),
        ('transport', _('Transports')),
        ('security', _('Sécurité')),
        ('other', _('Autre')),
    )
    
    # Core Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', db_index=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Relationships
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_authored')
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reports_assigned',
        limit_choices_to={'role__in': ['admin', 'moderator']}
    )
    
    # Location & Context
    location = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    # Stats & Tracking
    views_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    votes_count = models.IntegerField(default=0)
    
    # Content
    resolution_notes = models.TextField(blank=True, null=True)
    internal_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = _('Rapport')
        verbose_name_plural = _('Rapports')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['priority', 'status']),
        ]
    
    def __str__(self):
        return f"[{self.get_status_display()}] {self.title}"
    
    def get_status_badge(self):
        """Return status with color coding"""
        badges = {
            'open': 'bg-blue-500',
            'in_progress': 'bg-yellow-500',
            'resolved': 'bg-green-500',
            'closed': 'bg-gray-500',
            'rejected': 'bg-red-500',
        }
        return badges.get(self.status, 'bg-gray-500')


class ReportAttachment(models.Model):
    """File attachments for reports"""
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(
        upload_to='reports/attachments/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif'])]
    )
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField()  # in bytes
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Pièce Jointe')
        verbose_name_plural = _('Pièces Jointes')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.filename} - {self.report.title}"


class ReportComment(models.Model):
    """Comments on reports for collaboration"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_internal = models.BooleanField(default=False)  # Only visible to admin/moderator
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Commentaire')
        verbose_name_plural = _('Commentaires')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['report', '-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]
    
    def __str__(self):
        return f"Commentaire par {self.author.email} sur {self.report.title}"


class ReportHistory(models.Model):
    """Audit trail for report changes"""
    
    ACTION_CHOICES = (
        ('created', _('Créé')),
        ('status_changed', _('Statut changé')),
        ('assigned', _('Assigné')),
        ('commented', _('Commenté')),
        ('attachment_added', _('Pièce jointe ajoutée')),
        ('updated', _('Mis à jour')),
        ('reopened', _('Rouvert')),
    )
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = _('Historique Rapport')
        verbose_name_plural = _('Historiques Rapports')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['report', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.report.title}"


class ReportVote(models.Model):
    """Upvote/Downvote system for reports"""
    
    VOTE_CHOICES = (
        (1, _('Utile')),
        (-1, _('Non utile')),
    )
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.SmallIntegerField(choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Vote Rapport')
        verbose_name_plural = _('Votes Rapports')
        unique_together = ['report', 'user']
        indexes = [
            models.Index(fields=['report']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.report.title}"


class Like(models.Model):
    """Système de Like pour les rapports (style réseaux sociaux)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = _('Like')
        verbose_name_plural = _('Likes')
        unique_together = ('report', 'user')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} ❤️ {self.report.title}"
    
    @staticmethod
    def toggle_like(report, user):
        """Toggle like et retourner (liked, like_object)"""
        like, created = Like.objects.get_or_create(report=report, user=user)
        
        if not created:
            like.delete()
            return False, None
        
        return True, like
