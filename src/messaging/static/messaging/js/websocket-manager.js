// static/js/websocket-manager.js - NEW FILE
class ChatWebSocketManager {
    constructor(chatId, accessToken) {
        this.chatId = chatId;
        this.accessToken = accessToken;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.messageHandlers = [];
    }
    
    connect() {
        const wsScheme = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsScheme}//${window.location.host}/ws/chat/${this.chatId}/?token=${this.accessToken}`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = (event) => {
            console.log('WebSocket connected to chat', this.chatId);
            this.reconnectAttempts = 0;
            this.onConnected();
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.ws.onclose = (event) => {
            console.log('WebSocket disconnected');
            this.onDisconnected();
            
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                setTimeout(() => this.connect(), 1000 * this.reconnectAttempts);
            }
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
    
    sendMessage(content) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                'type': 'chat_message',
                'message': content
            }));
        } else {
            console.error('WebSocket not connected');
        }
    }
    
    sendTypingStart() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({'type': 'typing_start'}));
        }
    }
    
    sendTypingStop() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({'type': 'typing_stop'}));
        }
    }
    
    handleMessage(data) {
        switch(data.type) {
            case 'new_message':
                this.onNewMessage(data.data);
                break;
            case 'typing_start':
                this.onTypingStart(data.username);
                break;
            case 'typing_stop':
                this.onTypingStop(data.username);
                break;
            case 'user_online':
                this.onUserOnline(data.username);
                break;
            case 'user_offline':
                this.onUserOffline(data.username);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }
    
    // Override these in your app
    onConnected() {}
    onDisconnected() {}
    onNewMessage(message) {}
    onTypingStart(username) {}
    onTypingStop(username) {}
    onUserOnline(username) {}
    onUserOffline(username) {}
}

// Export for use in other files
window.ChatWebSocketManager = ChatWebSocketManager;