#!/usr/bin/env bash
# Démarrage rapide du projet CivicFix

echo "🚀 Démarrage du projet CivicFix..."

# Vérifier si la base de données existe
if [ ! -f "db.sqlite3" ]; then
    echo "📦 Création des migrations..."
    python manage.py makemigrations
    echo "📊 Application des migrations..."
    python manage.py migrate
    
    echo "👤 Création d'un superutilisateur..."
    echo "Email: admin@civicfix.com"
    echo "Mot de passe: admin123"
    python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@civicfix.com').exists():
    User.objects.create_superuser(
        email='admin@civicfix.com',
        username='admin',
        password='admin123',
        first_name='Admin',
        last_name='CivicFix'
    )
    print("✅ Superutilisateur créé!")
else:
    print("✅ Superutilisateur existe déjà!")
EOF
fi

echo "🎯 Lancement du serveur..."
echo "📱 Accédez à: http://127.0.0.1:8000/"
echo "🔐 Admin panel: http://127.0.0.1:8000/admin/"
echo "   Login: admin@civicfix.com / admin123"
echo ""
python manage.py runserver
