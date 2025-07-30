import React, { useState, useEffect } from 'react';
import { Card, Alert, Button, Spinner } from 'react-bootstrap';
import { endpoints } from '../services/api';

const DebugInfo = () => {
  const [apiStatus, setApiStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const testApiConnection = async () => {
    setLoading(true);
    try {
      console.log('Testing API connection...');
      const response = await endpoints.health();
      console.log('API health response:', response.data);
      setApiStatus({
        status: 'success',
        data: response.data,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('API connection failed:', error);
      setApiStatus({
        status: 'error',
        error: error.message,
        response: error.response?.data,
        timestamp: new Date().toISOString()
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    testApiConnection();
  }, []);

  const envInfo = {
    NODE_ENV: process.env.NODE_ENV,
    REACT_APP_API_URL: process.env.REACT_APP_API_URL,
    API_BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000'
  };

  return (
    <div className="p-4">
      <h2>Debug Information</h2>
      
      <Card className="mb-4">
        <Card.Header>Environment Variables</Card.Header>
        <Card.Body>
          <pre className="bg-light p-3 rounded">
            {JSON.stringify(envInfo, null, 2)}
          </pre>
        </Card.Body>
      </Card>

      <Card className="mb-4">
        <Card.Header>API Connection Test</Card.Header>
        <Card.Body>
          <Button 
            onClick={testApiConnection} 
            disabled={loading}
            className="mb-3"
          >
            {loading ? (
              <>
                <Spinner size="sm" className="me-2" />
                Testing...
              </>
            ) : (
              'Test API Connection'
            )}
          </Button>

          {apiStatus && (
            <div>
              {apiStatus.status === 'success' ? (
                <Alert variant="success">
                  <Alert.Heading>✅ API Connection Successful</Alert.Heading>
                  <p><strong>Timestamp:</strong> {apiStatus.timestamp}</p>
                  <pre className="bg-light p-2 rounded">
                    {JSON.stringify(apiStatus.data, null, 2)}
                  </pre>
                </Alert>
              ) : (
                <Alert variant="danger">
                  <Alert.Heading>❌ API Connection Failed</Alert.Heading>
                  <p><strong>Error:</strong> {apiStatus.error}</p>
                  <p><strong>Timestamp:</strong> {apiStatus.timestamp}</p>
                  {apiStatus.response && (
                    <pre className="bg-light p-2 rounded">
                      {JSON.stringify(apiStatus.response, null, 2)}
                    </pre>
                  )}
                </Alert>
              )}
            </div>
          )}
        </Card.Body>
      </Card>

      <Card>
        <Card.Header>Browser Information</Card.Header>
        <Card.Body>
          <pre className="bg-light p-3 rounded">
            {JSON.stringify({
              userAgent: navigator.userAgent,
              platform: navigator.platform,
              language: navigator.language,
              cookieEnabled: navigator.cookieEnabled,
              onLine: navigator.onLine,
              url: window.location.href,
              origin: window.location.origin
            }, null, 2)}
          </pre>
        </Card.Body>
      </Card>
    </div>
  );
};

export default DebugInfo; 