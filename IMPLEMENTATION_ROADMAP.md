# 🎯 PLAN D'ACTION COMPLET - CivicFix v2.0

**Date:** 16 décembre 2025  
**Statut:** 🚀 EN COURS D'IMPLÉMENTATION

---

## 📋 ANALYSE ACTUELLE DU PROJET

### ✅ Ce qui existe
- ✅ Modèles Django de base (User, Report, ReportComment, etc.)
- ✅ Views/API reports complet
- ✅ Dashboard admin/moderator
- ✅ Système de rôles (admin, moderator, user)
- ✅ UI moderne avec Tailwind CSS
- ✅ Système de votes (ReportVote) basique
- ✅ Pièces jointes (ReportAttachment)
- ✅ Historique (ReportHistory)

### ❌ Ce qui manque (À IMPLÉMENTER)
1. ❌ **Système de Likes** - Like professionnel avec notifications
2. ❌ **Modal Commentaires** - Ouverture dynamique des commentaires
3. ❌ **Notifications Complètes** - Types, marquage lu, redirection
4. ❌ **Loading Animations** - Spinners globaux, skeleton loaders
5. ❌ **Audit Trail Complet** - Pour CHAQUE action
6. ❌ **Permissions Strictes** - Décorators et mixins
7. ❌ **AJAX/HTMX** - Interactions sans rechargement
8. ❌ **Toast Notifications** - Feedback utilisateur stylisé

---

## 🔧 PLAN D'IMPLÉMENTATION (ORDRE PRIORITAIRE)
### **PHASE 1: SYSTÈME DE NOTIFICATIONS (2-3h)**

#### 1.1 Modèle Notification
```python
# apps/accounts/models.py - Ajouter
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like', '❤️ Rapport Aimé'),
        ('comment', '💬 Commentaire'),
        ('status_change', '🔄 Changement Statut'),
        ('assigned', '⚠️ Rapport Assigné'),
        ('resolved', '✅ Rapport Résolu'),
        ('new_report', '📢 Nouveau Rapport'),
        ('admin_action', '🛠️ Action Admin'),
    )
    
    recipient = ForeignKey(User, on_delete=CASCADE, related_name='notifications')
    actor = ForeignKey(User, on_delete=CASCADE)
    notification_type = CharField(max_length=20, choices=NOTIFICATION_TYPES)
    report = ForeignKey(Report, on_delete=CASCADE, null=True)
    content = TextField()
    is_read = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['is_read']),
        ]
```

#### 1.2 Vue Notifications
- Page `/notifications/`
- Badge compteur 🔴
- Marquer comme lu automatiquement au clic
- Redirection intelligente

#### 1.3 Règles de Notification
| Action | Citoyen | Modérateur | Admin |
|--------|---------|-----------|-------|
| Like sur rapport | ✓ | ✓ | ✓ |
| Commentaire | ✓ | ✓ | ✓ |
| Assignation | - | ✓ | ✓ |
| Changement statut | ✓ | - | ✓ |
| Rapport publié | - | ✓ | ✓ |
| Résolution | ✓ | - | - |

---

### **PHASE 2: SYSTÈME DE LIKES (2h)**

#### 2.1 Modèle Like
```python
class Like(models.Model):
    report = ForeignKey(Report, on_delete=CASCADE, related_name='likes')
    user = ForeignKey(User, on_delete=CASCADE)
    created_at = DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('report', 'user')
        ordering = ['-created_at']
```

#### 2.2 View AJAX
```python
@login_required
def toggle_like(request, report_id):
    # AJAX endpoint
    # Toggle like
    # Retourner JSON avec count et liked status
    # Créer notification Like
```

#### 2.3 Template Integration
- Bouton ❤️ dynamique
- Compteur en temps réel
- Animation au clic

---

### **PHASE 3: COMMENTAIRES DYNAMIQUES (3h)**

#### 3.1 Modal/Collapse Commentaires
```javascript
// Clic sur '💬 Commentaires'
// Affiche modal/collapse
// AJAX pour charger les commentaires
// Ajouter commentaire sans rechargement
```

#### 3.2 Affichage Professionnel
- Avatar du commentateur
- Rôle (👑 Admin, 🛡️ Modérateur, 👤 Citoyen)
- Date relative (il y a 2h)
- Contenu avec formatage

#### 3.3 Notifications
- Auteur rapport notifié
- Threadé dans les notifications

---

### **PHASE 4: LOADING ANIMATIONS (1.5h)**

#### 4.1 Spinner Global
```javascript
// showLoading() - Spinner plein écran
// hideLoading()
// Utilisé lors de:
// - Navigation
// - Formulaire
// - Like/Comment
```

#### 4.2 Skeleton Loaders
```html
<!-- Pendant chargement des rapports -->
<div class="skeleton report-card">
  <div class="skeleton-image"></div>
  <div class="skeleton-text"></div>
</div>
```

#### 4.3 Animations CSS
- Spinner circulaire
- Pulse/shimmer skeleton
- Fade transitions

---

### **PHASE 5: AUDIT LOG COMPLET (2h)**

#### 5.1 Enrichir AuditLog
```python
# Chaque action enregistre:
- actor (qui)
- action (quoi)
- target_user / target_report (sur qui/quoi)
- before/after values
- timestamp
- ip_address
- user_agent
```

#### 5.2 Déclencheurs
```python
# Signal pour:
- Report.save() → log
- Like.save() → log
- Comment.save() → log
- Report status change → log
- User role change → log
```

#### 5.3 Affichage Admin
- Liste audit complète
- Filtrer par action/date
- Voir before/after
- Traçabilité 100%

---

### **PHASE 6: PERMISSIONS STRICTES (1.5h)**

#### 6.1 Décorateurs
```python
@admin_only
@moderator_or_admin
@owner_or_admin
@authenticated_only
```

#### 6.2 Mixins
```python
class AdminRequiredMixin(UserPassesTestMixin)
class OwnerRequiredMixin(UserPassesTestMixin)
```

#### 6.3 Template Tags
```django
{% if user.is_admin %}
  <!-- Show admin only content -->
{% endif %}
```

---

### **PHASE 7: INTÉGRATION HTMX (2h)**

#### 7.1 Likes/Comments AJAX
```html
<button hx-post="/api/reports/{{ report.id }}/like/"
        hx-target="#likes-count"
        hx-swap="innerHTML">
  ❤️ Like
</button>
```

#### 7.2 Modal Commentaires
```html
<div hx-get="/api/reports/{{ report.id }}/comments/"
     hx-trigger="click"
     hx-swap="outerHTML">
  💬 Commentaires
</div>
```

---

### **PHASE 8: TOAST NOTIFICATIONS (1h)**

#### 8.1 JavaScript Toast
```javascript
showToast('Action réussie!', 'success');
showToast('Erreur', 'error');
```

#### 8.2 Intégration Django
```python
messages.success(request, "Rapport créé!")
# Converti automatiquement en toast
```

---

## 📦 LIVRABLES PAR PHASE

| Phase | Livrable | Fichiers | Estimé |
|-------|----------|----------|--------|
| 1 | Notifications | models.py, views.py, templates/ | 2-3h |
| 2 | Likes | models.py, api.js, templates/ | 2h |
| 3 | Commentaires | views.py, modals.js, templates/ | 3h |
| 4 | Loading | animations.css, loaders.js | 1.5h |
| 5 | Audit | models.py, admin/, signals.py | 2h |
| 6 | Permissions | decorators.py, mixins.py | 1.5h |
| 7 | HTMX | htmx-config.js, templates/ | 2h |
| 8 | Toasts | toasts.js, base.html | 1h |

**TEMPS TOTAL: 15-16 heures**

---

## 🚀 COMMENCER PAR

### Étape 1: Créer Notification Model
- [x] Migration
- [ ] Model
- [ ] Admin

### Étape 2: Like System
- [ ] Like Model
- [ ] API View
- [ ] JavaScript toggle
- [ ] Template button

### Étape 3: Intégration Progressive
...

---

## ✅ CHECKLIST FINALE

- [ ] Toutes notifications fonctionnelles
- [ ] Likes avec temps réel
- [ ] Commentaires en modal
- [ ] Loading animations
- [ ] Audit trail complet
- [ ] Permissions strictes
- [ ] AJAX fluide
- [ ] Toasts stylés
- [ ] Tests manuels
- [ ] Pas d'erreurs
- [ ] Performance OK
- [ ] Production ready

---

**STATUT:** 🟡 À COMMENCER

Attendez le go pour Phase 1!
