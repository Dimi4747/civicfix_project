/**
 * Comments Modal System - AJAX Handler
 * Charger et ajouter des commentaires sans rechargement
 */

class CommentsManager {
    constructor() {
        this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        this.currentReportId = null;
    }

    async openCommentsModal(reportId) {
        this.currentReportId = reportId;

        // Create modal
        const modal = document.createElement('div');
        modal.id = 'comments-modal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <!-- Header -->
                <div class="modal-header">
                    <h2 class="modal-title">
                        <i class="fas fa-comments"></i> Commentaires
                    </h2>
                    <button class="close-btn" onclick="commentsManager.closeModal()">&times;</button>
                </div>

                <!-- Comments List -->
                <div class="modal-body">
                    <div id="comments-list" class="comments-list loading">
                        <div class="spinner"></div>
                    </div>
                </div>

                <!-- Comment Form -->
                <div class="modal-footer">
                    <form id="comment-form" onsubmit="commentsManager.submitComment(event)">
                        <textarea 
                            name="content" 
                            placeholder="Écrivez votre commentaire..." 
                            class="comment-input"
                            required></textarea>
                        <div class="flex gap-2 mt-2">
                            <label class="flex items-center gap-2">
                                <input type="checkbox" name="is_internal" value="true" id="internal-checkbox">
                                <span class="text-sm text-gray-600">Commentaire interne</span>
                            </label>
                            <button type="submit" class="btn btn-primary btn-sm ml-auto">
                                Envoyer
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Add styles if not present
        if (!document.getElementById('comments-modal-styles')) {
            this.addModalStyles();
        }

        // Load comments
        await this.loadComments(reportId);
    }

    async loadComments(reportId) {
        try {
            const response = await fetch(`/api/reports/${reportId}/comments/`);
            const data = await response.json();

            const list = document.getElementById('comments-list');
            list.classList.remove('loading');

            if (data.status === 'success' && data.comments.length > 0) {
                list.innerHTML = data.comments.map(comment => `
                    <div class="comment-item">
                        <div class="comment-header">
                            <div class="flex items-center gap-2">
                                <div class="avatar">
                                    ${comment.author.initials}
                                </div>
                                <div>
                                    <strong>${comment.author.name}</strong>
                                    <span class="badge badge-sm badge-gray">${comment.author.role}</span>
                                    ${comment.is_internal ? '<span class="badge badge-sm badge-warning">Interne</span>' : ''}
                                </div>
                            </div>
                            <time class="text-xs text-gray-500">${comment.created_at_relative}</time>
                        </div>
                        <p class="comment-content">${this.escapeHtml(comment.content)}</p>
                    </div>
                `).join('');
            } else {
                list.innerHTML = `
                    <div class="text-center py-8 text-gray-500">
                        <i class="fas fa-comments text-3xl mb-2"></i>
                        <p>Aucun commentaire pour l'instant</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading comments:', error);
            document.getElementById('comments-list').innerHTML = `
                <div class="text-center py-8 text-red-500">
                    <p>Erreur lors du chargement des commentaires</p>
                </div>
            `;
        }
    }

    async submitComment(event) {
        event.preventDefault();

        const form = event.target;
        const content = form.content.value;
        const isInternal = form.is_internal.checked;

        try {
            const formData = new FormData();
            formData.append('content', content);
            formData.append('is_internal', isInternal ? 'true' : 'false');

            const response = await fetch(`/api/reports/${this.currentReportId}/comment/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                },
                body: formData
            });

            const data = await response.json();

            if (data.status === 'success') {
                // Clear form
                form.reset();

                // Reload comments
                await this.loadComments(this.currentReportId);

                // Show toast
                this.showToast('Commentaire ajouté ✓', 'success');
            } else {
                this.showToast(data.message || 'Erreur', 'error');
            }
        } catch (error) {
            console.error('Error submitting comment:', error);
            this.showToast('Erreur lors de l\'envoi du commentaire', 'error');
        }
    }

    closeModal() {
        const modal = document.getElementById('comments-modal');
        if (modal) {
            modal.classList.add('closing');
            setTimeout(() => modal.remove(), 300);
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="flex items-center gap-2">
                ${type === 'success' ? '<i class="fas fa-check-circle"></i>' : ''}
                ${type === 'error' ? '<i class="fas fa-exclamation-circle"></i>' : ''}
                <span>${message}</span>
            </div>
        `;

        document.body.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    addModalStyles() {
        const style = document.createElement('style');
        style.id = 'comments-modal-styles';
        style.innerHTML = `
            .modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: flex-end;
                z-index: 1000;
                animation: slideUp 0.3s ease;
            }

            .modal.closing {
                animation: slideDown 0.3s ease;
            }

            @keyframes slideUp {
                from {
                    transform: translateY(100%);
                }
                to {
                    transform: translateY(0);
                }
            }

            @keyframes slideDown {
                from {
                    transform: translateY(0);
                }
                to {
                    transform: translateY(100%);
                }
            }

            .modal-content {
                background: white;
                width: 100%;
                max-width: 600px;
                max-height: 80vh;
                border-radius: 16px 16px 0 0;
                display: flex;
                flex-direction: column;
                box-shadow: 0 -5px 40px rgba(0, 0, 0, 0.16);
            }

            .modal-header {
                padding: 20px;
                border-bottom: 1px solid #e5e7eb;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .modal-title {
                font-size: 20px;
                font-weight: 700;
                color: #111827;
            }

            .close-btn {
                background: none;
                border: none;
                font-size: 28px;
                color: #6b7280;
                cursor: pointer;
                padding: 0;
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .close-btn:hover {
                color: #1f2937;
            }

            .modal-body {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
            }

            .comments-list {
                display: flex;
                flex-direction: column;
                gap: 16px;
            }

            .comments-list.loading {
                align-items: center;
                justify-content: center;
                min-height: 200px;
            }

            .comment-item {
                padding: 16px;
                background-color: #f9fafb;
                border-radius: 8px;
            }

            .comment-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 12px;
            }

            .comment-content {
                color: #374151;
                line-height: 1.5;
            }

            .avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                font-size: 14px;
            }

            .modal-footer {
                padding: 20px;
                border-top: 1px solid #e5e7eb;
            }

            .comment-input {
                width: 100%;
                padding: 12px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                font-size: 14px;
                font-family: inherit;
                resize: vertical;
                min-height: 80px;
            }

            .comment-input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }

            .spinner {
                width: 40px;
                height: 40px;
                border: 4px solid #e5e7eb;
                border-top-color: #667eea;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
            }

            @keyframes spin {
                to {
                    transform: rotate(360deg);
                }
            }

            .badge {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
            }

            .badge-gray {
                background-color: #e5e7eb;
                color: #374151;
            }

            .badge-warning {
                background-color: #fef3c7;
                color: #92400e;
            }
        `;

        document.head.appendChild(style);
    }
}

// Initialize
const commentsManager = new CommentsManager();

// Auto-init all comment buttons
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-comments-btn]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const reportId = btn.dataset.reportId;
            commentsManager.openCommentsModal(reportId);
        });
    });
});
