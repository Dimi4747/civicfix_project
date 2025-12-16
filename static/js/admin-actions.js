/**
 * Admin Actions - Confirmations & Toasts
 * Gère les actions sensibles avec confirmations et notifications
 */

// ========== TOASTS ==========

function showToast(message, type = 'success', duration = 3000) {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} animate-slide-in`;
    
    const bgColor = {
        'success': 'bg-green-500',
        'error': 'bg-red-500',
        'warning': 'bg-amber-500',
        'info': 'bg-blue-500'
    }[type] || 'bg-blue-500';
    
    const icon = {
        'success': '✓',
        'error': '✕',
        'warning': '⚠',
        'info': 'ℹ'
    }[type] || 'ℹ';
    
    toast.innerHTML = `
        <div class="${bgColor} text-white px-6 py-4 rounded-lg shadow-lg flex items-center gap-3 max-w-md">
            <span class="text-xl">${icon}</span>
            <span>${message}</span>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('animate-slide-out');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'fixed top-4 right-4 z-50 space-y-3';
    document.body.appendChild(container);
    return container;
}

// ========== CONFIRMATIONS ==========

function showConfirmDialog(title, message, confirmText = 'Confirmer', cancelText = 'Annuler', onConfirm, isDangerous = false) {
    return new Promise((resolve) => {
        // Créer le backdrop
        const backdrop = document.createElement('div');
        backdrop.className = 'fixed inset-0 bg-black bg-opacity-50 z-40 animate-fade-in';
        backdrop.onclick = () => {
            cleanup();
            resolve(false);
        };
        
        // Créer le dialog
        const dialog = document.createElement('div');
        dialog.className = 'fixed inset-0 flex items-center justify-center z-50 animate-scale-in';
        
        const confirmBtn = isDangerous ? 
            'bg-red-600 hover:bg-red-700' : 
            'bg-blue-600 hover:bg-blue-700';
        
        dialog.innerHTML = `
            <div class="bg-white rounded-lg shadow-2xl max-w-md w-full mx-4 overflow-hidden">
                <!-- Header -->
                <div class="bg-gray-100 border-b px-6 py-4">
                    <h2 class="text-xl font-bold text-gray-900">${title}</h2>
                </div>
                
                <!-- Body -->
                <div class="px-6 py-4">
                    <p class="text-gray-700">${message}</p>
                </div>
                
                <!-- Footer -->
                <div class="bg-gray-50 px-6 py-4 flex justify-end gap-3">
                    <button class="btn-cancel px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-900 rounded-lg font-medium">
                        ${cancelText}
                    </button>
                    <button class="btn-confirm px-4 py-2 ${confirmBtn} text-white rounded-lg font-medium">
                        ${confirmText}
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(backdrop);
        document.body.appendChild(dialog);
        
        function cleanup() {
            backdrop.remove();
            dialog.remove();
        }
        
        const btnCancel = dialog.querySelector('.btn-cancel');
        const btnConfirm = dialog.querySelector('.btn-confirm');
        
        btnCancel.onclick = () => {
            cleanup();
            resolve(false);
        };
        
        btnConfirm.onclick = () => {
            cleanup();
            if (onConfirm) onConfirm();
            resolve(true);
        };
        
        // Échap pour fermer
        const handleEsc = (e) => {
            if (e.key === 'Escape') {
                document.removeEventListener('keydown', handleEsc);
                cleanup();
                resolve(false);
            }
        };
        document.addEventListener('keydown', handleEsc);
    });
}

// ========== ACTIONS UTILISATEURS ==========

async function confirmDeleteUser(userId, userName) {
    const confirmed = await showConfirmDialog(
        'Supprimer Utilisateur',
        `Êtes-vous sûr de vouloir supprimer l'utilisateur <strong>${userName}</strong>? Cette action est irréversible.`,
        'Supprimer',
        'Annuler',
        null,
        true
    );
    
    if (confirmed) {
        showToast('Suppression en cours...', 'info');
        // Le formulaire sera soumis automatiquement
        document.querySelector(`form[data-user-delete="${userId}"]`)?.submit();
    }
}

async function confirmToggleUserStatus(userId, currentStatus) {
    const action = currentStatus ? 'désactiver' : 'activer';
    const confirmed = await showConfirmDialog(
        'Changer le statut',
        `Voulez-vous ${action} ce compte utilisateur?`,
        action.charAt(0).toUpperCase() + action.slice(1),
        'Annuler',
        null
    );
    
    if (confirmed) {
        showToast(`Compte ${action}...`, 'info');
        document.querySelector(`form[data-user-toggle="${userId}"]`)?.submit();
    }
}

async function confirmUnlockUser(userId) {
    const confirmed = await showConfirmDialog(
        'Déverrouiller le compte',
        'Réinitialiser les tentatives de connexion échouées?',
        'Déverrouiller',
        'Annuler'
    );
    
    if (confirmed) {
        showToast('Déverrouillage en cours...', 'info');
        document.querySelector(`form[data-user-unlock="${userId}"]`)?.submit();
    }
}

// ========== ACTIONS RAPPORTS ==========

async function confirmDeleteReport(reportId, reportTitle) {
    const confirmed = await showConfirmDialog(
        'Supprimer Rapport',
        `Êtes-vous sûr de vouloir supprimer le rapport <strong>${reportTitle}</strong>? Cette action est irréversible.`,
        'Supprimer',
        'Annuler',
        null,
        true
    );
    
    if (confirmed) {
        showToast('Suppression en cours...', 'info');
        document.querySelector(`form[data-report-delete="${reportId}"]`)?.submit();
    }
}

// ========== ACTIONS ADMIN ==========

// Afficher un toast après une action réussie (depuis le backend)
document.addEventListener('DOMContentLoaded', function() {
    // Vérifier les messages Django
    const messages = document.querySelectorAll('[data-message]');
    messages.forEach(msg => {
        const text = msg.dataset.message;
        const type = msg.dataset.type || 'success';
        showToast(text, type);
    });
});

// ========== CSS ANIMATIONS ==========

const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    @keyframes scaleIn {
        from {
            transform: scale(0.95);
            opacity: 0;
        }
        to {
            transform: scale(1);
            opacity: 1;
        }
    }
    
    .animate-slide-in {
        animation: slideIn 0.3s ease-out;
    }
    
    .animate-slide-out {
        animation: slideOut 0.3s ease-out;
    }
    
    .animate-fade-in {
        animation: fadeIn 0.2s ease-out;
    }
    
    .animate-scale-in {
        animation: scaleIn 0.3s ease-out;
    }
`;
document.head.appendChild(style);
