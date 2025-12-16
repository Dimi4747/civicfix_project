#!/usr/bin/env python
"""
Verification Script for Admin/Moderator System
Vérifie que toutes les composantes du système Admin/Modérateur sont correctement installées
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.dashboard.models import AuditLog, AdminNotification
from apps.reports.models import Report

User = get_user_model()

def check_models():
    """Vérifier les modèles de BD"""
    print("\n🔍 Vérification des Modèles...")
    
    try:
        # Test AuditLog
        count = AuditLog.objects.count()
        print(f"  ✅ AuditLog - {count} logs")
        
        # Test AdminNotification  
        count = AdminNotification.objects.count()
        print(f"  ✅ AdminNotification - {count} notifications")
        
        return True
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False

def check_users():
    """Vérifier les utilisateurs"""
    print("\n👥 Vérification des Utilisateurs...")
    
    admins = User.objects.filter(role='admin')
    moderators = User.objects.filter(role='moderator')
    users = User.objects.filter(role='user')
    
    print(f"  ✅ Administrateurs: {admins.count()}")
    for u in admins:
        print(f"     - {u.email}")
    
    print(f"  ✅ Modérateurs: {moderators.count()}")
    for u in moderators:
        print(f"     - {u.email}")
    
    print(f"  ✅ Utilisateurs: {users.count()}")
    
    return True

def check_files():
    """Vérifier les fichiers"""
    print("\n📁 Vérification des Fichiers...")
    
    files_to_check = [
        # Views
        'apps/dashboard/admin_views.py',
        'apps/dashboard/utils.py',
        
        # Templates
        'templates/dashboard/admin/users_list.html',
        'templates/dashboard/admin/user_detail.html',
        'templates/dashboard/admin/user_edit.html',
        'templates/dashboard/admin/reports_admin.html',
        'templates/dashboard/admin/report_manage.html',
        'templates/dashboard/moderator/queue.html',
        'templates/dashboard/moderator/moderate_report.html',
        'templates/dashboard/audit_log.html',
        'templates/dashboard/admin_notifications.html',
        
        # Docs
        'ADMIN_MODERATOR_GUIDE.md',
        'IMPLEMENTATION_COMPLETE.md',
    ]
    
    missing = []
    for file_path in files_to_check:
        full_path = os.path.join('/'.join(file_path.split('/')))
        if os.path.exists(full_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ MANQUANT: {file_path}")
            missing.append(file_path)
    
    return len(missing) == 0

def check_routes():
    """Vérifier les routes"""
    print("\n🔗 Vérification des Routes...")
    
    from django.urls import reverse
    
    routes = [
        # Admin
        'dashboard:users-list',
        'dashboard:user-detail',
        'dashboard:user-edit',
        'dashboard:user-toggle-status',
        'dashboard:user-unlock',
        'dashboard:user-delete',
        
        # Reports
        'dashboard:reports-admin',
        'dashboard:report-manage',
        'dashboard:report-delete',
        
        # Moderator
        'dashboard:moderator-queue',
        'dashboard:moderate-report',
        
        # Audit
        'dashboard:audit-log',
        'dashboard:admin-notifications',
    ]
    
    for route in routes:
        try:
            url = reverse(route, args=[1] if '<' in route or 'delete' in route or 'manage' in route or 'moderate' in route or 'toggle' in route or 'unlock' in route or 'edit' in route or 'detail' in route else [])
            print(f"  ✅ {route}")
        except Exception as e:
            print(f"  ❌ {route} - {e}")
            return False
    
    return True

def check_permissions():
    """Vérifier les décorateurs"""
    print("\n🔐 Vérification des Permissions...")
    
    try:
        from apps.accounts.decorators import admin_required, admin_or_moderator_required
        print(f"  ✅ @admin_required decorator")
        print(f"  ✅ @admin_or_moderator_required decorator")
        return True
    except Exception as e:
        print(f"  ❌ Erreur d'import décorateurs: {e}")
        return False

def check_utils():
    """Vérifier les utilitaires"""
    print("\n🛠️  Vérification des Utilitaires...")
    
    try:
        from apps.dashboard.utils import (
            log_admin_action,
            notify_admin,
            get_client_ip,
            ban_user,
            promote_user_to_moderator,
            demote_moderator_to_user,
            get_admin_stats
        )
        print(f"  ✅ log_admin_action")
        print(f"  ✅ notify_admin")
        print(f"  ✅ get_client_ip")
        print(f"  ✅ ban_user")
        print(f"  ✅ promote_user_to_moderator")
        print(f"  ✅ demote_moderator_to_user")
        print(f"  ✅ get_admin_stats")
        return True
    except Exception as e:
        print(f"  ❌ Erreur d'import utilitaires: {e}")
        return False

def main():
    """Exécuter toutes les vérifications"""
    print("\n" + "="*60)
    print("🛡️  VÉRIFICATION DU SYSTÈME ADMIN/MODÉRATEUR")
    print("="*60)
    
    results = {
        'Modèles BD': check_models(),
        'Utilisateurs': check_users(),
        'Fichiers': check_files(),
        'Routes': check_routes(),
        'Permissions': check_permissions(),
        'Utilitaires': check_utils(),
    }
    
    print("\n" + "="*60)
    print("📊 RÉSUMÉ")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {check_name}")
    
    print("="*60)
    print(f"\n🎯 Résultat: {passed}/{total} vérifications réussies")
    
    if passed == total:
        print("\n🎉 LE SYSTÈME EST CORRECTEMENT INSTALLÉ!")
        print("\n📍 Accès aux interfaces:")
        print("  - Admin Users: http://localhost:8000/dashboard/admin/users/")
        print("  - Admin Reports: http://localhost:8000/dashboard/admin/reports/")
        print("  - Moderator Queue: http://localhost:8000/dashboard/moderator/queue/")
        print("  - Audit Log: http://localhost:8000/dashboard/audit-log/")
        print("  - Notifications: http://localhost:8000/dashboard/admin-notifications/")
        return 0
    else:
        print("\n⚠️  CERTAINES VÉRIFICATIONS ONT ÉCHOUÉ")
        print("Voir les détails ci-dessus pour corriger les problèmes.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
