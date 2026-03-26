# ✅ Checklist de Déploiement CivicFix

## Avant le Déploiement

### Configuration Locale
- [ ] Tester l'application en mode `DEBUG=False`
- [ ] Vérifier que tous les tests passent
- [ ] Générer un nouveau `SECRET_KEY` pour la production
- [ ] Mettre à jour `requirements.txt` : `pip freeze > requirements.txt`
- [ ] Collecter les fichiers statiques : `python manage.py collectstatic`
- [ ] Créer une sauvegarde de la base de données locale

### Fichiers de Configuration
- [ ] `passenger_wsgi.py` créé et configuré
- [ ] `.htaccess` créé et configuré avec les bons chemins
- [ ] `.env` préparé avec les variables de production
- [ ] `DEPLOYMENT_PASSENGER.md` lu et compris

## Sur le Serveur

### Étape 1 : Préparation
- [ ] Accès SSH configuré et testé
- [ ] Python 3.11+ installé sur le serveur
- [ ] Base de données créée (PostgreSQL ou MySQL)
- [ ] Utilisateur de base de données créé avec privilèges

### Étape 2 : Transfert des Fichiers
- [ ] Fichiers transférés via FTP/SFTP ou Git
- [ ] Permissions correctes sur les dossiers (755)
- [ ] Fichier `.env` créé avec les bonnes valeurs

### Étape 3 : Environnement Virtuel
- [ ] Environnement virtuel créé : `python3.11 -m venv venv`
- [ ] Environnement activé : `source venv/bin/activate`
- [ ] Dépendances installées : `pip install -r requirements.txt`
- [ ] psycopg2-binary installé (pour PostgreSQL)

### Étape 4 : Configuration Django
- [ ] `SECRET_KEY` unique générée
- [ ] `DEBUG=False` dans `.env`
- [ ] `ALLOWED_HOSTS` configuré avec votre domaine
- [ ] Base de données configurée dans `.env`
- [ ] Migrations appliquées : `python manage.py migrate`
- [ ] Superutilisateur créé : `python manage.py createsuperuser`
- [ ] Fichiers statiques collectés : `python manage.py collectstatic`

### Étape 5 : Configuration Passenger
- [ ] `passenger_wsgi.py` avec les bons chemins
- [ ] `.htaccess` avec les bons chemins utilisateur
- [ ] Application Python configurée dans cPanel
- [ ] Variables d'environnement ajoutées dans cPanel

### Étape 6 : Permissions et Sécurité
- [ ] Permissions sur `passenger_wsgi.py` : `chmod 644`
- [ ] Permissions sur `.htaccess` : `chmod 644`
- [ ] Permissions sur `media/` : `chmod -R 755`
- [ ] Permissions sur `staticfiles/` : `chmod -R 755`
- [ ] Dossier `logs/` créé : `mkdir logs`
- [ ] Dossier `tmp/` créé : `mkdir tmp`

### Étape 7 : Tests de Déploiement
- [ ] Application redémarrée : `touch tmp/restart.txt`
- [ ] Page d'accueil accessible
- [ ] Admin accessible : `/admin/`
- [ ] Connexion admin fonctionne
- [ ] Fichiers statiques se chargent (CSS, JS, images)
- [ ] Fichiers media accessibles
- [ ] Création d'un rapport test
- [ ] Upload d'image test

### Étape 8 : Configuration SSL/HTTPS
- [ ] Certificat SSL installé (Let's Encrypt via cPanel)
- [ ] Redirection HTTP → HTTPS configurée
- [ ] `SESSION_COOKIE_SECURE=True` dans settings
- [ ] `CSRF_COOKIE_SECURE=True` dans settings

### Étape 9 : Monitoring et Logs
- [ ] Logs Django accessibles : `tail -f logs/django.log`
- [ ] Logs Apache accessibles : `tail -f ~/logs/error_log`
- [ ] Système de monitoring configuré (optionnel)
- [ ] Alertes email configurées (optionnel)

### Étape 10 : Sauvegardes
- [ ] Script de sauvegarde base de données créé
- [ ] Sauvegarde automatique configurée (cron)
- [ ] Sauvegarde des fichiers media configurée
- [ ] Test de restauration effectué

## Post-Déploiement

### Tests Fonctionnels
- [ ] Inscription utilisateur
- [ ] Connexion utilisateur
- [ ] Création de rapport
- [ ] Upload de fichiers
- [ ] Commentaires
- [ ] Système de likes
- [ ] Dashboard admin
- [ ] Gestion des utilisateurs
- [ ] Modération des rapports

### Performance
- [ ] Temps de chargement < 3 secondes
- [ ] Images optimisées
- [ ] Cache configuré (optionnel)
- [ ] CDN configuré (optionnel)

### Sécurité
- [ ] Scan de sécurité effectué
- [ ] Fichiers sensibles protégés
- [ ] Mots de passe forts utilisés
- [ ] Accès SSH sécurisé
- [ ] Firewall configuré

### Documentation
- [ ] Documentation de déploiement mise à jour
- [ ] Procédures de maintenance documentées
- [ ] Contacts d'urgence notés
- [ ] Accès et credentials sauvegardés (coffre-fort)

## Maintenance Continue

### Quotidien
- [ ] Vérifier les logs d'erreur
- [ ] Surveiller l'espace disque
- [ ] Vérifier les performances

### Hebdomadaire
- [ ] Sauvegarder la base de données
- [ ] Vérifier les mises à jour de sécurité
- [ ] Analyser les statistiques d'utilisation

### Mensuel
- [ ] Mettre à jour les dépendances Python
- [ ] Nettoyer les anciens logs
- [ ] Optimiser la base de données
- [ ] Tester les sauvegardes

## Commandes Utiles

### Redémarrer l'application
```bash
touch ~/civicfix_project/tmp/restart.txt
```

### Voir les logs en temps réel
```bash
tail -f ~/civicfix_project/logs/django.log
tail -f ~/logs/error_log
```

### Mettre à jour l'application
```bash
cd ~/civicfix_project
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
touch tmp/restart.txt
```

### Sauvegarder la base de données
```bash
# PostgreSQL
pg_dump -U user civicfix_db > backup_$(date +%Y%m%d).sql

# MySQL
mysqldump -u user -p civicfix_db > backup_$(date +%Y%m%d).sql
```

## Contacts d'Urgence

- **Hébergeur** : o2switch - https://www.o2switch.fr/support/
- **Support Django** : https://docs.djangoproject.com/
- **Support Passenger** : https://www.phusionpassenger.com/docs/

## Notes

Date de déploiement : _______________
Version déployée : _______________
Déployé par : _______________
Problèmes rencontrés : _______________
