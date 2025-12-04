import React, { useState } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export default function ChatInterface({ modelId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        model_id: modelId,
        message: input,
        max_tokens: 256,
        temperature: 0.7
      });

      const aiMessage = { role: 'assistant', content: response.data.response };
      setMessages(prev => [...prev, aiMessage]);
    } catch (err) {
      const errorMessage = { 
        role: 'error', 
        content: err.response?.data?.error || 'Failed to get response' 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div className="card">
        <h2 className="card-title">Chat with {modelId}</h2>

        <div style={{
          height: '500px',
          overflowY: 'auto',
          marginBottom: '1rem',
          padding: '1rem',
          background: 'rgba(0,0,0,0.2)',
          borderRadius: '0.5rem'
        }}>
          {messages.length === 0 && (
            <p style={{ color: '#ccc', textAlign: 'center', marginTop: '2rem' }}>
              Start a conversation...
            </p>
          )}
          
          {messages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                marginBottom: '1rem',
                padding: '1rem',
                borderRadius: '0.5rem',
                background: msg.role === 'user' 
                  ? 'rgba(147, 51, 234, 0.2)' 
                  : msg.role === 'error'
                  ? 'rgba(239, 68, 68, 0.2)'
                  : 'rgba(59, 130, 246, 0.2)',
                marginLeft: msg.role === 'user' ? 'auto' : '0',
                marginRight: msg.role === 'user' ? '0' : 'auto',
                maxWidth: '80%'
              }}
            >
              <div style={{ 
                fontWeight: 'bold', 
                marginBottom: '0.5rem',
                color: msg.role === 'error' ? '#fca5a5' : '#fff'
              }}>
                {msg.role === 'user' ? '👤 You' : msg.role === 'error' ? '⚠️ Error' : '🤖 AI'}
              </div>
              <div style={{ whiteSpace: 'pre-wrap', color: '#fff' }}>
                {msg.content}
              </div>
            </div>
          ))}
          
          {loading && (
            <div style={{ 
              padding: '1rem', 
              background: 'rgba(59, 130, 246, 0.2)',
              borderRadius: '0.5rem',
              maxWidth: '80%'
            }}>
              <div style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>🤖 AI</div>
              <div>Thinking...</div>
            </div>
          )}
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="form-input"
            style={{ flex: 1 }}
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="btn btn-primary"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}