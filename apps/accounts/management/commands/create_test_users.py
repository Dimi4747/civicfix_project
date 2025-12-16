"""
Django management command to create test users
Usage: python manage.py create_test_users
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test admin and moderator users'

    def handle(self, *args, **options):
        # Delete existing test users
        User.objects.filter(email__in=['admin@civicfix.test', 'moderator@civicfix.test', 'user@civicfix.test']).delete()

        # Create Admin User
        admin = User.objects.create_user(
            email='admin@civicfix.test',
            username='admin_test',
            password='Admin12345!',
            first_name='Admin',
            last_name='Test',
            role='admin',
            is_verified=True
        )
        self.stdout.write(self.style.SUCCESS(f'✅ Admin créé: {admin.email}'))

        # Create Moderator User
        moderator = User.objects.create_user(
            email='moderator@civicfix.test',
            username='moderator_test',
            password='Moderator12345!',
            first_name='Moderator',
            last_name='Test',
            role='moderator',
            is_verified=True
        )
        self.stdout.write(self.style.SUCCESS(f'✅ Modérateur créé: {moderator.email}'))

        # Create Regular User
        user = User.objects.create_user(
            email='user@civicfix.test',
            username='user_test',
            password='User12345!',
            first_name='User',
            last_name='Test',
            role='user',
            is_verified=True
        )
        self.stdout.write(self.style.SUCCESS(f'✅ Utilisateur créé: {user.email}'))

        self.stdout.write(self.style.SUCCESS('\n=== UTILISATEURS TEST CRÉÉS ==='))
        self.stdout.write(self.style.WARNING('\n👑 ADMINISTRATEUR:'))
        self.stdout.write(f'   Email: {admin.email}')
        self.stdout.write(f'   Mot de passe: Admin12345!')
        self.stdout.write('   Accès: Tableau de bord complet + Gestion utilisateurs')

        self.stdout.write(self.style.WARNING('\n🛡️  MODÉRATEUR:'))
        self.stdout.write(f'   Email: {moderator.email}')
        self.stdout.write(f'   Mot de passe: Moderator12345!')
        self.stdout.write('   Accès: Gestion des rapports + Modération')

        self.stdout.write(self.style.WARNING('\n👤 UTILISATEUR:'))
        self.stdout.write(f'   Email: {user.email}')
        self.stdout.write(f'   Mot de passe: User12345!')
        self.stdout.write('   Accès: Créer et consulter les rapports')
