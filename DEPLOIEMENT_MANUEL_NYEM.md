# 🚀 Guide de Déploiement Manuel - CivicFix
## Configuration pour nyem.cdwfs.net

---

## 📋 Informations de Configuration

- **Dossier** : `~/nyem`
- **Base de données** : `civicfix`
- **Utilisateur BD** : `cdiu8226_nyemb`
- **Mot de passe BD** : `DIMitr02`
- **Sous-domaine** : `nyem.cdwfs.net`
- **Repository GitHub** : `https://github.com/Dimi4747/civicfix_project.git`

---

## 🎯 Étapes de Déploiement Manuel

### ÉTAPE 1 : Ouvrir le Terminal dans o2switch

1. Connectez-vous à votre compte o2switch
2. Allez dans **cPanel**
3. Cherchez **"Terminal"** dans la barre de recherche
4. Cliquez sur **"Terminal"** pour ouvrir le terminal web

---

### ÉTAPE 2 : Naviguer vers votre dossier

```bash
cd ~/nyem
```

Si le dossier n'existe pas encore, créez-le :
```bash
mkdir ~/nyem
cd ~/nyem
```

---

### ÉTAPE 3 : Cloner le projet depuis GitHub

```bash
git clone https://github.com/Dimi4747/civicfix_project.git .
```

**Note** : Le point `.` à la fin clone directement dans le dossier actuel sans créer de sous-dossier.

Si Git demande vos identifiants :
- Username : `Dimi4747`
- Password : Votre token GitHub (pas votre mot de passe)

---

### ÉTAPE 4 : Créer l'environnement virtuel Python

```bash
python3 -m venv venv
```

Vérifier que l'environnement est créé :
```bash
ls -la venv/
```

Vous devriez voir les dossiers `bin/`, `lib/`, etc.

---

### ÉTAPE 5 : Activer l'environnement virtuel

```bash
source venv/bin/activate
```

Votre prompt devrait maintenant afficher `(venv)` au début.

---

### ÉTAPE 6 : Mettre à jour pip

```bash
pip install --upgrade pip
```

---

### ÉTAPE 7 : Installer les dépendances

```bash
pip install -r requirements.txt
```

**Important** : Si vous utilisez MySQL au lieu de PostgreSQL, installez aussi :
```bash
pip install mysqlclient
```

Cette étape peut prendre 2-5 minutes. Attendez que tout soit installé.

---

### ÉTAPE 8 : Créer le fichier .env de production

```bash
cp .env.production .env
```

Ensuite, éditez le fichier pour générer une SECRET_KEY sécurisée :

```bash
nano .env
```

**Générer une SECRET_KEY** :
Dans le terminal, tapez :
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copiez la clé générée et remplacez `CHANGEZ-MOI-AVEC-UNE-CLE-SECURISEE-UNIQUE` dans le fichier `.env`.

Pour sauvegarder dans nano :
- Appuyez sur `Ctrl + X`
- Tapez `Y` pour confirmer
- Appuyez sur `Entrée`

---

### ÉTAPE 9 : Modifier settings.py pour MySQL

Ouvrez le fichier settings.py :
```bash
nano config/settings.py
```

Trouvez la section `DATABASES` et modifiez-la pour utiliser MySQL :

```python
# Database Configuration
if DEBUG:
    # Développement local → PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='civicfix'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }
else:
    # Production o2switch → MySQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DB_NAME', default='civicfix'),
            'USER': config('DB_USER', default='cdiu8226_nyemb'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
```

Sauvegardez avec `Ctrl + X`, `Y`, `Entrée`.

---

### ÉTAPE 10 : Créer les dossiers nécessaires

```bash
mkdir -p logs
mkdir -p tmp
mkdir -p media
mkdir -p staticfiles
```

---

### ÉTAPE 11 : Appliquer les migrations

```bash
python manage.py migrate
```

Si vous voyez des erreurs, vérifiez :
1. Que la base de données existe dans cPanel
2. Que les identifiants dans `.env` sont corrects
3. Que `mysqlclient` est installé

---

### ÉTAPE 12 : Créer un superutilisateur

```bash
python manage.py createsuperuser
```

Entrez :
- Email : `votre-email@example.com`
- Username : `admin`
- Password : (choisissez un mot de passe fort)

---

### ÉTAPE 13 : Collecter les fichiers statiques

```bash
python manage.py collectstatic --noinput
```

Cette commande copie tous les fichiers CSS, JS, images dans le dossier `staticfiles/`.

---

### ÉTAPE 14 : Définir les permissions

```bash
chmod 755 ~/nyem
chmod 644 ~/nyem/passenger_wsgi.py
chmod 644 ~/nyem/.htaccess
chmod -R 755 ~/nyem/media
chmod -R 755 ~/nyem/staticfiles
chmod -R 755 ~/nyem/logs
chmod -R 755 ~/nyem/tmp
```

---

### ÉTAPE 15 : Vérifier la configuration

```bash
python manage.py check --deploy
```

Si vous voyez des warnings, c'est normal. Les erreurs doivent être corrigées.

---

### ÉTAPE 16 : Redémarrer l'application Passenger

```bash
touch ~/nyem/tmp/restart.txt
```

Cette commande indique à Passenger de redémarrer votre application.

---

### ÉTAPE 17 : Tester l'application

Ouvrez votre navigateur et allez sur :
- **Site principal** : `https://nyem.cdwfs.net`
- **Admin** : `https://nyem.cdwfs.net/admin/`

---

## 🔧 Commandes Utiles

### Voir les logs en temps réel
```bash
tail -f ~/nyem/logs/django.log
```

### Voir les logs d'erreur Apache
```bash
tail -f ~/logs/error_log
```

### Redémarrer l'application
```bash
touch ~/nyem/tmp/restart.txt
```

### Mettre à jour depuis GitHub
```bash
cd ~/nyem
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
touch tmp/restart.txt
```

### Sauvegarder la base de données
```bash
mysqldump -u cdiu8226_nyemb -p civicfix > backup_$(date +%Y%m%d).sql
```

### Restaurer la base de données
```bash
mysql -u cdiu8226_nyemb -p civicfix < backup_20260326.sql
```

---

## ❌ Résolution des Problèmes

### Erreur 500 - Internal Server Error

1. Vérifiez les logs :
```bash
tail -f ~/nyem/logs/django.log
tail -f ~/logs/error_log
```

2. Vérifiez que `DEBUG=False` dans `.env`
3. Vérifiez que `ALLOWED_HOSTS` contient votre domaine
4. Redémarrez : `touch ~/nyem/tmp/restart.txt`

### Les fichiers statiques ne se chargent pas

1. Recollectez les fichiers :
```bash
cd ~/nyem
source venv/bin/activate
python manage.py collectstatic --noinput --clear
```

2. Vérifiez les permissions :
```bash
chmod -R 755 ~/nyem/staticfiles
```

3. Vérifiez le fichier `.htaccess`

### Erreur de connexion à la base de données

1. Vérifiez que la base existe dans cPanel → MySQL Databases
2. Vérifiez les identifiants dans `.env`
3. Testez la connexion :
```bash
mysql -u cdiu8226_nyemb -p
# Entrez le mot de passe : DIMitr02
# Si ça fonctionne, tapez : exit
```

### L'application ne démarre pas

1. Vérifiez que l'environnement virtuel est activé :
```bash
source ~/nyem/venv/bin/activate
```

2. Vérifiez que toutes les dépendances sont installées :
```bash
pip install -r requirements.txt
```

3. Vérifiez les chemins dans `passenger_wsgi.py` et `.htaccess`

---

## 📝 Checklist de Déploiement

- [ ] Terminal ouvert dans o2switch
- [ ] Navigué vers `~/nyem`
- [ ] Projet cloné depuis GitHub
- [ ] Environnement virtuel créé et activé
- [ ] Dépendances installées
- [ ] Fichier `.env` créé avec SECRET_KEY
- [ ] Settings.py modifié pour MySQL
- [ ] Dossiers créés (logs, tmp, media, staticfiles)
- [ ] Migrations appliquées
- [ ] Superutilisateur créé
- [ ] Fichiers statiques collectés
- [ ] Permissions définies
- [ ] Application redémarrée
- [ ] Site testé dans le navigateur
- [ ] Admin testé

---

## 🎓 Notes pour l'Apprentissage

Ce déploiement est **manuel** pour comprendre chaque étape. Plus tard, vous apprendrez :
- CI/CD avec GitHub Actions
- Déploiement automatique
- Docker et conteneurisation
- Monitoring et alertes

Pour l'instant, concentrez-vous sur la compréhension de chaque commande !

---

## 📞 Aide

Si vous rencontrez des problèmes :
1. Vérifiez les logs
2. Relisez les étapes
3. Demandez au professeur
4. Consultez la documentation Django

**Bon déploiement ! 🚀**
