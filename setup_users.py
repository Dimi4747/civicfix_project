#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import User

# Admin
if not User.objects.filter(email='admin@test.com').exists():
    User.objects.create_superuser(
        email='admin@test.com',
        password='TestPassword123!'
    )
    print("✅ Admin créé: admin@test.com")

# User normal
if not User.objects.filter(email='user@test.com').exists():
    User.objects.create_user(
        email='user@test.com',
        password='TestPassword123!',
        first_name='Test',
        last_name='User',
        username='testuser'
    )
    print("✅ User créé: user@test.com")

print("\n✅ Tous les utilisateurs sont prêts!")
print("📧 Utilisateurs disponibles:")
print("   - admin@test.com / TestPassword123!")
print("   - user@test.com / TestPassword123!")
