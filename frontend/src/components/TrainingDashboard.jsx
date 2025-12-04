import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export default function TrainingDashboard({ fileId, onTrainingStarted }) {
  const [baseModels, setBaseModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('unsloth/llama-3-8b-bnb-4bit');
  const [modelName, setModelName] = useState('');
  const [maxSteps, setMaxSteps] = useState(60);
  const [learningRate, setLearningRate] = useState(0.0002);
  const [training, setTraining] = useState(false);
  const [trainingId, setTrainingId] = useState(null);
  const [trainingStatus, setTrainingStatus] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchBaseModels();
  }, []);

  useEffect(() => {
    let interval;
    if (trainingId) {
      interval = setInterval(() => {
        fetchTrainingStatus(trainingId);
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [trainingId]);

  const fetchBaseModels = async () => {
    try {
      const response = await axios.get(`${API_URL}/base-models`);
      setBaseModels(response.data.models);
    } catch (err) {
      console.error('Failed to fetch base models:', err);
    }
  };

  const fetchTrainingStatus = async (id) => {
    try {
      const response = await axios.get(`${API_URL}/training-status/${id}`);
      setTrainingStatus(response.data);
      
      if (response.data.status === 'completed' || response.data.status === 'failed') {
        setTraining(false);
      }
    } catch (err) {
      console.error('Failed to fetch training status:', err);
    }
  };

  const startTraining = async () => {
    if (!fileId) {
      setError('Please upload training data first');
      return;
    }

    if (!modelName.trim()) {
      setError('Please enter a model name');
      return;
    }

    setTraining(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/start-training`, {
        file_id: fileId,
        model_name: selectedModel,
        max_steps: maxSteps,
        learning_rate: learningRate,
        batch_size: 1,
        output_name: modelName.trim()
      });

      setTrainingId(response.data.training_id);
      if (onTrainingStarted) {
        onTrainingStarted(response.data.training_id);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Training failed to start');
      setTraining(false);
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div className="card">
        <h2 className="card-title">Train Your Model</h2>

        {!training && !trainingStatus && (
          <div>
            <div className="form-group">
              <label className="form-label">Model Name</label>
              <input
                type="text"
                value={modelName}
                onChange={(e) => setModelName(e.target.value)}
                placeholder="my-awesome-model"
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Base Model</label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="form-input"
              >
                {baseModels.map((model) => (
                  <option key={model.id} value={model.id}>
                    {model.name} - {model.size}
                    {model.recommended && ' (Recommended)'}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-2">
              <div className="form-group">
                <label className="form-label">Max Steps</label>
                <input
                  type="number"
                  value={maxSteps}
                  onChange={(e) => setMaxSteps(parseInt(e.target.value))}
                  className="form-input"
                />
              </div>
              <div className="form-group">
                <label className="form-label">Learning Rate</label>
                <input
                  type="number"
                  step="0.0001"
                  value={learningRate}
                  onChange={(e) => setLearningRate(parseFloat(e.target.value))}
                  className="form-input"
                />
              </div>
            </div>

            <button
              onClick={startTraining}
              disabled={!fileId || training}
              className="btn btn-primary"
              style={{ width: '100%' }}
            >
              🚀 Start Training
            </button>

            {error && (
              <div className="alert alert-error">{error}</div>
            )}
          </div>
        )}

        {trainingStatus && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <span style={{ color: '#ccc' }}>Status:</span>
              <span style={{
                fontWeight: 'bold',
                color: trainingStatus.status === 'completed' ? '#86efac' :
                       trainingStatus.status === 'failed' ? '#fca5a5' : '#fcd34d'
              }}>
                {trainingStatus.status.toUpperCase()}
              </span>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: '#ccc', marginBottom: '0.5rem' }}>
                <span>Progress</span>
                <span>{trainingStatus.progress}%</span>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${trainingStatus.progress}%` }}
                ></div>
              </div>
            </div>

            <div className="grid grid-2" style={{ fontSize: '0.9rem', marginTop: '1rem' }}>
              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.75rem', borderRadius: '0.5rem' }}>
                <span style={{ color: '#ccc' }}>Current Step: </span>
                <span style={{ fontWeight: 'bold' }}>
                  {trainingStatus.current_step} / {trainingStatus.total_steps}
                </span>
              </div>
              {trainingStatus.loss && (
                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.75rem', borderRadius: '0.5rem' }}>
                  <span style={{ color: '#ccc' }}>Loss: </span>
                  <span style={{ fontWeight: 'bold' }}>
                    {trainingStatus.loss.toFixed(4)}
                  </span>
                </div>
              )}
            </div>

            {trainingStatus.status === 'completed' && (
              <div className="alert alert-success" style={{ marginTop: '1rem' }}>
                ✅ Training completed successfully!
              </div>
            )}

            {trainingStatus.status === 'failed' && (
              <div className="alert alert-error" style={{ marginTop: '1rem' }}>
                ❌ Training failed: {trainingStatus.error}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}