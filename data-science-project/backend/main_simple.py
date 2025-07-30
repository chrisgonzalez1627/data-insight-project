"""
Simplified FastAPI Backend for Data Science Project
Serves data insights, predictions, and analytics without external dependencies
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Data Science Analytics API",
    description="API for serving data insights, predictions, and analytics",
    version="1.0.0"
)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Get CORS origins from environment
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple ML Models class for demo
class SimpleMLModels:
    def __init__(self):
        self.models = {
            "covid_prediction": "linear_regression",
            "stock_prediction": "random_forest",
            "weather_prediction": "xgboost"
        }
        self.model_metadata = {
            "covid_prediction": {
                "features": ["cases", "deaths", "recovered"],
                "best_model": "linear_regression",
                "accuracy": 0.85
            },
            "stock_prediction": {
                "features": ["open", "high", "low", "volume"],
                "best_model": "random_forest",
                "accuracy": 0.78
            },
            "weather_prediction": {
                "features": ["temperature", "humidity", "pressure"],
                "best_model": "xgboost",
                "accuracy": 0.92
            }
        }
        self.feature_importance = {
            "covid_prediction": {"cases": 0.6, "deaths": 0.3, "recovered": 0.1},
            "stock_prediction": {"volume": 0.4, "high": 0.3, "low": 0.2, "open": 0.1},
            "weather_prediction": {"temperature": 0.5, "humidity": 0.3, "pressure": 0.2}
        }
    
    def get_model_summary(self):
        return {
            "total_models": len(self.models),
            "available_models": list(self.models.keys()),
            "model_types": list(set(self.models.values())),
            "metadata": self.model_metadata
        }
    
    def make_prediction(self, model_name, features_df):
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        # Simple mock prediction based on model type
        if self.models[model_name] == "linear_regression":
            return np.random.normal(100, 10, len(features_df))
        elif self.models[model_name] == "random_forest":
            return np.random.normal(150, 15, len(features_df))
        elif self.models[model_name] == "xgboost":
            return np.random.normal(25, 5, len(features_df))
        else:
            return np.random.normal(50, 10, len(features_df))

# Simple Data Processor class for demo
class SimpleDataProcessor:
    def __init__(self):
        pass
    
    def generate_sample_data(self, source_name, num_records=100):
        """Generate sample data for demonstration"""
        dates = pd.date_range(start='2024-01-01', periods=num_records, freq='D')
        
        if source_name == 'covid':
            data = {
                'date': dates,
                'cases': np.random.randint(100, 1000, num_records),
                'deaths': np.random.randint(10, 100, num_records),
                'recovered': np.random.randint(50, 500, num_records)
            }
        elif source_name == 'stock':
            data = {
                'date': dates,
                'open': np.random.uniform(100, 200, num_records),
                'high': np.random.uniform(150, 250, num_records),
                'low': np.random.uniform(50, 150, num_records),
                'close': np.random.uniform(100, 200, num_records),
                'volume': np.random.randint(1000000, 10000000, num_records)
            }
        elif source_name == 'weather':
            data = {
                'date': dates,
                'temperature': np.random.uniform(10, 30, num_records),
                'humidity': np.random.uniform(30, 90, num_records),
                'pressure': np.random.uniform(1000, 1020, num_records)
            }
        else:
            data = {
                'date': dates,
                'value': np.random.uniform(0, 100, num_records)
            }
        
        return pd.DataFrame(data)

# Initialize components
ml_models = SimpleMLModels()
data_processor = SimpleDataProcessor()

# Pydantic models for request/response
class PredictionRequest(BaseModel):
    model_name: str
    features: Dict[str, Any]

class DataSourceRequest(BaseModel):
    source: str
    limit: Optional[int] = 100

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Data Science Analytics API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/health",
            "/data/sources",
            "/data/{source}",
            "/insights",
            "/models",
            "/predict",
            "/analytics"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": len(ml_models.models),
        "uptime": "running"
    }

@app.get("/data/sources")
async def get_data_sources():
    """Get available data sources"""
    sources = [
        {
            "name": "covid",
            "filename": "covid_data.csv",
            "size_bytes": 1024,
            "type": "processed",
            "description": "COVID-19 pandemic statistics"
        },
        {
            "name": "stock",
            "filename": "stock_data.csv",
            "size_bytes": 2048,
            "type": "processed",
            "description": "Stock market data"
        },
        {
            "name": "weather",
            "filename": "weather_data.csv",
            "size_bytes": 1536,
            "type": "processed",
            "description": "Weather data"
        }
    ]
    
    return {"sources": sources}

@app.get("/data/{source}")
async def get_data(source: str, limit: int = Query(100, ge=1, le=1000)):
    """Get data from a specific source"""
    if source not in ['covid', 'stock', 'weather']:
        raise HTTPException(status_code=404, detail=f"Data source '{source}' not found")
    
    try:
        # Generate sample data
        df = data_processor.generate_sample_data(source, limit)
        
        # Convert to JSON-serializable format
        data = df.to_dict(orient='records')
        
        return {
            "source": source,
            "total_records": len(df),
            "columns": list(df.columns),
            "data": data
        }
        
    except Exception as e:
        logger.error(f"Error reading data for {source}: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading data: {str(e)}")

@app.get("/insights")
async def get_insights():
    """Get insights from all data sources"""
    insights = {}
    
    for source in ['covid', 'stock', 'weather']:
        try:
            df = data_processor.generate_sample_data(source, 50)
            
            source_insights = {
                'total_records': len(df),
                'columns': list(df.columns),
                'numeric_summary': {},
                'latest_data': df.tail(5).to_dict(orient='records')
            }
            
            # Numeric summary
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if col != 'date':
                    source_insights['numeric_summary'][col] = {
                        'mean': float(df[col].mean()),
                        'std': float(df[col].std()),
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                        'median': float(df[col].median())
                    }
            
            # Source-specific insights
            if source == 'covid' and 'cases' in df.columns:
                latest_cases = df['cases'].iloc[-1]
                latest_deaths = df['deaths'].iloc[-1]
                source_insights['covid_stats'] = {
                    'total_cases': int(latest_cases),
                    'total_deaths': int(latest_deaths),
                    'fatality_rate': float(latest_deaths / latest_cases * 100) if latest_cases > 0 else 0
                }
            
            elif source == 'stock' and 'close' in df.columns:
                latest_price = df['close'].iloc[-1]
                price_change = df['close'].pct_change().iloc[-1] if len(df) > 1 else 0
                source_insights['stock_stats'] = {
                    'latest_price': float(latest_price),
                    'daily_change': float(price_change * 100),
                    'volatility': float(df['close'].std() / df['close'].mean() * 100)
                }
            
            insights[source] = source_insights
            
        except Exception as e:
            logger.error(f"Error processing insights for {source}: {e}")
            continue
    
    return {"insights": insights}

@app.get("/models")
async def get_models():
    """Get information about trained models"""
    return ml_models.get_model_summary()

@app.post("/predict")
async def make_prediction(request: PredictionRequest):
    """Make predictions using trained models"""
    if request.model_name not in ml_models.models:
        raise HTTPException(
            status_code=404, 
            detail=f"Model '{request.model_name}' not found. Available models: {list(ml_models.models.keys())}"
        )
    
    try:
        # Convert features to DataFrame
        features_df = pd.DataFrame([request.features])
        
        # Make prediction
        prediction = ml_models.make_prediction(request.model_name, features_df)
        
        # Get model metadata
        metadata = ml_models.model_metadata.get(request.model_name, {})
        
        return {
            "model_name": request.model_name,
            "prediction": prediction.tolist() if hasattr(prediction, 'tolist') else prediction,
            "features_used": metadata.get('features', []),
            "model_type": metadata.get('best_model', 'unknown'),
            "accuracy": metadata.get('accuracy', 0.0),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/analytics")
async def get_analytics():
    """Get comprehensive analytics and statistics"""
    analytics = {
        "timestamp": datetime.now().isoformat(),
        "data_sources": {},
        "models": ml_models.get_model_summary(),
        "overall_stats": {
            "total_data_sources": 3,
            "total_records": 150,
            "data_directory_size_mb": 0.5
        }
    }
    
    # Data source analytics
    for source in ['covid', 'stock', 'weather']:
        df = data_processor.generate_sample_data(source, 50)
        analytics["data_sources"][source] = {
            "records": len(df),
            "columns": len(df.columns),
            "file_size_mb": 0.2,
            "last_updated": datetime.now().isoformat()
        }
    
    return analytics

@app.get("/analytics/{source}/trends")
async def get_trends(source: str, days: int = Query(30, ge=1, le=365)):
    """Get trend analysis for a specific data source"""
    if source not in ['covid', 'stock', 'weather']:
        raise HTTPException(status_code=404, detail=f"Data source '{source}' not found")
    
    try:
        df = data_processor.generate_sample_data(source, days)
        
        # Calculate trends for numeric columns
        trends = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if col != 'date':
                values = df[col].dropna()
                if len(values) > 1:
                    # Calculate trend (slope of linear regression)
                    x = np.arange(len(values))
                    slope = np.polyfit(x, values, 1)[0]
                    
                    trends[col] = {
                        "trend_direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
                        "trend_magnitude": float(abs(slope)),
                        "current_value": float(values.iloc[-1]),
                        "average_value": float(values.mean()),
                        "min_value": float(values.min()),
                        "max_value": float(values.max())
                    }
        
        return {
            "source": source,
            "analysis_period_days": days,
            "date_range": {
                "start": df['date'].min().isoformat(),
                "end": df['date'].max().isoformat()
            },
            "trends": trends,
            "total_records_analyzed": len(df)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing trends for {source}: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing trends: {str(e)}")

@app.post("/etl/run")
async def run_etl_pipeline():
    """Run the ETL pipeline to collect and process data"""
    try:
        logger.info("Starting ETL pipeline...")
        
        # Simulate ETL pipeline execution
        import time
        time.sleep(2)  # Simulate processing time
        
        # Generate fresh data for all sources
        sources = ['covid', 'stock', 'weather']
        processed_records = {}
        
        for source in sources:
            # Generate new sample data
            df = data_processor.generate_sample_data(source, 100)
            processed_records[source] = len(df)
            logger.info(f"Processed {len(df)} records for {source}")
        
        total_records = sum(processed_records.values())
        
        return {
            "status": "success",
            "message": "ETL pipeline completed successfully",
            "processed_records": processed_records,
            "total_records": total_records,
            "timestamp": datetime.now().isoformat(),
            "execution_time": "2.5 seconds"
        }
        
    except Exception as e:
        logger.error(f"ETL pipeline error: {e}")
        raise HTTPException(status_code=500, detail=f"ETL pipeline failed: {str(e)}")

@app.post("/models/train")
async def train_models():
    """Train or retrain all ML models"""
    try:
        logger.info("Starting model training...")
        
        # Simulate model training
        import time
        time.sleep(3)  # Simulate training time
        
        # Update model metrics with improved performance
        models_to_train = ['covid_prediction', 'stock_prediction', 'weather_prediction']
        training_results = {}
        
        for model_name in models_to_train:
            # Simulate improved model performance
            base_accuracy = 0.85
            improvement = np.random.uniform(0.01, 0.05)
            new_accuracy = min(0.98, base_accuracy + improvement)
            
            training_results[model_name] = {
                "status": "trained",
                "accuracy": float(new_accuracy),
                "training_time": f"{np.random.uniform(30, 120):.1f} seconds",
                "improvement": float(improvement)
            }
            
            logger.info(f"Trained {model_name} with accuracy: {new_accuracy:.3f}")
        
        return {
            "status": "success",
            "message": "All models trained successfully",
            "models_trained": len(models_to_train),
            "training_results": training_results,
            "timestamp": datetime.now().isoformat(),
            "total_training_time": "3.2 seconds"
        }
        
    except Exception as e:
        logger.error(f"Model training error: {e}")
        raise HTTPException(status_code=500, detail=f"Model training failed: {str(e)}")

@app.get("/export/report")
async def export_report():
    """Generate and export a comprehensive data report"""
    try:
        logger.info("Generating data report...")
        
        # Simulate report generation
        import time
        time.sleep(1)
        
        # Collect data for report
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "data_sources": {},
            "analytics_summary": {},
            "model_performance": {},
            "recommendations": []
        }
        
        # Add data source summaries
        for source in ['covid', 'stock', 'weather']:
            df = data_processor.generate_sample_data(source, 50)
            report_data["data_sources"][source] = {
                "total_records": len(df),
                "columns": list(df.columns),
                "last_updated": datetime.now().isoformat()
            }
        
        # Add analytics summary
        report_data["analytics_summary"] = {
            "total_data_points": 150,
            "data_freshness": "Recent",
            "trend_analysis": "Available",
            "prediction_models": 3
        }
        
        # Add model performance
        report_data["model_performance"] = {
            "covid_prediction": {"accuracy": 0.87, "status": "Active"},
            "stock_prediction": {"accuracy": 0.79, "status": "Active"},
            "weather_prediction": {"accuracy": 0.92, "status": "Active"}
        }
        
        # Add recommendations
        report_data["recommendations"] = [
            "Consider expanding COVID-19 data collection for better predictions",
            "Stock prediction model shows good performance, consider additional features",
            "Weather model accuracy is excellent, ready for production deployment"
        ]
        
        return {
            "status": "success",
            "message": "Report generated successfully",
            "report": report_data,
            "download_url": "/api/export/report/download",
            "format": "JSON"
        }
        
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 