/**
 * ANSE Dashboard Main Application
 * Orchestrates WebSocket connection, panel management, and UI updates
 */

class ANSEDashboard {
    constructor(config = {}) {
        this.config = {
            wsUrl: config.wsUrl || 'ws://localhost:8000',
            autoConnect: config.autoConnect !== false,
            ...config
        };

        this.ws = null;
        this.panelManager = null;
        this.stats = {
            totalEvents: 0,
            connectedTime: null,
            lastEvent: null
        };

        this.init();
    }

    /**
     * Initialize the dashboard
     */
    async init() {
        console.log('[Dashboard] Initializing ANSE Dashboard...');

        // Setup panel manager
        this.panelManager = new PanelManager('#panels-container');
        this.registerPanels();

        // Setup WebSocket
        this.ws = new ANSEWebSocketManager(this.config.wsUrl);
        this.setupWebSocketListeners();

        // Setup UI
        this.setupUI();

        // Auto-connect if enabled
        if (this.config.autoConnect) {
            await this.connect();
        }
    }

    /**
     * Register all panel types
     */
    registerPanels() {
        this.panelManager.registerPanel('sensor', SensorPanel);
        this.panelManager.registerPanel('actuator', ActuatorPanel);
        this.panelManager.registerPanel('reflex', ReflexPanel);
        this.panelManager.registerPanel('worldmodel', WorldModelPanel);
        this.panelManager.registerPanel('eventlog', EventLogPanel);

        console.log('[Dashboard] Panel types registered');
    }

    /**
     * Setup WebSocket event listeners
     */
    setupWebSocketListeners() {
        // Connection events
        this.ws.on('connected', (data) => {
            console.log('[Dashboard] Connected to ANSE backend');
            this.setConnectionStatus('connected');
            this.stats.connectedTime = data.timestamp;
            this.updateStatusBar();

            // Create default panels
            this.createDefaultPanels();
        });

        this.ws.on('disconnected', (data) => {
            console.log('[Dashboard] Disconnected from ANSE backend');
            this.setConnectionStatus('disconnected');
            this.updateStatusBar();
        });

        this.ws.on('error', (data) => {
            console.error('[Dashboard] WebSocket error:', data);
            this.setConnectionStatus('error');
        });

        // Event routing
        this.ws.on('sensor', (event) => this.handleEvent(event));
        this.ws.on('reflex', (event) => this.handleEvent(event));
        this.ws.on('actuator', (event) => this.handleEvent(event));
        this.ws.on('worldmodel', (event) => this.handleEvent(event));
        this.ws.on('system', (event) => this.handleEvent(event));
        this.ws.on('message', (event) => this.updateStats());
    }

    /**
     * Handle incoming events
     */
    handleEvent(event) {
        this.stats.lastEvent = event.timestamp;
        this.stats.totalEvents++;

        // Route to panel manager
        this.panelManager.routeEvent({
            type: event.type,
            timestamp: event.timestamp,
            data: event
        });

        this.updateStatusBar();
    }

    /**
     * Setup UI controls
     */
    setupUI() {
        // Connection button
        const connectBtn = document.querySelector('#connect-btn');
        if (connectBtn) {
            connectBtn.addEventListener('click', async () => {
                if (this.ws.isConnected()) {
                    this.disconnect();
                } else {
                    await this.connect();
                }
            });
        }

        // Stats
        this.updateStatusBar();
    }

    /**
     * Create default panels (world model and event log)
     */
    createDefaultPanels() {
        // World model panel is always shown
        if (!this.panelManager.getPanel('worldmodel-panel')) {
            this.panelManager.createPanel('worldmodel', 'worldmodel-panel', {});
        }

        // Event log panel is always shown
        if (!this.panelManager.getPanel('eventlog-panel')) {
            this.panelManager.createPanel('eventlog', 'eventlog-panel', {});
        }

        // Reflexes panel is always shown
        if (!this.panelManager.getPanel('reflexes-panel')) {
            this.panelManager.createPanel('reflex', 'reflexes-panel', {});
        }
    }

    /**
     * Connect to ANSE backend
     */
    async connect() {
        console.log('[Dashboard] Connecting to ANSE backend...');
        this.setConnectionStatus('connecting');

        try {
            await this.ws.connect();
            this.setConnectionStatus('connected');
        } catch (e) {
            console.error('[Dashboard] Connection failed:', e);
            this.setConnectionStatus('error');
        }
    }

    /**
     * Disconnect from ANSE backend
     */
    disconnect() {
        console.log('[Dashboard] Disconnecting from ANSE backend...');
        this.ws.disconnect();
        this.setConnectionStatus('disconnected');
    }

    /**
     * Set connection status in UI
     */
    setConnectionStatus(status) {
        const statusEl = document.querySelector('.connection-status');
        const statusBtn = document.querySelector('#connect-btn');

        if (statusEl) {
            statusEl.className = `connection-status status-${status}`;
            const messages = {
                'connected': 'Connected',
                'disconnected': 'Disconnected',
                'connecting': 'Connecting...',
                'error': 'Error'
            };
            statusEl.textContent = messages[status] || status;
        }

        if (statusBtn) {
            const btnTexts = {
                'connected': 'Disconnect',
                'disconnected': 'Connect',
                'connecting': 'Connecting...',
                'error': 'Retry'
            };
            statusBtn.textContent = btnTexts[status] || 'Connect';
            statusBtn.disabled = status === 'connecting';
        }
    }

    /**
     * Update statistics display
     */
    updateStats() {
        // Placeholder for future stats updates
    }

    /**
     * Update status bar
     */
    updateStatusBar() {
        const statsEl = document.querySelector('.stats-bar');
        if (!statsEl) return;

        const panelCount = this.panelManager.getPanelCount();
        const uptime = this.calculateUptime();

        statsEl.innerHTML = `
            <span>Panels: ${panelCount}</span>
            <span>Events: ${this.stats.totalEvents}</span>
            <span>Uptime: ${uptime}</span>
            <span>Status: ${this.ws.isConnected() ? '✓ Connected' : '✗ Disconnected'}</span>
        `;
    }

    /**
     * Calculate connection uptime
     */
    calculateUptime() {
        if (!this.stats.connectedTime) return 'N/A';

        const start = new Date(this.stats.connectedTime);
        const now = new Date();
        const seconds = Math.floor((now - start) / 1000);

        if (seconds < 60) return `${seconds}s`;
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
        return `${Math.floor(seconds / 3600)}h`;
    }

    /**
     * Public API: Get panel manager
     */
    getPanelManager() {
        return this.panelManager;
    }

    /**
     * Public API: Get WebSocket manager
     */
    getWebSocketManager() {
        return this.ws;
    }
}

// Initialize dashboard on page load
window.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new ANSEDashboard({
        wsUrl: 'ws://localhost:8001',
        autoConnect: true
    });
});

// Export for use
window.ANSEDashboard = ANSEDashboard;
