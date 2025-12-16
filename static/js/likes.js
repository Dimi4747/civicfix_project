/**
 * Like System - AJAX Handler
 * Toggle like/unlike avec mise à jour en temps réel
 */

class LikeManager {
    constructor() {
        this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }

    async toggleLike(reportId, likeButton) {
        try {
            const response = await fetch(`/api/reports/${reportId}/like/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (data.status === 'success') {
                // Update button state
                const button = likeButton || document.getElementById(`like-btn-${reportId}`);
                if (button) {
                    if (data.liked) {
                        button.classList.add('liked');
                        button.classList.remove('not-liked');
                        button.innerHTML = `<i class="fas fa-heart"></i> ${data.like_count}`;
                    } else {
                        button.classList.remove('liked');
                        button.classList.add('not-liked');
                        button.innerHTML = `<i class="far fa-heart"></i> ${data.like_count}`;
                    }
                }

                // Update like count
                const countEl = document.getElementById(`like-count-${reportId}`);
                if (countEl) {
                    countEl.textContent = data.like_count;
                }

                // Show toast
                this.showToast(data.message, 'success');
            } else {
                this.showToast(data.message || 'Erreur', 'error');
            }
        } catch (error) {
            console.error('Error toggling like:', error);
            this.showToast('Erreur lors de la mise à jour du like', 'error');
        }
    }

    async getLikesData(reportId) {
        try {
            const response = await fetch(`/api/reports/${reportId}/likes/`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching likes data:', error);
            return null;
        }
    }

    showToast(message, type = 'info') {
        // Create toast element
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

        // Animate in
        setTimeout(() => toast.classList.add('show'), 10);

        // Remove after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Initialize
const likeManager = new LikeManager();

// Auto-init all like buttons
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-like-btn]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const reportId = btn.dataset.reportId;
            likeManager.toggleLike(reportId, btn);
        });
    });
});
