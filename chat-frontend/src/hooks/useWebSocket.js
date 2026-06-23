import { useState , useEffect , useRef } from "react";


function useWebSocket(chatId , access_token){
    const [messages , setMessages] = useState([]);
    const [isConnected , setIsConnected] = useState(false);
    const wsRef = useRef(null);
    const reconnectTimeoutRef = useRef(null);
    const reconnectAttempts = useRef(0);
    const maxReconnectAttempts = 5;


    useEffect(() =>{
        if(!chatId || !access_token) return;

        connectWebSocket();

        return () => {
            console.log("--------------------------------------");
            console.log(wsRef.current);
            if (wsRef.current) {
                wsRef.current.close();
            }
            console.log(reconnectTimeoutRef.current);
            console.log("--------------------------------------");
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
        };
    }, [chatId, access_token]);


    const connectWebSocket = () => {
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

        const wsUrl = `${protocol}//localhost:8080/ws/chat/${chatId}/?token=${access_token}`;

        console.log('🔌 Connecting to WebSocket:', wsUrl);

        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log('✅ WebSocket connected to chat', chatId);
            setIsConnected(true);
            reconnectAttempts.current = 0;
        };

        ws.onmessage = (event) => {
            console.log("===========================================");
            console.log(event)
            console.log("-------------------------------------------")
            console.log(event.data);
            console.log("===========================================");
            const data = JSON.parse(event.data);
            console.log('📨 WebSocket message received:', data);

            handleWebSocketMessage(data);
        };

        ws.onerror = (error) => {
            console.error('❌ WebSocket error:', error);
        };

        ws.onclose = (event) => {
            console.log('🔌 WebSocket closed:', event.code, event.reason);
            setIsConnected(false);

            
            if (reconnectAttempts.current < maxReconnectAttempts) {
                reconnectAttempts.current += 1;
                const delay = 1000 * reconnectAttempts.current;
                console.log(`Reconnecting in ${delay}ms... (attempt ${reconnectAttempts.current})`);
                
                reconnectTimeoutRef.current = setTimeout(() => {
                connectWebSocket();
                }, delay);
            } else {
                console.error('Max reconnection attempts reached');
            }
        };
    };

    const handleWebSocketMessage = (data) => {
        switch (data.type) {
            case 'new_message':
                
                setMessages((prev) => [...prev, data.data]);
                break;

            case 'connection_established':
                console.log('Connection established:', data.message);
                break;

            case 'typing_start':
                console.log(`${data.username} is typing...`);
                break;

            case 'typing_stop':
                console.log(`${data.username} stopped typing`);
                break;

            case 'user_online':
                console.log(`${data.username} is online`);
                break;

            case 'user_offline':
                console.log(`${data.username} is offline`);
                break;

            default:
                console.log('Unknown message type:', data);
        }
    };

    const sendMessage = (content) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'chat_message',
                message: content,
            }));
            return true;
            } else {
                console.error('WebSocket not connected');
            return false;
        }
    };

    const sendTypingStart = () => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'typing_start',
            }));
        }
    };

    const sendTypingStop = () => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'typing_stop',
            }));
        }
    };

    return {
        messages,
        isConnected,
        sendMessage,
        sendTypingStart,
        sendTypingStop,
        setMessages, 
    };
}


export default useWebSocket;

