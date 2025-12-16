# 📹 GUIDE DE DÉMONSTRATION - Système Admin/Modérateur

## Scénario de Démonstration Complet (15-20 minutes)

### Préparation (5 minutes)

#### 1. Lancer le serveur
```bash
cd /path/to/civicfix_project
python manage.py runserver
```

#### 2. Créer des données de test
```bash
python manage.py create_test_users
```

#### 3. Accéder à l'application
- URL: http://localhost:8000
- Admin: admin@civicfix.test / password123
- Modérateur: moderator@civicfix.test / password123
- Utilisateur: user@civicfix.test / password123

---

## 🎬 Démo #1: Interface Admin - Gestion Utilisateurs (5 minutes)

### Étapes

**1. Se connecter en Admin**
```
URL: http://localhost:8000/accounts/login/
Email: admin@civicfix.test
Password: password123
Résultat: Redirection vers /dashboard/
```

**2. Accéder à la Gestion Utilisateurs**
```
URL: http://localhost:8000/dashboard/admin/users/
Affiche:
- Liste paginée de tous les utilisateurs
- Filtres: recherche, rôle, statut
- Tableau avec infos: email, rôle, statut, rapports, date inscription
```

**3. Montrer les Filtres**
```
Recherche: Tapez "moderator"
  → Affiche seulement moderator@civicfix.test
  
Rôle: Sélectionner "Modérateur"
  → Affiche seulement les modérateurs
  
Statut: Sélectionner "Actifs"
  → Affiche seulement les utilisateurs actifs

Bouton: "Réinitialiser"
  → Retour à la liste complète
```

**4. Consulter Détails Utilisateur**
```
Cliquer sur "Voir" pour user@civicfix.test
Affiche:
- Informations: email, nom, rôle, statut
- Cartes: rôle, statut, rapports, commentaires
- Historique de connexion
- Rapports créés (5 derniers)
- Journal d'audit de l'utilisateur
```

**5. Éditer Utilisateur**
```
Cliquer "✎ Éditer"
Formulaire:
- Prénom
- Nom
- Rôle (dropdown: Utilisateur / Modérateur / Admin)

Changer le rôle du user à "Modérateur"
Cliquer "✓ Enregistrer"
Résultat:
- Message de succès
- Redirection vers détails
- Action loggée dans audit trail
```

**6. Montrer les Actions Rapides**
```
Cliquer "✕ Désactiver le compte"
Confirmation: "Êtes-vous sûr..."
Action loggée immédiatement

Cliquer "🔓 Déverrouiller le compte" (si applicable)
Réinitialise les tentatives échouées

Action: "🗑️ Supprimer le compte"
Confirmation finale requise
```

**7. Retourner à la Liste**
```
Cliquer "← Retour"
Voir les modifications apportées
```

---

## 🎬 Démo #2: Admin - Gestion Rapports (5 minutes)

### Étapes

**1. Accéder à la Gestion Rapports**
```
URL: http://localhost:8000/dashboard/admin/reports/
Affiche:
- Liste paginée de tous les rapports
- Filtres: statut, priorité, recherche
- Tableau: titre, auteur, catégorie, statut, priorité, date, actions
```

**2. Utiliser les Filtres**
```
Recherche: "Infrastructure"
  → Filtre par titre

Statut: "open"
  → Affiche seulement les rapports ouverts

Priorité: "high"
  → Affiche seulement priorité haute

Bouton: "🔍 Filtrer"
  → Application des filtres
```

**3. Gérer un Rapport**
```
Cliquer "Gérer" sur un rapport
Affiche la page de gestion:
- Infos du rapport: auteur, catégorie, créé le, vues
- Formulaire d'édition
```

**4. Éditer le Rapport**
```
Champs éditables:
- Titre: Modifier le texte
- Description: Modifier le texte
- Statut: open → in_progress
- Priorité: medium → high
- Catégorie: (visible, lecture seule)

Assigné à: Sélectionner un modérateur
  → dropdown des modérateurs/admins

Ajouter une Note Interne:
  → Tapez une note pour les modérateurs

Cliquer "✓ Enregistrer"
Résultat: Action loggée
```

**5. Actions Supplémentaires**
```
Voir "Notes Internes Existantes" si présentes
  → Affiche l'historique des notes en couleur

Bouton "🗑️ Supprimer"
  → Supprime le rapport avec confirmation
```

**6. Pagination**
```
Naviguer entre les pages
Voir compteur "Page X sur Y"
```

---

## 🎬 Démo #3: Interface Modérateur - File de Modération (5 minutes)

### Étapes

**1. Se Déconnecter et Se Reconnecter en Modérateur**
```
Admin → Déconnexion
Login avec moderator@civicfix.test
Redirection automatique vers /dashboard/moderator/queue/
```

**2. Consulter la File de Modération**
```
Page affiche:
- Title: "🛡️ Ma File de Modération"
- Stats cards: Total, Ouverts, En Cours, Résolus
- Filtres par statut
- Cartes de rapports assignés

Chaque carte affiche:
- Titre du rapport
- Auteur et date
- Statut et priorité badges
- Description aperçu
- Catégorie et stats (vues, commentaires)
- Bouton "✎ Modérer Maintenant"
```

**3. Filtrer la File**
```
Sélectionner statut "open"
Cliquer "🔍 Filtrer"
Affiche seulement les rapports ouverts
```

**4. Modérer un Rapport**
```
Cliquer "✎ Modérer Maintenant"
Affiche page complète:
- Colonne gauche (2/3): Rapport complet
  * Titre et infos
  * Description complète
  * Statut et priorité
  * Catégorie
  * Commentaires des citoyens
  * Notes internes (admin/modérateur)

- Sidebar droite (1/3): Formulaire modération
  * Changement de statut (dropdown)
  * Notes de résolution (textarea)
  * Commentaire interne (textarea)
  * Bouton "✓ Enregistrer la Modération"
```

**5. Effectuer la Modération**
```
Changer statut: "open" → "in_progress"
Ajouter "Nous enquêtons sur ce problème"

Changer statut: "in_progress" → "resolved"
Ajouter note résolution: "Réparation complétée le 15/03"
Ajouter commentaire interne: "Client satisfait"

Cliquer "✓ Enregistrer la Modération"
Confirmation et redirection

Actions loggées dans audit trail
```

---

## 🎬 Démo #4: Journal d'Audit (3 minutes)

### Étapes

**1. Accéder au Journal d'Audit**
```
URL: http://localhost:8000/dashboard/audit-log/
(Admin seulement)
```

**2. Affichage du Journal**
```
Table avec colonnes:
- Date & Heure (timestamp)
- Acteur (admin qui a agi)
- Action (type d'action effectuée)
- Cible (utilisateur ou rapport affecté)
- Description (description lisible)
- Changements (before/after values)

Affiche les actions récentes des admins/modérateurs
```

**3. Utiliser les Filtres**
```
Filtre par Action:
- user_created, user_modified, user_deleted, etc.

Filtre par Acteur (Admin):
- Sélectionner admin@civicfix.test

Filtre par Date:
- À partir du 01/01/2024

Bouton "🔍 Filtrer"
```

**4. Voir les Détails des Changements**
```
Cliquer sur "📊 Voir" dans colonne "Changements"
Affiche un dropdown:
- Avant: Ancienne valeur (en rouge)
- Après: Nouvelle valeur (en vert)

Exemple:
- Avant: rôle = "user"
- Après: rôle = "moderator"
```

**5. Pagination et Navigation**
```
Naviguer entre les pages
Observer les logs s'accumuler
```

---

## 🎬 Démo #5: Notifications Admin (2 minutes)

### Étapes

**1. Accéder aux Notifications**
```
URL: http://localhost:8000/dashboard/admin-notifications/
Affiche notifications ciblées
```

**2. Affichage des Notifications**
```
Pour chaque notification:
- Badge "NOUVEAU" si non lue
- Badge "RÉSOLU" si résolu
- Titre et message
- Type avec emoji
- Lien vers ressource associée
- Timestamp

Types visibles:
🚩 Rapport Signalé
⚠️ Activité Suspecte
🔴 Rapport Urgent
🛑 Alerte Système
✓ Tâche Assignée
```

**3. Marquer comme Lu**
```
Cliquer sur une notification
Voir timestamp "lue à"
Ou utiliser "✓ Tout marquer comme lu"
```

**4. Suivre les Liens**
```
Cliquer "📋 Voir le rapport"
  → Redirection vers le rapport

Cliquer "👤 Voir l'utilisateur"
  → Redirection vers le profil
```

---

## 🎬 Démo #6: Intégration Navigation (1 minute)

### Étapes

**1. Menu Utilisateur Dropdown**
```
Cliquer sur l'avatar utilisateur (haut droit)
Affiche dropdown avec:
- Email et rôle (avec badge couleur)
- 👑 Admin (jaune)
- 🛡️ Modérateur (vert)
- 👤 Utilisateur (bleu)
```

**2. Liens du Menu**
```
Pour Admin visible:
- Tableau de Bord
- Gestion Utilisateurs (nouveau)
- Gestion Rapports (nouveau)
- Journal d'Audit (nouveau)
- Notifications (nouveau)
- Statistiques

Pour Modérateur visible:
- Ma File (nouveau)
- Notifications (nouveau)

Communs:
- Mon Profil
- Mes Rapports
- Sécurité
- Déconnexion
```

**3. Redirection Automatique**
```
Login en tant qu'admin → /dashboard/
Login en tant que modérateur → /dashboard/
Login en tant qu'utilisateur → /home/
```

---

## 📊 Points Clés à Mettre en Avant

### Sécurité
- ✅ Chaque action loggée automatiquement
- ✅ Traçabilité complète (IP, navigateur)
- ✅ Permissions strictes par rôle
- ✅ Confirmations pour actions dangereuses

### Facilité d'Utilisation
- ✅ Interfaces modernes et intuitives
- ✅ Filtres puissants
- ✅ Pagination claire
- ✅ Messages explicites

### Performance
- ✅ Pagination pour grandes listes
- ✅ Filtres côté serveur
- ✅ Chargement rapide

### Audit
- ✅ Journal d'audit complet
- ✅ Before/after values
- ✅ Contexte de sécurité

---

## 💡 Tips pour la Démo

1. **Préparer les données**
   - Créer plusieurs utilisateurs avec rôles différents
   - Créer plusieurs rapports avec statuts différents
   - Générer de l'historique pour l'audit

2. **Montrer les Transitions**
   - Passer d'admin à modérateur à utilisateur
   - Montrer comment chaque rôle voit une interface différente

3. **Highlight Sécurité**
   - Montrer le journal d'audit
   - Expliquer le logging automatique
   - Montrer les confirmations

4. **Interactivité**
   - Laisser tester les filtres
   - Montrer les changements en temps réel
   - Naviguer en temps réel

5. **Performance**
   - Montrer la pagination sur listes longues
   - Montrer les filtres qui réduisent la liste
   - Montrer la rapidité de navigation

---

## 🎥 Screenshots Recommandés

À capturer:
1. Dashboard admin
2. Liste utilisateurs avec filtres
3. Détail utilisateur avec historique
4. Gestion rapport avec notes
5. File de modération
6. Journal d'audit
7. Notifications
8. Menu utilisateur dropdown
9. Messages de succès
10. Confirmations de suppression

---

## ⏱️ Timeline Suggeré

- 0:00 - 2:00: Bienvenue et présentation
- 2:00 - 7:00: Démo #1 (Gestion Utilisateurs)
- 7:00 - 12:00: Démo #2 (Gestion Rapports)
- 12:00 - 17:00: Démo #3 (File Modérateur)
- 17:00 - 20:00: Démo #4 (Journal d'Audit)
- 20:00 - 22:00: Démo #5 (Notifications)
- 22:00 - 23:00: Démo #6 (Navigation)
- 23:00 - 25:00: Questions et conclusion

---

**Prêt pour impressionner avec une démo professionnelle! 🎉**
