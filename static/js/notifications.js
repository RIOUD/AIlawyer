/**
 * Notification System
 * Handles browser notifications, sound alerts, and notification management
 */

class NotificationSystem {
    constructor() {
        this.permission = 'default';
        this.soundEnabled = true;
        this.notificationQueue = [];
        this.isProcessing = false;
        
        this.initialize();
    }

    /**
     * Initialize notification system
     */
    async initialize() {
        // Request notification permission
        if ('Notification' in window) {
            this.permission = await this.requestPermission();
        }
        
        // Load settings
        this.loadSettings();
        
        // Start processing queue
        this.processQueue();
        
        // Setup notification sounds
        this.setupSounds();
    }

    /**
     * Request notification permission
     */
    async requestPermission() {
        if (!('Notification' in window)) {
            console.warn('Notifications not supported');
            return 'denied';
        }
        
        if (Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            return permission;
        }
        
        return Notification.permission;
    }

    /**
     * Load notification settings
     */
    loadSettings() {
        const saved = localStorage.getItem('notificationSettings');
        if (saved) {
            const settings = JSON.parse(saved);
            this.soundEnabled = settings.soundEnabled !== false;
        }
    }

    /**
     * Save notification settings
     */
    saveSettings() {
        const settings = {
            soundEnabled: this.soundEnabled
        };
        localStorage.setItem('notificationSettings', JSON.stringify(settings));
    }

    /**
     * Setup notification sounds
     */
    setupSounds() {
        // Create audio contexts for different notification types
        this.sounds = {
            default: this.createNotificationSound(800, 200),
            urgent: this.createNotificationSound(600, 300),
            reminder: this.createNotificationSound(1000, 150),
            deadline: this.createNotificationSound(400, 400)
        };
    }

    /**
     * Create notification sound using Web Audio API
     */
    createNotificationSound(frequency, duration) {
        return () => {
            if (!this.soundEnabled) return;
            
            try {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);
                oscillator.type = 'sine';
                
                gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration / 1000);
                
                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + duration / 1000);
            } catch (error) {
                console.warn('Could not play notification sound:', error);
            }
        };
    }

    /**
     * Show notification
     */
    showNotification(title, message, options = {}) {
        const notification = {
            id: Date.now().toString(),
            title,
            message,
            type: options.type || 'default',
            priority: options.priority || 'medium',
            icon: options.icon || '/favicon.ico',
            badge: options.badge || '/favicon.ico',
            tag: options.tag || 'calendar-notification',
            requireInteraction: options.requireInteraction || false,
            actions: options.actions || [],
            data: options.data || {},
            timestamp: new Date().toISOString()
        };
        
        // Add to queue
        this.notificationQueue.push(notification);
        
        // Process queue
        this.processQueue();
    }

    /**
     * Process notification queue
     */
    async processQueue() {
        if (this.isProcessing || this.notificationQueue.length === 0) {
            return;
        }
        
        this.isProcessing = true;
        
        while (this.notificationQueue.length > 0) {
            const notification = this.notificationQueue.shift();
            await this.displayNotification(notification);
            
            // Small delay between notifications
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        this.isProcessing = false;
    }

    /**
     * Display notification
     */
    async displayNotification(notification) {
        // Play sound
        this.playSound(notification.type);
        
        // Show browser notification
        if (this.permission === 'granted') {
            try {
                const browserNotification = new Notification(notification.title, {
                    body: notification.message,
                    icon: notification.icon,
                    badge: notification.badge,
                    tag: notification.tag,
                    requireInteraction: notification.requireInteraction,
                    actions: notification.actions,
                    data: notification.data,
                    silent: !this.soundEnabled
                });
                
                // Handle notification click
                browserNotification.onclick = (event) => {
                    this.handleNotificationClick(notification, event);
                    browserNotification.close();
                };
                
                // Handle notification action clicks
                browserNotification.onactionclick = (event) => {
                    this.handleActionClick(notification, event);
                };
                
                // Auto-close after 10 seconds (unless requireInteraction is true)
                if (!notification.requireInteraction) {
                    setTimeout(() => {
                        browserNotification.close();
                    }, 10000);
                }
                
            } catch (error) {
                console.error('Error showing browser notification:', error);
                this.showFallbackNotification(notification);
            }
        } else {
            this.showFallbackNotification(notification);
        }
        
        // Add to notification history
        this.addToHistory(notification);
    }

    /**
     * Play notification sound
     */
    playSound(type) {
        const sound = this.sounds[type] || this.sounds.default;
        if (sound) {
            sound();
        }
    }

    /**
     * Show fallback notification (when browser notifications are not available)
     */
    showFallbackNotification(notification) {
        // Create a custom notification element
        const notificationEl = document.createElement('div');
        notificationEl.className = `custom-notification custom-notification-${notification.priority}`;
        notificationEl.innerHTML = `
            <div class="custom-notification-content">
                <div class="custom-notification-title">${notification.title}</div>
                <div class="custom-notification-message">${notification.message}</div>
                <div class="custom-notification-time">${this.formatTime(new Date(notification.timestamp))}</div>
            </div>
            <button class="custom-notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add to page
        document.body.appendChild(notificationEl);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (notificationEl.parentNode) {
                notificationEl.remove();
            }
        }, 10000);
        
        // Add styles if not already present
        this.addFallbackStyles();
    }

    /**
     * Add fallback notification styles
     */
    addFallbackStyles() {
        if (document.getElementById('fallback-notification-styles')) {
            return;
        }
        
        const style = document.createElement('style');
        style.id = 'fallback-notification-styles';
        style.textContent = `
            .custom-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                padding: 15px;
                min-width: 300px;
                max-width: 400px;
                z-index: 10000;
                border-left: 4px solid #3498db;
                animation: slideInRight 0.3s ease-out;
            }
            .custom-notification-urgent {
                border-left-color: #e74c3c;
            }
            .custom-notification-high {
                border-left-color: #f39c12;
            }
            .custom-notification-medium {
                border-left-color: #3498db;
            }
            .custom-notification-low {
                border-left-color: #27ae60;
            }
            .custom-notification-content {
                margin-right: 30px;
            }
            .custom-notification-title {
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 5px;
            }
            .custom-notification-message {
                color: #7f8c8d;
                font-size: 0.9rem;
                margin-bottom: 5px;
            }
            .custom-notification-time {
                color: #95a5a6;
                font-size: 0.8rem;
            }
            .custom-notification-close {
                position: absolute;
                top: 10px;
                right: 10px;
                background: none;
                border: none;
                color: #95a5a6;
                cursor: pointer;
                padding: 5px;
            }
            .custom-notification-close:hover {
                color: #7f8c8d;
            }
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        
        document.head.appendChild(style);
    }

    /**
     * Handle notification click
     */
    handleNotificationClick(notification, event) {
        // Focus the window
        window.focus();
        
        // Handle different notification types
        switch (notification.type) {
            case 'deadline':
                this.handleDeadlineClick(notification);
                break;
            case 'reminder':
                this.handleReminderClick(notification);
                break;
            case 'meeting':
                this.handleMeetingClick(notification);
                break;
            default:
                this.handleDefaultClick(notification);
        }
        
        // Mark as read
        this.markAsRead(notification.id);
    }

    /**
     * Handle action click
     */
    handleActionClick(notification, event) {
        const action = notification.actions[event.actionIndex];
        if (action && action.handler) {
            action.handler(notification, event);
        }
    }

    /**
     * Handle deadline notification click
     */
    handleDeadlineClick(notification) {
        // Show deadline details or navigate to calendar
        if (window.calendar) {
            window.calendar.showDeadlines();
        }
    }

    /**
     * Handle reminder notification click
     */
    handleReminderClick(notification) {
        // Show event details or navigate to calendar
        if (window.calendar && notification.data.eventId) {
            const event = window.calendar.events.find(e => e.id === notification.data.eventId);
            if (event) {
                window.calendar.showEventDetails(event);
            }
        }
    }

    /**
     * Handle meeting notification click
     */
    handleMeetingClick(notification) {
        // Show meeting details or join meeting
        if (notification.data.meetingUrl) {
            window.open(notification.data.meetingUrl, '_blank');
        }
    }

    /**
     * Handle default notification click
     */
    handleDefaultClick(notification) {
        // Default behavior - just focus the window
        console.log('Notification clicked:', notification);
    }

    /**
     * Add notification to history
     */
    addToHistory(notification) {
        const history = this.getHistory();
        history.unshift(notification);
        
        // Keep only last 100 notifications
        if (history.length > 100) {
            history.splice(100);
        }
        
        localStorage.setItem('notificationHistory', JSON.stringify(history));
    }

    /**
     * Get notification history
     */
    getHistory() {
        const saved = localStorage.getItem('notificationHistory');
        return saved ? JSON.parse(saved) : [];
    }

    /**
     * Mark notification as read
     */
    markAsRead(notificationId) {
        const history = this.getHistory();
        const notification = history.find(n => n.id === notificationId);
        if (notification) {
            notification.read = true;
            localStorage.setItem('notificationHistory', JSON.stringify(history));
        }
    }

    /**
     * Clear notification history
     */
    clearHistory() {
        localStorage.removeItem('notificationHistory');
    }

    /**
     * Get unread notification count
     */
    getUnreadCount() {
        const history = this.getHistory();
        return history.filter(n => !n.read).length;
    }

    /**
     * Format time
     */
    formatTime(date) {
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * Test notification
     */
    testNotification() {
        this.showNotification('Test Notification', 'This is a test notification to verify the system is working.', {
            type: 'default',
            priority: 'medium'
        });
    }

    /**
     * Show urgent notification
     */
    showUrgentNotification(title, message, options = {}) {
        this.showNotification(title, message, {
            ...options,
            type: 'urgent',
            priority: 'urgent',
            requireInteraction: true
        });
    }

    /**
     * Show reminder notification
     */
    showReminderNotification(title, message, options = {}) {
        this.showNotification(title, message, {
            ...options,
            type: 'reminder',
            priority: 'high'
        });
    }

    /**
     * Show deadline notification
     */
    showDeadlineNotification(title, message, options = {}) {
        this.showNotification(title, message, {
            ...options,
            type: 'deadline',
            priority: 'urgent',
            requireInteraction: true
        });
    }

    /**
     * Toggle sound
     */
    toggleSound() {
        this.soundEnabled = !this.soundEnabled;
        this.saveSettings();
    }

    /**
     * Enable sound
     */
    enableSound() {
        this.soundEnabled = true;
        this.saveSettings();
    }

    /**
     * Disable sound
     */
    disableSound() {
        this.soundEnabled = false;
        this.saveSettings();
    }
}

// Initialize notification system
let notificationSystem;

document.addEventListener('DOMContentLoaded', () => {
    notificationSystem = new NotificationSystem();
});

// Global functions for testing
function testNotification() {
    if (notificationSystem) {
        notificationSystem.testNotification();
    }
}

function showUrgentNotification(title, message) {
    if (notificationSystem) {
        notificationSystem.showUrgentNotification(title, message);
    }
}

function showReminderNotification(title, message) {
    if (notificationSystem) {
        notificationSystem.showReminderNotification(title, message);
    }
}

function showDeadlineNotification(title, message) {
    if (notificationSystem) {
        notificationSystem.showDeadlineNotification(title, message);
    }
}

function toggleNotificationSound() {
    if (notificationSystem) {
        notificationSystem.toggleSound();
    }
}

// Export for use in other modules
window.NotificationSystem = NotificationSystem; 