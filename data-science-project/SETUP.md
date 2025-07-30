# Data Science Analytics Platform - Setup Guide

This guide will help you set up and run the complete Data Science Analytics Platform.

## Prerequisites

Before starting, ensure you have the following installed:

### Required Software
- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/)

### Optional (for enhanced functionality)
- **PostgreSQL** - For production database
- **Docker** - For containerized deployment

## Quick Start

### 1. Clone and Navigate to Project
```bash
git clone <your-repo-url>
cd data-science-project
```

### 2. Run the Complete Platform
```bash
python start.py
```

This single command will:
- Run the ETL pipeline to collect and process data
- Start the FastAPI backend server
- Start the React frontend development server
- Open the application in your browser

## Manual Setup (Alternative)

If you prefer to set up components individually:

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   - Windows: `venv\Scripts\activate`
   - Unix/Mac: `source venv/bin/activate`

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Start the FastAPI server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

### ETL Pipeline Setup

1. **Navigate to ETL directory:**
   ```bash
   cd etl
   ```

2. **Run the ETL pipeline:**
   ```bash
   python main.py --mode full
   ```

## Accessing the Application

Once everything is running:

- **Frontend Dashboard:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **API Health Check:** http://localhost:8000/health

## Project Structure

```
data-science-project/
├── backend/                 # FastAPI backend server
│   ├── main.py             # Main API application
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.js          # Main app component
│   │   └── index.js        # App entry point
│   ├── public/             # Static files
│   └── package.json        # Node.js dependencies
├── etl/                    # ETL pipeline
│   ├── main.py             # Main ETL orchestrator
│   ├── data_collector.py   # Data collection module
│   └── data_processor.py   # Data processing module
├── models/                 # Machine learning models
│   └── ml_models.py        # ML model training and prediction
├── data/                   # Data storage
├── notebooks/              # Jupyter notebooks for analysis
├── start.py               # Platform startup script
├── requirements.txt       # Main Python dependencies
└── README.md             # Project documentation
```

## Features

### Data Collection
- **COVID-19 Data:** Real-time pandemic statistics
- **Weather Data:** Historical weather patterns
- **Stock Market Data:** Financial indicators
- **Web Scraping:** Additional public datasets

### Data Processing
- Automated data cleaning and transformation
- Feature engineering
- Statistical analysis
- Data validation

### Machine Learning
- **COVID-19 Forecasting:** Predict future cases
- **Stock Price Prediction:** Predict stock prices
- **Weather Classification:** Classify weather conditions
- Multiple algorithms (Random Forest, XGBoost, SVM, etc.)

### Analytics & Visualization
- Interactive dashboards
- Real-time data visualization
- Trend analysis
- Statistical insights
- Custom charts and graphs

### API Endpoints
- `/data/sources` - List available data sources
- `/data/{source}` - Get data from specific source
- `/insights` - Get data insights
- `/models` - Get model information
- `/predict` - Make predictions
- `/analytics` - Get comprehensive analytics
- `/analytics/{source}/trends` - Get trend analysis

## Configuration

### Environment Variables
Create a `.env` file in the project root for custom configuration:

```env
# API Keys (optional - for enhanced data collection)
OPENWEATHER_API_KEY=your_openweather_api_key
ALPHA_VANTAGE_API_KEY=your_alphavantage_api_key

# Database Configuration (optional)
DATABASE_URL=postgresql://user:password@localhost/dbname

# Server Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

### API Keys (Optional)
For enhanced data collection, you can obtain free API keys:

1. **OpenWeatherMap:** https://openweathermap.org/api
2. **Alpha Vantage:** https://www.alphavantage.co/support/#api-key

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Kill processes using ports 3000 and 8000
   lsof -ti:3000 | xargs kill -9
   lsof -ti:8000 | xargs kill -9
   ```

2. **Python Dependencies Issues**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

3. **Node.js Dependencies Issues**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **ETL Pipeline Errors**
   - Check internet connection
   - Verify API endpoints are accessible
   - Review log files in the project directory

### Logs
- **ETL Pipeline:** `etl/etl_pipeline.log`
- **Backend:** Console output
- **Frontend:** Browser console

## Development

### Adding New Data Sources
1. Extend `DataCollector` class in `etl/data_collector.py`
2. Add processing logic in `etl/data_processor.py`
3. Update API endpoints in `backend/main.py`
4. Add frontend components in `frontend/src/components/`

### Adding New ML Models
1. Extend `MLModels` class in `models/ml_models.py`
2. Add model training methods
3. Update API endpoints
4. Add prediction interface in frontend

### Customizing Visualizations
- Modify Chart.js configurations in React components
- Add new chart types as needed
- Customize styling in `frontend/src/App.css`

## Production Deployment

### Docker Deployment
```bash
# Build and run with Docker
docker-compose up --build
```

### Manual Production Setup
1. Set up production database (PostgreSQL recommended)
2. Configure environment variables
3. Set up reverse proxy (nginx)
4. Use production WSGI server (gunicorn)
5. Build frontend for production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation at http://localhost:8000/docs

## Acknowledgments

- FastAPI for the backend framework
- React for the frontend framework
- Chart.js for data visualization
- Scikit-learn for machine learning
- Pandas for data processing 