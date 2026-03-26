"""
Accounts Models - User Management & Authentication
"""
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator, EmailValidator
from django.utils.translation import gettext_lazy as _
import uuid


class UserManager(BaseUserManager):
    """Custom user manager with email authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError(_("L'adresse email est requise"))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if not extra_fields.get('is_staff'):
            raise ValueError(_("Le superutilisateur doit avoir is_staff=True"))
        if not extra_fields.get('is_superuser'):
            raise ValueError(_("Le superutilisateur doit avoir is_superuser=True"))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User Model with extended fields"""
    
    ROLE_CHOICES = (
        ('admin', _('Administrateur')),
        ('moderator', _('Modérateur')),
        ('user', _('Utilisateur')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    username = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=20, blank=True, null=True)
    # avatar = models.ImageField(upload_to='avatars/%Y/%m/', blank=True, null=True)  # Disabled
    bio = models.TextField(blank=True, null=True, max_length=500)
    is_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    
    # Security & Activity Tracking
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(blank=True, null=True)
    two_factor_enabled = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = _('Utilisateur')
        verbose_name_plural = _('Utilisateurs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['role']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin' or self.is_superuser
    
    def is_moderator(self):
        """Check if user is moderator or admin (admins have moderator permissions)"""
        return self.role in ['moderator', 'admin'] or self.is_staff or self.is_superuser
    
    def get_reports_count(self):
        """Get total reports created by user"""
        from apps.reports.models import Report
        return Report.objects.filter(author=self).count()


class UserProfile(models.Model):
    """Extended user profile information"""
    
    DEPARTMENT_CHOICES = (
        ('infrastructure', _('Infrastructure')),
        ('environment', _('Environnement')),
        ('health', _('Santé')),
        ('education', _('Éducation')),
        ('transport', _('Transports')),
        ('other', _('Autre')),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='other')
    organization = models.CharField(max_length=255, blank=True, null=True)
    job_title = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    newsletter_subscription = models.BooleanField(default=True)
    
    # Stats
    total_reports_filed = models.IntegerField(default=0)
    total_reports_resolved = models.IntegerField(default=0)
    reputation_score = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Profil Utilisateur')
        verbose_name_plural = _('Profils Utilisateurs')
    
    def __str__(self):
        return f"Profil de {self.user.email}"


class LoginHistory(models.Model):
    """Track user login attempts for security auditing"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    success = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = _('Historique de Connexion')
        verbose_name_plural = _('Historiques de Connexion')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['ip_address', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.timestamp}"


class Notification(models.Model):
    """Système de notifications pour les utilisateurs"""
    
    NOTIFICATION_TYPES = (
        ('like', '<i class="fas fa-heart"></i> Rapport Aimé'),
        ('comment', '<i class="fas fa-comment"></i> Commentaire'),
        ('status_change', '<i class="fas fa-sync-alt"></i> Changement Statut'),
        ('assigned', '<i class="fas fa-exclamation-triangle"></i> Rapport Assigné'),
        ('resolved', '<i class="fas fa-check-circle"></i> Rapport Résolu'),
        ('new_report', '<i class="fas fa-bullhorn"></i> Nouveau Rapport'),
        ('admin_action', '<i class="fas fa-tools"></i> Action Admin'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_notifications')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actor_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    report = models.ForeignKey('reports.Report', on_delete=models.CASCADE, null=True, blank=True, related_name='report_notifications')
    content = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} → {self.recipient.email}"
    
    def mark_as_read(self):
        """Marquer la notification comme lue"""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    @staticmethod
    def create_notification(recipient, actor, notification_type, content, report=None):
        """Créer une notification de manière sécurisée"""
        if recipient != actor:  # Pas auto-notification
            return Notification.objects.create(
                recipient=recipient,
                actor=actor,
                notification_type=notification_type,
                content=content,
                report=report
            )
        return None


