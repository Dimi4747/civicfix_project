# 📡 Documentation API CivicFix

## Vue d'ensemble

CivicFix fournit une API REST complète pour l'intégration avec d'autres applications. Tous les endpoints nécessitent une authentification via JWT (sauf quelques exceptions).

## Base URL

```
http://localhost:8000/api/
```

## Authentification

### Obtenir les tokens JWT

**Endpoint:** `POST /accounts/api/login/`

```bash
curl -X POST http://localhost:8000/accounts/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "votre_mot_de_passe"
  }'
```

**Réponse:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "role": "user"
  }
}
```

### Utiliser le token

Ajouter le header `Authorization`:

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/reports/api/reports/
```

### Rafraîchir le token

**Endpoint:** `POST /accounts/api/token/refresh/`

```bash
curl -X POST http://localhost:8000/accounts/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "votre_refresh_token"
  }'
```

## Endpoints d'authentification

### 1. Inscription

**Endpoint:** `POST /accounts/api/register/`

**Description:** Créer un nouveau compte utilisateur

**Paramètres (Body):**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "secure_password_123",
  "password_confirm": "secure_password_123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Réponse (201):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "message": "Inscription réussie!"
}
```

### 2. Connexion

**Endpoint:** `POST /accounts/api/login/`

**Description:** Authentifier un utilisateur

**Paramètres:**
```json
{
  "email": "user@example.com",
  "password": "secure_password_123"
}
```

**Réponse:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "role": "user",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### 3. Profil utilisateur

**Endpoint:** `GET /accounts/api/profile/`

**Description:** Récupérer le profil de l'utilisateur authentifié

**Headers:** `Authorization: Bearer TOKEN`

**Réponse (200):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "avatar": "url/avatar.jpg",
  "bio": "Ma biographie",
  "reputation_score": 150,
  "created_at": "2025-01-15T10:30:00Z",
  "profile": {
    "phone": "+33612345678",
    "department": "75",
    "notifications_enabled": true
  }
}
```

## Endpoints Rapports

### 1. Lister les rapports

**Endpoint:** `GET /reports/api/reports/`

**Description:** Récupérer tous les rapports avec filtrage optionnel

**Paramètres (Query):**
- `page` (int): Numéro de page (défaut: 1)
- `search` (str): Recherche par titre/description
- `status` (str): Filtrer par statut (open, in_progress, resolved, closed, rejected)
- `category` (str): Filtrer par catégorie
- `priority` (str): Filtrer par priorité (low, medium, high, critical)
- `ordering` (str): Tri (-created_at, -view_count, -vote_count)

**Exemple:**
```bash
curl "http://localhost:8000/reports/api/reports/?status=open&category=infrastructure&page=1" \
  -H "Authorization: Bearer TOKEN"
```

**Réponse (200):**
```json
{
  "count": 150,
  "next": "http://localhost:8000/reports/api/reports/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid-1",
      "title": "Nid de poule rue de la paix",
      "description": "Grande cavité dangereuse",
      "status": "open",
      "priority": "high",
      "category": "infrastructure",
      "author": {
        "id": "uuid",
        "username": "user123"
      },
      "location": "75001 Paris",
      "latitude": 48.8566,
      "longitude": 2.3522,
      "view_count": 45,
      "comment_count": 8,
      "vote_count": 12,
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T15:45:00Z"
    }
  ]
}
```

### 2. Créer un rapport

**Endpoint:** `POST /reports/api/reports/create/`

**Description:** Créer un nouveau rapport

**Headers:** `Authorization: Bearer TOKEN`

**Paramètres (Body - Form Data):**
```json
{
  "title": "Problème d'éclairage public",
  "description": "L'éclairage public est défaillant depuis une semaine",
  "category": "infrastructure",
  "priority": "medium",
  "location": "Avenue des Champs-Élysées",
  "latitude": 48.8697,
  "longitude": 2.3076,
  "attachments": [
    "file_id_1",
    "file_id_2"
  ]
}
```

**Réponse (201):**
```json
{
  "id": "uuid-new",
  "title": "Problème d'éclairage public",
  "description": "L'éclairage public est défaillant depuis une semaine",
  "status": "open",
  "category": "infrastructure",
  "priority": "medium",
  "author": {
    "id": "uuid",
    "username": "user123"
  },
  "created_at": "2025-01-16T08:00:00Z",
  "message": "Rapport créé avec succès!"
}
```

### 3. Obtenir un rapport

**Endpoint:** `GET /reports/api/reports/{id}/`

**Description:** Récupérer les détails complets d'un rapport

**Paramètres:**
- `id` (uuid): ID du rapport

**Réponse (200):**
```json
{
  "id": "uuid",
  "title": "Nid de poule rue de la paix",
  "description": "Grande cavité dangereuse",
  "status": "in_progress",
  "priority": "high",
  "category": "infrastructure",
  "author": {
    "id": "uuid-author",
    "username": "john_doe",
    "email": "john@example.com"
  },
  "assigned_to": {
    "id": "uuid-admin",
    "username": "admin_user"
  },
  "location": "75001 Paris",
  "latitude": 48.8566,
  "longitude": 2.3522,
  "view_count": 156,
  "comment_count": 18,
  "vote_count": 45,
  "resolution_notes": "En attente de ressources",
  "attachments": [
    {
      "id": "uuid",
      "file": "url/document.pdf",
      "file_size": 2048,
      "uploaded_at": "2025-01-15T10:35:00Z"
    }
  ],
  "comments": [
    {
      "id": "uuid",
      "author": {
        "username": "user123"
      },
      "content": "Merci pour ce signalement!",
      "is_internal": false,
      "created_at": "2025-01-15T11:00:00Z"
    }
  ],
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-16T09:15:00Z"
}
```

### 4. Modifier un rapport

**Endpoint:** `PUT /reports/api/reports/{id}/update/`

**Description:** Modifier un rapport (propriétaire ou admin)

**Headers:** `Authorization: Bearer TOKEN`

**Paramètres:**
- `id` (uuid): ID du rapport
- Corps: Champs à modifier (titre, description, statut, etc.)

**Body:**
```json
{
  "title": "Nid de poule rue de la paix - Réparé",
  "status": "resolved",
  "resolution_notes": "Réparation effectuée le 16/01/2025"
}
```

**Réponse (200):**
```json
{
  "id": "uuid",
  "title": "Nid de poule rue de la paix - Réparé",
  "status": "resolved",
  "resolution_notes": "Réparation effectuée le 16/01/2025",
  "message": "Rapport mis à jour avec succès!"
}
```

### 5. Supprimer un rapport

**Endpoint:** `DELETE /reports/api/reports/{id}/delete/`

**Description:** Supprimer un rapport (propriétaire ou admin)

**Headers:** `Authorization: Bearer TOKEN`

**Paramètres:**
- `id` (uuid): ID du rapport

**Réponse (204):** Pas de contenu

**En cas d'erreur (403):**
```json
{
  "error": "Vous n'avez pas la permission de supprimer ce rapport"
}
```

### 6. Obtenir les commentaires

**Endpoint:** `GET /reports/api/reports/{id}/comments/`

**Description:** Lister les commentaires d'un rapport

**Paramètres:**
- `id` (uuid): ID du rapport
- `page` (int): Pagination optionnelle

**Réponse (200):**
```json
{
  "count": 8,
  "results": [
    {
      "id": "uuid",
      "author": {
        "id": "uuid",
        "username": "user123"
      },
      "content": "Excellent signalement! Investigation en cours.",
      "is_internal": false,
      "created_at": "2025-01-15T11:00:00Z"
    }
  ]
}
```

### 7. Ajouter un commentaire

**Endpoint:** `POST /reports/api/reports/{id}/comment/`

**Description:** Ajouter un commentaire à un rapport

**Headers:** `Authorization: Bearer TOKEN`

**Paramètres:**
- `id` (uuid): ID du rapport

**Body:**
```json
{
  "content": "Merci pour votre réactivité!",
  "is_internal": false
}
```

**Réponse (201):**
```json
{
  "id": "uuid-new",
  "report": "uuid",
  "author": {
    "username": "user123"
  },
  "content": "Merci pour votre réactivité!",
  "is_internal": false,
  "created_at": "2025-01-16T09:30:00Z"
}
```

### 8. Voter sur un rapport

**Endpoint:** `POST /reports/api/reports/{id}/vote/`

**Description:** Ajouter un vote à un rapport

**Headers:** `Authorization: Bearer TOKEN`

**Paramètres:**
- `id` (uuid): ID du rapport

**Body:**
```json
{
  "vote_type": "upvote"
}
```

**Réponse (201):**
```json
{
  "id": "uuid",
  "report": "uuid",
  "user": "uuid",
  "vote_type": "upvote",
  "created_at": "2025-01-16T10:00:00Z"
}
```

## Endpoints Dashboard (Admin/Modérateur)

### 1. Statistiques globales

**Endpoint:** `GET /dashboard/api/stats/`

**Description:** Obtenir les statistiques du système

**Headers:** `Authorization: Bearer TOKEN` (admin/modérateur requis)

**Réponse (200):**
```json
{
  "total_reports": 245,
  "open_reports": 45,
  "in_progress_reports": 80,
  "resolved_reports": 100,
  "closed_reports": 20,
  "total_users": 1250,
  "total_comments": 3400,
  "total_votes": 8900,
  "reports_today": 12,
  "users_today": 3
}
```

### 2. Données pour graphiques

**Endpoint:** `GET /dashboard/api/chart-data/`

**Description:** Obtenir les données formatées pour les graphiques

**Réponse (200):**
```json
{
  "status_distribution": {
    "open": 45,
    "in_progress": 80,
    "resolved": 100,
    "closed": 20
  },
  "category_distribution": {
    "infrastructure": 60,
    "environment": 45,
    "health": 30,
    "education": 25,
    "transport": 50,
    "safety": 35
  },
  "priority_distribution": {
    "low": 50,
    "medium": 100,
    "high": 80,
    "critical": 15
  },
  "daily_reports_30d": [
    {"date": "2025-01-15", "count": 8},
    {"date": "2025-01-16", "count": 12}
  ]
}
```

### 3. Rapports récents

**Endpoint:** `GET /dashboard/api/recent-reports/`

**Description:** Obtenir les rapports les plus récents

**Paramètres:**
- `limit` (int): Nombre de résultats (défaut: 10)

**Réponse (200):**
```json
{
  "results": [
    {
      "id": "uuid",
      "title": "Problème de trottoir",
      "status": "open",
      "created_at": "2025-01-16T10:00:00Z",
      "author": "user123"
    }
  ]
}
```

### 4. Activité utilisateur

**Endpoint:** `GET /dashboard/api/user-activity/`

**Description:** Obtenir les logs d'activité des utilisateurs

**Paramètres:**
- `page` (int): Pagination
- `user` (uuid): Filtrer par utilisateur (optionnel)
- `activity_type` (str): Filtrer par type d'activité

**Réponse (200):**
```json
{
  "count": 500,
  "results": [
    {
      "id": "uuid",
      "user": "user123",
      "activity_type": "report_created",
      "description": "Rapport créé: Nid de poule",
      "timestamp": "2025-01-16T10:00:00Z",
      "ip_address": "192.168.1.1"
    }
  ]
}
```

## Codes de statut HTTP

| Code | Signification |
|------|---------------|
| 200 | Succès (GET, PUT) |
| 201 | Créé (POST) |
| 204 | Pas de contenu (DELETE) |
| 400 | Requête invalide |
| 401 | Non authentifié |
| 403 | Accès refusé |
| 404 | Non trouvé |
| 429 | Trop de requêtes |
| 500 | Erreur serveur |

## Rate Limiting

Les endpoints API sont limités à **100 requêtes par heure** par utilisateur.

En cas de dépassement: `HTTP 429 Too Many Requests`

## Exemples avec curl

### Créer un rapport

```bash
ACCESS_TOKEN="votre_token_ici"

curl -X POST http://localhost:8000/reports/api/reports/create/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Arbre tombé",
    "description": "Un arbre obstrue la route",
    "category": "environment",
    "priority": "high",
    "location": "Rue de la Paix"
  }'
```

### Filtrer les rapports ouverts

```bash
curl -X GET "http://localhost:8000/reports/api/reports/?status=open&ordering=-created_at" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Modifier le statut d'un rapport

```bash
REPORT_ID="uuid-du-rapport"
ACCESS_TOKEN="votre_token_ici"

curl -X PUT http://localhost:8000/reports/api/reports/$REPORT_ID/update/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "resolved",
    "resolution_notes": "Réparation effectuée"
  }'
```

## Erreurs courantes

### 401 Unauthorized
```json
{
  "detail": "Invalid token."
}
```
**Solution:** Vérifiez votre token JWT

### 403 Forbidden
```json
{
  "error": "Vous n'avez pas la permission d'accéder à cette ressource"
}
```
**Solution:** Vérifiez vos droits (admin/modérateur requis)

### 404 Not Found
```json
{
  "detail": "Not found."
}
```
**Solution:** Vérifiez l'ID de la ressource

## WebSocket (Notifications en temps réel)

**URL:** `ws://localhost:8000/ws/notifications/`

**Authentification:** Par token JWT en paramètre

```javascript
const token = "votre_token_ici";
const socket = new WebSocket(`ws://localhost:8000/ws/notifications/?token=${token}`);

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Nouvelle notification:', data);
};
```

## Versions futures

- [ ] GraphQL endpoint
- [ ] Webhooks
- [ ] Pagination par curseur
- [ ] Bulk operations
- [ ] Rate limiting par IP
- [ ] API versioning

---

**Dernière mise à jour:** 2025-01-16  
**Version API:** 1.0
