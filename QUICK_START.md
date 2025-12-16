# 🚀 GUIDE DE DÉMARRAGE RAPIDE - Admin/Modérateur

## Installation en 3 Étapes

### Étape 1: Migrations
```bash
cd /path/to/civicfix_project
python manage.py makemigrations dashboard
python manage.py migrate dashboard
```

### Étape 2: Créer des Utilisateurs Test (Optionnel)
```bash
python manage.py create_test_users
```

Crée 3 comptes:
- **admin@civicfix.test** (Admin)
- **moderator@civicfix.test** (Modérateur)
- **user@civicfix.test** (Utilisateur)

Mot de passe pour tous: `password123`

### Étape 3: Lancer le Serveur
```bash
python manage.py runserver
```

---

## 🔓 Accès aux Interfaces

### Pour les Administrateurs
**Email:** admin@civicfix.test

1. **Gestion des Utilisateurs**
   - URL: http://localhost:8000/dashboard/admin/users/
   - Actions: Voir, Éditer, Activer/Désactiver, Déverrouiller, Supprimer

2. **Gestion des Rapports**
   - URL: http://localhost:8000/dashboard/admin/reports/
   - Actions: Voir, Éditer, Changer statut, Assigner, Supprimer

3. **Journal d'Audit**
   - URL: http://localhost:8000/dashboard/audit-log/
   - Contenu: Historique de toutes les actions

4. **Notifications**
   - URL: http://localhost:8000/dashboard/admin-notifications/
   - Contenu: Notifications ciblées

### Pour les Modérateurs
**Email:** moderator@civicfix.test

1. **Ma File de Modération**
   - URL: http://localhost:8000/dashboard/moderator/queue/
   - Contenu: Rapports assignés à vous

2. **Modérer un Rapport**
   - URL: http://localhost:8000/dashboard/moderator/reports/<id>/
   - Actions: Changer statut, Ajouter notes

3. **Notifications**
   - URL: http://localhost:8000/dashboard/admin-notifications/
   - Contenu: Vos notifications

### Pour les Utilisateurs Réguliers
**Email:** user@civicfix.test

1. **Créer un Rapport**
   - URL: http://localhost:8000/reports/create/
   - Action: Soumettre un rapport

2. **Voir Mes Rapports**
   - URL: http://localhost:8000/reports/my-reports/
   - Contenu: Vos rapports créés

---

## 📋 Workflows Principales

### Scenario 1: Admin Gère un Utilisateur
```
1. Aller à /dashboard/admin/users/
2. Rechercher l'utilisateur
3. Cliquer "Voir"
4. Voir les détails: rapports, connexions, audit
5. Cliquer "Éditer" pour changer rôle/infos
6. Action: Désactiver/Déverrouiller/Supprimer si nécessaire
7. Confirmé ✓ - Action loggée
```

### Scenario 2: Admin Modère un Rapport
```
1. Aller à /dashboard/admin/reports/
2. Rechercher/Filtrer le rapport
3. Cliquer "Gérer"
4. Modifier: titre, description, catégorie, priorité
5. Changer le statut (open → in_progress → resolved)
6. Assigner à un modérateur
7. Ajouter une note interne
8. Cliquer "Enregistrer"
9. Confirmé ✓ - Action loggée
```

### Scenario 3: Modérateur Traite son Rapport
```
1. Aller à /dashboard/moderator/queue/
2. Voir vos rapports assignés
3. Cliquer "Modérer Maintenant"
4. Lire le rapport complet
5. Voir les commentaires
6. Voir les notes internes (admin/modérateur)
7. Changer le statut
8. Ajouter notes de résolution
9. Ajouter commentaires internes
10. Cliquer "Enregistrer la Modération"
11. Confirmé ✓ - Action loggée
```

### Scenario 4: Admin Consulte l'Audit
```
1. Aller à /dashboard/audit-log/
2. Filtrer par action, acteur, ou date
3. Voir table complète des logs
4. Cliquer "Voir" sur les changements avant/après
5. Consulter contexte (IP, navigateur)
6. Vérifier traçabilité
```

---

## 🛠️ Configuration et Personnalisation

### Ajouter un Modérateur via l'Admin Panel
```
1. Connexion en tant qu'admin
2. /dashboard/admin/users/
3. Trouver l'utilisateur
4. Cliquer "Éditer"
5. Changer rôle de "Utilisateur" à "Modérateur"
6. Sauvegarder ✓
7. Maintenant accessible: /dashboard/moderator/queue/
```

### Assigner des Rapports au Modérateur
```
1. /dashboard/admin/reports/
2. Cliquer "Gérer" sur un rapport
3. Dans le formulaire: sélectionner "Assigné à"
4. Choisir le modérateur
5. Sauvegarder ✓
6. Modérateur verra dans sa file
```

### Ajouter une Note Interne
```
1. /dashboard/admin/reports/ ou moderate_report
2. Dans le formulaire "Ajouter une Note Interne"
3. Taper votre note
4. Sauvegarder ✓
5. Note visible pour admin/modérateurs seulement
```

---

## 🔍 Vérification de l'Installation

```bash
python verify_admin_system.py
```

Cela affiche:
- ✅ État des modèles
- ✅ Utilisateurs créés
- ✅ Fichiers présents
- ✅ Routes disponibles
- ✅ Permissions correctes
- ✅ Utilitaires chargés

---

## 📊 Cas d'Usage Courants

### "Je veux promouvoir un utilisateur en modérateur"
```
1. /dashboard/admin/users/
2. Voir l'utilisateur
3. Éditer → Changer rôle à "Modérateur"
4. Sauvegarder ✓
5. Automatique: La personne peut accéder à /dashboard/moderator/queue/
```

### "Je dois vérifier ce qu'un admin a fait"
```
1. /dashboard/audit-log/
2. Filtrer par "Acteur" (admin en question)
3. Voir toutes ses actions
4. Cliquer "Voir" pour before/after values
5. Contexte: IP, navigateur, heure
```

### "Un utilisateur spam les faux positifs"
```
1. /dashboard/admin/users/
2. Voir l'utilisateur
3. Cliquer "Désactiver le compte"
4. Confirmé ✓ - Compte inactif
5. Son compte est banni (ne peut plus accéder)
6. Action loggée pour audit
```

### "Un rapport critique doit être marqué urgent"
```
1. /dashboard/admin/reports/
2. Gérer le rapport
3. Changer statut → "in_progress"
4. Changer priorité → "critical"
5. Assigner à meilleur modérateur
6. Sauvegarder ✓
```

---

## 🆘 Troubleshooting

### Q: Je n'ai pas les droits d'accès
**A:** Vérifier votre rôle:
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(email='your@email.com')
>>> print(user.role)  # Doit être 'admin' ou 'moderator'
```

### Q: Les migrations n'appliquent pas
**A:** Réappliquer:
```bash
python manage.py migrate dashboard --fake-initial
python manage.py migrate dashboard
```

### Q: Templates non trouvés
**A:** Vérifier structure:
```bash
ls templates/dashboard/admin/
ls templates/dashboard/moderator/
```

### Q: Journal d'audit vide
**A:** C'est normal au départ. Il se remplit au fur et à mesure des actions admin/modérateur.

---

## 📚 Documentation Complète

- **[ADMIN_MODERATOR_GUIDE.md](ADMIN_MODERATOR_GUIDE.md)** - Guide détaillé 200+ lignes
- **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** - État du projet
- **[CHECKLIST.md](CHECKLIST.md)** - Checklist de tous les éléments

---

## 🔑 Points Clés à Retenir

✅ **Sécurité**
- Tous les admins/modérateurs sont loggés
- Chaque action enregistrée en audit trail
- Contexte IP/navigateur conservé

✅ **Permissions**
- Admins: Accès complet
- Modérateurs: Accès à rapports assignés
- Utilisateurs: Création rapports

✅ **Templates**
- Responsive et modernes
- Filtres et pagination
- Confirmations pour actions destructives

✅ **Logging**
- Automatique pour chaque action
- Traçabilité complète
- Before/after values

---

## 🎯 Prochaines Étapes

1. **Se connecter** avec admin@civicfix.test
2. **Explorer** les interfaces
3. **Créer du contenu** de test
4. **Consulter** les logs pour comprendre l'audit
5. **Lire** ADMIN_MODERATOR_GUIDE.md pour plus de détails

---

**🚀 C'est prêt! Commencez à utiliser le système Admin/Modérateur!**

Pour toute question, consultez la documentation ou explorez le code source.
