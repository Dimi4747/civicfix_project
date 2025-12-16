"""
Dashboard Models - Statistics & Analytics
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


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

