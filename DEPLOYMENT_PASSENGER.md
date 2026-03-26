# Guide de Déploiement Django avec Passenger (o2switch/cPanel)

## Prérequis

- Accès SSH à votre hébergement
- Python 3.11+ installé
- Accès à cPanel
- Base de données PostgreSQL ou MySQL créée

## Étape 1 : Préparer l'environnement local

### 1.1 Mettre à jour requirements.txt

```bash
pip freeze > requirements.txt
```

### 1.2 Collecter les fichiers statiques

```bash
python manage.py collectstatic --noinput
```

### 1.3 Tester en production locale

```bash
DEBUG=False python manage.py runserver
```

## Étape 2 : Transférer les fichiers sur le serveur

### 2.1 Via FTP/SFTP

Transférez tous les fichiers du projet vers votre serveur :
- Utilisez FileZilla ou WinSCP
- Destination : `/home/username/civicfix_project/`

### 2.2 Via Git (recommandé)

```bash
# Sur le serveur
cd ~
git clone https://github.com/votre-repo/civicfix_project.git
cd civicfix_project
```

## Étape 3 : Créer l'environnement virtuel

```bash
# Se connecter en SSH
ssh username@votre-domaine.com

# Créer l'environnement virtuel
cd ~/civicfix_project
python3.11 -m venv venv

# Activer l'environnement
source venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

## Étape 4 : Configurer la base de données

### 4.1 Créer la base de données via cPanel

1. Aller dans cPanel → MySQL Databases (ou PostgreSQL)
2. Créer une nouvelle base de données : `civicfix_db`
3. Créer un utilisateur et lui donner tous les privilèges
4. Noter les informations de connexion

### 4.2 Configurer le fichier .env

```bash
nano .env
```

Contenu du fichier `.env` pour production :

```env
# Django Settings
SECRET_KEY=votre-secret-key-super-securisee-changez-moi
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com

# Database Configuration - PostgreSQL
DB_NAME=civicfix_db
DB_USER=votre_user_db
DB_PASSWORD=votre_password_db
DB_HOST=localhost
DB_PORT=5432

# OU MySQL si vous utilisez MySQL
# DB_ENGINE=django.db.backends.mysql
# DB_PORT=3306

# Email Configuration (optionnel)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=mail.votre-domaine.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@votre-domaine.com
EMAIL_HOST_PASSWORD=votre-password-email

# CORS Settings
CORS_ALLOWED_ORIGINS=https://votre-domaine.com

# Features Flags
ENABLE_COMMENTS=True
ENABLE_VOTING=True
ENABLE_PDF_EXPORT=False
ENABLE_EMAIL_NOTIFICATIONS=True
ENABLE_WEBSOCKET_NOTIFICATIONS=False

# Pagination
PAGE_SIZE=20

# Admin Settings
ADMIN_URL=admin/
```

## Étape 5 : Configurer Passenger

### 5.1 Modifier passenger_wsgi.py

Éditez le fichier `passenger_wsgi.py` et ajustez les chemins :

```python
# Remplacez ces lignes avec vos vrais chemins
INTERP = os.path.expanduser("~/virtualenv/civicfix_project/venv/bin/python3")
```

### 5.2 Modifier .htaccess

Éditez le fichier `.htaccess` et remplacez `username` par votre nom d'utilisateur :

```apache
PassengerAppRoot /home/VOTRE_USERNAME/civicfix_project
PassengerPython /home/VOTRE_USERNAME/civicfix_project/venv/bin/python3

Alias /static /home/VOTRE_USERNAME/civicfix_project/staticfiles
Alias /media /home/VOTRE_USERNAME/civicfix_project/media
```

## Étape 6 : Appliquer les migrations

```bash
cd ~/civicfix_project
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

## Étape 7 : Créer un superutilisateur

```bash
python manage.py createsuperuser
```

## Étape 8 : Configurer les permissions

```bash
# Donner les bonnes permissions
chmod 755 ~/civicfix_project
chmod 644 ~/civicfix_project/passenger_wsgi.py
chmod 644 ~/civicfix_project/.htaccess

# Permissions pour les dossiers media et static
chmod -R 755 ~/civicfix_project/media
chmod -R 755 ~/civicfix_project/staticfiles
```

## Étape 9 : Configuration cPanel

### 9.1 Configurer l'application Python dans cPanel

1. Aller dans cPanel → "Setup Python App"
2. Cliquer sur "Create Application"
3. Remplir les informations :
   - Python version : 3.11
   - Application root : `civicfix_project`
   - Application URL : `/` (ou votre sous-domaine)
   - Application startup file : `passenger_wsgi.py`
   - Application Entry point : `application`

### 9.2 Variables d'environnement

Dans cPanel → Setup Python App → Variables d'environnement, ajoutez :
- `DJANGO_SETTINGS_MODULE` = `config.settings`

## Étape 10 : Redémarrer l'application

### Via cPanel
1. Aller dans "Setup Python App"
2. Cliquer sur "Restart" à côté de votre application

### Via SSH
```bash
touch ~/civicfix_project/tmp/restart.txt
```

## Étape 11 : Vérification

1. Visitez votre site : `https://votre-domaine.com`
2. Vérifiez l'admin : `https://votre-domaine.com/admin/`
3. Testez la création d'un rapport

## Dépannage

### Erreur 500 - Internal Server Error

```bash
# Vérifier les logs
tail -f ~/logs/error_log
tail -f ~/civicfix_project/logs/django.log
```

### Les fichiers statiques ne se chargent pas

```bash
# Recollectez les fichiers statiques
python manage.py collectstatic --noinput --clear

# Vérifiez les permissions
chmod -R 755 ~/civicfix_project/staticfiles
```

### Base de données inaccessible

```bash
# Testez la connexion
python manage.py dbshell
```

### Redémarrer l'application

```bash
# Méthode 1 : Via fichier restart
touch ~/civicfix_project/tmp/restart.txt

# Méthode 2 : Via Passenger
passenger-config restart-app ~/civicfix_project
```

## Maintenance

### Mettre à jour l'application

```bash
cd ~/civicfix_project
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
touch tmp/restart.txt
```

### Sauvegarder la base de données

```bash
# PostgreSQL
pg_dump -U votre_user civicfix_db > backup_$(date +%Y%m%d).sql

# MySQL
mysqldump -u votre_user -p civicfix_db > backup_$(date +%Y%m%d).sql
```

### Logs

```bash
# Logs Apache
tail -f ~/logs/error_log

# Logs Django (si configuré)
tail -f ~/civicfix_project/logs/django.log
```

## Sécurité en Production

1. ✅ `DEBUG=False` dans `.env`
2. ✅ `SECRET_KEY` unique et sécurisée
3. ✅ `ALLOWED_HOSTS` configuré correctement
4. ✅ HTTPS activé (Let's Encrypt via cPanel)
5. ✅ Fichiers sensibles protégés dans `.htaccess`
6. ✅ Base de données avec mot de passe fort
7. ✅ Sauvegardes régulières configurées

## Support

Pour toute question :
- Documentation Django : https://docs.djangoproject.com/
- Documentation Passenger : https://www.phusionpassenger.com/
- Support o2switch : https://www.o2switch.fr/support/
