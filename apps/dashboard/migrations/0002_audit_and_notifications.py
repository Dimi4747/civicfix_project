# Generated migration for dashboard models

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
        ('accounts', '0001_initial'),
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action', models.CharField(
                    choices=[
                        ('user_created', 'Utilisateur créé'),
                        ('user_modified', 'Utilisateur modifié'),
                        ('user_deleted', 'Utilisateur supprimé'),
                        ('user_activated', 'Utilisateur activé'),
                        ('user_deactivated', 'Utilisateur désactivé'),
                        ('role_changed', 'Rôle changé'),
                        ('password_reset', 'Mot de passe réinitialisé'),
                        ('report_status_changed', 'Statut du rapport changé'),
                        ('report_assigned', 'Rapport assigné'),
                        ('report_deleted', 'Rapport supprimé'),
                        ('report_modified', 'Rapport modifié'),
                        ('internal_note_added', 'Note interne ajoutée'),
                        ('resolution_note_added', 'Note de résolution ajoutée'),
                        ('report_reviewed', 'Rapport examiné'),
                        ('comment_approved', 'Commentaire approuvé'),
                        ('comment_rejected', 'Commentaire rejeté'),
                    ],
                    db_index=True,
                    max_length=50
                )),
                ('description', models.TextField()),
                ('old_value', models.TextField(blank=True, help_text='Ancienne valeur (avant changement)', null=True)),
                ('new_value', models.TextField(blank=True, help_text='Nouvelle valeur (après changement)', null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('actor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs_created', to='accounts.user')),
                ('target_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs_about_user', to='accounts.user')),
                ('target_report', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to='reports.report')),
            ],
            options={
                'verbose_name': "Journal d'audit",
                'verbose_name_plural': "Journaux d'audit",
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AdminNotification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('notification_type', models.CharField(
                    choices=[
                        ('report_flagged', 'Rapport signalé'),
                        ('user_suspicious', 'Activité utilisateur suspecte'),
                        ('urgent_report', 'Rapport urgent'),
                        ('system_alert', 'Alerte système'),
                        ('task_assigned', 'Tâche assignée'),
                    ],
                    max_length=50
                )),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('is_resolved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admin_notifications', to='accounts.user')),
                ('related_report', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='reports.report')),
                ('related_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admin_notifications_about', to='accounts.user')),
            ],
            options={
                'verbose_name': 'Notification Admin',
                'verbose_name_plural': 'Notifications Admin',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['actor', '-created_at'], name='dashboard_a_actor_i_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['action', '-created_at'], name='dashboard_a_action__idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['target_user', '-created_at'], name='dashboard_a_target_u_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['target_report', '-created_at'], name='dashboard_a_target_r_idx'),
        ),
        migrations.AddIndex(
            model_name='adminnotification',
            index=models.Index(fields=['recipient', 'is_read', '-created_at'], name='dashboard_a_recipie_idx'),
        ),
        migrations.AddIndex(
            model_name='adminnotification',
            index=models.Index(fields=['notification_type', '-created_at'], name='dashboard_a_notifi_idx'),
        ),
    ]
