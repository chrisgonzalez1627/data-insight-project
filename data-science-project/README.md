# Data Science Project: Multi-Source Analytics Platform

A comprehensive data science project that demonstrates data collection, ETL processing, machine learning, and interactive visualizations.

## Project Overview

This project includes:
- **Data Collection**: Multiple APIs (COVID-19, Weather, Stock Market) and web scraping
- **ETL Pipeline**: Data cleaning, transformation, and preparation
- **Machine Learning**: Predictive models for various datasets
- **Backend API**: FastAPI server serving insights and predictions
- **Frontend**: React application with interactive visualizations

## Project Structure

```
data-science-project/
├── backend/                 # FastAPI backend
├── frontend/               # React frontend
├── data/                   # Data storage
├── notebooks/              # Jupyter notebooks for analysis
├── etl/                    # ETL pipeline scripts
├── models/                 # Trained ML models
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Features

### Data Sources
- **COVID-19 Data**: Real-time pandemic statistics
- **Weather Data**: Historical weather patterns
- **Stock Market Data**: Financial indicators
- **Web Scraping**: Additional public datasets

### Analytics & ML
- Time series forecasting
- Classification models
- Regression analysis
- Statistical insights

### Visualizations
- Interactive charts with Chart.js
- Real-time data dashboards
- Predictive model results
- Statistical summaries

## Quick Start

### Local Development

1. **Setup Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Setup Frontend**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Run ETL Pipeline**:
   ```bash
   python etl/main.py
   ```

### Production Deployment

For production deployment to Vercel (frontend) and Heroku (backend):

1. **Quick Deployment**: Follow [QUICK_START.md](QUICK_START.md)
2. **Detailed Guide**: Follow [DEPLOYMENT.md](DEPLOYMENT.md)
3. **Automated Script**: Run `./deploy.sh`

**Prerequisites**:
- GitHub repository
- Heroku account
- Vercel account

## Technologies Used

- **Backend**: FastAPI, SQLAlchemy, Pandas, Scikit-learn
- **Frontend**: React, Chart.js, Axios
- **Data Processing**: Pandas, NumPy, BeautifulSoup
- **Machine Learning**: Scikit-learn, XGBoost
- **Database**: SQLite (development), PostgreSQL (production) 