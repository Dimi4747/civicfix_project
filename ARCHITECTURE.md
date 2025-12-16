# 🏗️ Architecture CivicFix

## Vue d'ensemble système

```
┌─────────────────────────────────────────────────────────────┐
│                     Couche Présentation                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Frontend (HTML/CSS/JS avec TailwindCSS)            │   │
│  │  - Templates Django                                  │   │
│  │  - SPA Assets (Chart.js, Font Awesome)              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   Couche Application                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Django 6.0 Application Server                      │   │
│  │  - Views (Function-based & Class-based)             │   │
│  │  - Forms (Django Forms)                             │   │
│  │  - Middleware (Authentication, CORS, etc.)          │   │
│  │  - URL Routing (urls.py)                            │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  REST API (Django REST Framework)                   │   │
│  │  - JWT Authentication (SimpleJWT)                   │   │
│  │  - Pagination & Filtering                           │   │
│  │  - Rate Limiting & Throttling                       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   Couche Métier                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Models Django (ORM)                                │   │
│  │  - User & UserProfile                              │   │
│  │  - Report & ReportComment & ReportAttachment       │   │
│  │  - DashboardStats & UserActivityLog                │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Signals & Handlers                                │   │
│  │  - Auto-create UserProfile on User creation         │   │
│  │  - Audit trail updates                              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   Couche Persistance                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  SQLite (Développement) / PostgreSQL (Production)   │   │
│  │  - Tables: users, reports, comments, attachments    │   │
│  │  - Migrations Django (Database Schema)              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Structure des applications

### 1️⃣ Apps (Applications Django)

```
apps/
├── accounts/                 # Gestion des utilisateurs
│   ├── models.py            # User, UserProfile, LoginHistory
│   ├── views.py             # Auth views & API endpoints
│   ├── forms.py             # Registration, Login, Profile forms
│   ├── urls.py              # Routes (/accounts/...)
│   ├── admin.py             # Admin customization
│   ├── signals.py           # Signal handlers
│   └── apps.py              # App configuration
│
├── reports/                  # Gestion des rapports
│   ├── models.py            # Report, Comment, Attachment, Vote, History
│   ├── views.py             # CRUD views & API endpoints
│   ├── forms.py             # Report, Comment, Filter forms
│   ├── urls.py              # Routes (/reports/...)
│   ├── admin.py             # Admin customization
│   └── apps.py              # App configuration
│
└── dashboard/               # Statistiques & Admin
    ├── models.py            # DashboardStats, ActivityLog, Notification
    ├── views.py             # Dashboard views & API
    ├── urls.py              # Routes (/dashboard/...)
    ├── admin.py             # Admin customization
    └── apps.py              # App configuration
```

### 2️⃣ Configuration Globale

```
config/
├── settings.py              # Paramètres Django (230+ lignes)
│   ├── INSTALLED_APPS
│   ├── DATABASES
│   ├── REST_FRAMEWORK
│   ├── AUTHENTICATION_CLASSES
│   ├── MIDDLEWARE
│   ├── TEMPLATES
│   └── STATIC_FILES
├── urls.py                  # Routeur principal
├── asgi.py                  # ASGI pour WebSocket (Channels)
└── wsgi.py                  # WSGI pour production
```

### 3️⃣ Templates

```
templates/
├── base.html                # Template de base (navigation, footer)
├── home.html                # Page d'accueil
├── accounts/
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── profile_edit.html
│   └── password_change.html
├── reports/
│   ├── list.html            # Lister avec filtres
│   ├── detail.html          # Détails + commentaires
│   ├── create.html
│   ├── edit.html
│   ├── my_reports.html
│   └── delete_confirm.html
└── dashboard/
    ├── index.html           # Tableau de bord principal
    ├── reports.html
    ├── users.html
    ├── statistics.html
    ├── activity.html
    └── notifications.html
```

### 4️⃣ Fichiers Statiques

```
static/
├── css/
│   └── style.css            # Styles personnalisés (250+ lignes)
├── js/
│   ├── chart.js             # Chart.js CDN
│   ├── tailwind.js          # TailwindCSS CDN
│   └── app.js               # Application JS personnalisée
└── images/
    └── logo.png
```

## Modèles de données (Schéma)

### User Model (Comptes)

```python
class User(AbstractUser):
    id              # UUID primary key
    email           # Unique
    username        # Unique
    password        # Hashed
    first_name      # Optional
    last_name       # Optional
    role            # 'admin', 'moderator', 'user'
    avatar          # Image file
    bio             # TextField
    is_active       # Boolean
    failed_login_attempts  # Integer (sécurité)
    locked_until    # DateTime (account lockout)
    created_at      # DateTime
    updated_at      # DateTime
```

### UserProfile Model

```python
class UserProfile:
    user            # OneToOne FK
    phone           # Optional
    department      # Région/Département
    reputation_score # Integer
    email_verified  # Boolean
    notifications_enabled  # Boolean
    created_at      # DateTime
    updated_at      # DateTime
```

### Report Model (Rapports)

```python
class Report:
    id              # UUID primary key
    title           # CharField
    description     # TextField
    status          # Choices: open, in_progress, resolved, closed, rejected
    priority        # Choices: low, medium, high, critical
    category        # Choices: infrastructure, environment, health, education, transport, safety, other
    author          # FK User
    assigned_to     # FK User (nullable)
    location        # CharField
    latitude        # FloatField (nullable)
    longitude       # FloatField (nullable)
    resolution_notes # TextField (nullable)
    view_count      # Integer
    created_at      # DateTime
    updated_at      # DateTime
```

### ReportComment Model

```python
class ReportComment:
    id              # UUID primary key
    report          # FK Report
    author          # FK User
    content         # TextField
    is_internal     # Boolean (visible admin seulement)
    created_at      # DateTime
    updated_at      # DateTime
```

### ReportAttachment Model

```python
class ReportAttachment:
    id              # UUID primary key
    report          # FK Report
    file            # FileField
    file_size       # Integer
    uploaded_at     # DateTime
```

### ReportVote Model

```python
class ReportVote:
    id              # UUID primary key
    report          # FK Report
    user            # FK User
    vote_type       # Choices: 'upvote', 'downvote'
    created_at      # DateTime
    unique_together # (report, user)
```

### ReportHistory Model (Audit Trail)

```python
class ReportHistory:
    id              # UUID primary key
    report          # FK Report
    field_name      # CharField
    old_value       # TextField
    new_value       # TextField
    changed_by      # FK User
    changed_at      # DateTime
```

### DashboardStats Model

```python
class DashboardStats:
    id              # UUID primary key
    date            # Date
    total_reports   # Integer
    open_reports    # Integer
    in_progress_reports  # Integer
    resolved_reports # Integer
    closed_reports  # Integer
    rejected_reports # Integer
    total_users     # Integer
    total_comments  # Integer
    total_votes     # Integer
    created_at      # DateTime
```

## Flux d'authentification

```
┌──────────────┐
│   Client     │
└──────┬───────┘
       │
       │ 1. POST /accounts/api/login/
       │    { email, password }
       ↓
┌──────────────────────────────┐
│   Django Auth Backend         │
│   - Validate credentials      │
│   - Check user role           │
│   - Track failed attempts     │
└──────┬───────────────────────┘
       │
       │ 2. Generate JWT Tokens
       ↓
┌──────────────────────────────┐
│   SimpleJWT Token Handler     │
│   - Access Token (1h)         │
│   - Refresh Token (7d)        │
└──────┬───────────────────────┘
       │
       │ 3. Return tokens to client
       ↓
┌──────────────┐
│   Client     │ (stores tokens in localStorage)
└──────┬───────┘
       │
       │ 4. Authorization: Bearer ACCESS_TOKEN
       ↓
┌──────────────────────────────┐
│   REST API Endpoint           │
│   - Verify JWT signature      │
│   - Check token expiration    │
│   - Validate permissions      │
└──────┬───────────────────────┘
       │
       │ 5. Process request
       ↓
┌──────────────────────────────┐
│   View Function/Class         │
│   - Execute business logic    │
│   - Return response           │
└──────────────────────────────┘
```

## Cycle de vie des rapports

```
┌─────────────┐
│    OPEN     │  ← Créé par un citoyen
└──────┬──────┘
       │
       │ (Admin assigne)
       ↓
┌──────────────────┐
│  IN_PROGRESS     │  ← En cours de traitement
└──────┬───────────┘
       │
       ├─────────────────────┐
       │                     │
       │                     │
       ↓                     ↓
┌──────────────┐      ┌─────────────┐
│  RESOLVED    │      │  REJECTED   │
└──────────────┘      └─────────────┘
       │                     │
       │                     │
       ├─────────────────────┤
       │                     │
       ↓                     ↓
  (optionnel)          (optionnel)
┌──────────────┐      
│   CLOSED     │      
└──────────────┘      
```

## Flux des requêtes API

### Exemple: Créer un rapport

```
1. Client envoie:
   POST /reports/api/reports/create/
   Headers: Authorization: Bearer TOKEN
   Body: {
     title: "...",
     description: "...",
     category: "infrastructure",
     priority: "high"
   }

2. Middleware:
   - Parse JSON
   - Verify CSRF token (si applicable)
   - Log request

3. URL Router:
   - Match la route avec reports/urls.py
   - Dispatch vers report_create_view()

4. Authentification:
   - JWT token verification (SimpleJWT)
   - User lookup from token

5. Permissions:
   - IsAuthenticated check
   - RBAC (role-based access control)

6. View Function:
   - Validate form data
   - Check user permissions
   - Create report instance
   - Log activity (UserActivityLog)
   - Create audit trail (ReportHistory)
   - Save to database

7. Response:
   {
     "id": "uuid",
     "title": "...",
     "status": "open",
     "created_at": "2025-01-16T10:00:00Z"
   }

8. Logging:
   - Request log
   - Activity log
   - Audit trail
```

## Performance & Optimisations

### Indexes de base de données

```sql
-- Reqêtes fréquentes
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_category ON reports(category);
CREATE INDEX idx_reports_author ON reports(author_id);
CREATE INDEX idx_reports_created ON reports(created_at DESC);

-- Recherche
CREATE INDEX idx_reports_title ON reports(title);
CREATE FULLTEXT INDEX idx_reports_search ON reports(title, description);

-- Filtrages
CREATE INDEX idx_comments_report ON reports_reportcomment(report_id);
CREATE INDEX idx_votes_report ON reports_reportvote(report_id, vote_type);
CREATE INDEX idx_activity_user ON dashboard_useractivitylog(user_id);
CREATE INDEX idx_activity_type ON dashboard_useractivitylog(activity_type);
```

### Caching (Optionnel)

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 15 minutes
def report_list_view(request):
    # Cached response
    ...

# Cache les résultats de recherche
from django.core.cache import cache
cache.set('reports_open', queryset, 300)  # 5 minutes
```

### Pagination

- **Par défaut:** 20 résultats par page
- **API:** Pagination cursor-based (optionnel)

## Sécurité

### Authentification
- ✅ Mot de passes hachés (PBKDF2)
- ✅ JWT pour API (SimpleJWT)
- ✅ Session cookies pour web
- ✅ CSRF protection

### Autorisations
- ✅ Role-based access control (RBAC)
- ✅ Object-level permissions
- ✅ Field-level visibility (is_internal)

### Validation
- ✅ Form validation (Django Forms)
- ✅ Model validation
- ✅ API serializer validation

### Protection
- ✅ Rate limiting (API)
- ✅ SQL injection prevention (ORM)
- ✅ XSS protection (Template escaping)
- ✅ CORS configuration
- ✅ Account lockout (5 failed attempts)

## Déploiement

### Développement
```
SQLite + Django Dev Server + Hot Reload
```

### Production
```
PostgreSQL + Gunicorn + Nginx + SystemD
```

### Architecture production recommandée

```
┌─────────────────────────────────────┐
│   Internet (Users)                  │
└────────────────┬────────────────────┘
                 │
         ┌───────▼────────┐
         │  Cloudflare    │ (CDN & DDoS Protection)
         └───────┬────────┘
                 │
         ┌───────▼────────┐
         │   Nginx        │ (Reverse Proxy, Load Balancer)
         │   (Port 443)   │
         └───────┬────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼──┐   ┌──────▼──┐   ┌──────▼──┐
│Gunicorn│   │Gunicorn│   │Gunicorn│ (Application Servers)
│ :8000 │   │ :8001  │   │ :8002  │
└───┬──┘   └──────┬──┘   └──────┬──┘
    │            │            │
    └────────────┼────────────┘
                 │
         ┌───────▼────────┐
         │  PostgreSQL    │ (Database)
         │  Master-Slave  │
         └────────────────┘
                 │
         ┌───────▼────────┐
         │ Redis/Memcached│ (Cache & Sessions)
         └────────────────┘
```

## Tests

### Structure des tests

```
apps/accounts/tests.py       → UserAuthenticationTests, APITests
apps/reports/tests.py        → ReportModelTests, ReportAPITests, PDFExportTests
apps/dashboard/tests.py      → DashboardViewTests, MetricsTests
```

### Exécution

```bash
# Tous les tests
python manage.py test

# Par app
python manage.py test apps.accounts

# Avec couverture
coverage run --source='.' manage.py test
coverage report
```

## Futures améliorations

- [ ] GraphQL API
- [ ] WebSocket real-time notifications (Channels)
- [ ] Elasticsearch for full-text search
- [ ] Mobile app (React Native)
- [ ] Advanced reporting & exports (CSV, Excel)
- [ ] Map integration (Google Maps, Leaflet)
- [ ] Machine learning for issue classification
- [ ] Community voting & badges system
- [ ] Email notifications
- [ ] SMS alerts

---

**Version:** 1.0  
**Dernière mise à jour:** 2025-01-16  
**Mainteneur:** CivicFix Team
