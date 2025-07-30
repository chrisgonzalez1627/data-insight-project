"""
FastAPI Backend for Data Science Project
Serves data insights, predictions, and analytics
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

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.ml_models import MLModels
from etl.data_processor import DataProcessor

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

# Initialize components
ml_models = MLModels()
data_processor = DataProcessor()

# Load models if they exist
models_dir = "../models"
if os.path.exists(models_dir):
    model_files = [f for f in os.listdir(models_dir) if f.endswith('.joblib')]
    if model_files:
        latest_model = sorted(model_files)[-1]
        try:
            ml_models.load_models(os.path.join(models_dir, latest_model))
            logger.info(f"Loaded models from {latest_model}")
        except Exception as e:
            logger.warning(f"Could not load models: {e}")

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
        "models_loaded": len(ml_models.models)
    }

@app.get("/data/sources")
async def get_data_sources():
    """Get available data sources"""
    data_dir = "../data"
    sources = []
    
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.endswith('.csv'):
                source_name = filename.replace('processed_', '').replace('raw_', '').split('_')[0]
                filepath = os.path.join(data_dir, filename)
                file_size = os.path.getsize(filepath)
                
                sources.append({
                    "name": source_name,
                    "filename": filename,
                    "size_bytes": file_size,
                    "type": "processed" if filename.startswith("processed_") else "raw"
                })
    
    return {"sources": sources}

@app.get("/data/{source}")
async def get_data(source: str, limit: int = Query(100, ge=1, le=1000)):
    """Get data from a specific source"""
    data_dir = "../data"
    
    # Look for processed data first, then raw data
    processed_file = os.path.join(data_dir, f"processed_{source}_{datetime.now().strftime('%Y%m%d')}.csv")
    raw_file = os.path.join(data_dir, f"raw_{source}_{datetime.now().strftime('%Y%m%d')}.csv")
    
    file_to_read = None
    if os.path.exists(processed_file):
        file_to_read = processed_file
    elif os.path.exists(raw_file):
        file_to_read = raw_file
    else:
        # Try to find any file with this source name
        for filename in os.listdir(data_dir):
            if filename.startswith(f"processed_{source}_") or filename.startswith(f"raw_{source}_"):
                file_to_read = os.path.join(data_dir, filename)
                break
    
    if not file_to_read or not os.path.exists(file_to_read):
        raise HTTPException(status_code=404, detail=f"Data source '{source}' not found")
    
    try:
        df = pd.read_csv(file_to_read)
        
        # Convert date columns
        date_cols = ['date', 'datetime']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
        
        # Limit results
        df = df.head(limit)
        
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
    data_dir = "../data"
    insights = {}
    
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.startswith('processed_') and filename.endswith('.csv'):
                source_name = filename.replace('processed_', '').split('_')[0]
                filepath = os.path.join(data_dir, filename)
                
                try:
                    df = pd.read_csv(filepath)
                    
                    # Convert date columns
                    date_cols = ['date', 'datetime']
                    for col in date_cols:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col])
                    
                    source_insights = {
                        'total_records': len(df),
                        'columns': list(df.columns),
                        'numeric_summary': {},
                        'latest_data': {}
                    }
                    
                    # Numeric summary
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    for col in numeric_cols:
                        source_insights['numeric_summary'][col] = {
                            'mean': float(df[col].mean()),
                            'std': float(df[col].std()),
                            'min': float(df[col].min()),
                            'max': float(df[col].max()),
                            'median': float(df[col].median())
                        }
                    
                    # Latest data (last 5 records)
                    if len(df) > 0:
                        latest_data = df.tail(5).to_dict(orient='records')
                        source_insights['latest_data'] = latest_data
                    
                    # Source-specific insights
                    if source_name == 'covid' and 'cases' in df.columns:
                        latest_cases = df['cases'].iloc[-1] if len(df) > 0 else 0
                        latest_deaths = df['deaths'].iloc[-1] if len(df) > 0 else 0
                        source_insights['covid_stats'] = {
                            'total_cases': int(latest_cases),
                            'total_deaths': int(latest_deaths),
                            'fatality_rate': float(latest_deaths / latest_cases * 100) if latest_cases > 0 else 0
                        }
                    
                    elif source_name == 'stock' and 'close' in df.columns:
                        latest_price = df['close'].iloc[-1] if len(df) > 0 else 0
                        price_change = df['close'].pct_change().iloc[-1] if len(df) > 1 else 0
                        source_insights['stock_stats'] = {
                            'latest_price': float(latest_price),
                            'daily_change': float(price_change * 100),
                            'volatility': float(df['daily_return'].std() * 100) if 'daily_return' in df.columns else 0
                        }
                    
                    insights[source_name] = source_insights
                    
                except Exception as e:
                    logger.error(f"Error processing insights for {source_name}: {e}")
                    continue
    
    return {"insights": insights}

@app.get("/models")
async def get_models():
    """Get information about trained models"""
    model_summary = ml_models.get_model_summary()
    
    # Add feature importance if available
    if ml_models.feature_importance:
        model_summary['feature_importance'] = ml_models.feature_importance
    
    return model_summary

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
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/analytics")
async def get_analytics():
    """Get comprehensive analytics and statistics"""
    data_dir = "../data"
    analytics = {
        "timestamp": datetime.now().isoformat(),
        "data_sources": {},
        "models": {},
        "overall_stats": {}
    }
    
    # Data source analytics
    if os.path.exists(data_dir):
        total_records = 0
        sources_count = 0
        
        for filename in os.listdir(data_dir):
            if filename.endswith('.csv'):
                source_name = filename.replace('processed_', '').replace('raw_', '').split('_')[0]
                filepath = os.path.join(data_dir, filename)
                
                try:
                    df = pd.read_csv(filepath)
                    records = len(df)
                    total_records += records
                    sources_count += 1
                    
                    analytics["data_sources"][source_name] = {
                        "records": records,
                        "columns": len(df.columns),
                        "file_size_mb": round(os.path.getsize(filepath) / (1024 * 1024), 2),
                        "last_updated": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                    }
                    
                except Exception as e:
                    logger.error(f"Error analyzing {filename}: {e}")
        
        analytics["overall_stats"] = {
            "total_data_sources": sources_count,
            "total_records": total_records,
            "data_directory_size_mb": round(sum(os.path.getsize(os.path.join(data_dir, f)) for f in os.listdir(data_dir) if f.endswith('.csv')) / (1024 * 1024), 2)
        }
    
    # Model analytics
    model_summary = ml_models.get_model_summary()
    analytics["models"] = model_summary
    
    return analytics

@app.get("/analytics/{source}/trends")
async def get_trends(source: str, days: int = Query(30, ge=1, le=365)):
    """Get trend analysis for a specific data source"""
    data_dir = "../data"
    
    # Find the data file
    file_to_read = None
    for filename in os.listdir(data_dir):
        if filename.startswith(f"processed_{source}_") or filename.startswith(f"raw_{source}_"):
            file_to_read = os.path.join(data_dir, filename)
            break
    
    if not file_to_read or not os.path.exists(file_to_read):
        raise HTTPException(status_code=404, detail=f"Data source '{source}' not found")
    
    try:
        df = pd.read_csv(file_to_read)
        
        # Convert date columns
        date_cols = ['date', 'datetime']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
                break
        
        if not any(col in df.columns for col in date_cols):
            raise HTTPException(status_code=400, detail="No date column found in data")
        
        # Get the date column
        date_col = next(col for col in date_cols if col in df.columns)
        
        # Sort by date and get recent data
        df = df.sort_values(date_col)
        recent_data = df.tail(days)
        
        # Calculate trends for numeric columns
        trends = {}
        numeric_cols = recent_data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if col != date_col:
                values = recent_data[col].dropna()
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
                "start": recent_data[date_col].min().isoformat(),
                "end": recent_data[date_col].max().isoformat()
            },
            "trends": trends,
            "total_records_analyzed": len(recent_data)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing trends for {source}: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing trends: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 