/**
 * Real-time WebSocket client for live data updates
 */
class RealtimeClient {
    constructor(options = {}) {
        this.sessionId = window.sessionId || options.sessionId;
        this.wsUrl = options.wsUrl || this._getWebSocketUrl();
        this.reconnectInterval = options.reconnectInterval || 5000;
        this.maxReconnectAttempts = options.maxReconnectAttempts || 10;
        this.reconnectAttempts = 0;
        this.isConnected = false;
        this.ws = null;
        this.pingInterval = null;
        this.reconnectTimeout = null;

        // Event callbacks
        this.callbacks = {
            onConnect: options.onConnect || (() => {}),
            onDisconnect: options.onDisconnect || (() => {}),
            onMessage: options.onMessage || (() => {}),
            onError: options.onError || (() => {}),
            onDataChange: options.onDataChange || (() => {})
        };

        // Message handlers for different event types
        this.messageHandlers = new Map();
        this._setupDefaultHandlers();
    }

    _getWebSocketUrl() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        return `${protocol}//${host}/ws/realtime/${this.sessionId}`;
    }

    _setupDefaultHandlers() {
        // Connection status handler
        this.messageHandlers.set('connection_status', (data) => {
            console.log('🔌 Real-time connection status:', data);
            if (data.status === 'connected') {
                this.isConnected = true;
                this.callbacks.onConnect(data);
            }
        });

        // Pong handler for keep-alive
        this.messageHandlers.set('pong', (data) => {
            console.debug('🏓 Received pong');
        });

        // Data change handlers
        this.messageHandlers.set('account_change', (data) => {
            console.log('🏦 Account change detected:', data);
            this.callbacks.onDataChange('account', data);
        });

        this.messageHandlers.set('transaction_change', (data) => {
            console.log('💳 Transaction change detected:', data);
            this.callbacks.onDataChange('transaction', data);
        });

        this.messageHandlers.set('category_change', (data) => {
            console.log('📊 Category change detected:', data);
            this.callbacks.onDataChange('category', data);
        });

        // Data refresh handler
        this.messageHandlers.set('data_refresh', (data) => {
            console.log('🔄 Data refresh triggered:', data);
            this.callbacks.onDataChange('refresh', data);
        });

        // Error handler
        this.messageHandlers.set('error', (data) => {
            console.error('❌ Real-time error:', data);
            this.callbacks.onError(data);
        });

        // Status response handler
        this.messageHandlers.set('status_response', (data) => {
            console.log('📊 Real-time status:', data);
        });
    }

    connect() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            console.log('🔌 Already connected');
            return;
        }

        console.log('🔌 Connecting to real-time service...');

        try {
            this.ws = new WebSocket(this.wsUrl);

            this.ws.onopen = () => {
                console.log('🔌 WebSocket connection established');
                this.reconnectAttempts = 0;
                this._startPingInterval();
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this._handleMessage(data);
                } catch (error) {
                    console.error('❌ Failed to parse WebSocket message:', error, event.data);
                }
            };

            this.ws.onclose = (event) => {
                console.log('🔌 WebSocket connection closed:', event.code, event.reason);
                this.isConnected = false;
                this._stopPingInterval();
                this.callbacks.onDisconnect(event);

                // Attempt to reconnect if not explicitly closed
                if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
                    this._scheduleReconnect();
                }
            };

            this.ws.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.callbacks.onError(error);
            };

        } catch (error) {
            console.error('❌ Failed to create WebSocket connection:', error);
            this.callbacks.onError(error);
            this._scheduleReconnect();
        }
    }

    disconnect() {
        console.log('🔌 Disconnecting from real-time service...');

        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = null;
        }

        this._stopPingInterval();

        if (this.ws) {
            this.ws.close(1000, 'Client disconnect');
            this.ws = null;
        }

        this.isConnected = false;
        this.reconnectAttempts = 0;
    }

    _scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('❌ Max reconnection attempts reached');
            return;
        }

        this.reconnectAttempts++;
        console.log(`🔄 Scheduling reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${this.reconnectInterval}ms`);

        this.reconnectTimeout = setTimeout(() => {
            this.connect();
        }, this.reconnectInterval);
    }

    _startPingInterval() {
        // Send ping every 30 seconds to keep connection alive
        this.pingInterval = setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.send('ping', { timestamp: Date.now() });
            }
        }, 30000);
    }

    _stopPingInterval() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
        }
    }

    _handleMessage(data) {
        const messageType = data.type;

        // Call general message callback
        this.callbacks.onMessage(data);

        // Call specific message handler if exists
        const handler = this.messageHandlers.get(messageType);
        if (handler) {
            handler(data);
        } else {
            console.debug('🔌 Unhandled message type:', messageType, data);
        }
    }

    send(type, data = {}) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            console.warn('⚠️ Cannot send message - WebSocket not connected');
            return false;
        }

        const message = {
            type,
            session_id: this.sessionId,
            timestamp: Date.now(),
            ...data
        };

        try {
            this.ws.send(JSON.stringify(message));
            console.debug('📤 Sent message:', message);
            return true;
        } catch (error) {
            console.error('❌ Failed to send message:', error);
            return false;
        }
    }

    // Public methods for common operations
    refreshData(dataType = 'all') {
        return this.send('refresh_data', { data_type: dataType });
    }

    getStatus() {
        return this.send('get_status');
    }

    // Custom message handler registration
    addMessageHandler(type, handler) {
        this.messageHandlers.set(type, handler);
    }

    removeMessageHandler(type) {
        this.messageHandlers.delete(type);
    }

    // Get connection state
    getConnectionState() {
        if (!this.ws) return 'disconnected';

        switch (this.ws.readyState) {
            case WebSocket.CONNECTING: return 'connecting';
            case WebSocket.OPEN: return 'connected';
            case WebSocket.CLOSING: return 'closing';
            case WebSocket.CLOSED: return 'closed';
            default: return 'unknown';
        }
    }

    // Get connection info
    getConnectionInfo() {
        return {
            sessionId: this.sessionId,
            wsUrl: this.wsUrl,
            isConnected: this.isConnected,
            state: this.getConnectionState(),
            reconnectAttempts: this.reconnectAttempts,
            maxReconnectAttempts: this.maxReconnectAttempts
        };
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RealtimeClient;
}
