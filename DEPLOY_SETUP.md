# 📋 Configuration et Déploiement - CivicFix

## 🚀 Démarrage Rapide

### 1. Installation des Dépendances
```bash
pip install -r requirements.txt
```

### 2. Initialiser la Base de Données
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 3. Lancer le Serveur
```bash
python manage.py runserver
# Ou avec Daphne pour WebSockets:
daphne -b 127.0.0.1 -p 8000 config.asgi:application
```

### 4. Accéder l'Application
- **Accueil**: http://127.0.0.1:8000/
- **Admin Django**: http://127.0.0.1:8000/admin/
- **Tableau de Bord Admin**: http://127.0.0.1:8000/dashboard/

---

## 🔧 Variables d'Environnement (.env)

```ini
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# JWT Auth
JWT_SECRET_KEY=your-jwt-secret

# Site Settings
SITE_NAME=CivicFix
SITE_DOMAIN=localhost:8000
```

---

## 🗂️ Structure du Projet

```
civicfix_project/
├── apps/
│   ├── accounts/          # Authentification & Utilisateurs
│   ├── reports/           # Rapports & Issues
│   ├── dashboard/         # Admin & Analytics
│   └── ...
├── config/                # Configuration Django
├── static/                # CSS, JS, images
├── templates/             # HTML templates
├── manage.py
└── requirements.txt
```

---

## 🛠️ Créer Utilisateurs de Test

```bash
python manage.py create_test_users
```

Crée automatiquement:
- 1 Admin (admin@test.com)
- 2 Modérateurs (moderator1@test.com, moderator2@test.com)
- 5 Utilisateurs normaux (user1@test.com...user5@test.com)
- Mot de passe: `TestPassword123!`

---

## 📊 API Endpoints

### Notifications
- `GET /notifications/` - Page notifications
- `GET /api/notifications/unread/` - Compteur non-lues
- `POST /api/notifications/<id>/read/` - Marquer comme lue
- `POST /api/notifications/read-all/` - Marquer tout comme lu

### Likes
- `POST /api/reports/<id>/like/` - Toggle like
- `GET /api/reports/<id>/likes/` - Données likes

### Commentaires
- `GET /api/reports/<id>/comments/` - Charger commentaires
- `POST /api/reports/<id>/comment/` - Ajouter commentaire

---

## 🔐 Sécurité

### CSRF Protection
- Tous les formulaires incluent le token `{% csrf_token %}`
- Les requêtes AJAX passent via `X-CSRFToken` header

### Authentification
- Custom User model avec UUID primary key
- Email-based auth (pas d'username)
- JWT tokens pour API
- Role-based access control (RBAC)

### Decorateurs
```python
@login_required          # Accès authentifiés uniquement
@admin_required          # Admin uniquement
@admin_or_moderator_required  # Admin + Modérateurs
@owner_or_admin          # Propriétaire du rapport ou admin
```

---

## 📝 Audit Logging

Chaque action sensible est enregistrée dans la table `AuditLog`:
- User changes
- Report status changes
- Report assignments
- Admin actions
- Deletions

**Consulter l'audit log**:
```bash
# Via Django shell
python manage.py shell
from apps.dashboard.models import AuditLog
AuditLog.objects.all()[:10]  # Les 10 dernières entrées
```

---

## 🎨 Personnalisation du Thème

Le projet utilise **Tailwind CSS 3.0** en CDN. Personnalisez les couleurs dans `templates/base.html`:

```javascript
tailwind.config = {
    theme: {
        extend: {
            colors: {
                'blue-primary': '#2563EB',      // Couleur primaire
                'blue-secondary': '#3B82F6',    // Couleur secondaire
                'gray-bg': '#F9FAFB',           // Fond
            }
        }
    }
}
```

---

## 📱 Responsive Design

- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px)
- Navigation adaptive pour mobile
- Tous les formulaires responsive

---

## ⚡ Performance

### Database Indexes
- Tous les filtres courants ont des indexes
- Foreign keys indexés par défaut
- Timestamps indexés pour les requêtes range

### Caching (À venir)
```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache 5 minutes
def view_name(request):
    pass
```

### Query Optimization
```python
# Utiliser select_related pour ForeignKey
reports = Report.objects.select_related('author', 'category')

# Utiliser prefetch_related pour ManyToMany
reports = Report.objects.prefetch_related('comments', 'attachments')
```

---

## 🧪 Tests

```bash
# Lancer tous les tests
python manage.py test

# Test app spécifique
python manage.py test apps.reports

# Avec coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

---

## 🚢 Déploiement

### Préparation
```bash
# Créer un .env avec les paramètres de production
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
SECRET_KEY=your-strong-secret-key

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Vérifier la configuration
python manage.py check --deploy
```

### Avec Gunicorn + Nginx

**gunicorn_config.py**:
```python
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

**Lancer**:
```bash
gunicorn config.wsgi:application --config gunicorn_config.py
```

---

## 📞 Support & Troubleshooting

### Erreur: Port 8000 déjà utilisé
```bash
python manage.py runserver 8001
```

### Erreur: Module non trouvé
```bash
pip install -r requirements.txt --upgrade
```

### Réinitialiser la base de données
```bash
python manage.py flush  # Effacer toutes les données
python manage.py migrate  # Créer les tables
python manage.py createsuperuser  # Créer admin
```

### Vider le cache
```bash
python manage.py clear_cache
```

---

## 📚 Documentation Supplémentaire

- [Django Documentation](https://docs.djangoproject.com/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Font Awesome Icons](https://fontawesome.com/icons)
- [Chart.js Docs](https://www.chartjs.org/docs)

---

**Dernière mise à jour**: Décembre 2025
**Version**: 1.0.0
**License**: MIT
