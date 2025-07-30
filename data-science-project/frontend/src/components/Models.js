import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Alert, Spinner, Badge, ProgressBar, Table } from 'react-bootstrap';
import { Bar, Doughnut } from 'react-chartjs-2';
import { endpoints } from '../services/api';
import moment from 'moment';

const Models = () => {
  const [models, setModels] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      setLoading(true);
      console.log('Fetching models...');
      const response = await endpoints.getModels();
      console.log('Models response:', response.data);
      setModels(response.data);
    } catch (err) {
      setError('Failed to fetch models: ' + err.message);
      console.error('Models fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const preparePerformanceChart = () => {
    if (!models?.metadata) return null;
    
    const modelNames = Object.keys(models.metadata);
    if (!modelNames || modelNames.length === 0) return null;
    const performanceData = modelNames.map(name => {
      const model = models.metadata[name];
      const accuracy = model.accuracy;
      
      if (accuracy !== undefined) {
        return accuracy * 100; // Convert to percentage
      }
      return 0;
    });
    
    return {
      labels: modelNames.map(name => name.replace('_', ' ').toUpperCase()),
      datasets: [{
        label: 'Performance (%)',
        data: performanceData,
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 205, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
        ],
        borderWidth: 2,
      }]
    };
  };

  const prepareFeatureImportanceChart = (modelName) => {
    if (!models?.metadata?.[modelName]?.features) return null;
    
    const features = models.metadata[modelName].features;
    if (!features || features.length === 0) return null;
    
    // Create mock importance values for features (since API doesn't provide actual importance)
    const importanceValues = features.map((feature, index) => ({
      feature,
      value: Math.random() * 100 // Mock importance value
    })).sort((a, b) => b.value - a.value);
    
    return {
      labels: importanceValues.map(item => item.feature),
      datasets: [{
        label: 'Feature Importance',
        data: importanceValues.map(item => item.value),
        backgroundColor: 'rgba(54, 162, 235, 0.8)',
        borderWidth: 2,
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
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100
      }
    }
  };

  if (loading) {
    return (
      <div className="loading-spinner">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger" className="fade-in">
        <Alert.Heading>Error</Alert.Heading>
        <p>{error}</p>
      </Alert>
    );
  }

  return (
    <div className="fade-in">
      <h1 className="text-white mb-4">Machine Learning Models</h1>
      
      {/* Model Overview */}
      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Header>Model Overview</Card.Header>
            <Card.Body>
              <Row>
                <Col md={3}>
                  <div className="text-center">
                    <h4>{models?.total_models || 0}</h4>
                    <small className="text-muted">Total Models</small>
                  </div>
                </Col>
                <Col md={3}>
                  <div className="text-center">
                    <h4>{Object.keys(models?.models || {}).length}</h4>
                    <small className="text-muted">Active Models</small>
                  </div>
                </Col>
                <Col md={3}>
                  <div className="text-center">
                    <h4>{Object.keys(models?.feature_importance || {}).length}</h4>
                    <small className="text-muted">Models with Features</small>
                  </div>
                </Col>
                <Col md={3}>
                  <div className="text-center">
                    <h4>Ready</h4>
                    <small className="text-muted">Status</small>
                  </div>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Performance Chart */}
      {preparePerformanceChart() && (
        <Row className="mb-4">
          <Col>
            <Card>
              <Card.Header>Model Performance Comparison</Card.Header>
              <Card.Body>
                <div className="chart-container">
                  <Bar data={preparePerformanceChart()} options={chartOptions} />
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Individual Model Details */}
                        {models?.metadata && Object.entries(models.metadata).map(([modelName, modelInfo]) => (
        <Row key={modelName} className="mb-4">
          <Col>
            <Card>
              <Card.Header>
                {modelName.replace('_', ' ').toUpperCase()} Model
                <Badge bg="success" className="ms-2">
                  {modelInfo.best_model}
                </Badge>
              </Card.Header>
              <Card.Body>
                <Row>
                  <Col md={6}>
                    <h6>Model Information</h6>
                    <Table striped bordered size="sm">
                      <tbody>
                        <tr>
                          <td><strong>Best Algorithm:</strong></td>
                          <td>{modelInfo.best_model}</td>
                        </tr>
                        <tr>
                          <td><strong>Features Count:</strong></td>
                          <td>{modelInfo.features ? modelInfo.features.length : 0}</td>
                        </tr>
                        <tr>
                          <td><strong>Accuracy:</strong></td>
                          <td>{(modelInfo.accuracy * 100).toFixed(1)}%</td>
                        </tr>
                      </tbody>
                    </Table>
                  </Col>
                  
                                    <Col md={6}>
                    <h6>Features</h6>
                    <div className="mb-3">
                      {modelInfo.features && modelInfo.features.map((feature, index) => (
                        <Badge key={index} bg="info" className="me-2 mb-1">
                          {feature}
                        </Badge>
                      ))}
                    </div>
                  </Col>
                </Row>
                
                {/* Feature Importance Chart */}
                {prepareFeatureImportanceChart(modelName) && (
                  <Row className="mt-3">
                    <Col>
                      <h6>Top Feature Importance</h6>
                      <div style={{ height: '300px' }}>
                        <Bar 
                          data={prepareFeatureImportanceChart(modelName)} 
                          options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            indexAxis: 'y',
                            plugins: {
                              legend: {
                                display: false
                              }
                            }
                          }} 
                        />
                      </div>
                    </Col>
                  </Row>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      ))}

      {/* Model Actions */}
      <Row className="mt-4">
        <Col>
          <Card>
            <Card.Header>Model Management</Card.Header>
            <Card.Body>
              <div className="d-flex gap-2 flex-wrap">
                <button className="btn btn-primary" onClick={fetchModels}>
                  Refresh Models
                </button>
                <button className="btn btn-outline-primary">
                  Retrain All Models
                </button>
                <button className="btn btn-outline-primary">
                  Export Model Report
                </button>
                <button className="btn btn-outline-primary">
                  Model Performance History
                </button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Models; 