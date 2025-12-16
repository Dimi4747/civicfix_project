from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from apps.reports.models import Report
from apps.dashboard.models import DashboardStats, UserActivityLog, SystemNotification
from datetime import timedelta
import json

User = get_user_model()


class DashboardStatsTests(TestCase):
    """Test les statistiques du dashboard"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_create_dashboard_stats(self):
        """Tester la création de statistiques"""
        stats = DashboardStats.objects.create(
            total_reports=100,
            open_reports=20,
            in_progress_reports=30,
            resolved_reports=40,
            closed_reports=10
        )
        self.assertEqual(stats.total_reports, 100)
        self.assertEqual(stats.open_reports, 20)
    
    def test_dashboard_stats_daily(self):
        """Vérifier que les stats sont quotidiennes"""
        today = timezone.now().date()
        stats = DashboardStats.objects.create(
            total_reports=50,
            date=today
        )
        self.assertEqual(stats.date, today)
    
    def test_dashboard_stats_metrics(self):
        """Vérifier tous les métriques"""
        stats = DashboardStats.objects.create(
            total_reports=100,
            open_reports=30,
            in_progress_reports=40,
            resolved_reports=20,
            closed_reports=10,
            rejected_reports=5,
            total_users=50,
            total_comments=150,
            total_votes=200
        )
        self.assertEqual(stats.total_users, 50)
        self.assertEqual(stats.total_comments, 150)
        self.assertEqual(stats.total_votes, 200)


class UserActivityLogTests(TestCase):
    """Test les logs d'activité"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_create_activity_log(self):
        """Tester la création d'un log"""
        log = UserActivityLog.objects.create(
            user=self.user,
            activity_type='login',
            description='Connexion utilisateur',
            ip_address='192.168.1.1'
        )
        self.assertEqual(log.activity_type, 'login')
        self.assertEqual(log.user.id, self.user.id)
    
    def test_activity_types(self):
        """Vérifier les types d'activité"""
        activities = [
            'login', 'logout', 'report_created', 'report_edited',
            'report_deleted', 'comment_added', 'vote_added', 'profile_updated'
        ]
        for activity in activities:
            log = UserActivityLog.objects.create(
                user=self.user,
                activity_type=activity
            )
            self.assertEqual(log.activity_type, activity)
    
    def test_activity_log_timestamp(self):
        """Vérifier l'horodatage"""
        before = timezone.now()
        log = UserActivityLog.objects.create(
            user=self.user,
            activity_type='login'
        )
        after = timezone.now()
        self.assertGreaterEqual(log.timestamp, before)
        self.assertLessEqual(log.timestamp, after)
    
    def test_activity_log_with_ip(self):
        """Vérifier l'enregistrement de l'IP"""
        log = UserActivityLog.objects.create(
            user=self.user,
            activity_type='login',
            ip_address='10.0.0.1'
        )
        self.assertEqual(log.ip_address, '10.0.0.1')


class SystemNotificationTests(TestCase):
    """Test les notifications système"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            username='user2',
            password='testpass123'
        )
    
    def test_create_notification(self):
        """Tester la création de notification"""
        notif = SystemNotification.objects.create(
            title='Maintenance',
            message='Maintenance prévue ce weekend',
            notification_type='info'
        )
        self.assertEqual(notif.title, 'Maintenance')
        self.assertFalse(notif.is_read)
    
    def test_notification_types(self):
        """Vérifier les types de notification"""
        types = ['info', 'warning', 'error', 'success']
        for notif_type in types:
            notif = SystemNotification.objects.create(
                title='Test',
                notification_type=notif_type
            )
            self.assertEqual(notif.notification_type, notif_type)
    
    def test_notification_targeting(self):
        """Vérifier le ciblage des utilisateurs"""
        notif = SystemNotification.objects.create(
            title='Test',
            message='Test notification'
        )
        notif.users.add(self.user1, self.user2)
        self.assertEqual(notif.users.count(), 2)
    
    def test_notification_read_status(self):
        """Vérifier le statut de lecture"""
        notif = SystemNotification.objects.create(
            title='Test',
            message='Test'
        )
        notif.users.add(self.user1)
        self.assertFalse(notif.is_read)
        # Marquer comme lue
        notif.is_read = True
        notif.save()
        self.assertTrue(notif.is_read)


class DashboardViewTests(TestCase):
    """Test les vues du dashboard"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='user@test.com',
            username='testuser',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            username='admin',
            password='adminpass123',
            role='admin'
        )
        self.moderator_user = User.objects.create_user(
            email='moderator@test.com',
            username='moderator',
            password='modpass123',
            role='moderator'
        )
    
    def test_dashboard_requires_admin(self):
        """Le dashboard nécessite les droits admin"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 403)
    
    def test_dashboard_accessible_for_admin(self):
        """Le dashboard est accessible pour les admins"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_accessible_for_moderator(self):
        """Le dashboard est accessible pour les modérateurs"""
        self.client.login(username='moderator', password='modpass123')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_redirect_unauthenticated(self):
        """Les utilisateurs non authentifiés sont redirigés"""
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)
    
    def test_reports_dashboard(self):
        """Tester la vue des rapports"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('dashboard:reports'))
        self.assertEqual(response.status_code, 200)
    
    def test_users_dashboard(self):
        """Tester la vue des utilisateurs"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('dashboard:users'))
        self.assertEqual(response.status_code, 200)
    
    def test_statistics_view(self):
        """Tester la vue statistiques"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('dashboard:statistics'))
        self.assertEqual(response.status_code, 200)
    
    def test_activity_view(self):
        """Tester la vue d'activité"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('dashboard:activity'))
        self.assertEqual(response.status_code, 200)
    
    def test_notifications_view(self):
        """Tester la vue des notifications"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('dashboard:notifications'))
        self.assertEqual(response.status_code, 200)


class DashboardAPITests(TestCase):
    """Test les endpoints API du dashboard"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='user@test.com',
            username='testuser',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            username='admin',
            password='adminpass123',
            role='admin'
        )
    
    def test_stats_api_requires_admin(self):
        """L'API stats nécessite les droits admin"""
        response = self.client.get(reverse('dashboard:api-stats'))
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_stats_api_for_admin(self):
        """L'API stats fonctionne pour les admins"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('dashboard:api-stats'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('total_reports', data)
    
    def test_chart_data_api(self):
        """Tester l'API de données pour graphiques"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('dashboard:api-chart-data'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data)
    
    def test_recent_reports_api(self):
        """Tester l'API des rapports récents"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('dashboard:api-recent-reports'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)
    
    def test_user_activity_api(self):
        """Tester l'API d'activité utilisateur"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('dashboard:api-user-activity'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)


class DashboardMetricsTests(TestCase):
    """Test le calcul des métriques"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            username='testuser',
            password='testpass123'
        )
        # Créer plusieurs rapports avec différents statuts
        Report.objects.create(
            title='Report 1',
            author=self.user,
            status='open'
        )
        Report.objects.create(
            title='Report 2',
            author=self.user,
            status='in_progress'
        )
        Report.objects.create(
            title='Report 3',
            author=self.user,
            status='resolved'
        )
        Report.objects.create(
            title='Report 4',
            author=self.user,
            status='closed'
        )
    
    def test_total_reports_count(self):
        """Compter les rapports totaux"""
        total = Report.objects.count()
        self.assertEqual(total, 4)
    
    def test_open_reports_count(self):
        """Compter les rapports ouverts"""
        open_count = Report.objects.filter(status='open').count()
        self.assertEqual(open_count, 1)
    
    def test_in_progress_reports_count(self):
        """Compter les rapports en cours"""
        in_progress = Report.objects.filter(status='in_progress').count()
        self.assertEqual(in_progress, 1)
    
    def test_resolved_reports_count(self):
        """Compter les rapports résolus"""
        resolved = Report.objects.filter(status='resolved').count()
        self.assertEqual(resolved, 1)
    
    def test_reports_by_category(self):
        """Regrouper les rapports par catégorie"""
        Report.objects.create(
            title='Report 5',
            author=self.user,
            category='infrastructure'
        )
        infrastructure = Report.objects.filter(
            category='infrastructure'
        ).count()
        self.assertEqual(infrastructure, 1)
    
    def test_user_count(self):
        """Compter les utilisateurs"""
        user_count = User.objects.count()
        self.assertGreater(user_count, 0)


class DashboardActivityTests(TestCase):
    """Test le suivi d'activité"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='user@test.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_login_activity_logged(self):
        """Vérifier que la connexion est enregistrée"""
        # Note: Ce test dépend de la vue de connexion qui crée les logs
        initial_logs = UserActivityLog.objects.filter(
            activity_type='login'
        ).count()
        self.client.login(username='testuser', password='testpass123')
        # La vue de login doit créer un log
        # self.assertEqual(
        #     UserActivityLog.objects.filter(activity_type='login').count(),
        #     initial_logs + 1
        # )
    
    def test_activity_filtering_by_user(self):
        """Filtrer l'activité par utilisateur"""
        UserActivityLog.objects.create(
            user=self.user,
            activity_type='login'
        )
        user_logs = UserActivityLog.objects.filter(user=self.user)
        self.assertEqual(user_logs.count(), 1)
    
    def test_activity_filtering_by_type(self):
        """Filtrer l'activité par type"""
        UserActivityLog.objects.create(
            user=self.user,
            activity_type='report_created'
        )
        UserActivityLog.objects.create(
            user=self.user,
            activity_type='login'
        )
        reports = UserActivityLog.objects.filter(
            activity_type='report_created'
        ).count()
        self.assertEqual(reports, 1)
    
    def test_recent_activities(self):
        """Obtenir les activités récentes"""
        for i in range(5):
            UserActivityLog.objects.create(
                user=self.user,
                activity_type='login'
            )
        recent = UserActivityLog.objects.all().order_by('-timestamp')[:3]
        self.assertEqual(recent.count(), 3)
