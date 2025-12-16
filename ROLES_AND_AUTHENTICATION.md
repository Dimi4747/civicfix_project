# 🔐 Système de Rôles et Authentification - CivicFix

## Vue d'ensemble

Le système d'authentification CivicFix supporte 3 rôles utilisateur avec des interfaces et permissions différentes:

### 1. **👑 Administrateur (Admin)**
- Accès complet à toutes les fonctionnalités
- Gestion des utilisateurs
- Gestion des rapports
- Statistiques avancées
- Voir l'historique d'activité
- Gérer les notifications système

### 2. **🛡️ Modérateur (Moderator)**
- Modération des signalements
- Traitement des rapports
- Voir l'historique d'activité
- Pas d'accès à la gestion des utilisateurs

### 3. **👤 Utilisateur Regular (User)**
- Créer des signalements
- Voir tous les rapports
- Consulter ses propres rapports
- Pas d'accès au tableau de bord

---

## 🚀 Démarrage Rapide

### Créer les utilisateurs de test

```bash
python manage.py create_test_users
```

Cela crée automatiquement:
- **Admin**: `admin@civicfix.test` / `Admin12345!`
- **Modérateur**: `moderator@civicfix.test` / `Moderator12345!`
- **Utilisateur**: `user@civicfix.test` / `User12345!`

### Connexion

1. Allez à [http://localhost:8000/accounts/login/](http://localhost:8000/accounts/login/)
2. Connectez-vous avec vos identifiants
3. Vous serez automatiquement redirigé selon votre rôle:
   - **Admin/Modérateur** → Dashboard (`/dashboard/`)
   - **Utilisateur** → Accueil (`/`)

---

## 📋 Flux de Redirection

```
┌─────────────────┐
│  Connexion OK   │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Rôle ?  │
    └────┬────┘
         │
    ┌────┴──────────┬──────────────┐
    │               │              │
  ADMIN         MODERATOR         USER
    │               │              │
    └───┬───────────┘              │
        │                          │
        ▼                          ▼
  /dashboard/          /accounts/home/
  (Interface           (Interface
   complète)            utilisateur)
```

---

## 🔐 Décorateurs de Sécurité

### Pour les Admin uniquement
```python
from apps.accounts.decorators import admin_required

@admin_required
def my_admin_view(request):
    # Code accessible uniquement aux administrateurs
    pass
```

### Pour les Admin et Modérateurs
```python
from apps.accounts.decorators import admin_or_moderator_required

@admin_or_moderator_required
def my_moderator_view(request):
    # Code accessible aux admin et modérateurs
    pass
```

---

## 📱 Interfaces par Rôle

### Dashboard Admin (`/dashboard/`)
- **Widgets**: Metrics, Charts, Reports
- **Menu Principal**:
  - 📊 Gestion Rapports
  - 👥 Gestion Utilisateurs
  - 📈 Statistiques
  - 📋 Historique d'Activité
  - 🔔 Notifications

### Dashboard Modérateur (`/dashboard/`)
- **Menu Principal**:
  - 📊 Modérer les Signalements
  - 📋 Historique d'Activité

### Interface Utilisateur
- Créer un nouveau rapport (`/reports/create/`)
- Voir tous les rapports (`/reports/`)
- Consulter mes rapports (`/reports/my_reports/`)
- Modifier mon profil (`/accounts/profile/edit/`)

---

## 🛠️ Gestion des Rôles

### Assigner un rôle à un utilisateur

#### Via Django Shell
```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.get(email='email@example.com')
user.role = 'admin'  # ou 'moderator' ou 'user'
user.save()
```

#### Via Django Admin
1. Allez à `/admin/`
2. Sélectionnez l'utilisateur
3. Changez le champ `role`
4. Sauvegardez

---

## 🔍 Vérification des Rôles

### Dans les Templates
```html
{% if user.role == 'admin' %}
    <!-- Contenu pour les admins -->
{% elif user.role == 'moderator' %}
    <!-- Contenu pour les modérateurs -->
{% else %}
    <!-- Contenu pour les utilisateurs -->
{% endif %}
```

### Dans les Vues
```python
# Vérifier si admin
if request.user.role == 'admin':
    # ...

# Utiliser les méthodes du modèle
if request.user.is_admin():
    # ...

if request.user.is_moderator():
    # ...
```

---

## 🎛️ Menu Utilisateur

Le menu utilisateur (en haut à droite) affiche:
- Badge de rôle avec couleur:
  - 👑 **Jaune** pour Admin
  - 🛡️ **Vert** pour Modérateur
  - 👤 **Bleu** pour Utilisateur
- Liens d'accès rapide au Dashboard (pour admin/modérateur)
- Lien vers Mon Profil, Mes Rapports, Sécurité
- Bouton Déconnexion

---

## 📊 Exemple: Créer un Admin depuis Django Admin

1. Créez un utilisateur normal
2. Connectez-vous à `/admin/`
3. Allez dans "Utilisateurs"
4. Sélectionnez l'utilisateur
5. Changez le rôle de "Utilisateur" à "Administrateur"
6. Sauvegardez

L'utilisateur aura maintenant accès au Dashboard Admin!

---

## ⚠️ Important

- Les mots de passe des utilisateurs de test sont fournis à titre d'exemple
- **Ne pas utiliser en production** - Changez tous les mots de passe
- Les permissions sont vérifiées côté serveur (sécurité)
- Les redirections sont automatiques selon le rôle

---

## 📞 Support

Pour plus de détails sur:
- L'authentification → Voir `apps/accounts/views.py`
- Les modèles → Voir `apps/accounts/models.py`
- Les décorateurs → Voir `apps/accounts/decorators.py`
- Les vues du dashboard → Voir `apps/dashboard/views.py`
