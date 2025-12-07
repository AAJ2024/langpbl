import React, { useState, useEffect } from 'react';
import LearningAI from './components/LearningAI';
import axios from 'axios';
import './App.css';

function App() {
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/models');
      const availableModels = response.data.models;
      setModels(availableModels);
      
      if (availableModels.length > 0) {
        setSelectedModel(availableModels[0].id);
      }
      setLoading(false);
    } catch (err) {
      console.error('Failed to load models:', err);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="app">
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100vh',
          color: '#fff'
        }}>
          <h2>Loading AI...</h2>
        </div>
      </div>
    );
  }

  if (models.length === 0) {
    return (
      <div className="app">
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100vh',
          color: '#fff',
          flexDirection: 'column',
          gap: '1rem'
        }}>
          <h2>⚠️ No AI Models Found</h2>
          <p>Please train a model first.</p>
          <div style={{ 
            background: 'rgba(147, 51, 234, 0.2)', 
            padding: '1rem', 
            borderRadius: '0.5rem',
            maxWidth: '500px'
          }}>
            <p style={{ fontSize: '0.9rem', marginBottom: '0.5rem' }}>Run this command:</p>
            <code style={{ 
              background: 'rgba(0,0,0,0.3)', 
              padding: '0.5rem', 
              display: 'block',
              borderRadius: '0.25rem'
            }}>
              cd backend && python train_standalone.py
            </code>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <nav className="navbar">
        <div className="nav-container">
          <div className="nav-brand">
            <span className="brand-text">🧠 Continuously Learning AI</span>
          </div>
        </div>
      </nav>

      <main className="main-content">
        {selectedModel && <LearningAI modelId={selectedModel} />}
      </main>
    </div>
  );
}

export default App;