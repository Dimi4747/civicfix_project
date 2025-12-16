# 🚀 Guide d'Installation CivicFix

## Table des matières

1. [Prérequis](#prérequis)
2. [Installation locale](#installation-locale)
3. [Configuration](#configuration)
4. [Base de données](#base-de-données)
5. [Tests](#tests)
6. [Démarrage](#démarrage)
7. [Déploiement production](#déploiement-production)
8. [Dépannage](#dépannage)

## Prérequis

- **Python 3.10+** → [Télécharger](https://www.python.org/downloads/)
- **PostgreSQL 12+** (optionnel, SQLite par défaut pour dev)
- **Git** → [Télécharger](https://git-scm.com/)
- **pip** (inclus avec Python)
- **virtualenv** (recommandé)

### Vérifier les installations

```bash
python --version
pip --version
```

## Installation locale

### 1️⃣ Cloner le repository

```bash
git clone https://github.com/votre-username/civicfix.git
cd civicfix_project
```

### 2️⃣ Créer un environnement virtuel

#### Sous Linux/macOS
```bash
python3 -m venv env
source env/bin/activate
```

#### Sous Windows
```bash
python -m venv env
env\Scripts\activate
```

Après activation, votre terminal affichera `(env)` au début de la ligne.

### 3️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

**Important:** Cela installera:
- Django 6.0
- Django REST Framework
- SimpleJWT
- Django Channels
- Pillow
- ReportLab
- Et autres...

Vérifiez:
```bash
pip list | grep -i django
```

## Configuration

### 1. Créer le fichier `.env`

Copier le fichier exemple:

```bash
cp .env.example .env
```

### 2. Générer une clé secrète

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Copier la clé générée dans `.env`:

```env
SECRET_KEY=votre-clé-générée-ici
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Configuration de la base de données

#### Option A: SQLite (par défaut)

```env
# Déjà configuré par défaut, aucune action nécessaire
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

#### Option B: PostgreSQL

1. **Installer PostgreSQL:**

   **Sous Windows:**
   - Télécharger: https://www.postgresql.org/download/windows/
   - Installer avec pgAdmin

   **Sous Linux:**
   ```bash
   sudo apt-get install postgresql postgresql-contrib
   ```

   **Sous macOS:**
   ```bash
   brew install postgresql
   ```

2. **Créer la base de données:**

   ```bash
   psql -U postgres
   CREATE DATABASE civicfix_db;
   CREATE USER civicfix_user WITH PASSWORD 'votre_mot_de_passe';
   GRANT ALL PRIVILEGES ON DATABASE civicfix_db TO civicfix_user;
   \q
   ```

3. **Configurer `.env`:**

   ```env
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=civicfix_db
   DB_USER=civicfix_user
   DB_PASSWORD=votre_mot_de_passe
   DB_HOST=localhost
   DB_PORT=5432
   ```

4. **Installer le driver:**

   ```bash
   pip install psycopg2-binary
   ```

## Base de données

### Créer les migrations

```bash
python manage.py makemigrations
```

Cela créera les fichiers de migration basés sur vos modèles.

### Appliquer les migrations

```bash
python manage.py migrate
```

Cela crée toutes les tables dans la base de données.

### Vérifier les migrations

```bash
python manage.py showmigrations
```

### Créer un superutilisateur (admin)

```bash
python manage.py createsuperuser
```

Vous serez invité à entrer:
- **Email:** admin@example.com
- **Username:** admin
- **Password:** votre_mot_de_passe_sécurisé

### Charger les données de test (optionnel)

```bash
python manage.py loaddata fixtures/initial_data.json
```

### Sauvegarder les données

```bash
python manage.py dumpdata > backup.json
```

## Tests

### Exécuter tous les tests

```bash
python manage.py test
```

### Tests par app

```bash
python manage.py test apps.accounts
python manage.py test apps.reports
python manage.py test apps.dashboard
```

### Tests avec couverture

```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Génère un rapport HTML
```

### Tests spécifiques

```bash
python manage.py test apps.accounts.tests.UserAuthenticationTests
python manage.py test apps.reports.tests.ReportModelTests.test_create_report
```

## Démarrage

### Démarrer le serveur de développement

```bash
python manage.py runserver
```

Accédez à:
- 🏠 **Accueil:** http://localhost:8000
- 🔐 **Admin:** http://localhost:8000/admin
- 📊 **Dashboard:** http://localhost:8000/dashboard
- 📋 **API:** http://localhost:8000/reports/api/reports/

### Démarrer sur un port différent

```bash
python manage.py runserver 0.0.0.0:8001
```

### Démarrer avec rechargement automatique

```bash
python manage.py runserver --reload
```

## Déploiement production

### 1. Mettre à jour les settings

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=votre-vraie-clé-secrète
```

### 2. Collecter les fichiers statiques

```bash
python manage.py collectstatic --noinput
```

### 3. Compresser les assets

```bash
pip install django-compressor
python manage.py compress
```

### 4. Avec Gunicorn

**Installer:**
```bash
pip install gunicorn
```

**Tester:**
```bash
gunicorn config.wsgi:application --bind 127.0.0.1:8000
```

**Service systemd (`/etc/systemd/system/civicfix.service`):**
```ini
[Unit]
Description=CivicFix Django Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/civicfix_project
ExecStart=/path/to/env/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Démarrer:**
```bash
sudo systemctl enable civicfix
sudo systemctl start civicfix
sudo systemctl status civicfix
```

### 5. Avec Nginx

**Configuration (`/etc/nginx/sites-available/civicfix`):**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/civicfix_project/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /path/to/civicfix_project/media/;
        expires 7d;
    }
}
```

**Activer:**
```bash
sudo ln -s /etc/nginx/sites-available/civicfix /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL avec Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 7. Sauvegarde de la base de données

**PostgreSQL:**
```bash
pg_dump civicfix_db > backup_$(date +%Y%m%d).sql
```

**Restaurer:**
```bash
psql civicfix_db < backup_20250116.sql
```

### 8. Monitoring

**Logs Django:**
```bash
tail -f /var/log/civicfix/django.log
```

**Logs Nginx:**
```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## Docker (Optionnel)

### Créer `Dockerfile`

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Créer `docker-compose.yml`

```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: civicfix_db
      POSTGRES_USER: civicfix_user
      POSTGRES_PASSWORD: your_password

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
```

### Démarrer avec Docker

```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## Dépannage

### Erreur: "ModuleNotFoundError: No module named 'django'"

**Solution:** Vérifiez que votre environnement virtuel est activé:
```bash
source env/bin/activate  # Linux/macOS
env\Scripts\activate     # Windows
```

### Erreur: "django.db.migrations.exceptions.ProgrammingError"

**Solution:** Appliquez les migrations:
```bash
python manage.py migrate
```

### Erreur: "No such table: reports_report"

**Solution:** Les migrations n'ont pas été appliquées:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Fichiers statiques manquants

**Solution:** Collectez les static files:
```bash
python manage.py collectstatic --noinput
```

### Erreur de permission (port 8000 occupé)

**Solution:** Utilisez un autre port:
```bash
python manage.py runserver 8001
```

Ou tuez le processus:
```bash
lsof -i :8000
kill -9 <PID>
```

### Erreur "CSRF token missing"

**Solution:** Vérifiez que les cookies sont activés et incluez le token CSRF dans les formulaires.

### Connexion à PostgreSQL échouée

**Vérifications:**
1. PostgreSQL est-il démarré?
   ```bash
   sudo systemctl status postgresql
   ```

2. Les identifiants sont-ils corrects?
   ```bash
   psql -U civicfix_user -d civicfix_db -h localhost
   ```

3. Le driver est-il installé?
   ```bash
   pip install psycopg2-binary
   ```

### Erreur "SECRET_KEY is missing"

**Solution:** Générez et configurez une clé:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Copiez-la dans `.env`:
```env
SECRET_KEY=votre-clé-ici
```

## Commandes utiles

```bash
# Nettoyer la base de données
python manage.py flush

# Créer des données de test
python manage.py shell
# >>> from apps.accounts.models import User
# >>> User.objects.create_user('test@test.com', 'testuser', 'password123')

# Vérifier les problèmes de configuration
python manage.py check

# Générer un rapport de performance
python manage.py dbshell

# Créer une backup
python manage.py dumpdata > backup.json

# Restaurer une backup
python manage.py loaddata backup.json
```

## Support et ressources

- 📚 [Documentation Django](https://docs.djangoproject.com/)
- 📚 [Django REST Framework](https://www.django-rest-framework.org/)
- 💬 [Forum Django](https://forum.djangoproject.com/)
- 🐛 [Issues GitHub](https://github.com/votre-username/civicfix/issues)

---

**Installation réussie?** Explorez les features:
- 👤 [Authentification](http://localhost:8000/accounts/register/)
- 📋 [Créer un rapport](http://localhost:8000/reports/create/)
- 🔐 [Admin panel](http://localhost:8000/admin/)

Bon développement! 🚀
