import React, { useState, useEffect } from 'react';
import { Card, Button, Alert, Spinner } from 'react-bootstrap';
import { endpoints } from '../services/api';

const ApiTest = () => {
  const [testResults, setTestResults] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const testEndpoints = async () => {
    setLoading(true);
    setError(null);
    const results = {};

    try {
      // Test health endpoint
      console.log('Testing health endpoint...');
      const healthRes = await endpoints.health();
      results.health = {
        status: 'success',
        data: healthRes.data,
        url: healthRes.config.url
      };
      console.log('Health test result:', healthRes.data);

      // Test analytics endpoint
      console.log('Testing analytics endpoint...');
      const analyticsRes = await endpoints.getAnalytics();
      results.analytics = {
        status: 'success',
        data: analyticsRes.data,
        url: analyticsRes.config.url
      };
      console.log('Analytics test result:', analyticsRes.data);

      // Test insights endpoint
      console.log('Testing insights endpoint...');
      const insightsRes = await endpoints.getInsights();
      results.insights = {
        status: 'success',
        data: insightsRes.data,
        url: insightsRes.config.url
      };
      console.log('Insights test result:', insightsRes.data);

      // Test data sources endpoint
      console.log('Testing data sources endpoint...');
      const sourcesRes = await endpoints.getDataSources();
      results.sources = {
        status: 'success',
        data: sourcesRes.data,
        url: sourcesRes.config.url
      };
      console.log('Data sources test result:', sourcesRes.data);

    } catch (err) {
      console.error('API Test Error:', err);
      setError(`API Test Failed: ${err.message}`);
      results.error = {
        status: 'error',
        message: err.message,
        response: err.response?.data,
        status: err.response?.status
      };
    }

    setTestResults(results);
    setLoading(false);
  };

  const getApiBaseUrl = () => {
    return process.env.REACT_APP_API_URL || 'http://localhost:8000';
  };

  return (
    <div className="p-4">
      <h2>API Connection Test</h2>
      
      <Card className="mb-4">
        <Card.Header>Environment Information</Card.Header>
        <Card.Body>
          <p><strong>API Base URL:</strong> {getApiBaseUrl()}</p>
          <p><strong>Environment:</strong> {process.env.NODE_ENV}</p>
          <p><strong>Backend URL:</strong> https://data-science-backend-2024-11b411fad5ba.herokuapp.com</p>
        </Card.Body>
      </Card>

      <Button 
        onClick={testEndpoints} 
        disabled={loading}
        className="mb-4"
      >
        {loading ? (
          <>
            <Spinner animation="border" size="sm" className="me-2" />
            Testing API...
          </>
        ) : (
          'Test All API Endpoints'
        )}
      </Button>

      {error && (
        <Alert variant="danger" className="mb-4">
          <Alert.Heading>Error</Alert.Heading>
          <p>{error}</p>
        </Alert>
      )}

      {Object.keys(testResults).length > 0 && (
        <div>
          <h3>Test Results</h3>
                          {testResults && Object.entries(testResults).map(([endpoint, result]) => (
            <Card key={endpoint} className="mb-3">
              <Card.Header>
                {endpoint.charAt(0).toUpperCase() + endpoint.slice(1)} Endpoint
              </Card.Header>
              <Card.Body>
                {result.status === 'success' ? (
                  <div>
                    <Alert variant="success">✅ Success</Alert>
                    <p><strong>URL:</strong> {result.url}</p>
                    <p><strong>Response:</strong></p>
                    <pre className="bg-light p-2 rounded">
                      {JSON.stringify(result.data, null, 2)}
                    </pre>
                  </div>
                ) : (
                  <div>
                    <Alert variant="danger">❌ Failed</Alert>
                    <p><strong>Error:</strong> {result.message}</p>
                    {result.response && (
                      <p><strong>Response:</strong> {JSON.stringify(result.response)}</p>
                    )}
                  </div>
                )}
              </Card.Body>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default ApiTest; 