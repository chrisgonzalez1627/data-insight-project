import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Form, Button, Alert, Spinner, Badge, ProgressBar } from 'react-bootstrap';
// import { Line, Bar, Doughnut } from 'react-chartjs-2'; // Temporarily commented out
import { endpoints } from '../services/api';
import moment from 'moment';

const Analytics = () => {
  const [sources, setSources] = useState([]);
  const [selectedSource, setSelectedSource] = useState('');
  const [trends, setTrends] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [days, setDays] = useState(30);

  useEffect(() => {
    fetchSources();
    fetchInsights();
  }, []);

  useEffect(() => {
    if (selectedSource) {
      fetchTrends();
    }
  }, [selectedSource, days]);

  const fetchSources = async () => {
    try {
      console.log('Fetching sources for analytics...');
      const response = await endpoints.getDataSources();
      console.log('Analytics sources response:', response.data);
      setSources(response.data.sources || []);
    } catch (err) {
      console.error('Sources fetch error:', err);
      setError('Failed to fetch data sources: ' + err.message);
    }
  };

  const fetchInsights = async () => {
    try {
      console.log('Fetching insights...');
      const response = await endpoints.getInsights();
      console.log('Insights response:', response.data);
      setInsights(response.data);
    } catch (err) {
      console.error('Insights fetch error:', err);
      // Don't set error for insights as it's not critical
    }
  };

  const fetchTrends = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching trends for source:', selectedSource, 'days:', days);
      const response = await endpoints.getTrends(selectedSource, days);
      console.log('Trends response:', response.data);
      setTrends(response.data);
    } catch (err) {
      console.error('Trends fetch error:', err);
      setError(`Failed to fetch trends for ${selectedSource}: ` + err.message);
    } finally {
      setLoading(false);
    }
  };

  const prepareTrendChartData = () => {
    if (!trends?.trends || typeof trends.trends !== 'object') {
      console.log('No trends data available for chart');
      return null;
    }
    
    const trendData = trends.trends;
    const labels = Object.keys(trendData);
    
    if (labels.length === 0) {
      console.log('No trend labels available');
      return null;
    }
    
    const datasets = [];
    
    // Create datasets for different metrics
    const metrics = ['current_value', 'average_value', 'min_value', 'max_value'];
    const colors = ['rgb(255, 99, 132)', 'rgb(54, 162, 235)', 'rgb(255, 205, 86)', 'rgb(75, 192, 192)'];
    
    metrics.forEach((metric, index) => {
      const data = labels && Array.isArray(labels) ? labels.map(label => {
        const value = trendData[label]?.[metric];
        return typeof value === 'number' ? value : 0;
      }) : [];
      
      if (data.some(val => val !== 0)) {
        datasets.push({
          label: metric.replace('_', ' ').toUpperCase(),
          data: data,
          borderColor: colors[index],
          backgroundColor: colors[index].replace('rgb', 'rgba').replace(')', ', 0.1)'),
          tension: 0.1
        });
      }
    });
    
    return datasets.length > 0 ? { labels, datasets } : null;
  };

  const prepareTrendDirectionChart = () => {
    if (!trends?.trends || typeof trends.trends !== 'object') {
      console.log('No trends data available for direction chart');
      return null;
    }
    
    const trendData = trends.trends;
    const directions = {};
    
    if (trendData && typeof trendData === 'object') {
      Object.values(trendData).forEach(trend => {
        if (trend && typeof trend === 'object' && trend.trend_direction) {
          const direction = trend.trend_direction;
          directions[direction] = (directions[direction] || 0) + 1;
        }
      });
    }
    
    const labels = Object.keys(directions);
    if (labels.length === 0) {
      console.log('No trend directions available');
      return null;
    }
    
    return {
      labels: labels,
      datasets: [{
        data: Object.values(directions),
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

  const getTrendIcon = (direction) => {
    switch (direction) {
      case 'increasing': return '↗️';
      case 'decreasing': return '↘️';
      case 'stable': return '→';
      default: return '❓';
    }
  };

  const getTrendColor = (direction) => {
    switch (direction) {
      case 'increasing': return 'success';
      case 'decreasing': return 'danger';
      case 'stable': return 'warning';
      default: return 'secondary';
    }
  };

  // Debug logging
  console.log('Analytics render state:', {
    sources: sources ? sources.length : 'undefined',
    sourcesType: typeof sources,
    sourcesIsArray: Array.isArray(sources),
    selectedSource,
    trends: trends ? { trends_count: Object.keys(trends.trends || {}).length } : null,
    insights: insights ? { insights_count: Object.keys(insights.insights || {}).length } : null,
    loading,
    error
  });

  return (
    <div className="fade-in">
      <h1 className="text-white mb-4">Analytics Dashboard</h1>
      
      {error && (
        <Alert variant="danger" className="mb-4">
          <Alert.Heading>Error</Alert.Heading>
          <p>{error}</p>
        </Alert>
      )}

      {/* Source Selection */}
      <Row className="mb-4">
        <Col md={6}>
          <Card>
            <Card.Header>Select Data Source for Trend Analysis</Card.Header>
            <Card.Body>
              <Form.Select 
                value={selectedSource} 
                onChange={(e) => setSelectedSource(e.target.value)}
              >
                <option value="">Choose a data source...</option>
                {sources && Array.isArray(sources) && sources.map((source, index) => (
                  <option key={index} value={source.name}>
                    {source.name} - {source.description}
                  </option>
                ))}
              </Form.Select>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={6}>
          <Card>
            <Card.Header>Analysis Period</Card.Header>
            <Card.Body>
              <Form.Group>
                <Form.Label>Days to Analyze</Form.Label>
                <Form.Control
                  type="number"
                  value={days}
                  onChange={(e) => setDays(parseInt(e.target.value) || 30)}
                  min="1"
                  max="365"
                />
              </Form.Group>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Insights Overview */}
      {insights && insights.insights && (
        <Row className="mb-4">
          <Col>
            <Card>
              <Card.Header>Data Insights Overview</Card.Header>
              <Card.Body>
                <Row>
                  {insights?.insights && Object.entries(insights.insights).map(([sourceName, sourceData]) => (
                    <Col md={4} key={sourceName} className="mb-3">
                      <Card className="h-100">
                        <Card.Header>{sourceName.toUpperCase()}</Card.Header>
                        <Card.Body>
                          <div className="text-center">
                            <h4>{sourceData.total_records?.toLocaleString() || 0}</h4>
                            <small className="text-muted">Total Records</small>
                          </div>
                          {sourceData.covid_stats && (
                            <div className="mt-2">
                              <small className="text-muted">COVID Stats:</small>
                              <div>Cases: {sourceData.covid_stats.total_cases?.toLocaleString()}</div>
                              <div>Deaths: {sourceData.covid_stats.total_deaths?.toLocaleString()}</div>
                              <div>Fatality Rate: {sourceData.covid_stats.fatality_rate?.toFixed(2)}%</div>
                            </div>
                          )}
                          {sourceData.stock_stats && (
                            <div className="mt-2">
                              <small className="text-muted">Stock Stats:</small>
                              <div>Price: ${sourceData.stock_stats.latest_price?.toFixed(2)}</div>
                              <div>Change: {sourceData.stock_stats.daily_change?.toFixed(2)}%</div>
                              <div>Volatility: {sourceData.stock_stats.volatility?.toFixed(2)}%</div>
                            </div>
                          )}
                        </Card.Body>
                      </Card>
                    </Col>
                  ))}
                </Row>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Trend Analysis */}
      {selectedSource && trends && (
        <>
          {/* Trend Summary */}
          <Row className="mb-4">
            <Col>
              <Card>
                <Card.Header>
                  Trend Analysis for {selectedSource.toUpperCase()}
                  <Badge bg="info" className="ms-2">
                    {days} days
                  </Badge>
                </Card.Header>
                <Card.Body>
                  {trends?.trends && Object.entries(trends.trends).map(([metric, trend]) => (
                    <div key={metric} className="mb-3">
                      <div className="d-flex justify-content-between align-items-center">
                        <div>
                          <strong>{metric.replace('_', ' ').toUpperCase()}</strong>
                          <Badge 
                            bg={getTrendColor(trend.trend_direction)} 
                            className="ms-2"
                          >
                            {getTrendIcon(trend.trend_direction)} {trend.trend_direction}
                          </Badge>
                        </div>
                        <div className="text-end">
                          <div>Current: {trend.current_value?.toFixed(2)}</div>
                          <div>Average: {trend.average_value?.toFixed(2)}</div>
                        </div>
                      </div>
                      <ProgressBar 
                        now={Math.abs(trend.trend_magnitude) * 100} 
                        variant={getTrendColor(trend.trend_direction)}
                        className="mt-1"
                      />
                    </div>
                  ))}
                </Card.Body>
              </Card>
            </Col>
          </Row>

                      {/* Trend Charts - Temporarily Disabled */}
            {/* <Row>
              {prepareTrendChartData() && (
                <Col md={8}>
                  <Card>
                    <Card.Header>Trend Metrics</Card.Header>
                    <Card.Body>
                      <div className="chart-container">
                        <Line 
                          data={prepareTrendChartData()} 
                          options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                              legend: { position: 'top' },
                              title: { display: true, text: 'Trend Analysis' }
                            },
                            scales: { y: { beginAtZero: true } }
                          }} 
                        />
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
              )}
              
              {prepareTrendDirectionChart() && (
                <Col md={4}>
                  <Card>
                    <Card.Header>Trend Directions</Card.Header>
                    <Card.Body>
                      <div className="chart-container">
                        <Doughnut 
                          data={prepareTrendDirectionChart()} 
                          options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                              legend: { position: 'bottom' }
                            }
                          }} 
                        />
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
              )}
            </Row> */}
        </>
      )}

      {!selectedSource && (
        <Alert variant="info">
          <Alert.Heading>Select a Data Source</Alert.Heading>
          <p>Choose a data source above to view trend analysis and insights.</p>
        </Alert>
      )}
    </div>
  );
};

export default Analytics; 