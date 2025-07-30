import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Form, Button, Alert, Spinner, Badge, Table } from 'react-bootstrap';
import { Line, Bar } from 'react-chartjs-2';
import { endpoints } from '../services/api';

const Predictions = () => {
  const [models, setModels] = useState(null);
  const [selectedModel, setSelectedModel] = useState('');
  const [features, setFeatures] = useState({});
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [predictionHistory, setPredictionHistory] = useState([]);

  useEffect(() => {
    fetchModels();
  }, []);

  useEffect(() => {
    if (selectedModel && models?.models?.[selectedModel]) {
      initializeFeatures();
    }
  }, [selectedModel, models]);

  const fetchModels = async () => {
    try {
      console.log('Fetching models for predictions...');
      const response = await endpoints.getModels();
      console.log('Models response for predictions:', response.data);
      setModels(response.data);
    } catch (err) {
      setError('Failed to fetch models: ' + err.message);
      console.error('Models fetch error:', err);
    }
  };

  const initializeFeatures = () => {
    const modelInfo = models.metadata[selectedModel];
    const featureList = modelInfo.features || [];
    
    const initialFeatures = {};
    featureList.forEach(feature => {
      initialFeatures[feature] = '';
    });
    
    setFeatures(initialFeatures);
  };

  const handleFeatureChange = (feature, value) => {
    setFeatures(prev => ({
      ...prev,
      [feature]: value
    }));
  };

  const makePrediction = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Validate features
      const missingFeatures = Object.entries(features).filter(([key, value]) => !value);
      if (missingFeatures.length > 0) {
        setError(`Please fill in all required features: ${missingFeatures && Array.isArray(missingFeatures) ? missingFeatures.map(([key]) => key).join(', ') : 'unknown'}`);
        return;
      }

      const response = await endpoints.makePrediction(selectedModel, features);
      
      setPrediction(response.data);
      
      // Add to history
      setPredictionHistory(prev => [{
        ...response.data,
        timestamp: new Date().toISOString(),
        features: { ...features }
      }, ...prev.slice(0, 9)]); // Keep last 10 predictions
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to make prediction');
      console.error('Prediction error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getModelDescription = (modelName) => {
    const descriptions = {
      'covid_forecast': 'Predicts COVID-19 cases for the next day based on historical data',
      'stock_prediction': 'Predicts stock closing price for the next trading day',
      'weather_classification': 'Classifies weather conditions based on temperature and other factors'
    };
    return descriptions[modelName] || 'Make predictions using this trained model';
  };

  const getFeatureDescription = (feature) => {
    const descriptions = {
      // COVID features
      'cases': 'Total number of COVID-19 cases',
      'deaths': 'Total number of COVID-19 deaths',
      'recovered': 'Total number of recovered cases',
      'new_cases': 'New cases reported today',
      'new_deaths': 'New deaths reported today',
      'case_fatality_rate': 'Fatality rate percentage',
      'recovery_rate': 'Recovery rate percentage',
      
      // Stock features
      'open': 'Opening stock price',
      'high': 'Highest stock price of the day',
      'low': 'Lowest stock price of the day',
      'volume': 'Trading volume',
      'daily_return': 'Daily return percentage',
      'volatility': 'Price volatility measure',
      'rsi': 'Relative Strength Index',
      'macd': 'MACD indicator value',
      
      // Weather features
      'temperature': 'Temperature in Celsius',
      'humidity': 'Humidity percentage',
      'pressure': 'Atmospheric pressure',
      'wind_speed': 'Wind speed in m/s',
      'hour': 'Hour of the day (0-23)',
      'month': 'Month of the year (1-12)'
    };
    return descriptions[feature] || feature;
  };

  const getFeatureType = (feature) => {
    const numericFeatures = ['cases', 'deaths', 'recovered', 'new_cases', 'new_deaths', 
                           'case_fatality_rate', 'recovery_rate', 'open', 'high', 'low', 
                           'volume', 'daily_return', 'volatility', 'rsi', 'macd', 
                           'temperature', 'humidity', 'pressure', 'wind_speed'];
    
    return numericFeatures.includes(feature) ? 'number' : 'text';
  };

  const prepareHistoryChart = () => {
    if (!predictionHistory || !Array.isArray(predictionHistory) || predictionHistory.length < 2) return null;
    
    const labels = predictionHistory.map((_, index) => `Prediction ${predictionHistory.length - index}`);
    const data = predictionHistory.map(pred => {
      const value = Array.isArray(pred.prediction) ? pred.prediction[0] : pred.prediction;
      return typeof value === 'number' ? value : 0;
    }).reverse();
    
    return {
      labels,
      datasets: [{
        label: 'Prediction Values',
        data: data,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        tension: 0.1
      }]
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Prediction History'
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  };

  return (
    <div className="fade-in">
      <h1 className="text-white mb-4">Make Predictions</h1>
      
      {/* Model Selection */}
      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Header>Select Model</Card.Header>
            <Card.Body>
              <Form.Select 
                value={selectedModel} 
                onChange={(e) => setSelectedModel(e.target.value)}
              >
                <option value="">Choose a model...</option>
                {models?.metadata && Object.keys(models.metadata).map((modelName) => (
                  <option key={modelName} value={modelName}>
                    {modelName.replace('_', ' ').toUpperCase()} - {models.metadata[modelName].best_model}
                  </option>
                ))}
              </Form.Select>
              {selectedModel && (
                <div className="mt-2">
                  <small className="text-muted">
                    {getModelDescription(selectedModel)}
                  </small>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" className="mb-4">
          <Alert.Heading>Error</Alert.Heading>
          <p>{error}</p>
        </Alert>
      )}

      {selectedModel && (
        <>
          {/* Feature Input Form */}
          <Row className="mb-4">
            <Col>
              <Card>
                <Card.Header>
                  Input Features
                  <Badge bg="info" className="ms-2">
                    {Object.keys(features).length} features required
                  </Badge>
                </Card.Header>
                <Card.Body>
                  <Row>
                    {features && Object.entries(features).map(([feature, value]) => (
                      <Col md={6} lg={4} key={feature} className="mb-3">
                        <Form.Group>
                          <Form.Label>
                            {feature.replace(/_/g, ' ').toUpperCase()}
                            <small className="text-muted d-block">
                              {getFeatureDescription(feature)}
                            </small>
                          </Form.Label>
                          <Form.Control
                            type={getFeatureType(feature)}
                            value={value}
                            onChange={(e) => handleFeatureChange(feature, e.target.value)}
                            placeholder={`Enter ${feature.replace(/_/g, ' ')}`}
                          />
                        </Form.Group>
                      </Col>
                    ))}
                  </Row>
                  <div className="mt-3">
                    <Button 
                      variant="primary" 
                      onClick={makePrediction}
                      disabled={loading || Object.values(features).some(v => !v)}
                    >
                      {loading ? <Spinner size="sm" /> : 'Make Prediction'}
                    </Button>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {/* Prediction Result */}
          {prediction && (
            <Row className="mb-4">
              <Col>
                <Card>
                  <Card.Header>
                    Prediction Result
                    <Badge bg="success" className="ms-2">
                      {prediction.model_type}
                    </Badge>
                  </Card.Header>
                  <Card.Body>
                    <Row>
                      <Col md={6}>
                        <h5>Prediction Value</h5>
                        <div className="text-center">
                          <h2 className="text-primary">
                            {Array.isArray(prediction.prediction) 
                              ? prediction.prediction[0] 
                              : prediction.prediction}
                          </h2>
                          <small className="text-muted">
                            {selectedModel === 'covid_forecast' && 'Predicted Cases'}
                            {selectedModel === 'stock_prediction' && 'Predicted Price ($)'}
                            {selectedModel === 'weather_classification' && 'Weather Category'}
                          </small>
                        </div>
                      </Col>
                      <Col md={6}>
                        <h5>Model Information</h5>
                        <Table striped bordered size="sm">
                          <tbody>
                            <tr>
                              <td><strong>Model:</strong></td>
                              <td>{prediction.model_name}</td>
                            </tr>
                            <tr>
                              <td><strong>Algorithm:</strong></td>
                              <td>{prediction.model_type}</td>
                            </tr>
                            <tr>
                              <td><strong>Features Used:</strong></td>
                              <td>{prediction.features_used.length}</td>
                            </tr>
                            <tr>
                              <td><strong>Timestamp:</strong></td>
                              <td>{new Date(prediction.timestamp).toLocaleString()}</td>
                            </tr>
                          </tbody>
                        </Table>
                      </Col>
                    </Row>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          )}

          {/* Prediction History */}
          {predictionHistory.length > 0 && (
            <Row className="mb-4">
              <Col>
                <Card>
                  <Card.Header>Prediction History</Card.Header>
                  <Card.Body>
                    {prepareHistoryChart() && (
                      <div className="chart-container mb-4">
                        <Line data={prepareHistoryChart()} options={chartOptions} />
                      </div>
                    )}
                    
                    <Table striped bordered hover>
                      <thead>
                        <tr>
                          <th>Timestamp</th>
                          <th>Model</th>
                          <th>Prediction</th>
                          <th>Algorithm</th>
                        </tr>
                      </thead>
                      <tbody>
                        {predictionHistory.map((pred, index) => (
                          <tr key={index}>
                            <td>{new Date(pred.timestamp).toLocaleString()}</td>
                            <td>{pred.model_name}</td>
                            <td>
                              {Array.isArray(pred.prediction) 
                                ? pred.prediction[0] 
                                : pred.prediction}
                            </td>
                            <td>{pred.model_type}</td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          )}
        </>
      )}

      {/* Quick Actions */}
      <Row className="mt-4">
        <Col>
          <Card>
            <Card.Header>Quick Actions</Card.Header>
            <Card.Body>
              <div className="d-flex gap-2 flex-wrap">
                <button className="btn btn-primary" onClick={fetchModels}>
                  Refresh Models
                </button>
                <button className="btn btn-outline-primary">
                  Clear History
                </button>
                <button className="btn btn-outline-primary">
                  Export Predictions
                </button>
                <button className="btn btn-outline-primary">
                  Batch Prediction
                </button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Predictions; 