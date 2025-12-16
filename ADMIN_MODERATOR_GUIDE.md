# 🛡️ Système Complet Admin/Modérateur - Documentation

## Vue d'ensemble

Ce document détaille la mise en œuvre complète du système d'administration et de modération pour CivicFix, incluant la gestion des utilisateurs, des rapports, l'audit et les notifications.

---

## 🏗️ Architecture du Système

### Modèles Principaux

#### 1. **AuditLog** - Journal d'Audit
```python
# Enregistre toutes les actions des administrateurs et modérateurs
- actor: User (qui a effectué l'action)
- action: Choix prédéfinis (20+ types d'actions)
- target_user: User (utilisateur affecté, optionnel)
- target_report: Report (rapport affecté, optionnel)
- description: Texte lisible par l'humain
- old_value / new_value: Pour le suivi des changements
- ip_address / user_agent: Contexte de sécurité
- created_at: Timestamp
```

**Actions Disponibles:**
- Gestion Utilisateurs: `user_created`, `user_modified`, `user_deleted`, `user_activated`, `user_deactivated`, `role_changed`, `password_reset`
- Gestion Rapports: `report_status_changed`, `report_assigned`, `report_deleted`, `report_modified`, `internal_note_added`, `resolution_note_added`
- Modération: `report_reviewed`, `comment_approved`, `comment_rejected`

#### 2. **AdminNotification** - Notifications Admin
```python
# Notifications ciblées pour les administrateurs et modérateurs
- recipient: User (destinataire)
- notification_type: Choix (report_flagged, user_suspicious, urgent_report, system_alert, task_assigned)
- title / message: Contenu
- related_report / related_user: Références
- is_read / is_resolved: État
- created_at / read_at: Timestamps
```

---

## 👨‍💼 Capacités par Rôle

### 👑 Administrateur
| Fonction | Accès | Actions |
|----------|-------|---------|
| **Gestion Utilisateurs** | Complet | CRUD, changement de rôle, (dés)activation, déverrouillage |
| **Gestion Rapports** | Complet | Édition, suppression, statut, assignment, notes |
| **Modération** | Oui | Accès aux rapports, modération complète |
| **Journal d'Audit** | Lecture | Voir tout l'historique |
| **Permissions** | Oui | Peut tout faire |

**Routes Admin:**
- `GET /dashboard/admin/users/` - Liste des utilisateurs
- `GET /dashboard/admin/users/<id>/` - Détail utilisateur
- `GET /dashboard/admin/users/<id>/edit/` - Éditer utilisateur
- `POST /dashboard/admin/users/<id>/toggle-status/` - (Dés)activer
- `POST /dashboard/admin/users/<id>/unlock/` - Déverrouiller
- `POST /dashboard/admin/users/<id>/delete/` - Supprimer
- `GET /dashboard/admin/reports/` - Gestion rapports
- `GET /dashboard/admin/reports/<id>/manage/` - Gérer un rapport
- `POST /dashboard/admin/reports/<id>/delete/` - Supprimer un rapport
- `GET /dashboard/audit-log/` - Journal d'audit

### 🛡️ Modérateur
| Fonction | Accès | Actions |
|----------|-------|---------|
| **Ma File** | Assignés | Voir rapports assignés |
| **Modération** | Rapports assignés | Changer statut, ajouter notes |
| **Journal d'Audit** | Lecture limité | Voir ses propres actions |
| **Permissions** | Non | Pas d'accès admin |
| **Créer Rapports** | Oui | Peut signaler des problèmes |

**Routes Modérateur:**
- `GET /dashboard/moderator/queue/` - Ma file de modération
- `GET /dashboard/moderator/reports/<id>/` - Modérer un rapport
- `GET /dashboard/admin-notifications/` - Mes notifications

### 👤 Utilisateur Régulier
| Fonction | Accès | Actions |
|----------|-------|---------|
| **Créer Rapports** | Oui | Soumettre des rapports |
| **Voir Ses Rapports** | Propres rapports | Consultation |
| **Commenter** | Oui | Ajouter des commentaires |
| **Admin/Modérateur** | Non | Pas d'accès |

---

## 🔐 Sécurité et Permissions

### Décorateurs de Sécurité
```python
from apps.accounts.decorators import admin_required, admin_or_moderator_required

@admin_required
def admin_only_view(request):
    """Accès Admin uniquement"""
    pass

@admin_or_moderator_required  
def admin_or_moderator_view(request):
    """Accès Admin ou Modérateur"""
    pass
```

### Vérifications d'Accès
```python
# Dans les vues
if not request.user.is_admin():
    return HttpResponseForbidden()

# Dans les templates
{% if request.user.is_admin %}
    {# Contenu admin #}
{% endif %}
```

### Logging Automatique
```python
from apps.dashboard.utils import log_admin_action

# Chaque action sensible est loggée
log_admin_action(
    actor=request.user,
    action='report_status_changed',
    description="Statut changé de 'open' à 'resolved'",
    target_report=report,
    old_value='open',
    new_value='resolved',
    ip_address=get_client_ip(request)
)
```

---

## 📋 Vues et Templates

### Admin - Gestion Utilisateurs
**Vue:** `apps/dashboard/admin_views.py::users_list_view`
**Template:** `dashboard/admin/users_list.html`
- Liste paginée de tous les utilisateurs
- Filtres: Recherche, Rôle, Statut (actif/inactif/verrouillé)
- Actions: Voir détails, Éditer, Activer/Désactiver, Déverrouiller, Supprimer

**Détail Utilisateur:**
- Informations personnelles
- Historique de connexion
- Rapports créés
- Journal d'audit des actions
- Actions rapides: Activer/Désactiver, Déverrouiller, Supprimer

### Admin - Gestion Rapports
**Vue:** `apps/dashboard/admin_views.py::reports_admin_view`
**Template:** `dashboard/admin/reports_admin.html`
- Liste paginée de tous les rapports
- Filtres: Recherche, Statut, Priorité
- Tableau avec colonnes: Titre, Auteur, Catégorie, Statut, Priorité, Date, Actions

**Gérer Rapport:**
- Édition: Titre, Description
- Changement: Statut, Priorité, Catégorie
- Assignment à un modérateur
- Ajout de notes internes
- Affichage des notes précédentes

### Modérateur - File de Modération
**Vue:** `apps/dashboard/admin_views.py::moderator_queue_view`
**Template:** `dashboard/moderator/queue.html`
- Liste des rapports assignés
- Filtrage par statut
- Statistiques: Total, Ouverts, En Cours, Résolus
- Cartes informatives pour chaque rapport

**Modérer Rapport:**
**Vue:** `apps/dashboard/admin_views.py::moderate_report_view`
**Template:** `dashboard/moderator/moderate_report.html`
- Vue complète du rapport
- Affichage des commentaires
- Notes internes visibles
- Formulaire de modération:
  - Changement de statut
  - Ajout de notes de résolution
  - Ajout de commentaires internes

### Journal d'Audit
**Vue:** `apps/dashboard/admin_views.py::audit_log_view`
**Template:** `dashboard/audit_log.html`
- Table complète des logs
- Filtres: Action, Acteur, Date
- Colonnes: Date/Heure, Acteur, Action, Cible, Description, Changements
- Détails des modifications (avant/après)

### Notifications Admin
**Vue:** `apps/dashboard/admin_views.py::admin_notifications_view`
**Template:** `dashboard/admin_notifications.html`
- Notifications ciblées par destinataire
- Marquage comme lu/résolu
- Liens vers rapports/utilisateurs
- Types: Rapport signalé, Activité suspecte, Urgent, Alerte, Tâche

---

## 🔄 Workflows Principaux

### Workflow 1: Gestion d'un Utilisateur
```
Admin accède à /dashboard/admin/users/
    ↓
Admin filtre/recherche un utilisateur
    ↓
Admin clique "Voir" → user_detail_view
    ↓
Admin choisit une action:
    - Éditer: user_edit_view → change rôle/infos → AuditLog.log_action('role_changed' ou 'user_modified')
    - Désactiver: user_toggle_status_view → AuditLog.log_action('user_deactivated')
    - Déverrouiller: user_unlock_view → AuditLog.log_action('user_modified')
    - Supprimer: user_delete_view → AuditLog.log_action('user_deleted')
    ↓
Message de succès
    ↓
Journalisation dans AuditLog
```

### Workflow 2: Modération d'un Rapport
```
Modérateur accède à /dashboard/moderator/queue/
    ↓
Modérateur voit ses rapports assignés
    ↓
Modérateur clique "Modérer Maintenant"
    ↓
moderate_report_view (avec permission check)
    ↓
Modérateur:
    - Change le statut du rapport
    - Ajoute une note de résolution
    - Ajoute un commentaire interne
    ↓
Form POST → moderate_report_view
    ↓
Toutes les modifications loggées dans AuditLog
    ↓
Messages de succès
    ↓
Redirection vers la même page ou file
```

### Workflow 3: Audit Trail
```
Toute action sensible:
    ↓
log_admin_action() appelé
    ↓
AuditLog.objects.create():
    - actor (qui)
    - action (quoi)
    - description (comment)
    - target_user/target_report (sur qui/quoi)
    - old_value/new_value (changement)
    - ip_address/user_agent (contexte)
    ↓
Accessible dans /dashboard/audit-log/
    ↓
Filtrable par action, acteur, date
    ↓
Traçabilité complète
```

---

## 🛠️ Installation et Configuration

### 1. Migration de la Base de Données
```bash
python manage.py makemigrations dashboard
python manage.py migrate dashboard
```

### 2. Vérification des Modèles
```bash
python manage.py shell
>>> from apps.dashboard.models import AuditLog, AdminNotification
>>> AuditLog.objects.count()
>>> AdminNotification.objects.count()
```

### 3. Création de Utilisateurs Test (Admin/Modérateur)
```bash
python manage.py create_test_users

# Créera:
# - admin@civicfix.test (Administrateur)
# - moderator@civicfix.test (Modérateur)  
# - user@civicfix.test (Utilisateur régulier)
```

### 4. Accès aux Interfaces
- **Admin Panel:** `/dashboard/admin/users/`
- **Modérateur Queue:** `/dashboard/moderator/queue/`
- **Audit Log:** `/dashboard/audit-log/`
- **Notifications:** `/dashboard/admin-notifications/`

---

## 📊 Utilisation de l'API d'Audit

### Logging d'Actions
```python
from apps.dashboard.utils import log_admin_action, get_client_ip

# Logging complet
log_admin_action(
    actor=request.user,
    action='user_modified',
    description="Email modifié",
    target_user=modified_user,
    old_value='old@email.com',
    new_value='new@email.com',
    ip_address=get_client_ip(request),
    user_agent=request.META.get('HTTP_USER_AGENT')
)
```

### Notification Admin
```python
from apps.dashboard.utils import notify_admin

# Notifier tous les admins
notify_admin(
    title="Rapport urgent détecté",
    message=f"Un rapport critique a été créé par {user.email}",
    notification_type='urgent_report',
    related_report=report
)

# Notifier un modérateur spécifique
notify_admin(
    title="Nouveau rapport assigné",
    message=f"Rapport: {report.title}",
    notification_type='task_assigned',
    recipient=moderator,
    related_report=report
)
```

### Fonctions Utilitaires
```python
from apps.dashboard.utils import (
    ban_user,
    promote_user_to_moderator,
    demote_moderator_to_user,
    get_admin_stats
)

# Ban un utilisateur
ban_user(
    user=bad_user,
    reason="Abus de signalement",
    admin=request.user
)

# Promouvoir un utilisateur
promote_user_to_moderator(user=promoted_user, admin=request.user)

# Rétrograder un modérateur
demote_moderator_to_user(user=demoted_moderator, admin=request.user)

# Obtenir les statistiques
stats = get_admin_stats()
print(stats['total_users'], stats['pending_reports'])
```

---

## 🎯 Points Clés de Sécurité

### ✓ Accès Contrôlé
- Tous les endpoints admin/modérateur protégés par décorateurs
- Vérifications d'autorisation dans les vues
- Permissions en base de données

### ✓ Audit Complet
- Chaque action loggée avec horodatage
- Traçabilité de qui a fait quoi quand et pourquoi
- IP et User Agent enregistrés

### ✓ Prévention d'Abus
- Les admins ne peuvent pas supprimer leur propre compte
- Les modérateurs n'ont accès qu'à leurs rapports assignés
- Verrouillage de compte après tentatives échouées

### ✓ Notifications
- Les modérateurs avertis des nouvelles tâches
- Les admins alertés des problèmes critiques
- Historique complet des notifications

---

## 🔧 Dépannage

### Problème: Permission Denied (403)
**Solution:** Vérifier le rôle de l'utilisateur
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(email='test@example.com')
>>> print(user.role)  # Doit être 'admin' ou 'moderator'
```

### Problème: Journal d'audit vide
**Solution:** Vérifier les migrations
```bash
python manage.py showmigrations dashboard
python manage.py migrate dashboard
```

### Problème: Templates non trouvés
**Solution:** Vérifier la structure des répertoires
```
templates/
├── dashboard/
│   ├── admin/
│   │   ├── users_list.html
│   │   ├── user_detail.html
│   │   ├── user_edit.html
│   │   ├── reports_admin.html
│   │   └── report_manage.html
│   └── moderator/
│       ├── queue.html
│       └── moderate_report.html
```

---

## 📈 Cas d'Usage

### Cas 1: Un utilisateur signale trop de faux positifs
```
Admin détecte pattern dans audit log
    ↓
Admin accède au profil de l'utilisateur
    ↓
Admin active "Ban User" depuis le dashboard
    ↓
Utilisateur désactivé, action loggée
    ↓
Notification envoyée aux modérateurs
```

### Cas 2: Promouvoir un utilisateur de confiance
```
Admin voit activité positive d'un utilisateur
    ↓
Admin utilise function promote_user_to_moderator()
    ↓
Rôle changé de 'user' à 'moderator'
    ↓
Accès au /dashboard/moderator/queue/ activé
    ↓
Premier rapports assigné
```

### Cas 3: Audit d'une action douteuse
```
Admin voit log anormal dans audit dashboard
    ↓
Admin clique sur le log pour voir détails
    ↓
Avant/Après values affichés
    ↓
Contexte (IP, user agent) disponible
    ↓
Admin peut confronter l'acteur si nécessaire
```

---

## 🚀 Améliorations Futures

1. **Export de Rapports**: Exporter audit logs en CSV/PDF
2. **Alertes Email**: Notifier les admins par email
3. **Webhook**: Intégrations externes des événements
4. **2FA Admin**: Double authentification pour admins
5. **Historique Avancé**: Timeline visuelle des changements
6. **Bulk Actions**: Modifier plusieurs utilisateurs/rapports
7. **Scheduled Reports**: Rapports d'audit automatiques
8. **Approvals**: Workflow d'approbation pour actions sensibles

---

## 📞 Support

Pour toute question ou problème:
1. Consulter les logs d'erreur: `/dashboard/audit-log/`
2. Vérifier les logs système Django
3. Consulter les notifications: `/dashboard/admin-notifications/`
4. Réviser ce document

---

**Version:** 1.0  
**Dernière mise à jour:** 2024  
**Statut:** Production Ready ✅
