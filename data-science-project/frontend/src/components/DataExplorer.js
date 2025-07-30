import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Table, Form, Button, Alert, Spinner, Badge } from 'react-bootstrap';
import { Line } from 'react-chartjs-2';
import { endpoints } from '../services/api';
import moment from 'moment';

const DataExplorer = () => {
  const [sources, setSources] = useState([]);
  const [selectedSource, setSelectedSource] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [limit, setLimit] = useState(100);
  const [filterColumn, setFilterColumn] = useState('');
  const [filterValue, setFilterValue] = useState('');
  const [sortColumn, setSortColumn] = useState('');
  const [sortDirection, setSortDirection] = useState('asc');

  useEffect(() => {
    fetchSources();
  }, []);

  useEffect(() => {
    if (selectedSource) {
      fetchData();
    }
  }, [selectedSource, limit]);

  const fetchSources = async () => {
    try {
      console.log('Fetching data sources...');
      const response = await endpoints.getDataSources();
      console.log('Data sources response:', response.data);
      setSources(response.data.sources || []);
    } catch (err) {
      console.error('Sources fetch error:', err);
      setError('Failed to fetch data sources: ' + err.message);
    }
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching data for source:', selectedSource, 'limit:', limit);
      const response = await endpoints.getData(selectedSource, limit);
      console.log('Data response:', response.data);
      setData(response.data);
    } catch (err) {
      console.error('Data fetch error:', err);
      setError(`Failed to fetch data for ${selectedSource}: ` + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (column) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  const getSortedData = () => {
    if (!data?.data || !Array.isArray(data.data)) {
      console.log('No data available for sorting');
      return [];
    }
    
    let sortedData = [...data.data];
    
    if (sortColumn) {
      sortedData.sort((a, b) => {
        let aVal = a[sortColumn];
        let bVal = b[sortColumn];
        
        // Handle date sorting
        if (aVal && bVal && (typeof aVal === 'string' && aVal.includes('T'))) {
          aVal = new Date(aVal);
          bVal = new Date(bVal);
        }
        
        // Handle numeric sorting
        if (typeof aVal === 'number' && typeof bVal === 'number') {
          return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
        }
        
        // Handle string sorting
        if (typeof aVal === 'string' && typeof bVal === 'string') {
          return sortDirection === 'asc' 
            ? aVal.localeCompare(bVal) 
            : bVal.localeCompare(aVal);
        }
        
        return 0;
      });
    }
    
    // Apply filter
    if (filterColumn && filterValue) {
      sortedData = sortedData.filter(item => {
        const value = item[filterColumn];
        if (value === null || value === undefined) return false;
        return value.toString().toLowerCase().includes(filterValue.toLowerCase());
      });
    }
    
    return sortedData;
  };

  const prepareChartData = () => {
    if (!data?.data || !Array.isArray(data.data) || data.data.length === 0) {
      console.log('No data available for chart');
      return null;
    }
    
    const sortedData = getSortedData();
    if (!sortedData || !Array.isArray(sortedData) || sortedData.length === 0) {
      console.log('No sorted data available for chart');
      return null;
    }
    
    const sampleData = sortedData.slice(0, 20); // Limit for chart
    
    // Additional safety check for sampleData
    if (!sampleData || sampleData.length === 0 || !sampleData[0]) {
      console.log('No valid sample data for chart');
      return null;
    }
    
    // Find numeric columns
    const numericColumns = Object.keys(sampleData[0] || {}).filter(key => {
      const value = sampleData[0][key];
      return typeof value === 'number' && !isNaN(value);
    });
    
    if (numericColumns.length === 0) {
      console.log('No numeric columns found for chart');
      return null;
    }
    
    const labels = sampleData && Array.isArray(sampleData) ? sampleData.map((_, index) => `Record ${index + 1}`) : [];
    const datasets = numericColumns && Array.isArray(numericColumns) ? numericColumns.slice(0, 3).map((column, index) => ({
      label: column,
      data: sampleData && Array.isArray(sampleData) ? sampleData.map(item => item[column] || 0) : [],
      borderColor: `hsl(${index * 120}, 70%, 50%)`,
      backgroundColor: `hsla(${index * 120}, 70%, 50%, 0.1)`,
      tension: 0.1
    })) : [];
    
    return { labels, datasets };
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
        text: 'Data Visualization'
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  };

  const formatValue = (value) => {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'number') return value.toLocaleString();
    if (typeof value === 'string' && value.includes('T')) {
      return moment(value).format('YYYY-MM-DD HH:mm:ss');
    }
    return value.toString();
  };

  // Debug logging
  console.log('DataExplorer render state:', {
    sources: sources ? sources.length : 'undefined',
    sourcesType: typeof sources,
    sourcesIsArray: Array.isArray(sources),
    selectedSource,
    data: data ? { total_records: data.total_records, columns: data.columns?.length, data_length: data.data?.length } : null,
    loading,
    error
  });

  return (
    <div className="fade-in">
      <h1 className="text-white mb-4">Data Explorer</h1>
      
      {/* Source Selection */}
      <Row className="mb-4">
        <Col md={6}>
          <Card>
            <Card.Header>Select Data Source</Card.Header>
            <Card.Body>
              <Form.Select 
                value={selectedSource} 
                onChange={(e) => setSelectedSource(e.target.value)}
              >
                <option value="">Choose a data source...</option>
                {sources && Array.isArray(sources) && sources.map((source, index) => (
                  <option key={index} value={source.name}>
                    {source.name} ({source.type}) - {source.size_bytes} bytes
                  </option>
                ))}
              </Form.Select>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={6}>
          <Card>
            <Card.Header>Data Controls</Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>Records Limit</Form.Label>
                    <Form.Control
                      type="number"
                      value={limit}
                      onChange={(e) => setLimit(parseInt(e.target.value) || 100)}
                      min="1"
                      max="1000"
                    />
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group>
                    <Form.Label>&nbsp;</Form.Label>
                    <div>
                      <Button 
                        variant="primary" 
                        onClick={fetchData}
                        disabled={!selectedSource || loading}
                      >
                        {loading ? <Spinner size="sm" /> : 'Refresh Data'}
                      </Button>
                    </div>
                  </Form.Group>
                </Col>
              </Row>
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

      {data && data.data && Array.isArray(data.data) && (
        <>
          {/* Data Statistics */}
          <Row className="mb-4">
            <Col>
              <Card>
                <Card.Header>Data Overview</Card.Header>
                <Card.Body>
                  <Row>
                    <Col md={3}>
                      <div className="text-center">
                        <h4>{data.total_records?.toLocaleString() || 0}</h4>
                        <small className="text-muted">Total Records</small>
                      </div>
                    </Col>
                    <Col md={3}>
                      <div className="text-center">
                        <h4>{data.columns?.length || 0}</h4>
                        <small className="text-muted">Columns</small>
                      </div>
                    </Col>
                    <Col md={3}>
                      <div className="text-center">
                        <h4>{getSortedData() ? getSortedData().length : 0}</h4>
                        <small className="text-muted">Filtered Records</small>
                      </div>
                    </Col>
                    <Col md={3}>
                      <div className="text-center">
                        <h4>{selectedSource}</h4>
                        <small className="text-muted">Source</small>
                      </div>
                    </Col>
                  </Row>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {/* Filters and Sorting */}
          <Row className="mb-4">
            <Col>
              <Card>
                <Card.Header>Filters & Sorting</Card.Header>
                <Card.Body>
                  <Row>
                    <Col md={4}>
                      <Form.Group>
                        <Form.Label>Filter Column</Form.Label>
                        <Form.Select 
                          value={filterColumn} 
                          onChange={(e) => setFilterColumn(e.target.value)}
                        >
                          <option value="">Select column...</option>
                          {data.columns?.map((col, index) => (
                            <option key={index} value={col}>{col}</option>
                          ))}
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col md={4}>
                      <Form.Group>
                        <Form.Label>Filter Value</Form.Label>
                        <Form.Control
                          type="text"
                          value={filterValue}
                          onChange={(e) => setFilterValue(e.target.value)}
                          placeholder="Enter filter value..."
                        />
                      </Form.Group>
                    </Col>
                    <Col md={4}>
                      <Form.Group>
                        <Form.Label>Sort Column</Form.Label>
                        <Form.Select 
                          value={sortColumn} 
                          onChange={(e) => setSortColumn(e.target.value)}
                        >
                          <option value="">No sorting</option>
                          {data.columns?.map((col, index) => (
                            <option key={index} value={col}>{col}</option>
                          ))}
                        </Form.Select>
                      </Form.Group>
                    </Col>
                  </Row>
                  {sortColumn && (
                    <div className="mt-2">
                      <Button
                        variant="outline-secondary"
                        size="sm"
                        onClick={() => setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')}
                      >
                        Sort: {sortColumn} ({sortDirection.toUpperCase()})
                      </Button>
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {/* Data Visualization */}
          {(() => {
            try {
              const chartData = prepareChartData();
              if (chartData) {
                return (
                  <Row className="mb-4">
                    <Col>
                      <Card>
                        <Card.Header>Data Visualization</Card.Header>
                        <Card.Body>
                          <div className="chart-container">
                            <Line data={chartData} options={chartOptions} />
                          </div>
                        </Card.Body>
                      </Card>
                    </Col>
                  </Row>
                );
              }
              return null;
            } catch (error) {
              console.error('Error rendering chart:', error);
              return (
                <Row className="mb-4">
                  <Col>
                    <Card>
                      <Card.Header>Data Visualization</Card.Header>
                      <Card.Body>
                        <Alert variant="warning">
                          Error rendering chart: {error.message}
                        </Alert>
                      </Card.Body>
                    </Card>
                  </Col>
                </Row>
              );
            }
          })()}

          {/* Data Table */}
          <Row>
            <Col>
              <Card>
                <Card.Header>
                  Data Table 
                  <Badge bg="secondary" className="ms-2">
                    {getSortedData() ? getSortedData().length : 0} records
                  </Badge>
                </Card.Header>
                <Card.Body className="table-container">
                  {(() => {
                    try {
                      const sortedData = getSortedData();
                      if (sortedData && sortedData.length > 0) {
                        return (
                          <Table striped bordered hover responsive>
                            <thead>
                              <tr>
                                {data.columns?.map((column, index) => (
                                  <th 
                                    key={index}
                                    onClick={() => handleSort(column)}
                                    style={{ cursor: 'pointer' }}
                                  >
                                    {column}
                                    {sortColumn === column && (
                                      <span className="ms-1">
                                        {sortDirection === 'asc' ? '↑' : '↓'}
                                      </span>
                                    )}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {sortedData.slice(0, 50).map((row, rowIndex) => (
                                <tr key={rowIndex}>
                                  {data.columns?.map((column, colIndex) => (
                                    <td key={colIndex}>
                                      {formatValue(row[column])}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </Table>
                        );
                      } else {
                        return <p className="text-muted text-center">No data to display</p>;
                      }
                    } catch (error) {
                      console.error('Error rendering table:', error);
                      return (
                        <Alert variant="warning">
                          Error rendering table: {error.message}
                        </Alert>
                      );
                    }
                  })()}
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </>
      )}

      {!data && !loading && selectedSource && (
        <Alert variant="info">
          <Alert.Heading>No Data</Alert.Heading>
          <p>Select a data source and click "Refresh Data" to load data.</p>
        </Alert>
      )}
    </div>
  );
};

export default DataExplorer; 