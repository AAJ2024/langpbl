import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export default function ModelManager({ onModelSelected }) {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleting, setDeleting] = useState(null);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/models`);
      setModels(response.data.models);
      setError(null);
    } catch (err) {
      setError('Failed to load models');
    } finally {
      setLoading(false);
    }
  };

  const deleteModel = async (modelId) => {
    if (!window.confirm(`Are you sure you want to delete "${modelId}"?`)) {
      return;
    }

    setDeleting(modelId);
    try {
      await axios.delete(`${API_URL}/models/${modelId}`);
      await fetchModels();
    } catch (err) {
      alert('Failed to delete model');
    } finally {
      setDeleting(null);
    }
  };

  if (loading) {
    return (
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        <div className="card">
          <p style={{ textAlign: 'center', color: '#ccc' }}>Loading models...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        <div className="card">
          <div className="alert alert-error">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 className="card-title" style={{ marginBottom: 0 }}>My Models</h2>
          <button onClick={fetchModels} className="btn btn-secondary">
            🔄 Refresh
          </button>
        </div>

        {models.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: '#ccc' }}>
            <p style={{ fontSize: '3rem', marginBottom: '1rem' }}>📦</p>
            <p>No models yet. Train your first model!</p>
          </div>
        ) : (
          <div className="grid grid-2">
            {models.map((model) => (
              <div
                key={model.id}
                style={{
                  background: 'rgba(0,0,0,0.3)',
                  padding: '1.5rem',
                  borderRadius: '0.75rem',
                  border: '1px solid rgba(147, 51, 234, 0.3)'
                }}
              >
                <h3 style={{ 
                  fontSize: '1.25rem', 
                  marginBottom: '1rem',
                  color: '#fff',
                  wordBreak: 'break-word'
                }}>
                  🤖 {model.name}
                </h3>
                
                <div style={{ fontSize: '0.9rem', color: '#ccc', marginBottom: '1rem' }}>
                  <p>📅 Created: {new Date(model.created_at).toLocaleDateString()}</p>
                  <p>💾 Size: {model.size_mb.toFixed(2)} MB</p>
                </div>

                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    onClick={() => onModelSelected(model.id)}
                    className="btn btn-primary"
                    style={{ flex: 1 }}
                  >
                    💬 Chat
                  </button>
                  <button
                    onClick={() => deleteModel(model.id)}
                    disabled={deleting === model.id}
                    className="btn btn-danger"
                  >
                    {deleting === model.id ? '...' : '🗑️'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}