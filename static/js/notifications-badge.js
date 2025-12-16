/**
 * Notifications Badge - Update unread count
 * Synchronisation en temps réel de l'icône notification
 */

class NotificationBadge {
    constructor() {
        this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }

    async updateUnreadCount() {
        try {
            const response = await fetch('/api/notifications/unread/');
            const data = await response.json();

            const badge = document.getElementById('notification-badge');
            if (badge) {
                if (data.unread_count > 0) {
                    badge.textContent = data.unread_count;
                    badge.style.display = 'inline-flex';
                } else {
                    badge.style.display = 'none';
                }
            }
        } catch (error) {
            console.error('Error updating notification badge:', error);
        }
    }

    startAutoUpdate(interval = 30000) {
        // Update immediately
        this.updateUnreadCount();

        // Update every 30 seconds
        setInterval(() => this.updateUnreadCount(), interval);
    }
}

// Initialize
const notificationBadge = new NotificationBadge();
document.addEventListener('DOMContentLoaded', () => {
    notificationBadge.startAutoUpdate();
});
