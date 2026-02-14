/**
 * WebSocket Handler for ANSE Dashboard
 * Manages connection to ANSE backend and event distribution to panels
 * 
 * Event Types:
 * - sensor_event: New sensor reading
 * - reflex_event: Reflex triggered/cleared
 * - actuator_event: Actuator command executed
 * - world_model_update: Complete interpreted state snapshot
 * - system_event: System-level events (startup, shutdown, etc.)
 */

class ANSEWebSocketManager {
    constructor(url = 'ws://localhost:8000') {
        this.url = url;
        this.ws = null;
        this.listeners = {};
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.isManualClose = false;
    }

    /**
     * Connect to ANSE WebSocket server
     */
    async connect() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            return Promise.resolve();
        }

        if (this.isConnecting) {
            return;
        }

        this.isConnecting = true;
        this.isManualClose = false;

        return new Promise((resolve, reject) => {
            try {
                this.ws = new WebSocket(this.url);

                this.ws.onopen = () => {
                    console.log('[WebSocket] Connected to ANSE backend');
                    this.isConnecting = false;
                    this.reconnectAttempts = 0;
                    this.emit('connected', { timestamp: new Date().toISOString() });
                    resolve();
                };

                this.ws.onmessage = (event) => {
                    try {
                        const message = JSON.parse(event.data);
                        this.handleMessage(message);
                    } catch (e) {
                        console.error('[WebSocket] Failed to parse message:', e);
                    }
                };

                this.ws.onerror = (error) => {
                    console.error('[WebSocket] Error:', error);
                    this.isConnecting = false;
                    this.emit('error', { message: 'WebSocket error' });
                    reject(error);
                };

                this.ws.onclose = () => {
                    console.log('[WebSocket] Connection closed');
                    this.isConnecting = false;
                    this.emit('disconnected', { timestamp: new Date().toISOString() });

                    // Attempt reconnect if not manual close
                    if (!this.isManualClose && this.reconnectAttempts < this.maxReconnectAttempts) {
                        this.reconnectAttempts++;
                        console.log(`[WebSocket] Reconnecting... attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
                        setTimeout(() => this.connect(), this.reconnectDelay * this.reconnectAttempts);
                    }
                };
            } catch (e) {
                this.isConnecting = false;
                reject(e);
            }
        });
    }

    /**
     * Handle incoming message from backend
     */
    handleMessage(message) {
        const { type, timestamp, data } = message;

        // Route to specific handler based on type
        switch (type) {
            case 'sensor_event':
                this.emit('sensor', { ...data, timestamp, type });
                break;

            case 'reflex_event':
                this.emit('reflex', { ...data, timestamp, type });
                break;

            case 'actuator_event':
                this.emit('actuator', { ...data, timestamp, type });
                break;

            case 'world_model_update':
                this.emit('worldmodel', { ...data, timestamp, type });
                break;

            case 'system_event':
                this.emit('system', { ...data, timestamp, type });
                break;

            default:
                console.warn('[WebSocket] Unknown message type:', type);
        }

        // Emit to all listeners
        this.emit('message', message);
    }

    /**
     * Register event listener
     */
    on(eventName, callback) {
        if (!this.listeners[eventName]) {
            this.listeners[eventName] = [];
        }
        this.listeners[eventName].push(callback);

        // Return unsubscribe function
        return () => {
            this.listeners[eventName] = this.listeners[eventName].filter(cb => cb !== callback);
        };
    }

    /**
     * Emit event to all listeners
     */
    emit(eventName, data) {
        if (this.listeners[eventName]) {
            this.listeners[eventName].forEach(callback => {
                try {
                    callback(data);
                } catch (e) {
                    console.error(`[WebSocket] Error in listener for ${eventName}:`, e);
                }
            });
        }
    }

    /**
     * Send message to backend (if needed)
     */
    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            console.warn('[WebSocket] Connection not open, cannot send message');
        }
    }

    /**
     * Disconnect from backend
     */
    disconnect() {
        this.isManualClose = true;
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    /**
     * Check if connected
     */
    isConnected() {
        return this.ws && this.ws.readyState === WebSocket.OPEN;
    }
}

// Export for use in browser
window.ANSEWebSocketManager = ANSEWebSocketManager;
