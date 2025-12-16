#!/usr/bin/env python
"""
Script d'installation automatique CivicFix
Exécute les étapes principales de configuration
"""

import os
import sys
import django
import subprocess
from pathlib import Path

# Ajouter le répertoire du projet au path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model

User = get_user_model()


def print_header(text):
    """Afficher un en-tête"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")


def print_success(text):
    """Afficher un message de succès"""
    print(f"✅ {text}")


def print_error(text):
    """Afficher un message d'erreur"""
    print(f"❌ {text}")


def print_info(text):
    """Afficher une information"""
    print(f"ℹ️  {text}")


def create_migrations():
    """Créer les migrations"""
    print_header("Création des migrations")
    try:
        call_command('makemigrations', verbosity=2)
        print_success("Migrations créées avec succès")
    except Exception as e:
        print_error(f"Erreur lors de la création des migrations: {e}")
        return False
    return True


def apply_migrations():
    """Appliquer les migrations"""
    print_header("Application des migrations")
    try:
        call_command('migrate', verbosity=2)
        print_success("Migrations appliquées avec succès")
    except Exception as e:
        print_error(f"Erreur lors de l'application des migrations: {e}")
        return False
    return True


def collect_static():
    """Collecter les fichiers statiques"""
    print_header("Collecte des fichiers statiques")
    try:
        call_command('collectstatic', interactive=False, verbosity=1)
        print_success("Fichiers statiques collectés avec succès")
    except Exception as e:
        print_error(f"Erreur lors de la collecte: {e}")
        return False
    return True


def create_superuser():
    """Créer un superutilisateur"""
    print_header("Création d'un superutilisateur")
    
    if User.objects.filter(username='admin').exists():
        print_info("Un administrateur existe déjà")
        return True
    
    try:
        email = input("Email de l'administrateur (admin@example.com): ").strip() or "admin@example.com"
        username = input("Nom d'utilisateur (admin): ").strip() or "admin"
        password = input("Mot de passe: ").strip()
        
        if not password:
            print_error("Le mot de passe est requis")
            return False
        
        User.objects.create_superuser(
            email=email,
            username=username,
            password=password
        )
        print_success(f"Superutilisateur '{username}' créé avec succès")
        return True
    except Exception as e:
        print_error(f"Erreur lors de la création du superutilisateur: {e}")
        return False


def create_test_data():
    """Créer des données de test"""
    print_header("Création de données de test")
    
    from apps.reports.models import Report
    from apps.accounts.models import User
    
    # Créer un utilisateur de test
    if not User.objects.filter(username='testuser').exists():
        user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpass123'
        )
        print_success(f"Utilisateur de test créé: testuser")
        
        # Créer quelques rapports de test
        categories = ['infrastructure', 'environment', 'health']
        for i in range(5):
            Report.objects.create(
                title=f"Rapport de test {i+1}",
                description=f"Description du rapport de test {i+1}",
                author=user,
                category=categories[i % len(categories)],
                priority=['low', 'medium', 'high'][i % 3]
            )
        print_success("5 rapports de test créés")
    else:
        print_info("L'utilisateur de test existe déjà")
    
    return True


def run_tests():
    """Exécuter les tests"""
    print_header("Exécution des tests")
    
    try:
        call_command('test', verbosity=2)
        print_success("Tous les tests ont réussi")
        return True
    except Exception as e:
        print_error(f"Certains tests ont échoué: {e}")
        return False


def verify_installation():
    """Vérifier l'installation"""
    print_header("Vérification de l'installation")
    
    # Vérifier Django
    try:
        import django
        print_success(f"Django {django.get_version()} installé")
    except ImportError:
        print_error("Django non installé")
        return False
    
    # Vérifier DRF
    try:
        import rest_framework
        print_success("Django REST Framework installé")
    except ImportError:
        print_error("Django REST Framework non installé")
        return False
    
    # Vérifier Channels
    try:
        import channels
        print_success("Django Channels installé")
    except ImportError:
        print_error("Django Channels non installé")
    
    # Vérifier Pillow
    try:
        import PIL
        print_success("Pillow installé")
    except ImportError:
        print_error("Pillow non installé")
    
    # Vérifier ReportLab
    try:
        import reportlab
        print_success("ReportLab installé")
    except ImportError:
        print_error("ReportLab non installé")
    
    # Vérifier la base de données
    try:
        from django.db import connection
        connection.ensure_connection()
        print_success("Connexion à la base de données réussie")
    except Exception as e:
        print_error(f"Erreur de connexion à la BD: {e}")
        return False
    
    return True


def display_next_steps():
    """Afficher les étapes suivantes"""
    print_header("Étapes suivantes")
    print("""
1. Démarrer le serveur:
   python manage.py runserver

2. Accéder à l'application:
   - Accueil: http://localhost:8000
   - Admin: http://localhost:8000/admin
   - API: http://localhost:8000/reports/api/reports/

3. Identifiants de test:
   - Email: admin@example.com
   - Nom d'utilisateur: admin

4. Documentation:
   - README.md - Vue d'ensemble du projet
   - INSTALLATION.md - Guide d'installation complet
   - API_DOCUMENTATION.md - Documentation de l'API REST

5. Modifier votre .env pour la configuration
    """)


def main():
    """Fonction principale"""
    print("\n")
    print("╔════════════════════════════════════════════════════════╗")
    print("║         🚀 Installation CivicFix v1.0                 ║")
    print("║     Plateforme de Signalement Civique en Django        ║")
    print("╚════════════════════════════════════════════════════════╝")
    
    steps = [
        ("Vérifier l'installation", verify_installation),
        ("Créer les migrations", create_migrations),
        ("Appliquer les migrations", apply_migrations),
        ("Collecter les fichiers statiques", collect_static),
        ("Créer un superutilisateur", create_superuser),
    ]
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                print_error(f"Échec de l'étape: {step_name}")
                sys.exit(1)
        except KeyboardInterrupt:
            print_error("\nInstallation annulée par l'utilisateur")
            sys.exit(1)
    
    # Demander si créer les données de test
    print_header("Données de test")
    response = input("Voulez-vous créer des données de test? (o/n): ").strip().lower()
    if response in ['o', 'oui', 'y', 'yes']:
        create_test_data()
    
    # Demander si exécuter les tests
    response = input("\nVoulez-vous exécuter les tests? (o/n): ").strip().lower()
    if response in ['o', 'oui', 'y', 'yes']:
        run_tests()
    
    # Afficher les étapes suivantes
    display_next_steps()
    
    print("\n✨ Installation terminée avec succès!\n")


if __name__ == '__main__':
    main()
