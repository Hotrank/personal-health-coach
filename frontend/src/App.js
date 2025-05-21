// -- Import statements stay here --
import React, { useState, useEffect, useRef } from 'react';
import { GoogleLogin, googleLogout } from '@react-oauth/google';
import { jwtDecode } from 'jwt-decode';
import ReactMarkdown from 'react-markdown';
import './App.css';

// -- Subcomponents --

const LoginSection = ({ onSuccess }) => (
  <div className="login-section">
    <GoogleLogin
      onSuccess={onSuccess}
      onError={() => alert('Login Failed')}
    />
  </div>
);

const WelcomeSection = ({ user, onLogout }) => (
  <div className="welcome">
    <p>Welcome, {user.name}</p>
    <button onClick={onLogout}>Logout</button>
  </div>
);

const ChatWindow = ({ messages, endRef }) => (
  <div className="chat-window">
    {messages.map((msg, idx) => (
      <div key={idx} className={`message ${msg.sender === 'user' ? 'user' : 'bot'}`}>
        <strong>{msg.sender === 'user' ? 'You' : 'Coach'}:</strong>
        <ReactMarkdown>{msg.text}</ReactMarkdown>
      </div>
    ))}
    <div ref={endRef} />
  </div>
);

const ChatForm = ({ userInput, setUserInput, onSubmit }) => (
  <form onSubmit={onSubmit} className="chat-form">
    <input
      type="text"
      value={userInput}
      onChange={(e) => setUserInput(e.target.value)}
      placeholder="Type a message..."
    />
    <button type="submit">Send</button>
  </form>
);

function App() {
  const [user, setUser] = useState(null);
  const [userInput, setUserInput] = useState('');
  const [messages, setMessages] = useState([]);
  const endOfMessagesRef = useRef(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleGoogleLoginSuccess = async (credentialResponse) => {
    const token = credentialResponse.credential;
    const decoded = jwtDecode(token);
    setUser({ ...decoded, credential: token });

    try {
      const res = await fetch('http://127.0.0.1:8000/verify-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
      });

      if (!res.ok) throw new Error('Token verification failed');
      const verifiedUser = await res.json();
      console.log('User verified:', verifiedUser);
    } catch (error) {
      console.error('Error verifying token:', error);
      alert('Login verification failed');
      setUser(null);
    }
  };

  const handleLogout = () => {
    googleLogout();
    setUser(null);
    setMessages([]);
    setUserInput('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    addMessage({ sender: 'user', text: userInput });
    addMessage({ sender: 'bot', text: '' });

    try {
      const res = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: userInput, token: user?.credential }),
      });

      if (!res.body) throw new Error('No response body');
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let botText = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        botText += decoder.decode(value, { stream: true });

        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = { sender: 'bot', text: botText };
          return updated;
        });
      }
    } catch (error) {
      addMessage({ sender: 'bot', text: 'Error: backend unavailable.' });
    }

    setUserInput('');
  };

  const addMessage = (msg) => setMessages((prev) => [...prev, msg]);

  return (
    <div className="App">
      <h1>My Health Coach</h1>
      {!user ? (
        <LoginSection onSuccess={handleGoogleLoginSuccess} />
      ) : (
        <>
          <WelcomeSection user={user} onLogout={handleLogout} />
          <ChatWindow messages={messages} endRef={endOfMessagesRef} />
          <ChatForm
            userInput={userInput}
            setUserInput={setUserInput}
            onSubmit={handleSubmit}
          />
        </>
      )}
    </div>
  );
}

export { ChatWindow };
export default App;
