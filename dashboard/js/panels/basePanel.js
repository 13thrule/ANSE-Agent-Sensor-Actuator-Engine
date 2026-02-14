/**
 * Base Panel Class
 * All dashboard panels inherit from this class
 * Provides common functionality for rendering, updating, and destroying panels
 */

class BasePanel {
    constructor(panelId, config = {}) {
        this.panelId = panelId;
        this.panelType = config.panelType || 'base';
        this.config = config;
        this.element = null;
        this.data = {};
        this.lastUpdate = null;
        this.eventHistory = [];
        this.maxHistorySize = 100;
    }

    /**
     * Render the panel into the DOM
     */
    render(container) {
        // Create panel element
        this.element = this.createPanelElement();
        container.appendChild(this.element);
        this.onRender();
    }

    /**
     * Create the base panel element structure
     */
    createPanelElement() {
        const panel = document.createElement('div');
        panel.className = `panel ${this.panelType}-panel`;
        panel.id = this.panelId;
        panel.innerHTML = `
            <div class="panel-header">
                <div class="panel-title">${this.getTitle()}</div>
                <div class="panel-status">
                    <span class="status-indicator status-idle"></span>
                    <span class="status-text">Ready</span>
                </div>
            </div>
            <div class="panel-content">
                ${this.getContentHTML()}
            </div>
        `;
        return panel;
    }

    /**
     * Get panel title (override in subclasses)
     */
    getTitle() {
        return 'Panel';
    }

    /**
     * Get panel content HTML (override in subclasses)
     */
    getContentHTML() {
        return '<p>No content</p>';
    }

    /**
     * Called after panel is rendered (override in subclasses)
     */
    onRender() {
        // Override in subclasses
    }

    /**
     * Update panel with new event data
     */
    update(event) {
        this.lastUpdate = new Date();
        this.eventHistory.unshift(event);
        if (this.eventHistory.length > this.maxHistorySize) {
            this.eventHistory.pop();
        }

        // Update status indicator
        this.setStatus('active');

        // Call subclass update
        this.onUpdate(event);
    }

    /**
     * Called when panel receives update (override in subclasses)
     */
    onUpdate(event) {
        // Override in subclasses
    }

    /**
     * Set panel status
     */
    setStatus(status) {
        const indicator = this.element?.querySelector('.status-indicator');
        const text = this.element?.querySelector('.status-text');
        const time = new Date().toLocaleTimeString();

        if (indicator) {
            indicator.className = `status-indicator status-${status}`;
        }
        if (text) {
            text.textContent = `${status.toUpperCase()} · ${time}`;
        }
    }

    /**
     * Get content container
     */
    getContentElement() {
        return this.element?.querySelector('.panel-content');
    }

    /**
     * Destroy the panel
     */
    destroy() {
        if (this.element) {
            this.onDestroy();
            this.element.remove();
            this.element = null;
        }
    }

    /**
     * Called before panel is destroyed (override in subclasses)
     */
    onDestroy() {
        // Override in subclasses
    }

    /**
     * Get event history
     */
    getHistory() {
        return this.eventHistory;
    }

    /**
     * Clear event history
     */
    clearHistory() {
        this.eventHistory = [];
    }
}

// Export for use in browser
window.BasePanel = BasePanel;
