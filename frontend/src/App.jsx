import React, { useState } from 'react';
import DataUpload from './components/DataUpload';
import TrainingDashboard from './components/TrainingDashboard';
import ChatInterface from './components/ChatInterface';
import ModelManager from './components/ModelManager';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('upload');
  const [uploadedFileId, setUploadedFileId] = useState(null);
  const [trainingId, setTrainingId] = useState(null);
  const [selectedModel, setSelectedModel] = useState(null);

  const handleFileUploaded = (fileId) => {
    setUploadedFileId(fileId);
    setCurrentView('train');
  };

  const handleTrainingStarted = (id) => {
    setTrainingId(id);
  };

  const handleModelSelected = (modelId) => {
    setSelectedModel(modelId);
    setCurrentView('chat');
  };

  return (
    <div className="app">
      <nav className="navbar">
        <div className="nav-container">
          <div className="nav-brand">
            <span className="brand-text">🦥 Unsloth AI</span>
          </div>
          <div className="nav-buttons">
            <button
              onClick={() => setCurrentView('upload')}
              className={currentView === 'upload' ? 'nav-btn active' : 'nav-btn'}
            >
              Upload Data
            </button>
            <button
              onClick={() => setCurrentView('train')}
              className={currentView === 'train' ? 'nav-btn active' : 'nav-btn'}
            >
              Train Model
            </button>
            <button
              onClick={() => setCurrentView('models')}
              className={currentView === 'models' ? 'nav-btn active' : 'nav-btn'}
            >
              My Models
            </button>
            <button
              onClick={() => setCurrentView('chat')}
              className={currentView === 'chat' ? 'nav-btn active' : 'nav-btn'}
              disabled={!selectedModel}
            >
              Chat
            </button>
          </div>
        </div>
      </nav>

      <main className="main-content">
        {currentView === 'upload' && (
          <DataUpload onFileUploaded={handleFileUploaded} />
        )}
        {currentView === 'train' && (
          <TrainingDashboard
            fileId={uploadedFileId}
            onTrainingStarted={handleTrainingStarted}
          />
        )}
        {currentView === 'models' && (
          <ModelManager onModelSelected={handleModelSelected} />
        )}
        {currentView === 'chat' && selectedModel && (
          <ChatInterface modelId={selectedModel} />
        )}
      </main>
    </div>
  );
}

export default App;