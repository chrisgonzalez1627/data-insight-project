import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Alert, Spinner } from 'react-bootstrap';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { endpoints } from '../services/api';
import moment from 'moment';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const Dashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState({
    etl: false,
    train: false,
    export: false
  });
  const [actionResults, setActionResults] = useState({
    etl: null,
    train: null,
    export: null
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [analyticsRes, insightsRes] = await Promise.all([
        endpoints.getAnalytics(),
        endpoints.getInsights()
      ]);
      
      setAnalytics(analyticsRes.data);
      setInsights(insightsRes.data);
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error('Dashboard data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const runETLPipeline = async () => {
    try {
      setActionLoading(prev => ({ ...prev, etl: true }));
      setActionResults(prev => ({ ...prev, etl: null }));
      
      const response = await endpoints.runETLPipeline();
      setActionResults(prev => ({ ...prev, etl: response.data }));
      
      // Refresh dashboard data after ETL completion
      setTimeout(() => {
        fetchDashboardData();
      }, 1000);
      
    } catch (err) {
      setActionResults(prev => ({ 
        ...prev, 
        etl: { status: 'error', message: err.message } 
      }));
      console.error('ETL pipeline error:', err);
    } finally {
      setActionLoading(prev => ({ ...prev, etl: false }));
    }
  };

  const trainModels = async () => {
    try {
      setActionLoading(prev => ({ ...prev, train: true }));
      setActionResults(prev => ({ ...prev, train: null }));
      
      const response = await endpoints.trainModels();
      setActionResults(prev => ({ ...prev, train: response.data }));
      
      // Refresh dashboard data after training completion
      setTimeout(() => {
        fetchDashboardData();
      }, 1000);
      
    } catch (err) {
      setActionResults(prev => ({ 
        ...prev, 
        train: { status: 'error', message: err.message } 
      }));
      console.error('Model training error:', err);
    } finally {
      setActionLoading(prev => ({ ...prev, train: false }));
    }
  };

  const exportReport = async () => {
    try {
      setActionLoading(prev => ({ ...prev, export: true }));
      setActionResults(prev => ({ ...prev, export: null }));
      
      const response = await endpoints.exportReport();
      setActionResults(prev => ({ ...prev, export: response.data }));
      
    } catch (err) {
      setActionResults(prev => ({ 
        ...prev, 
        export: { status: 'error', message: err.message } 
      }));
      console.error('Report export error:', err);
    } finally {
      setActionLoading(prev => ({ ...prev, export: false }));
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

  // Prepare chart data
  const prepareChartData = (sourceName) => {
    if (!insights?.insights?.[sourceName]?.latest_data) return null;
    
    const data = insights.insights[sourceName].latest_data;
    if (!data || !Array.isArray(data)) return null;
    const labels = data.map((item, index) => `Day ${index + 1}`);
    
    if (sourceName === 'covid') {
      return {
        labels,
        datasets: [
          {
            label: 'Cases',
            data: data.map(item => item.cases || 0),
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            tension: 0.1
          },
          {
            label: 'Deaths',
            data: data.map(item => item.deaths || 0),
            borderColor: 'rgb(54, 162, 235)',
            backgroundColor: 'rgba(54, 162, 235, 0.5)',
            tension: 0.1
          }
        ]
      };
    }
    
    if (sourceName === 'stock') {
      return {
        labels,
        datasets: [
          {
            label: 'Close Price',
            data: data.map(item => item.close || 0),
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.5)',
            tension: 0.1
          }
        ]
      };
    }
    
    if (sourceName === 'weather') {
      return {
        labels,
        datasets: [
          {
            label: 'Temperature (°C)',
            data: data.map(item => item.temperature || 0),
            borderColor: 'rgb(255, 205, 86)',
            backgroundColor: 'rgba(255, 205, 86, 0.5)',
            tension: 0.1
          }
        ]
      };
    }
    
    return null;
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
        text: 'Recent Data Trends'
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  };

  // Calculate statistics
  const totalRecords = analytics?.overall_stats?.total_records || 0;
  const totalSources = analytics?.overall_stats?.total_data_sources || 0;
  const totalModels = analytics?.models?.total_models || 0;
  const dataSize = analytics?.overall_stats?.data_directory_size_mb || 0;

  // Debug logging
  console.log('Dashboard render state:', {
    analytics: analytics ? { 
      overall_stats: analytics.overall_stats,
      data_sources: analytics.data_sources ? Object.keys(analytics.data_sources) : null,
      timestamp: analytics.timestamp 
    } : null,
    insights: insights ? { 
      insights_count: Object.keys(insights.insights || {}).length 
    } : null,
    loading,
    error
  });

  return (
    <div className="fade-in">
      <h1 className="text-white mb-4">Dashboard Overview</h1>
      
      {/* Statistics Cards */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="stats-card">
            <div className="stat-value">{totalRecords.toLocaleString()}</div>
            <div className="stat-label">Total Records</div>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stats-card">
            <div className="stat-value">{totalSources}</div>
            <div className="stat-label">Data Sources</div>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stats-card">
            <div className="stat-value">{totalModels}</div>
            <div className="stat-label">ML Models</div>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stats-card">
            <div className="stat-value">{dataSize.toFixed(1)} MB</div>
            <div className="stat-label">Data Size</div>
          </Card>
        </Col>
      </Row>

      {/* Data Source Overview */}
      <Row className="mb-4">
        <Col md={6}>
          <Card>
            <Card.Header>Data Sources Overview</Card.Header>
            <Card.Body>
              {analytics?.data_sources ? (
                <div className="chart-container">
                  <Doughnut
                    data={{
                      labels: Object.keys(analytics.data_sources),
                      datasets: [
                        {
                          data: analytics.data_sources ? Object.values(analytics.data_sources).map(source => source.records) : [],
                          backgroundColor: [
                            'rgba(255, 99, 132, 0.8)',
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 205, 86, 0.8)',
                            'rgba(75, 192, 192, 0.8)',
                          ],
                          borderWidth: 2,
                        },
                      ],
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'bottom',
                        },
                      },
                    }}
                  />
                </div>
              ) : (
                <p className="text-muted">No data sources available</p>
              )}
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={6}>
          <Card>
            <Card.Header>System Status</Card.Header>
            <Card.Body>
              <div className="mb-3">
                <strong>API Status:</strong>
                <span className="badge badge-success ms-2">Healthy</span>
              </div>
              <div className="mb-3">
                <strong>Models Loaded:</strong>
                <span className="badge badge-success ms-2">{totalModels}</span>
              </div>
              <div className="mb-3">
                <strong>Last Updated:</strong>
                <span className="text-muted ms-2">
                  {analytics?.timestamp ? moment(analytics.timestamp).format('MMMM Do YYYY, h:mm:ss a') : 'N/A'}
                </span>
              </div>
              <div>
                <strong>Data Freshness:</strong>
                <span className="badge badge-warning ms-2">Recent</span>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Data Trends */}
      <Row>
        {['covid', 'stock', 'weather'].map(sourceName => {
          const chartData = prepareChartData(sourceName);
          if (!chartData) return null;
          
          return (
            <Col md={4} key={sourceName}>
              <Card>
                <Card.Header>{sourceName.charAt(0).toUpperCase() + sourceName.slice(1)} Trends</Card.Header>
                <Card.Body>
                  <div className="chart-container">
                    <Line data={chartData} options={chartOptions} />
                  </div>
                </Card.Body>
              </Card>
            </Col>
          );
        })}
      </Row>

      {/* Quick Actions */}
      <Row className="mt-4">
        <Col>
          <Card>
            <Card.Header>Quick Actions</Card.Header>
            <Card.Body>
              <div className="d-flex gap-2 flex-wrap mb-3">
                <button className="btn btn-primary" onClick={fetchDashboardData}>
                  Refresh Data
                </button>
                <button 
                  className="btn btn-outline-primary" 
                  onClick={runETLPipeline}
                  disabled={actionLoading.etl}
                >
                  {actionLoading.etl ? (
                    <>
                      <Spinner animation="border" size="sm" className="me-2" />
                      Running ETL...
                    </>
                  ) : (
                    'Run ETL Pipeline'
                  )}
                </button>
                <button 
                  className="btn btn-outline-primary" 
                  onClick={trainModels}
                  disabled={actionLoading.train}
                >
                  {actionLoading.train ? (
                    <>
                      <Spinner animation="border" size="sm" className="me-2" />
                      Training Models...
                    </>
                  ) : (
                    'Train Models'
                  )}
                </button>
                <button 
                  className="btn btn-outline-primary" 
                  onClick={exportReport}
                  disabled={actionLoading.export}
                >
                  {actionLoading.export ? (
                    <>
                      <Spinner animation="border" size="sm" className="me-2" />
                      Generating Report...
                    </>
                  ) : (
                    'Export Report'
                  )}
                </button>
              </div>

              {/* Action Results */}
              {(actionResults.etl || actionResults.train || actionResults.export) && (
                <div className="mt-3">
                  {actionResults.etl && (
                    <Alert 
                      variant={actionResults.etl.status === 'success' ? 'success' : 'danger'}
                      className="mb-2"
                    >
                      <strong>ETL Pipeline:</strong> {actionResults.etl.message}
                      {actionResults.etl.status === 'success' && (
                        <div className="mt-2">
                          <small>
                            Processed {actionResults.etl.total_records} records across {Object.keys(actionResults.etl.processed_records).length} sources
                          </small>
                        </div>
                      )}
                    </Alert>
                  )}

                  {actionResults.train && (
                    <Alert 
                      variant={actionResults.train.status === 'success' ? 'success' : 'danger'}
                      className="mb-2"
                    >
                      <strong>Model Training:</strong> {actionResults.train.message}
                      {actionResults.train.status === 'success' && (
                        <div className="mt-2">
                          <small>
                            Trained {actionResults.train.models_trained} models with improved accuracy
                          </small>
                        </div>
                      )}
                    </Alert>
                  )}

                  {actionResults.export && (
                    <Alert 
                      variant={actionResults.export.status === 'success' ? 'success' : 'danger'}
                      className="mb-2"
                    >
                      <strong>Report Export:</strong> {actionResults.export.message}
                      {actionResults.export.status === 'success' && (
                        <div className="mt-2">
                          <small>
                            Report generated successfully. Format: {actionResults.export.format}
                          </small>
                        </div>
                      )}
                    </Alert>
                  )}
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 