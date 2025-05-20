import React, { useState } from 'react';
import './App.css';

function App() {
  const [userInput, setUserInput] = useState('');
  const [messages, setMessages] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!userInput.trim()) return;

    const newUserMessage = { sender: 'user', text: userInput };
    setMessages((prev) => [...prev, newUserMessage]);

    try {
      const res = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: userInput }),
      });

      const data = await res.json();
      const newBotMessage = { sender: 'bot', text: data.response };
      setMessages((prev) => [...prev, newBotMessage]);
    } catch (error) {
      const errorMessage = { sender: 'bot', text: 'Error: backend unavailable.' };
      setMessages((prev) => [...prev, errorMessage]);
    }

    setUserInput('');
  };

  return (
    <div className="App">
      <h1>Health Coach</h1>
      <div className="chat-window">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.sender === 'user' ? 'user' : 'bot'}`}
          >
            <strong>{msg.sender === 'user' ? 'You' : 'coach'}:</strong> {msg.text}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="chat-form">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Type a message..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

export default App;

