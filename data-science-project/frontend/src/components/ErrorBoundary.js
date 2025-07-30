import React from 'react';
import { Alert, Button } from 'react-bootstrap';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // You can also log the error to an error reporting service
    console.error('Error caught by boundary:', error, errorInfo);
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return (
        <div className="p-4">
          <Alert variant="danger">
            <Alert.Heading>Something went wrong!</Alert.Heading>
            <p>
              This component encountered an error. Please check the console for more details.
            </p>
            <hr />
            <div className="d-flex justify-content-between">
              <Button 
                variant="outline-danger" 
                onClick={() => window.location.reload()}
              >
                Reload Page
              </Button>
              <Button 
                variant="outline-secondary" 
                onClick={() => this.setState({ hasError: false, error: null, errorInfo: null })}
              >
                Try Again
              </Button>
            </div>
            {this.state.error && (
              <details className="mt-3">
                <summary>Error Details</summary>
                <pre className="mt-2 p-2 bg-light rounded">
                  {this.state.error.toString()}
                </pre>
                {this.state.errorInfo && (
                  <pre className="mt-2 p-2 bg-light rounded">
                    {this.state.errorInfo.componentStack}
                  </pre>
                )}
              </details>
            )}
          </Alert>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 