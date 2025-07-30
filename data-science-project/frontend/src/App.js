import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container, Navbar, Nav } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Import components
import Dashboard from './components/Dashboard';
import DataExplorer from './components/DataExplorer';
import Analytics from './components/Analytics';
import Models from './components/Models';
import Predictions from './components/Predictions';
import ApiTest from './components/ApiTest';
import DebugInfo from './components/DebugInfo';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar bg="dark" variant="dark" expand="lg" className="mb-4">
          <Container>
            <Navbar.Brand href="/">
              <i className="fas fa-chart-line me-2"></i>
              Data Science Analytics
            </Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
              <Nav className="me-auto">
                              <Nav.Link href="/">Dashboard</Nav.Link>
              <Nav.Link href="/data">Data Explorer</Nav.Link>
              <Nav.Link href="/analytics">Analytics</Nav.Link>
              <Nav.Link href="/models">Models</Nav.Link>
                              <Nav.Link href="/predictions">Predictions</Nav.Link>
                <Nav.Link href="/test">API Test</Nav.Link>
                <Nav.Link href="/debug">Debug</Nav.Link>
              </Nav>
            </Navbar.Collapse>
          </Container>
        </Navbar>

        <Container fluid>
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/data" element={<DataExplorer />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/models" element={<Models />} />
              <Route path="/predictions" element={<Predictions />} />
              <Route path="/test" element={<ApiTest />} />
              <Route path="/debug" element={<DebugInfo />} />
            </Routes>
          </ErrorBoundary>
        </Container>
      </div>
    </Router>
  );
}

export default App; 