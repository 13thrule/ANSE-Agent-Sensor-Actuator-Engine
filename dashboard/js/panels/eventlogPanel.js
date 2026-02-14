/**
 * Event Log Panel
 * Displays all system events in real-time
 * Shows sensor, reflex, actuator, and world model events
 */

class EventLogPanel extends BasePanel {
    constructor(panelId, config) {
        super(panelId, config);
        this.panelType = 'eventlog';
        this.events = [];
        this.maxEvents = 100;
        this.autoScroll = true;
        this.filterType = 'all'; // 'all', 'sensor', 'reflex', 'actuator', 'worldmodel'
    }

    getTitle() {
        return '📋 Event Log';
    }

    getContentHTML() {
        return `
            <div class="eventlog-content">
                <div class="log-controls">
                    <div class="filter-buttons">
                        <button class="filter-btn active" data-filter="all">All</button>
                        <button class="filter-btn" data-filter="sensor">Sensors</button>
                        <button class="filter-btn" data-filter="reflex">Reflexes</button>
                        <button class="filter-btn" data-filter="actuator">Actuators</button>
                        <button class="filter-btn" data-filter="worldmodel">World Model</button>
                    </div>
                    <div class="log-actions">
                        <button class="clear-btn" id="clear-log-btn">Clear</button>
                        <label class="autoscroll-label">
                            <input type="checkbox" id="autoscroll-toggle" checked>
                            Auto-scroll
                        </label>
                    </div>
                </div>
                <div class="event-list" id="event-list"></div>
            </div>
        `;
    }

    onRender() {
        this.setupControls();
        this.updateDisplay();
    }

    setupControls() {
        // Filter buttons
        this.element.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.element.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.filterType = e.target.dataset.filter;
                this.updateDisplay();
            });
        });

        // Clear button
        const clearBtn = this.element.querySelector('#clear-log-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.events = [];
                this.updateDisplay();
            });
        }

        // Auto-scroll toggle
        const autoscrollToggle = this.element.querySelector('#autoscroll-toggle');
        if (autoscrollToggle) {
            autoscrollToggle.addEventListener('change', (e) => {
                this.autoScroll = e.target.checked;
            });
        }
    }

    onUpdate(event) {
        // Add event to log
        this.events.unshift({
            type: event.type,
            timestamp: event.timestamp || new Date().toISOString(),
            data: event.data,
            raw: event
        });

        // Limit size
        if (this.events.length > this.maxEvents) {
            this.events.pop();
        }

        this.updateDisplay();
        this.setStatus('active');
    }

    updateDisplay() {
        const list = this.element.querySelector('#event-list');
        if (!list) return;

        // Filter events
        const filtered = this.filterType === 'all'
            ? this.events
            : this.events.filter(e => e.type === this.filterType);

        // Render events
        list.innerHTML = filtered.map((event, idx) => {
            return this.renderEvent(event, idx);
        }).join('');

        // Auto-scroll to bottom
        if (this.autoScroll) {
            list.scrollTop = list.scrollHeight;
        }
    }

    renderEvent(event, idx) {
        const time = new Date(event.timestamp).toLocaleTimeString();
        const icon = this.getEventIcon(event.type);
        const summary = this.getEventSummary(event);

        return `
            <div class="event-entry event-${event.type}">
                <span class="event-icon">${icon}</span>
                <span class="event-time">${time}</span>
                <span class="event-type">${event.type.toUpperCase()}</span>
                <span class="event-summary">${summary}</span>
                <details class="event-details">
                    <summary>Details</summary>
                    <pre>${JSON.stringify(event.data, null, 2)}</pre>
                </details>
            </div>
        `;
    }

    getEventIcon(type) {
        const icons = {
            'sensor': '📡',
            'reflex': '⚡',
            'actuator': '⚙️',
            'worldmodel': '🧠',
            'system': '⚙️'
        };
        return icons[type] || '•';
    }

    getEventSummary(event) {
        const { data, type } = event;

        switch (type) {
            case 'sensor':
                return `${data.sensor_name}: ${data.value} ${data.sensor_type}`;

            case 'reflex':
                return `${data.reflex_name} ${data.triggered ? 'triggered' : 'cleared'}`;

            case 'actuator':
                return `${data.actuator_name} → ${data.state}`;

            case 'worldmodel':
                return `Distance: ${data.distance_cm}cm, Safe: ${data.safe ? 'yes' : 'no'}`;

            case 'system':
                return data.message || 'system event';

            default:
                return 'event';
        }
    }

    onDestroy() {
        // Cleanup
    }
}

// Export for use in browser
window.EventLogPanel = EventLogPanel;
