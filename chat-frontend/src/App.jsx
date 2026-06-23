import { useState , useEffect } from "react";

import Login from "./components/Login";
import ChatList from "./components/ChatList";
import ChatWindow from "./components/ChatWindow";
import { sendMessage } from "./services/api";


function App(){

  const [isLoggedIn , setIsLoggedIn] = useState(false);
  const [selectedChat, setSelectedChat] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if(token){
      setIsLoggedIn(true);
    }
  } , [])

  const handleLoginSuccess = (data) => {
    setIsLoggedIn(true);
  };


  const handleLogout = () => {
    localStorage.clear();
    setIsLoggedIn(false);
    setSelectedChat(null);
  }


  if (!isLoggedIn) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div style={styles.container}>
      <div style={styles.sidebar}>
        <div style={styles.header}>
          <h2>Chats</h2>
          <button onClick={handleLogout} style={styles.logoutButton}>
            Logout
          </button>
        </div>
        <ChatList onSelectChat={setSelectedChat} />
      </div>
      <div style={styles.main}>
        <ChatWindow chat={selectedChat}/>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    height: '100vh',
  },
  sidebar: {
    width: '300px',
    borderRight: '1px solid #ddd',
  },
  header: {
    padding: '20px',
    borderBottom: '1px solid #ddd',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  main: {
    flex: 1,
  },
  logoutButton: {
    padding: '5px 10px',
    backgroundColor: '#dc3545',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
};

export default App;
