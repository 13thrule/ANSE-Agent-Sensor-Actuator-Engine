/**
 * Actuator Panel
 * Displays actuator state and command history
 * Dynamically created for each active actuator plugin
 */

class ActuatorPanel extends BasePanel {
    constructor(panelId, config) {
        super(panelId, config);
        this.panelType = 'actuator';
        this.actuatorName = config.actuatorName || 'Unknown';
        this.actuatorType = config.actuatorType || 'generic';
        this.state = config.state || 'IDLE';
        this.lastCommand = null;
        this.commandCount = 0;
        this.stateHistory = [];
        this.maxHistorySize = 20;
    }

    getTitle() {
        return `⚙️ ${this.formatName(this.actuatorName)}`;
    }

    getContentHTML() {
        return `
            <div class="actuator-content">
                <div class="actuator-state">
                    <div class="state-badge state-${this.state.toLowerCase()}">
                        ${this.state}
                    </div>
                    <div class="state-description">${this.getStateDescription()}</div>
                </div>
                <div class="actuator-info">
                    <div class="info-row">
                        <span class="info-label">Type:</span>
                        <span class="info-value">${this.actuatorType}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Commands:</span>
                        <span class="info-value">0</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Last:</span>
                        <span class="info-value">--</span>
                    </div>
                </div>
                <div class="actuator-history">
                    <div class="history-header">State History</div>
                    <div class="history-list"></div>
                </div>
            </div>
        `;
    }

    onRender() {
        // Initialize
        this.updateDisplay();
    }

    onUpdate(event) {
        const { state, timestamp } = event.data;
        const previousState = this.state;
        this.state = state;
        this.commandCount++;
        this.lastCommand = timestamp;

        // Track state changes
        this.stateHistory.unshift({
            state,
            timestamp,
            duration: this.calculateDuration(timestamp)
        });
        if (this.stateHistory.length > this.maxHistorySize) {
            this.stateHistory.pop();
        }

        // Add animation if state changed
        if (previousState !== state) {
            this.element.classList.add('state-change');
            setTimeout(() => {
                this.element.classList.remove('state-change');
            }, 500);
        }

        this.updateDisplay();
        this.setStatus('active');
    }

    updateDisplay() {
        // Update state badge
        const badge = this.element.querySelector('.state-badge');
        if (badge) {
            badge.className = `state-badge state-${this.state.toLowerCase()}`;
            badge.textContent = this.state;
        }

        // Update description
        const description = this.element.querySelector('.state-description');
        if (description) {
            description.textContent = this.getStateDescription();
        }

        // Update info
        const infoValues = this.element.querySelectorAll('.info-value');
        if (infoValues.length >= 3) {
            infoValues[1].textContent = this.commandCount;
            infoValues[2].textContent = this.lastCommand ? this.formatTime(this.lastCommand) : '--';
        }

        // Update history
        this.updateHistory();
    }

    updateHistory() {
        const historyList = this.element.querySelector('.history-list');
        if (!historyList) return;

        historyList.innerHTML = this.stateHistory.slice(0, 5).map((entry, idx) => `
            <div class="history-entry">
                <span class="history-state">${entry.state}</span>
                <span class="history-time">${this.formatTime(entry.timestamp)}</span>
                ${idx === 0 ? '<span class="history-current">current</span>' : ''}
            </div>
        `).join('');
    }

    getStateDescription() {
        const descriptions = {
            'IDLE': 'Waiting for commands',
            'MOVING': 'Currently executing',
            'STOPPED': 'Execution halted',
            'ERROR': 'Error detected',
            'DISABLED': 'Not available'
        };
        return descriptions[this.state] || this.state;
    }

    calculateDuration(timestamp) {
        // Calculate how long actuator has been in current state
        if (!this.stateHistory.length) return 0;
        const now = new Date(timestamp);
        const prev = new Date(this.stateHistory[0]?.timestamp || timestamp);
        return Math.floor((now - prev) / 1000);
    }

    formatTime(isoString) {
        try {
            const date = new Date(isoString);
            return date.toLocaleTimeString();
        } catch {
            return '--';
        }
    }

    formatName(name) {
        return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
}

// Export for use in browser
window.ActuatorPanel = ActuatorPanel;
