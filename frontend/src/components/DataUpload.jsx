import React, { useState } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export default function DataUpload({ onFileUploaded }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
      setUploadResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_URL}/upload-data`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setUploadResult(response.data);
      if (onFileUploaded) {
        onFileUploaded(response.data.file_id);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div className="card">
        <h2 className="card-title">Upload Training Data</h2>

        <div className="form-group">
          <label className="form-label">Select JSON, JSONL, or CSV file</label>
          <input
            type="file"
            accept=".json,.jsonl,.csv"
            onChange={handleFileChange}
            className="form-input"
          />
          {file && (
            <p style={{ marginTop: '0.5rem', color: '#ccc', fontSize: '0.9rem' }}>
              Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
            </p>
          )}
        </div>

        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="btn btn-primary"
          style={{ width: '100%' }}
        >
          {uploading ? 'Uploading...' : 'Upload Data'}
        </button>

        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        {uploadResult && (
          <div className="alert alert-success">
            <p style={{ fontWeight: 'bold' }}>✅ Upload Successful!</p>
            <p style={{ fontSize: '0.9rem', marginTop: '0.25rem' }}>
              File: {uploadResult.filename}
            </p>
            <p style={{ fontSize: '0.9rem' }}>
              Rows: {uploadResult.rows}
            </p>
          </div>
        )}

        <div className="alert alert-info" style={{ marginTop: '2rem' }}>
          <h3 style={{ marginBottom: '0.5rem' }}>Data Format Example:</h3>
          <pre style={{ fontSize: '0.85rem', overflow: 'auto' }}>
{`[
  {
    "instruction": "Your question or task",
    "input": "Optional context",
    "output": "Expected response"
  }
]`}
          </pre>
        </div>
      </div>
    </div>
  );
}