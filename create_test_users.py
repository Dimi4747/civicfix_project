"""
Script to create test admin and moderator users
Run: python manage.py shell < create_test_users.py
"""

from django.contrib.auth import get_user_model

User = get_user_model()

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
print(f"✅ Admin créé: {admin.email} (Mot de passe: Admin12345!)")

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
print(f"✅ Modérateur créé: {moderator.email} (Mot de passe: Moderator12345!)")

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
print(f"✅ Utilisateur créé: {user.email} (Mot de passe: User12345!)")

print("\n=== UTILISATEURS TEST ===")
print("\n👑 ADMINISTRATEUR:")
print(f"   Email: {admin.email}")
print(f"   Mot de passe: Admin12345!")
print(f"   Accès: Tableau de bord complet + Gestion utilisateurs")

print("\n🛡️  MODÉRATEUR:")
print(f"   Email: {moderator.email}")
print(f"   Mot de passe: Moderator12345!")
print(f"   Accès: Gestion des rapports + Modération")

print("\n👤 UTILISATEUR:")
print(f"   Email: {user.email}")
print(f"   Mot de passe: User12345!")
print(f"   Accès: Créer et consulter les rapports")
