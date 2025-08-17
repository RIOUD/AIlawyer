/**
 * Advanced Calendar System
 * Comprehensive calendar management with notifications, deadlines, export, sharing, and sync
 */

class AdvancedCalendar {
    constructor() {
        this.calendar = null;
        this.events = [];
        this.deadlines = [];
        this.notifications = [];
        this.settings = this.loadSettings();
        this.syncStatus = 'synced';
        this.currentFilter = 'all';
        
        this.initializeCalendar();
        this.loadSampleData();
        this.setupEventListeners();
        this.startNotificationService();
        this.startSyncService();
    }

    /**
     * Initialize FullCalendar
     */
    initializeCalendar() {
        const calendarEl = document.getElementById('calendar');
        
        this.calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            headerToolbar: false, // We have custom header
            height: 'auto',
            selectable: true,
            editable: true,
            eventClick: (info) => this.handleEventClick(info),
            eventDrop: (info) => this.handleEventDrop(info),
            eventResize: (info) => this.handleEventResize(info),
            select: (info) => this.handleDateSelect(info),
            eventDidMount: (info) => this.handleEventMount(info),
            dayMaxEvents: 3,
            moreLinkClick: 'popover',
            eventTimeFormat: {
                hour: '2-digit',
                minute: '2-digit',
                meridiem: 'short'
            },
            eventDisplay: 'block',
            eventColor: '#3498db',
            eventTextColor: '#ffffff',
            eventBorderColor: '#2980b9'
        });
        
        this.calendar.render();
        this.updateCalendarTitle();
    }

    /**
     * Load sample data for demonstration
     */
    loadSampleData() {
        // Sample events
        this.events = [
            {
                id: '1',
                title: 'Client Meeting - Smith Case',
                start: '2024-01-15T10:00:00',
                end: '2024-01-15T11:00:00',
                type: 'meeting',
                client: 'John Smith',
                caseId: 'CASE-001',
                caseName: 'Smith Employment Dispute',
                location: 'Conference Room A',
                description: 'Initial consultation for employment dispute',
                priority: 'high',
                billing_code: 'CONSULTATION',
                color: '#27ae60',
                recurring: false,
                recurringPattern: 'none'
            },
            {
                id: '2',
                title: 'Court Hearing - Johnson v. Corp',
                start: '2024-01-16T14:00:00',
                end: '2024-01-16T15:30:00',
                type: 'court',
                client: 'Sarah Johnson',
                location: 'District Court Room 3',
                description: 'Motion hearing for summary judgment',
                priority: 'high',
                billing_code: 'COURT_APPEARANCE',
                color: '#e74c3c'
            },
            {
                id: '3',
                title: 'Document Review Deadline',
                start: '2024-01-17T17:00:00',
                end: '2024-01-17T17:00:00',
                type: 'deadline',
                client: 'Tech Startup Inc.',
                description: 'Review and approve merger documents',
                priority: 'urgent',
                billing_code: 'DOCUMENT_REVIEW',
                color: '#c0392b',
                allDay: true
            },
            {
                id: '4',
                title: 'Contract Negotiation',
                start: '2024-01-18T13:00:00',
                end: '2024-01-18T15:00:00',
                type: 'consultation',
                client: 'Global Enterprises',
                location: 'Client Office',
                description: 'Final contract terms negotiation',
                priority: 'medium',
                billing_code: 'NEGOTIATION',
                color: '#9b59b6'
            },
            {
                id: '5',
                title: 'Legal Research - Patent Case',
                start: '2024-01-19T09:00:00',
                end: '2024-01-19T12:00:00',
                type: 'work',
                description: 'Research prior art for patent litigation',
                priority: 'medium',
                billing_code: 'LEGAL_RESEARCH',
                color: '#f39c12'
            }
        ];

        // Sample deadlines
        this.deadlines = [
            {
                id: 'd1',
                title: 'File Motion for Summary Judgment',
                dueDate: '2024-01-20T17:00:00',
                client: 'Johnson v. Corp',
                priority: 'urgent',
                description: 'Deadline to file motion for summary judgment'
            },
            {
                id: 'd2',
                title: 'Submit Discovery Responses',
                dueDate: '2024-01-22T17:00:00',
                client: 'Smith Employment Case',
                priority: 'high',
                description: 'Responses to first set of interrogatories'
            },
            {
                id: 'd3',
                title: 'Contract Review Deadline',
                dueDate: '2024-01-25T17:00:00',
                client: 'Tech Startup Inc.',
                priority: 'medium',
                description: 'Review and approve merger agreement'
            }
        ];

        // Sample notifications
        this.notifications = [
            {
                id: 'n1',
                title: 'Court Hearing Reminder',
                message: 'Court hearing for Johnson v. Corp in 30 minutes',
                type: 'reminder',
                priority: 'high',
                timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
                read: false,
                eventId: '2'
            },
            {
                id: 'n2',
                title: 'Deadline Approaching',
                message: 'Document review deadline for Tech Startup Inc. due tomorrow',
                type: 'deadline',
                priority: 'urgent',
                timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
                read: false,
                eventId: '3'
            },
            {
                id: 'n3',
                title: 'Client Meeting Scheduled',
                message: 'New client meeting scheduled for next week',
                type: 'info',
                priority: 'medium',
                timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
                read: true
            }
        ];

        this.renderEvents();
        this.renderDeadlines();
        this.renderNotifications();
        this.renderCaseTimeline();
        this.updateStats();
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Quick add form
        document.getElementById('quickAddForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.addQuickEvent();
        });

        // Recurring event checkbox
        document.getElementById('quickEventRecurring')?.addEventListener('change', (e) => {
            const patternSelect = document.getElementById('quickEventRecurringPattern');
            if (patternSelect) {
                patternSelect.style.display = e.target.checked ? 'block' : 'none';
            }
        });

        // Case filter buttons
        document.querySelectorAll('.case-filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.filterByCase(e.target.dataset.case);
            });
        });

        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.filterEvents(e.target.dataset.filter);
            });
        });

        // Calendar action buttons
        document.getElementById('exportCalendar')?.addEventListener('click', () => this.exportCalendar());
        document.getElementById('shareCalendar')?.addEventListener('click', () => this.shareCalendar());
        document.getElementById('syncCalendar')?.addEventListener('click', () => this.syncCalendar());
        document.getElementById('showSettings')?.addEventListener('click', () => this.showSettings());

        // Settings form
        document.getElementById('saveSettings')?.addEventListener('click', () => this.saveSettings());
    }

    /**
     * Handle event click
     */
    handleEventClick(info) {
        const event = this.events.find(e => e.id === info.event.id);
        if (event) {
            this.showEventDetails(event);
        }
    }

    /**
     * Handle event drag and drop
     */
    handleEventDrop(info) {
        const event = this.events.find(e => e.id === info.event.id);
        if (event) {
            event.start = info.event.start.toISOString();
            event.end = info.event.end?.toISOString();
            this.saveEvents();
            this.showNotification('Event moved successfully', 'success');
        }
    }

    /**
     * Handle event resize
     */
    handleEventResize(info) {
        const event = this.events.find(e => e.id === info.event.id);
        if (event) {
            event.start = info.event.start.toISOString();
            event.end = info.event.end.toISOString();
            this.saveEvents();
            this.showNotification('Event duration updated', 'success');
        }
    }

    /**
     * Handle date selection
     */
    handleDateSelect(info) {
        this.showQuickAdd(info.start);
    }

    /**
     * Handle event mount (for custom styling)
     */
    handleEventMount(info) {
        const event = this.events.find(e => e.id === info.event.id);
        if (event) {
            info.el.style.backgroundColor = event.color;
            if (event.priority === 'urgent') {
                info.el.classList.add('urgent-event');
            }
        }
    }

    /**
     * Render events on calendar
     */
    renderEvents() {
        this.calendar.removeAllEvents();
        
        const filteredEvents = this.currentFilter === 'all' 
            ? this.events 
            : this.events.filter(e => e.type === this.currentFilter);
        
        this.calendar.addEventSource(filteredEvents);
    }

    /**
     * Filter events by type
     */
    filterEvents(filter) {
        this.currentFilter = filter;
        
        // Update filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
        
        this.renderEvents();
    }

    /**
     * Add quick event
     */
    addQuickEvent() {
        const title = document.getElementById('quickEventTitle').value;
        const dateTime = document.getElementById('quickEventDateTime').value;
        const type = document.getElementById('quickEventType').value;
        const isRecurring = document.getElementById('quickEventRecurring')?.checked || false;
        const recurringPattern = document.getElementById('quickEventRecurringPattern')?.value || 'none';
        
        if (!title || !dateTime) {
            this.showNotification('Please fill in all required fields', 'error');
            return;
        }
        
        // Check for conflicts
        const conflicts = this.checkEventConflicts(dateTime, new Date(new Date(dateTime).getTime() + 60 * 60 * 1000).toISOString());
        if (conflicts.length > 0) {
            this.showConflictWarning(conflicts, () => {
                this.createEvent(title, dateTime, type, isRecurring, recurringPattern);
            });
            return;
        }
        
        this.createEvent(title, dateTime, type, isRecurring, recurringPattern);
    }

    /**
     * Create event with conflict checking
     */
    createEvent(title, dateTime, type, isRecurring = false, recurringPattern = 'none') {
        const baseEvent = {
            id: Date.now().toString(),
            title: title,
            start: dateTime,
            end: new Date(new Date(dateTime).getTime() + 60 * 60 * 1000).toISOString(),
            type: type,
            priority: 'medium',
            billing_code: this.getBillingCode(type),
            color: this.getEventColor(type),
            recurring: isRecurring,
            recurringPattern: recurringPattern
        };
        
        if (isRecurring && recurringPattern !== 'none') {
            const recurringEvents = this.generateRecurringEvents(baseEvent);
            this.events.push(...recurringEvents);
        } else {
            this.events.push(baseEvent);
        }
        
        this.renderEvents();
        this.updateStats();
        this.hideQuickAdd();
        this.showNotification('Event added successfully', 'success');
        
        // Reset form
        document.getElementById('quickAddForm').reset();
    }

    /**
     * Check for event conflicts
     */
    checkEventConflicts(start, end) {
        const startTime = new Date(start);
        const endTime = new Date(end);
        
        return this.events.filter(event => {
            const eventStart = new Date(event.start);
            const eventEnd = new Date(event.end);
            
            // Check for overlap
            return (startTime < eventEnd && endTime > eventStart);
        });
    }

    /**
     * Show conflict warning
     */
    showConflictWarning(conflicts, onConfirm) {
        const conflictList = conflicts.map(event => 
            `• ${event.title} (${this.formatDateTime(event.start)})`
        ).join('\n');
        
        const message = `This event conflicts with:\n${conflictList}\n\nDo you want to proceed anyway?`;
        
        if (confirm(message)) {
            onConfirm();
        }
    }

    /**
     * Generate recurring events
     */
    generateRecurringEvents(baseEvent) {
        const events = [];
        const startDate = new Date(baseEvent.start);
        const endDate = new Date(baseEvent.end);
        const duration = endDate - startDate;
        
        let currentDate = new Date(startDate);
        const maxEvents = 52; // Limit to 1 year of recurring events
        let eventCount = 0;
        
        while (eventCount < maxEvents) {
            const eventStart = new Date(currentDate);
            const eventEnd = new Date(currentDate.getTime() + duration);
            
            events.push({
                ...baseEvent,
                id: `${baseEvent.id}_${eventCount}`,
                start: eventStart.toISOString(),
                end: eventEnd.toISOString(),
                originalEventId: baseEvent.id
            });
            
            // Calculate next occurrence
            switch (baseEvent.recurringPattern) {
                case 'daily':
                    currentDate.setDate(currentDate.getDate() + 1);
                    break;
                case 'weekly':
                    currentDate.setDate(currentDate.getDate() + 7);
                    break;
                case 'biweekly':
                    currentDate.setDate(currentDate.getDate() + 14);
                    break;
                case 'monthly':
                    currentDate.setMonth(currentDate.getMonth() + 1);
                    break;
                case 'quarterly':
                    currentDate.setMonth(currentDate.getMonth() + 3);
                    break;
                default:
                    return events;
            }
            
            eventCount++;
        }
        
        return events;
    }

    /**
     * Show quick add panel
     */
    showQuickAdd(date = null) {
        const panel = document.getElementById('quickAddPanel');
        panel.style.display = 'block';
        
        if (date) {
            const dateTime = date.toISOString().slice(0, 16);
            document.getElementById('quickEventDateTime').value = dateTime;
        }
    }

    /**
     * Hide quick add panel
     */
    hideQuickAdd() {
        document.getElementById('quickAddPanel').style.display = 'none';
    }

    /**
     * Show event details modal
     */
    showEventDetails(event) {
        document.getElementById('eventModalTitle').textContent = event.title;
        
        const modalBody = document.getElementById('eventModalBody');
        modalBody.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="event-detail-item">
                        <span class="event-detail-label">Date & Time:</span>
                        <span class="event-detail-value">${this.formatDateTime(event.start)}</span>
                    </div>
                    <div class="event-detail-item">
                        <span class="event-detail-label">Duration:</span>
                        <span class="event-detail-value">${this.calculateDuration(event.start, event.end)}</span>
                    </div>
                    <div class="event-detail-item">
                        <span class="event-detail-label">Type:</span>
                        <span class="event-detail-value">${event.type.charAt(0).toUpperCase() + event.type.slice(1)}</span>
                    </div>
                    <div class="event-detail-item">
                        <span class="event-detail-label">Priority:</span>
                        <span class="event-detail-value">
                            <span class="badge bg-${this.getPriorityColor(event.priority)}">${event.priority}</span>
                        </span>
                    </div>
                </div>
                <div class="col-md-6">
                    ${event.client ? `
                    <div class="event-detail-item">
                        <span class="event-detail-label">Client:</span>
                        <span class="event-detail-value">${event.client}</span>
                    </div>
                    ` : ''}
                    ${event.location ? `
                    <div class="event-detail-item">
                        <span class="event-detail-label">Location:</span>
                        <span class="event-detail-value">${event.location}</span>
                    </div>
                    ` : ''}
                    <div class="event-detail-item">
                        <span class="event-detail-label">Billing Code:</span>
                        <span class="event-detail-value">${event.billing_code}</span>
                    </div>
                    ${event.description ? `
                    <div class="event-detail-item">
                        <span class="event-detail-label">Description:</span>
                        <span class="event-detail-value">${event.description}</span>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        // Store current event for actions
        this.currentEvent = event;
        
        const modal = new bootstrap.Modal(document.getElementById('eventModal'));
        modal.show();
    }

    /**
     * Edit current event
     */
    editEvent() {
        if (this.currentEvent) {
            // In a real implementation, this would open an edit form
            this.showNotification('Edit functionality would open here', 'info');
        }
    }

    /**
     * Share current event
     */
    shareEvent() {
        if (this.currentEvent) {
            const shareData = {
                title: this.currentEvent.title,
                text: `Calendar event: ${this.currentEvent.title}`,
                url: window.location.href
            };
            
            if (navigator.share) {
                navigator.share(shareData);
            } else {
                // Fallback: copy to clipboard
                navigator.clipboard.writeText(`${shareData.title} - ${shareData.url}`);
                this.showNotification('Event link copied to clipboard', 'success');
            }
        }
    }

    /**
     * Export current event
     */
    exportEvent() {
        if (this.currentEvent) {
            const eventData = {
                title: this.currentEvent.title,
                start: this.currentEvent.start,
                end: this.currentEvent.end,
                description: this.currentEvent.description || '',
                location: this.currentEvent.location || '',
                type: this.currentEvent.type
            };
            
            const blob = new Blob([JSON.stringify(eventData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${this.currentEvent.title.replace(/[^a-z0-9]/gi, '_')}.json`;
            a.click();
            URL.revokeObjectURL(url);
            
            this.showNotification('Event exported successfully', 'success');
        }
    }

    /**
     * Delete current event
     */
    deleteEvent() {
        if (this.currentEvent && confirm('Are you sure you want to delete this event?')) {
            this.events = this.events.filter(e => e.id !== this.currentEvent.id);
            this.renderEvents();
            this.updateStats();
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('eventModal'));
            modal.hide();
            
            this.showNotification('Event deleted successfully', 'success');
        }
    }

    /**
     * Export calendar
     */
    exportCalendar() {
        const calendarData = {
            events: this.events,
            deadlines: this.deadlines,
            exportDate: new Date().toISOString(),
            version: '1.0'
        };
        
        const blob = new Blob([JSON.stringify(calendarData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `calendar_export_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.showNotification('Calendar exported successfully', 'success');
    }

    /**
     * Share calendar
     */
    shareCalendar() {
        const shareData = {
            title: 'My Legal Calendar',
            text: 'Check out my legal practice calendar',
            url: window.location.href
        };
        
        if (navigator.share) {
            navigator.share(shareData);
        } else {
            // Fallback: show share options
            this.showShareOptions();
        }
    }

    /**
     * Show share options
     */
    showShareOptions() {
        const shareUrl = window.location.href;
        const shareText = 'Check out my legal practice calendar';
        
        const shareOptions = `
            <div class="share-options">
                <h6>Share Calendar</h6>
                <div class="share-buttons">
                    <button class="btn btn-primary btn-sm" onclick="window.open('mailto:?subject=Legal Calendar&body=${encodeURIComponent(shareText + ' ' + shareUrl)}')">
                        <i class="fas fa-envelope"></i> Email
                    </button>
                    <button class="btn btn-success btn-sm" onclick="navigator.clipboard.writeText('${shareText + ' ' + shareUrl}')">
                        <i class="fas fa-copy"></i> Copy Link
                    </button>
                    <button class="btn btn-info btn-sm" onclick="window.open('https://wa.me/?text=${encodeURIComponent(shareText + ' ' + shareUrl)}')">
                        <i class="fab fa-whatsapp"></i> WhatsApp
                    </button>
                </div>
            </div>
        `;
        
        // Show in a modal or notification
        this.showNotification('Share options available', 'info');
    }

    /**
     * Sync calendar
     */
    async syncCalendar() {
        this.setSyncStatus('syncing');
        
        try {
            // Simulate sync process
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // In a real implementation, this would sync with external calendars
            this.setSyncStatus('synced');
            this.showNotification('Calendar synced successfully', 'success');
        } catch (error) {
            this.setSyncStatus('error');
            this.showNotification('Sync failed. Please try again.', 'error');
        }
    }

    /**
     * Set sync status
     */
    setSyncStatus(status) {
        this.syncStatus = status;
        const indicators = document.querySelectorAll('.sync-indicator');
        
        indicators.forEach(indicator => {
            indicator.className = `sync-indicator ${status}`;
        });
        
        const statusText = document.getElementById('syncStatusText');
        if (statusText) {
            const statusMessages = {
                'synced': 'Last synced: Just now',
                'syncing': 'Syncing...',
                'error': 'Sync failed'
            };
            statusText.textContent = statusMessages[status] || 'Unknown status';
        }
    }

    /**
     * Show settings modal
     */
    showSettings() {
        const modal = new bootstrap.Modal(document.getElementById('settingsModal'));
        modal.show();
    }

    /**
     * Save settings
     */
    saveSettings() {
        const settings = {
            emailNotifications: document.getElementById('emailNotifications').checked,
            browserNotifications: document.getElementById('browserNotifications').checked,
            smsNotifications: document.getElementById('smsNotifications').checked,
            reminderTime: document.getElementById('reminderTime').value,
            googleSync: document.getElementById('googleSync').checked,
            outlookSync: document.getElementById('outlookSync').checked,
            appleSync: document.getElementById('appleSync').checked
        };
        
        this.settings = settings;
        localStorage.setItem('calendarSettings', JSON.stringify(settings));
        
        const modal = bootstrap.Modal.getInstance(document.getElementById('settingsModal'));
        modal.hide();
        
        this.showNotification('Settings saved successfully', 'success');
    }

    /**
     * Load settings
     */
    loadSettings() {
        const saved = localStorage.getItem('calendarSettings');
        return saved ? JSON.parse(saved) : {
            emailNotifications: true,
            browserNotifications: true,
            smsNotifications: false,
            reminderTime: '15',
            googleSync: false,
            outlookSync: false,
            appleSync: false
        };
    }

    /**
     * Start notification service
     */
    startNotificationService() {
        // Check for notifications every minute
        setInterval(() => {
            this.checkDeadlines();
            this.checkUpcomingEvents();
        }, 60000);
        
        // Initial check
        this.checkDeadlines();
        this.checkUpcomingEvents();
    }

    /**
     * Start sync service
     */
    startSyncService() {
        // Auto-sync every 5 minutes
        setInterval(() => {
            if (this.settings.googleSync || this.settings.outlookSync || this.settings.appleSync) {
                this.syncCalendar();
            }
        }, 300000);
    }

    /**
     * Check deadlines
     */
    checkDeadlines() {
        const now = new Date();
        const urgentDeadlines = this.deadlines.filter(deadline => {
            const dueDate = new Date(deadline.dueDate);
            const timeDiff = dueDate - now;
            return timeDiff > 0 && timeDiff <= 24 * 60 * 60 * 1000; // Within 24 hours
        });
        
        urgentDeadlines.forEach(deadline => {
            this.createNotification({
                title: 'Deadline Approaching',
                message: `${deadline.title} is due ${this.formatTimeUntil(deadline.dueDate)}`,
                type: 'deadline',
                priority: deadline.priority,
                eventId: deadline.id
            });
        });
    }

    /**
     * Check upcoming events
     */
    checkUpcomingEvents() {
        const now = new Date();
        const reminderTime = parseInt(this.settings.reminderTime) * 60 * 1000; // Convert to milliseconds
        
        const upcomingEvents = this.events.filter(event => {
            const eventTime = new Date(event.start);
            const timeDiff = eventTime - now;
            return timeDiff > 0 && timeDiff <= reminderTime;
        });
        
        upcomingEvents.forEach(event => {
            this.createNotification({
                title: 'Event Reminder',
                message: `${event.title} starts ${this.formatTimeUntil(event.start)}`,
                type: 'reminder',
                priority: event.priority || 'medium',
                eventId: event.id
            });
        });
    }

    /**
     * Create notification
     */
    createNotification(notification) {
        notification.id = Date.now().toString();
        notification.timestamp = new Date().toISOString();
        notification.read = false;
        
        this.notifications.unshift(notification);
        this.renderNotifications();
        this.updateNotificationCount();
        
        // Show browser notification if enabled
        if (this.settings.browserNotifications && 'Notification' in window) {
            if (Notification.permission === 'granted') {
                new Notification(notification.title, {
                    body: notification.message,
                    icon: '/favicon.ico'
                });
            } else if (Notification.permission !== 'denied') {
                Notification.requestPermission();
            }
        }
    }

    /**
     * Render deadlines
     */
    renderDeadlines() {
        const deadlineList = document.getElementById('deadlineList');
        if (!deadlineList) return;
        
        const sortedDeadlines = this.deadlines
            .sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate))
            .slice(0, 5);
        
        if (sortedDeadlines.length === 0) {
            deadlineList.innerHTML = '<p class="text-muted">No upcoming deadlines</p>';
            return;
        }
        
        deadlineList.innerHTML = sortedDeadlines.map(deadline => `
            <div class="deadline-item">
                <div>
                    <div class="deadline-title">${deadline.title}</div>
                    <div class="deadline-time ${this.isUrgent(deadline.dueDate) ? 'deadline-urgent' : ''}">
                        ${this.formatTimeUntil(deadline.dueDate)}
                    </div>
                </div>
                <span class="badge bg-${this.getPriorityColor(deadline.priority)}">${deadline.priority}</span>
            </div>
        `).join('');
        
        // Update deadline count
        const urgentCount = this.deadlines.filter(d => this.isUrgent(d.dueDate)).length;
        document.getElementById('deadlineCount').textContent = urgentCount;
    }

    /**
     * Render notifications
     */
    renderNotifications() {
        const notificationList = document.getElementById('notificationList');
        if (!notificationList) return;
        
        const unreadNotifications = this.notifications.filter(n => !n.read);
        
        if (unreadNotifications.length === 0) {
            notificationList.innerHTML = '<p class="text-muted p-3">No new notifications</p>';
            return;
        }
        
        notificationList.innerHTML = unreadNotifications.map(notification => `
            <div class="notification-item unread" onclick="calendar.markNotificationRead('${notification.id}')">
                <div class="notification-priority ${notification.priority}"></div>
                <div class="notification-title">${notification.title}</div>
                <div class="notification-time">${this.formatTimeAgo(notification.timestamp)}</div>
            </div>
        `).join('');
        
        this.updateNotificationCount();
    }

    /**
     * Mark notification as read
     */
    markNotificationRead(notificationId) {
        const notification = this.notifications.find(n => n.id === notificationId);
        if (notification) {
            notification.read = true;
            this.renderNotifications();
        }
    }

    /**
     * Update notification count
     */
    updateNotificationCount() {
        const unreadCount = this.notifications.filter(n => !n.read).length;
        const countElement = document.getElementById('notificationCount');
        if (countElement) {
            countElement.textContent = unreadCount;
            countElement.style.display = unreadCount > 0 ? 'flex' : 'none';
        }
    }

    /**
     * Update statistics
     */
    updateStats() {
        const today = new Date().toISOString().split('T')[0];
        const todayEvents = this.events.filter(e => e.start.startsWith(today)).length;
        const weekEvents = this.events.filter(e => {
            const eventDate = new Date(e.start);
            const weekFromNow = new Date();
            weekFromNow.setDate(weekFromNow.getDate() + 7);
            return eventDate <= weekFromNow && eventDate >= new Date();
        }).length;
        const urgentDeadlines = this.deadlines.filter(d => this.isUrgent(d.dueDate)).length;
        
        document.getElementById('todayEvents').textContent = todayEvents;
        document.getElementById('weekEvents').textContent = weekEvents;
        document.getElementById('urgentDeadlines').textContent = urgentDeadlines;
    }

    /**
     * Calendar navigation
     */
    previousMonth() {
        this.calendar.prev();
        this.updateCalendarTitle();
    }

    nextMonth() {
        this.calendar.next();
        this.updateCalendarTitle();
    }

    today() {
        this.calendar.today();
        this.updateCalendarTitle();
    }

    /**
     * Update calendar title
     */
    updateCalendarTitle() {
        const title = this.calendar.view.title;
        document.getElementById('calendarTitle').textContent = title;
    }

    /**
     * Save events to storage
     */
    saveEvents() {
        localStorage.setItem('calendarEvents', JSON.stringify(this.events));
        localStorage.setItem('calendarDeadlines', JSON.stringify(this.deadlines));
    }

    /**
     * Get events by case
     */
    getEventsByCase(caseId) {
        return this.events.filter(event => event.caseId === caseId);
    }

    /**
     * Get case timeline
     */
    getCaseTimeline(caseId) {
        const caseEvents = this.getEventsByCase(caseId);
        const caseDeadlines = this.deadlines.filter(deadline => deadline.caseId === caseId);
        
        const timeline = [...caseEvents, ...caseDeadlines].sort((a, b) => {
            const dateA = new Date(a.start || a.dueDate);
            const dateB = new Date(b.start || b.dueDate);
            return dateA - dateB;
        });
        
        return timeline;
    }

    /**
     * Add case to event
     */
    addCaseToEvent(eventId, caseId, caseName) {
        const event = this.events.find(e => e.id === eventId);
        if (event) {
            event.caseId = caseId;
            event.caseName = caseName;
            this.saveEvents();
            this.renderEvents();
            this.showNotification('Case linked to event successfully', 'success');
        }
    }

    /**
     * Remove case from event
     */
    removeCaseFromEvent(eventId) {
        const event = this.events.find(e => e.id === eventId);
        if (event) {
            delete event.caseId;
            delete event.caseName;
            this.saveEvents();
            this.renderEvents();
            this.showNotification('Case unlinked from event', 'success');
        }
    }

    /**
     * Get case statistics
     */
    getCaseStatistics(caseId) {
        const caseEvents = this.getEventsByCase(caseId);
        const caseDeadlines = this.deadlines.filter(deadline => deadline.caseId === caseId);
        
        return {
            totalEvents: caseEvents.length,
            upcomingEvents: caseEvents.filter(e => new Date(e.start) > new Date()).length,
            totalDeadlines: caseDeadlines.length,
            urgentDeadlines: caseDeadlines.filter(d => this.isUrgent(d.dueDate)).length,
            totalHours: caseEvents.reduce((total, event) => {
                const duration = new Date(event.end) - new Date(event.start);
                return total + (duration / (1000 * 60 * 60));
            }, 0)
        };
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }

    /**
     * Utility functions
     */
    getEventColor(type) {
        const colors = {
            'meeting': '#27ae60',
            'court': '#e74c3c',
            'deadline': '#c0392b',
            'consultation': '#9b59b6',
            'work': '#f39c12'
        };
        return colors[type] || '#3498db';
    }

    getBillingCode(type) {
        const codes = {
            'meeting': 'CONSULTATION',
            'court': 'COURT_APPEARANCE',
            'deadline': 'DOCUMENT_REVIEW',
            'consultation': 'CONSULTATION',
            'work': 'LEGAL_RESEARCH'
        };
        return codes[type] || 'GENERAL';
    }

    getPriorityColor(priority) {
        const colors = {
            'urgent': 'danger',
            'high': 'warning',
            'medium': 'info',
            'low': 'success'
        };
        return colors[priority] || 'secondary';
    }

    formatDateTime(dateString) {
        return new Date(dateString).toLocaleString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    formatTimeUntil(dateString) {
        const now = new Date();
        const target = new Date(dateString);
        const diff = target - now;
        
        if (diff < 0) return 'Overdue';
        
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        
        if (days > 0) return `in ${days} day${days > 1 ? 's' : ''}`;
        if (hours > 0) return `in ${hours} hour${hours > 1 ? 's' : ''}`;
        if (minutes > 0) return `in ${minutes} minute${minutes > 1 ? 's' : ''}`;
        return 'now';
    }

    formatTimeAgo(dateString) {
        const now = new Date();
        const past = new Date(dateString);
        const diff = now - past;
        
        const minutes = Math.floor(diff / (1000 * 60));
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        
        if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
        if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        return 'Just now';
    }

    calculateDuration(start, end) {
        const startTime = new Date(start);
        const endTime = new Date(end);
        const diff = endTime - startTime;
        
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        
        if (hours > 0) return `${hours}h ${minutes}m`;
        return `${minutes} minutes`;
    }

    isUrgent(dateString) {
        const now = new Date();
        const target = new Date(dateString);
        const diff = target - now;
        return diff > 0 && diff <= 24 * 60 * 60 * 1000; // Within 24 hours
    }

    /**
     * Render case timeline
     */
    renderCaseTimeline(caseId = 'all') {
        const timelineContainer = document.getElementById('caseTimeline');
        if (!timelineContainer) return;
        
        let timeline;
        if (caseId === 'all') {
            // Show all case events
            const allCaseEvents = this.events.filter(e => e.caseId);
            const allCaseDeadlines = this.deadlines.filter(d => d.caseId);
            timeline = [...allCaseEvents, ...allCaseDeadlines];
        } else {
            // Show specific case timeline
            timeline = this.getCaseTimeline(caseId);
        }
        
        // Sort by date
        timeline.sort((a, b) => {
            const dateA = new Date(a.start || a.dueDate);
            const dateB = new Date(b.start || b.dueDate);
            return dateA - dateB;
        });
        
        if (timeline.length === 0) {
            timelineContainer.innerHTML = '<p class="text-muted">No case events found</p>';
            return;
        }
        
        timelineContainer.innerHTML = timeline.map(item => {
            const isEvent = item.start !== undefined;
            const date = isEvent ? new Date(item.start) : new Date(item.dueDate);
            const icon = this.getEventIcon(isEvent ? item.type : 'deadline');
            const iconClass = isEvent ? item.type : 'deadline';
            
            return `
                <div class="case-timeline-item">
                    <div class="case-timeline-icon ${iconClass}">
                        <i class="fas fa-${icon}"></i>
                    </div>
                    <div class="case-timeline-content">
                        <div class="case-timeline-title">${item.title}</div>
                        <div class="case-timeline-time">${this.formatDateTime(date.toISOString())}</div>
                    </div>
                    ${item.caseId ? `<span class="case-timeline-case">${item.caseId}</span>` : ''}
                </div>
            `;
        }).join('');
    }

    /**
     * Filter events by case
     */
    filterByCase(caseId) {
        // Update filter buttons
        document.querySelectorAll('.case-filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-case="${caseId}"]`).classList.add('active');
        
        // Filter calendar events
        if (caseId === 'all') {
            this.renderEvents();
        } else {
            const caseEvents = this.events.filter(e => e.caseId === caseId);
            this.calendar.removeAllEvents();
            this.calendar.addEventSource(caseEvents);
        }
        
        // Update timeline
        this.renderCaseTimeline(caseId);
    }

    /**
     * Get event icon
     */
    getEventIcon(type) {
        const icons = {
            'meeting': 'users',
            'court': 'gavel',
            'deadline': 'clock',
            'consultation': 'user-md',
            'work': 'briefcase'
        };
        return icons[type] || 'calendar';
    }
}

// Global functions for HTML onclick handlers
function showCalendar() {
    // Already on calendar view
}

function showDeadlines() {
    calendar.renderDeadlines();
}

function showNotifications() {
    const panel = document.getElementById('notificationPanel');
    panel.style.display = panel.style.display === 'block' ? 'none' : 'block';
}

function hideNotifications() {
    document.getElementById('notificationPanel').style.display = 'none';
}

function showQuickAdd() {
    calendar.showQuickAdd();
}

function hideQuickAdd() {
    calendar.hideQuickAdd();
}

function previousMonth() {
    calendar.previousMonth();
}

function nextMonth() {
    calendar.nextMonth();
}

function today() {
    calendar.today();
}

function exportCalendar() {
    calendar.exportCalendar();
}

function shareCalendar() {
    calendar.shareCalendar();
}

function syncCalendar() {
    calendar.syncCalendar();
}

function showSettings() {
    calendar.showSettings();
}

function saveSettings() {
    calendar.saveSettings();
}

function editEvent() {
    calendar.editEvent();
}

function shareEvent() {
    calendar.shareEvent();
}

function exportEvent() {
    calendar.exportEvent();
}

function deleteEvent() {
    calendar.deleteEvent();
}

// Initialize calendar when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.calendar = new AdvancedCalendar();
}); 