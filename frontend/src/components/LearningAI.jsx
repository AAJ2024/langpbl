import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export default function LearningAI({ modelId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [retraining, setRetraining] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Update stats every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/stats`);
      setStats(response.data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

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
        temperature: 0.7,
        session_id: sessionId
      });

      const aiMessage = { role: 'assistant', content: response.data.response };
      setMessages(prev => [...prev, aiMessage]);
      
      // Update stats after conversation
      fetchStats();
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

  const handleRetrain = async () => {
    if (!window.confirm('This will retrain the AI with all recent conversations. Continue?')) {
      return;
    }

    setRetraining(true);
    try {
      const response = await axios.post(`${API_URL}/retrain`, {
        model_id: modelId
      });
      
      alert(`✅ Retraining started! Training ID: ${response.data.training_id}`);
      fetchStats();
    } catch (err) {
      alert('❌ Failed to start retraining');
    } finally {
      setRetraining(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      {/* Stats Panel */}
      {stats && (
        <div className="card" style={{ marginBottom: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem', color: '#fff' }}>
                🧠 Continuous Learning AI
              </h3>
              <div style={{ display: 'flex', gap: '2rem', color: '#ccc', fontSize: '0.9rem' }}>
                <div>
                  📚 Total Conversations: <span style={{ color: '#fff', fontWeight: 'bold' }}>{stats.total}</span>
                </div>
                <div>
                  ⏳ Pending Training: <span style={{ color: '#fcd34d', fontWeight: 'bold' }}>{stats.pending_training}</span>
                </div>
              </div>
            </div>
            <button
              onClick={handleRetrain}
              disabled={retraining || stats.pending_training === 0}
              className="btn btn-primary"
            >
              {retraining ? '⏳ Training...' : '🚀 Retrain AI'}
            </button>
          </div>
          
          {stats.pending_training >= 20 && (
            <div className="alert alert-info" style={{ marginTop: '1rem', marginBottom: 0 }}>
              💡 You have {stats.pending_training} new conversations! Consider retraining the AI to improve its responses.
            </div>
          )}
        </div>
      )}

      {/* Chat Interface */}
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
            <div style={{ textAlign: 'center', marginTop: '2rem' }}>
              <p style={{ color: '#ccc', fontSize: '1.1rem', marginBottom: '1rem' }}>
                👋 Hi! I'm a continuously learning AI.
              </p>
              <p style={{ color: '#999', fontSize: '0.9rem' }}>
                Every conversation helps me get smarter! 🧠
              </p>
            </div>
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
            placeholder="Type your message... (I'll remember this!)"
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