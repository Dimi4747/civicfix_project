"""
Dashboard Models - Statistics & Analytics
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import uuid


User = get_user_model()


class DashboardStats(models.Model):
    """Daily statistics snapshot for dashboard analytics"""
    
    date = models.DateField(unique=True, db_index=True)
    
    # Report Stats
    total_reports = models.IntegerField(default=0)
    open_reports = models.IntegerField(default=0)
    in_progress_reports = models.IntegerField(default=0)
    resolved_reports = models.IntegerField(default=0)
    closed_reports = models.IntegerField(default=0)
    
    # User Stats
    total_users = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    
    # Performance
    average_resolution_time = models.IntegerField(default=0)  # in hours
    reports_created_today = models.IntegerField(default=0)
    reports_resolved_today = models.IntegerField(default=0)
    
    # Category Distribution
    category_infrastructure = models.IntegerField(default=0)
    category_environment = models.IntegerField(default=0)
    category_health = models.IntegerField(default=0)
    category_education = models.IntegerField(default=0)
    category_transport = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Statistiques Tableau de Bord')
        verbose_name_plural = _('Statistiques Tableau de Bord')
        ordering = ['-date']
    
    def __str__(self):
        return f"Stats du {self.date}"


class UserActivityLog(models.Model):
    """Track user activities on the platform"""
    
    ACTIVITY_CHOICES = (
        ('login', _('Connexion')),
        ('logout', _('Déconnexion')),
        ('report_created', _('Rapport créé')),
        ('report_updated', _('Rapport mis à jour')),
        ('report_commented', _('Commentaire ajouté')),
        ('file_uploaded', _('Fichier téléchargé')),
        ('profile_updated', _('Profil mis à jour')),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_CHOICES, db_index=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = _('Activité Utilisateur')
        verbose_name_plural = _('Activités Utilisateurs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['activity_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_activity_type_display()}"


class SystemNotification(models.Model):
    """System-wide notifications for users"""
    
    TYPE_CHOICES = (
        ('info', _('Information')),
        ('warning', _('Avertissement')),
        ('error', _('Erreur')),
        ('success', _('Succès')),
    )
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    is_active = models.BooleanField(default=True)
    target_users = models.ManyToManyField(User, blank=True, related_name='notifications')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Notification Système')
        verbose_name_plural = _('Notifications Système')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class AuditLog(models.Model):
    """Log all admin and moderator actions for security and accountability"""
    
    ACTION_CHOICES = (
        # User Management
        ('user_created', _('Utilisateur créé')),
        ('user_modified', _('Utilisateur modifié')),
        ('user_deleted', _('Utilisateur supprimé')),
        ('user_activated', _('Utilisateur activé')),
        ('user_deactivated', _('Utilisateur désactivé')),
        ('role_changed', _('Rôle changé')),
        ('password_reset', _('Mot de passe réinitialisé')),
        
        # Report Management
        ('report_status_changed', _('Statut du rapport changé')),
        ('report_assigned', _('Rapport assigné')),
        ('report_deleted', _('Rapport supprimé')),
        ('report_modified', _('Rapport modifié')),
        ('internal_note_added', _('Note interne ajoutée')),
        ('resolution_note_added', _('Note de résolution ajoutée')),
        
        # Moderation
        ('report_reviewed', _('Rapport examiné')),
        ('comment_approved', _('Commentaire approuvé')),
        ('comment_rejected', _('Commentaire rejeté')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Actor & Action
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs_created')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)
    
    # Target
    target_user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='audit_logs_about_user'
    )
    target_report = models.ForeignKey(
        'reports.Report',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    
    # Details
    description = models.TextField()
    old_value = models.TextField(blank=True, null=True, help_text="Ancienne valeur (avant changement)")
    new_value = models.TextField(blank=True, null=True, help_text="Nouvelle valeur (après changement)")
    
    # Context
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = _('Journal d\'audit')
        verbose_name_plural = _('Journaux d\'audit')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['actor', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['target_user', '-created_at']),
            models.Index(fields=['target_report', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.actor} - {self.get_action_display()} - {self.created_at}"
    
    @classmethod
    def log_action(cls, actor, action, description, target_user=None, target_report=None, 
                   old_value=None, new_value=None, ip_address=None, user_agent=None):
        """Helper method to log an action"""
        return cls.objects.create(
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


class AdminNotification(models.Model):
    """Notifications for admin and moderator actions"""
    
    NOTIFICATION_TYPE_CHOICES = (
        ('report_flagged', _('Rapport signalé')),
        ('user_suspicious', _('Activité utilisateur suspecte')),
        ('urgent_report', _('Rapport urgent')),
        ('system_alert', _('Alerte système')),
        ('task_assigned', _('Tâche assignée')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Notification details
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # References
    related_report = models.ForeignKey(
        'reports.Report',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    related_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_notifications_about'
    )
    
    # Status
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = _('Notification Admin')
        verbose_name_plural = _('Notifications Admin')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
            models.Index(fields=['notification_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_notification_type_display()})"
    
    def mark_as_read(self):
        """Mark notification as read"""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save()

