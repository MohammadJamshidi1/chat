import { useState, useEffect } from 'react';
import { getChatList } from '../services/api';

function ChatList({ onSelectChat }) {
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadChats();
  }, []);


  const loadChats = async () => {
    try {
        const data = await getChatList();
        setChats(data);
        setLoading(false);
    }
    catch(error){
        setError('Failed to load chats');
        setLoading(false);
    }
  };

   if (loading) return <div>Loading chats...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div style={styles.container}>
      <h3>Your Chats</h3>
      {chats.length === 0 ? (
        <p>No chats yet. Start a conversation!</p>
      ) : (
        <div style={styles.chatList}>
          {chats.map((chat) => (
            <div
              key={chat.id}
              onClick={() => onSelectChat(chat)}
              style={styles.chatItem}
            >
              <div style={styles.chatInfo}>
                <strong>
                  {chat.participants.map(p => p.username).join(', ')}
                </strong>
                {chat.last_message && (
                  <p style={styles.lastMessage}>
                    {chat.last_message.content}
                  </p>
                )}
              </div>
              <div style={styles.chatMeta}>
                {chat.last_message && (
                  <small>
                    {new Date(chat.last_message.sent_at).toLocaleTimeString()}
                  </small>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    width: '300px',
    borderRight: '1px solid #ddd',
    padding: '20px',
    height: '100vh',
    overflowY: 'auto',
  },
  chatList: {
    marginTop: '20px',
  },
  chatItem: {
    padding: '15px',
    borderBottom: '1px solid #eee',
    cursor: 'pointer',
    display: 'flex',
    justifyContent: 'space-between',
    transition: 'background 0.2s',
  },
  chatInfo: {
    flex: 1,
  },
  lastMessage: {
    color: '#666',
    fontSize: '14px',
    margin: '5px 0 0 0',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  chatMeta: {
    fontSize: '12px',
    color: '#999',
  },
};

export default ChatList;
