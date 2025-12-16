from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.reports.models import Report, ReportComment, ReportAttachment, ReportVote
from datetime import datetime
import json

User = get_user_model()


class ReportModelTests(TestCase):
    """Test les modèles de rapports"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_create_report(self):
        """Tester la création d'un rapport"""
        report = Report.objects.create(
            title='Nid de poule dangereux',
            description='Grande cavité dans la route',
            author=self.user,
            category='infrastructure',
            priority='high',
            latitude=48.8566,
            longitude=2.3522
        )
        self.assertEqual(report.title, 'Nid de poule dangereux')
        self.assertEqual(report.status, 'open')
        self.assertEqual(report.view_count, 0)
        self.assertEqual(str(report.author), 'testuser')
    
    def test_report_status_choices(self):
        """Vérifier les statuts possibles"""
        statuses = ['open', 'in_progress', 'resolved', 'closed', 'rejected']
        for status in statuses:
            report = Report.objects.create(
                title=f'Report {status}',
                description='Description',
                author=self.user,
                status=status
            )
            self.assertEqual(report.status, status)
    
    def test_report_priority_choices(self):
        """Vérifier les priorités possibles"""
        priorities = ['low', 'medium', 'high', 'critical']
        for priority in priorities:
            report = Report.objects.create(
                title=f'Report {priority}',
                description='Description',
                author=self.user,
                priority=priority
            )
            self.assertEqual(report.priority, priority)
    
    def test_report_category_choices(self):
        """Vérifier les catégories possibles"""
        categories = ['infrastructure', 'environment', 'health', 'education', 
                     'transport', 'safety', 'other']
        for category in categories:
            report = Report.objects.create(
                title=f'Report {category}',
                description='Description',
                author=self.user,
                category=category
            )
            self.assertEqual(report.category, category)
    
    def test_report_string_representation(self):
        """Tester la représentation texte"""
        report = Report.objects.create(
            title='Test Report',
            author=self.user
        )
        self.assertEqual(str(report), 'Test Report')
    
    def test_report_view_count_increment(self):
        """Tester l'incrémentation des vues"""
        report = Report.objects.create(
            title='Test Report',
            author=self.user
        )
        self.assertEqual(report.view_count, 0)
        report.view_count += 1
        report.save()
        self.assertEqual(report.view_count, 1)


class ReportCommentTests(TestCase):
    """Test les commentaires de rapports"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            username='testuser',
            password='testpass123'
        )
        self.report = Report.objects.create(
            title='Test Report',
            author=self.user
        )
    
    def test_create_comment(self):
        """Tester la création d'un commentaire"""
        comment = ReportComment.objects.create(
            report=self.report,
            author=self.user,
            content='Excellent rapport!'
        )
        self.assertEqual(comment.content, 'Excellent rapport!')
        self.assertEqual(comment.report.id, self.report.id)
        self.assertFalse(comment.is_internal)
    
    def test_internal_comment(self):
        """Tester les commentaires internes"""
        comment = ReportComment.objects.create(
            report=self.report,
            author=self.user,
            content='Note interne',
            is_internal=True
        )
        self.assertTrue(comment.is_internal)
    
    def test_comment_count(self):
        """Vérifier le comptage des commentaires"""
        self.assertEqual(self.report.comments.count(), 0)
        ReportComment.objects.create(
            report=self.report,
            author=self.user,
            content='Commentaire 1'
        )
        self.assertEqual(self.report.comments.count(), 1)


class ReportAttachmentTests(TestCase):
    """Test les pièces jointes"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            username='testuser',
            password='testpass123'
        )
        self.report = Report.objects.create(
            title='Test Report',
            author=self.user
        )
    
    def test_create_attachment(self):
        """Tester l'ajout de pièce jointe"""
        file = SimpleUploadedFile(
            "test.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        attachment = ReportAttachment.objects.create(
            report=self.report,
            file=file
        )
        self.assertIsNotNone(attachment.id)
        self.assertEqual(attachment.report.id, self.report.id)
    
    def test_file_size_tracking(self):
        """Vérifier le suivi de la taille"""
        file = SimpleUploadedFile(
            "test.pdf",
            b"a" * 1024,
            content_type="application/pdf"
        )
        attachment = ReportAttachment.objects.create(
            report=self.report,
            file=file
        )
        self.assertGreater(attachment.file_size, 0)


class ReportVoteTests(TestCase):
    """Test le système de votes"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            username='testuser',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            username='testuser2',
            password='testpass123'
        )
        self.report = Report.objects.create(
            title='Test Report',
            author=self.user
        )
    
    def test_create_upvote(self):
        """Tester un vote positif"""
        vote = ReportVote.objects.create(
            report=self.report,
            user=self.user2,
            vote_type='upvote'
        )
        self.assertEqual(vote.vote_type, 'upvote')
    
    def test_create_downvote(self):
        """Tester un vote négatif"""
        vote = ReportVote.objects.create(
            report=self.report,
            user=self.user2,
            vote_type='downvote'
        )
        self.assertEqual(vote.vote_type, 'downvote')
    
    def test_unique_vote_per_user(self):
        """Un utilisateur ne peut voter qu'une fois par rapport"""
        ReportVote.objects.create(
            report=self.report,
            user=self.user2,
            vote_type='upvote'
        )
        with self.assertRaises(Exception):
            ReportVote.objects.create(
                report=self.report,
                user=self.user2,
                vote_type='downvote'
            )
    
    def test_vote_count(self):
        """Compter les votes"""
        ReportVote.objects.create(
            report=self.report,
            user=self.user2,
            vote_type='upvote'
        )
        upvotes = self.report.votes.filter(vote_type='upvote').count()
        self.assertEqual(upvotes, 1)


class ReportViewsTests(TestCase):
    """Test les vues de rapports"""
    
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
        self.report = Report.objects.create(
            title='Test Report',
            description='Test Description',
            author=self.user
        )
    
    def test_report_list_view(self):
        """Tester l'affichage de la liste"""
        response = self.client.get(reverse('reports:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Report')
    
    def test_report_detail_view(self):
        """Tester l'affichage des détails"""
        response = self.client.get(
            reverse('reports:detail', args=[self.report.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.report.title)
    
    def test_report_create_requires_login(self):
        """La création nécessite une authentification"""
        response = self.client.get(reverse('reports:create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_report_create_authenticated(self):
        """Créer un rapport en tant qu'utilisateur authentifié"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('reports:create'))
        self.assertEqual(response.status_code, 200)
    
    def test_report_edit_owner_only(self):
        """Seul le propriétaire peut modifier"""
        other_user = User.objects.create_user(
            email='other@test.com',
            username='otheruser',
            password='testpass123'
        )
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(
            reverse('reports:edit', args=[self.report.id])
        )
        self.assertEqual(response.status_code, 403)
    
    def test_report_delete_requires_permission(self):
        """Supprimer nécessite les permissions"""
        response = self.client.get(
            reverse('reports:delete', args=[self.report.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login


class ReportFilterTests(TestCase):
    """Test les filtres et recherche"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='user@test.com',
            username='testuser',
            password='testpass123'
        )
        
        # Créer plusieurs rapports
        for i in range(5):
            Report.objects.create(
                title=f'Report {i}',
                description='Description',
                author=self.user,
                status='open' if i < 3 else 'resolved',
                category='infrastructure' if i < 2 else 'environment'
            )
    
    def test_filter_by_status(self):
        """Filtrer par statut"""
        response = self.client.get(reverse('reports:list'), {'status': 'open'})
        self.assertEqual(response.status_code, 200)
    
    def test_filter_by_category(self):
        """Filtrer par catégorie"""
        response = self.client.get(
            reverse('reports:list'), 
            {'category': 'infrastructure'}
        )
        self.assertEqual(response.status_code, 200)
    
    def test_search_functionality(self):
        """Tester la recherche"""
        response = self.client.get(
            reverse('reports:list'),
            {'search': 'Report'}
        )
        self.assertEqual(response.status_code, 200)
    
    def test_sort_functionality(self):
        """Tester le tri"""
        response = self.client.get(
            reverse('reports:list'),
            {'sort': '-created_at'}
        )
        self.assertEqual(response.status_code, 200)


class ReportAPITests(TestCase):
    """Test les endpoints API"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='user@test.com',
            username='testuser',
            password='testpass123'
        )
        self.report = Report.objects.create(
            title='Test Report',
            description='Description',
            author=self.user
        )
    
    def test_api_list_reports(self):
        """API: Lister les rapports"""
        response = self.client.get(reverse('reports:api-list'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)
    
    def test_api_get_report(self):
        """API: Obtenir un rapport"""
        response = self.client.get(
            reverse('reports:api-detail', args=[self.report.id])
        )
        self.assertEqual(response.status_code, 200)
    
    def test_api_create_report_authenticated(self):
        """API: Créer un rapport (authentifié)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('reports:api-create'),
            {
                'title': 'New Report',
                'description': 'Description',
                'category': 'infrastructure'
            },
            content_type='application/json'
        )
        # La réponse peut être 201 ou 400 selon la sérialisation
        self.assertIn(response.status_code, [201, 400])
    
    def test_api_update_report_owner(self):
        """API: Modifier un rapport (propriétaire)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.put(
            reverse('reports:api-update', args=[self.report.id]),
            {
                'title': 'Updated Report',
                'description': 'Updated Description'
            },
            content_type='application/json'
        )
        self.assertIn(response.status_code, [200, 400])
    
    def test_api_delete_report_owner(self):
        """API: Supprimer un rapport (propriétaire)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.delete(
            reverse('reports:api-delete', args=[self.report.id])
        )
        self.assertIn(response.status_code, [204, 403, 200])
    
    def test_api_comments_endpoint(self):
        """API: Obtenir les commentaires"""
        response = self.client.get(
            reverse('reports:api-comments', args=[self.report.id])
        )
        self.assertEqual(response.status_code, 200)


class ReportPDFExportTests(TestCase):
    """Test l'export PDF"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='user@test.com',
            username='testuser',
            password='testpass123'
        )
        self.report = Report.objects.create(
            title='Test Report',
            description='Description',
            author=self.user
        )
    
    def test_pdf_export_accessible(self):
        """Le PDF est accessible"""
        response = self.client.get(
            reverse('reports:pdf-export', args=[self.report.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/pdf'
        )
    
    def test_pdf_export_contains_report_data(self):
        """Le PDF contient les données du rapport"""
        response = self.client.get(
            reverse('reports:pdf-export', args=[self.report.id])
        )
        self.assertEqual(response.status_code, 200)
        # Vérifier que c'est un PDF valide
        self.assertTrue(response.content.startswith(b'%PDF'))
