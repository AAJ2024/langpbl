import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export default function FinancialAdvisor({ modelId }) {
  const [formData, setFormData] = useState({
    age: '',
    income: '',
    debt: '',
    savings: '',
    city: '',
    state: '',
    goals: ''
  });
  const [advice, setAdvice] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [availableLocations, setAvailableLocations] = useState([]);

  useEffect(() => {
    fetchAvailableLocations();
  }, []);

  const fetchAvailableLocations = async () => {
    try {
      const response = await axios.get(`${API_URL}/available-locations`);
      setAvailableLocations(response.data.locations);
    } catch (err) {
      console.error('Failed to fetch locations:', err);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setAdvice(null);

    try {
      const response = await axios.post(`${API_URL}/financial-advice`, {
        ...formData,
        age: parseInt(formData.age),
        income: parseFloat(formData.income),
        debt: parseFloat(formData.debt),
        savings: parseFloat(formData.savings),
        model_id: modelId,
        session_id: `session_${Date.now()}`
      });

      setAdvice(response.data.advice);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to get financial advice');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <div className="card">
        <h2 className="card-title">💰 Location-Based Financial Advisor</h2>
        <p style={{ color: '#ccc', marginBottom: '2rem' }}>
          Get personalized financial advice with local resources for your area
        </p>

        {!advice ? (
          <form onSubmit={handleSubmit}>
            <div className="grid grid-2">
              <div className="form-group">
                <label className="form-label">Age</label>
                <input
                  type="number"
                  name="age"
                  value={formData.age}
                  onChange={handleChange}
                  placeholder="25"
                  className="form-input"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Annual Income ($)</label>
                <input
                  type="number"
                  name="income"
                  value={formData.income}
                  onChange={handleChange}
                  placeholder="40000"
                  className="form-input"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Total Debt ($)</label>
                <input
                  type="number"
                  name="debt"
                  value={formData.debt}
                  onChange={handleChange}
                  placeholder="100000"
                  className="form-input"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Current Savings ($)</label>
                <input
                  type="number"
                  name="savings"
                  value={formData.savings}
                  onChange={handleChange}
                  placeholder="5000"
                  className="form-input"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">City</label>
                <input
                  type="text"
                  name="city"
                  value={formData.city}
                  onChange={handleChange}
                  placeholder="Athens"
                  className="form-input"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">State</label>
                <input
                  type="text"
                  name="state"
                  value={formData.state}
                  onChange={handleChange}
                  placeholder="GA"
                  className="form-input"
                  required
                  maxLength={2}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Financial Goals</label>
              <textarea
                name="goals"
                value={formData.goals}
                onChange={handleChange}
                placeholder="Pay off student loans, build emergency fund, start investing..."
                className="form-input"
                rows="4"
                required
              />
            </div>

            {availableLocations.length > 0 && (
              <div className="alert alert-info">
                📍 Supported locations: {availableLocations.join(', ')}
              </div>
            )}

            {error && (
              <div className="alert alert-error">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{ width: '100%', marginTop: '1rem' }}
            >
              {loading ? '🔄 Generating Advice...' : '🚀 Get Financial Advice'}
            </button>
          </form>
        ) : (
          <div>
            <div style={{
              background: 'rgba(0,0,0,0.2)',
              padding: '1.5rem',
              borderRadius: '0.75rem',
              marginBottom: '1rem',
              maxHeight: '600px',
              overflowY: 'auto'
            }}>
              <div style={{ whiteSpace: 'pre-wrap', color: '#fff', lineHeight: '1.6' }}>
                {advice}
              </div>
            </div>

            <button
              onClick={() => {
                setAdvice(null);
                setFormData({
                  age: '',
                  income: '',
                  debt: '',
                  savings: '',
                  city: '',
                  state: '',
                  goals: ''
                });
              }}
              className="btn btn-secondary"
              style={{ width: '100%' }}
            >
              ← Get New Advice
            </button>
          </div>
        )}
      </div>
    </div>
  );
}