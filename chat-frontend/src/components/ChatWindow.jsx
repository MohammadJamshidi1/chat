import { useState, useEffect, useRef } from 'react';
import { getChatMessages } from '../services/api';
import useWebSocket from '../hooks/useWebSocket';

function ChatWindow({ chat }) {
  const [initialMessages, setInitialMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newMessage, setNewMessage] = useState('');
  const messagesEndRef = useRef(null);
  const typingTimeoutRef = useRef(null);
  
  const currentUserId = localStorage.getItem('user_id');
  const accessToken = localStorage.getItem('access_token');

  const { 
    messages: wsMessages, 
    isConnected, 
    sendMessage: sendWebSocketMessage,
    sendTypingStart,
    sendTypingStop,
    setMessages: setWsMessages 
  } = useWebSocket(chat?.id, accessToken);

  const allMessages = [...initialMessages, ...wsMessages];

  useEffect(() => {
    if (chat) {
      loadMessages();
    }
  }, [chat]);

  useEffect(() => {
    scrollToBottom();
  }, [allMessages]);

  const loadMessages = async () => {
    try {
      setLoading(true);
      const request = await getChatMessages(chat.id);
      setInitialMessages(request.messages);
      setWsMessages([]); 
      setLoading(false);
    } catch (err) {
      console.error('Failed to load messages:', err);
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = (e) => {
    e.preventDefault();
    if (newMessage.trim()) {

      const sent = sendWebSocketMessage(newMessage);
      
      if (sent) {
        setNewMessage('');
        sendTypingStop();
      } else {
        alert('WebSocket not connected. Please refresh.');
      }
    }
  };

  const handleTyping = () => {
    sendTypingStart();
    
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    
    typingTimeoutRef.current = setTimeout(() => {
      sendTypingStop();
    }, 1000);
  };

  if (!chat) {
    return (
      <div style={styles.container}>
        <p style={styles.noChat}>Select a chat to start messaging</p>
      </div>
    );
  }

  if (loading) {
    return <div style={styles.container}>Loading messages...</div>;
  }

  return (
    <div style={styles.container}>
      {/* Chat Header */}
      <div style={styles.header}>
        <h3>{chat.participants.map(p => p.username).join(', ')}</h3>
        <div style={styles.connectionStatus}>
          <span style={{
            ...styles.statusDot,
            backgroundColor: isConnected ? '#28a745' : '#dc3545'
          }} />
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      </div>

      {/* Messages */}
      <div style={styles.messagesContainer}>
        {allMessages.length === 0 ? (
          <p style={styles.noMessages}>No messages yet. Say hi! 👋</p>
        ) : (
          allMessages.map((message, index) => {
            const isMyMessage = message.sender.id == currentUserId;
            return (
              <div
                key={message.id || `msg-${index}`}
                style={{
                  ...styles.messageWrapper,
                  justifyContent: isMyMessage ? 'flex-end' : 'flex-start',
                }}
              >
                <div
                  style={{
                    ...styles.message,
                    backgroundColor: isMyMessage ? '#007bff' : '#e9ecef',
                    color: isMyMessage ? 'white' : 'black',
                  }}
                >
                  {!isMyMessage && (
                    <strong style={styles.senderName}>
                      {message.sender.username}
                    </strong>
                  )}
                  <p style={styles.messageContent}>{message.content}</p>
                  <small style={styles.timestamp}>
                    {new Date(message.sent_at).toLocaleTimeString()}
                  </small>
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <form onSubmit={handleSend} style={styles.inputContainer}>
        <input
          type="text"
          value={newMessage}
          onChange={(e) => {
            setNewMessage(e.target.value);
            handleTyping();
          }}
          placeholder="Type a message..."
          style={styles.input}
          disabled={!isConnected}
        />
        <button 
          type="submit" 
          style={{
            ...styles.sendButton,
            opacity: isConnected ? 1 : 0.5,
            cursor: isConnected ? 'pointer' : 'not-allowed'
          }}
          disabled={!isConnected}
        >
          Send
        </button>
      </form>
    </div>
  );
}

const styles = {
  container: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
  },
  header: {
    padding: '20px',
    borderBottom: '1px solid #ddd',
    backgroundColor: '#f8f9fa',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  connectionStatus: {
    display: 'flex',
    alignItems: 'center',
    fontSize: '14px',
    color: '#666',
  },
  statusDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    marginRight: '8px',
  },
  messagesContainer: {
    flex: 1,
    overflowY: 'auto',
    padding: '20px',
    backgroundColor: '#f5f5f5',
  },
  noChat: {
    textAlign: 'center',
    marginTop: '50px',
    color: '#666',
  },
  noMessages: {
    textAlign: 'center',
    color: '#666',
  },
  messageWrapper: {
    display: 'flex',
    marginBottom: '10px',
  },
  message: {
    maxWidth: '60%',
    padding: '10px 15px',
    borderRadius: '18px',
    wordWrap: 'break-word',
  },
  senderName: {
    display: 'block',
    fontSize: '12px',
    marginBottom: '5px',
    opacity: 0.8,
  },
  messageContent: {
    margin: '0',
  },
  timestamp: {
    fontSize: '11px',
    opacity: 0.7,
    display: 'block',
    marginTop: '5px',
  },
  inputContainer: {
    display: 'flex',
    padding: '20px',
    borderTop: '1px solid #ddd',
    backgroundColor: 'white',
  },
  input: {
    flex: 1,
    padding: '10px',
    fontSize: '16px',
    border: '1px solid #ddd',
    borderRadius: '20px',
    outline: 'none',
  },
  sendButton: {
    marginLeft: '10px',
    padding: '10px 20px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '20px',
    cursor: 'pointer',
  },
};

export default ChatWindow;