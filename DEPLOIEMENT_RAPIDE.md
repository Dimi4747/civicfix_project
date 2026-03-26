# ⚡ Déploiement Rapide - CivicFix sur nyem.cdwfs.net

## 📋 Informations
- Dossier: `~/nyem`
- BD: `civicfix` / User: `cdiu8226_nyemb` / Pass: `DIMitr02`
- Domaine: `nyem.cdwfs.net`
- GitHub: `https://github.com/Dimi4747/civicfix_project.git`

---

## 🚀 Commandes à Exécuter (Copier-Coller)

### 1. Cloner le projet
```bash
cd ~
mkdir -p nyem
cd nyem
git clone https://github.com/Dimi4747/civicfix_project.git .
```

### 2. Créer l'environnement virtuel
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configurer l'environnement
```bash
cp .env.production .env
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
**→ Copiez la clé générée**

```bash
nano .env
```
**→ Remplacez SECRET_KEY par la clé copiée, sauvegardez (Ctrl+X, Y, Entrée)**

### 4. Créer les dossiers
```bash
mkdir -p logs tmp media staticfiles
```

### 5. Base de données
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Fichiers statiques
```bash
python manage.py collectstatic --noinput
```

### 7. Permissions
```bash
chmod 755 ~/nyem
chmod 644 ~/nyem/passenger_wsgi.py
chmod 644 ~/nyem/.htaccess
chmod -R 755 ~/nyem/media ~/nyem/staticfiles ~/nyem/logs ~/nyem/tmp
```

### 8. Démarrer
```bash
touch ~/nyem/tmp/restart.txt
```

---

## ✅ Vérification
- Site: `https://nyem.cdwfs.net`
- Admin: `https://nyem.cdwfs.net/admin/`

---

## 🔧 Commandes Utiles

**Voir les logs:**
```bash
tail -f ~/nyem/logs/django.log
```

**Redémarrer:**
```bash
touch ~/nyem/tmp/restart.txt
```

**Mettre à jour:**
```bash
cd ~/nyem
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
touch tmp/restart.txt
```

---

## ❌ Problèmes?

**Erreur 500:**
```bash
tail -f ~/logs/error_log
tail -f ~/nyem/logs/django.log
```

**Fichiers statiques manquants:**
```bash
cd ~/nyem
source venv/bin/activate
python manage.py collectstatic --noinput --clear
chmod -R 755 ~/nyem/staticfiles
touch tmp/restart.txt
```

**BD inaccessible:**
```bash
mysql -u cdiu8226_nyemb -p
# Password: DIMitr02
```

---

**📖 Guide complet:** Voir `DEPLOIEMENT_MANUEL_NYEM.md`
