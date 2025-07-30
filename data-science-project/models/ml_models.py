"""
Machine Learning Models Module
Handles model training, evaluation, and predictions for various data types
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple, Any
import joblib
import json

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVR, SVC
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

logger = logging.getLogger(__name__)

class MLModels:
    """Main machine learning class for training and evaluating models"""
    
    def __init__(self):
        self.models = {}
        self.model_metadata = {}
        self.feature_importance = {}
    
    def train_covid_forecasting_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train COVID-19 forecasting model"""
        logger.info("Training COVID-19 forecasting model...")
        
        if df.empty or len(df) < 10:
            logger.warning("Insufficient data for COVID-19 model training")
            return {}
        
        # Prepare features for COVID forecasting
        feature_cols = [
            'cases', 'deaths', 'recovered', 'new_cases', 'new_deaths',
            'case_fatality_rate', 'recovery_rate', 'cases_7d_avg',
            'deaths_7d_avg', 'cases_growth_rate', 'deaths_growth_rate',
            'day_of_year', 'week_of_year', 'month'
        ]
        
        # Use available features
        available_features = [col for col in feature_cols if col in df.columns]
        
        if len(available_features) < 3:
            logger.warning("Insufficient features for COVID-19 model")
            return {}
        
        # Target: predict next day's cases
        df_model = df.copy()
        df_model['target_cases'] = df_model['cases'].shift(-1)
        df_model = df_model.dropna()
        
        if len(df_model) < 10:
            logger.warning("Insufficient data after target creation")
            return {}
        
        X = df_model[available_features]
        y = df_model['target_cases']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train multiple models
        models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'linear_regression': LinearRegression(),
            'xgboost': xgb.XGBRegressor(n_estimators=100, random_state=42)
        }
        
        best_model = None
        best_score = -float('inf')
        results = {}
        
        for name, model in models.items():
            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                results[name] = {
                    'mse': mse,
                    'r2': r2,
                    'rmse': np.sqrt(mse)
                }
                
                if r2 > best_score:
                    best_score = r2
                    best_model = model
                    
            except Exception as e:
                logger.error(f"Error training {name}: {e}")
                continue
        
        if best_model is None:
            logger.warning("No models trained successfully")
            return {}
        
        # Store best model
        self.models['covid_forecast'] = best_model
        self.model_metadata['covid_forecast'] = {
            'features': available_features,
            'best_model': list(results.keys())[list(results.values()).index(max(results.values(), key=lambda x: x['r2']))],
            'performance': results,
            'trained_date': datetime.now().isoformat()
        }
        
        # Feature importance for tree-based models
        if hasattr(best_model, 'feature_importances_'):
            self.feature_importance['covid_forecast'] = dict(zip(available_features, best_model.feature_importances_))
        
        logger.info(f"COVID-19 model trained with R² = {best_score:.3f}")
        return results
    
    def train_stock_prediction_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train stock price prediction model"""
        logger.info("Training stock prediction model...")
        
        if df.empty or len(df) < 20:
            logger.warning("Insufficient data for stock model training")
            return {}
        
        # Prepare features for stock prediction
        feature_cols = [
            'open', 'high', 'low', 'volume', 'daily_return', 'volatility',
            'sma_5', 'sma_20', 'ema_12', 'ema_26', 'macd', 'macd_signal',
            'rsi', 'bb_middle', 'bb_upper', 'bb_lower', 'momentum_5',
            'momentum_10', 'volume_sma', 'volume_ratio', 'price_change',
            'price_change_pct', 'high_low_ratio', 'close_open_ratio',
            'day_of_week', 'month', 'quarter'
        ]
        
        available_features = [col for col in feature_cols if col in df.columns]
        
        if len(available_features) < 5:
            logger.warning("Insufficient features for stock model")
            return {}
        
        # Target: predict next day's close price
        df_model = df.copy()
        df_model['target_close'] = df_model['close'].shift(-1)
        df_model = df_model.dropna()
        
        if len(df_model) < 20:
            logger.warning("Insufficient data after target creation")
            return {}
        
        X = df_model[available_features]
        y = df_model['target_close']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train models
        models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'xgboost': xgb.XGBRegressor(n_estimators=100, random_state=42),
            'svr': SVR(kernel='rbf')
        }
        
        best_model = None
        best_score = -float('inf')
        results = {}
        
        for name, model in models.items():
            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                results[name] = {
                    'mse': mse,
                    'r2': r2,
                    'rmse': np.sqrt(mse)
                }
                
                if r2 > best_score:
                    best_score = r2
                    best_model = model
                    
            except Exception as e:
                logger.error(f"Error training {name}: {e}")
                continue
        
        if best_model is None:
            logger.warning("No stock models trained successfully")
            return {}
        
        # Store best model
        self.models['stock_prediction'] = best_model
        self.model_metadata['stock_prediction'] = {
            'features': available_features,
            'best_model': list(results.keys())[list(results.values()).index(max(results.values(), key=lambda x: x['r2']))],
            'performance': results,
            'trained_date': datetime.now().isoformat()
        }
        
        # Feature importance
        if hasattr(best_model, 'feature_importances_'):
            self.feature_importance['stock_prediction'] = dict(zip(available_features, best_model.feature_importances_))
        
        logger.info(f"Stock model trained with R² = {best_score:.3f}")
        return results
    
    def train_weather_classification_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train weather classification model"""
        logger.info("Training weather classification model...")
        
        if df.empty or len(df) < 10:
            logger.warning("Insufficient data for weather model training")
            return {}
        
        # Prepare features for weather classification
        feature_cols = [
            'temperature', 'humidity', 'pressure', 'wind_speed',
            'temp_fahrenheit', 'hour', 'day_of_week', 'month',
            'is_summer', 'is_winter', 'is_weekend'
        ]
        
        available_features = [col for col in feature_cols if col in df.columns]
        
        if len(available_features) < 3:
            logger.warning("Insufficient features for weather model")
            return {}
        
        # Target: classify weather conditions
        df_model = df.copy()
        
        # Create weather categories based on temperature and conditions
        df_model['weather_category'] = pd.cut(
            df_model['temperature'],
            bins=[-float('inf'), 0, 15, 25, float('inf')],
            labels=['Cold', 'Cool', 'Warm', 'Hot']
        )
        
        df_model = df_model.dropna()
        
        if len(df_model) < 10:
            logger.warning("Insufficient data after target creation")
            return {}
        
        X = df_model[available_features]
        y = df_model['weather_category']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train models
        models = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'logistic_regression': LogisticRegression(random_state=42),
            'svc': SVC(random_state=42)
        }
        
        best_model = None
        best_score = -float('inf')
        results = {}
        
        for name, model in models.items():
            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                
                accuracy = accuracy_score(y_test, y_pred)
                
                results[name] = {
                    'accuracy': accuracy,
                    'classification_report': classification_report(y_test, y_pred, output_dict=True)
                }
                
                if accuracy > best_score:
                    best_score = accuracy
                    best_model = model
                    
            except Exception as e:
                logger.error(f"Error training {name}: {e}")
                continue
        
        if best_model is None:
            logger.warning("No weather models trained successfully")
            return {}
        
        # Store best model
        self.models['weather_classification'] = best_model
        self.model_metadata['weather_classification'] = {
            'features': available_features,
            'best_model': list(results.keys())[list(results.values()).index(max(results.values(), key=lambda x: x['accuracy']))],
            'performance': results,
            'trained_date': datetime.now().isoformat()
        }
        
        # Feature importance
        if hasattr(best_model, 'feature_importances_'):
            self.feature_importance['weather_classification'] = dict(zip(available_features, best_model.feature_importances_))
        
        logger.info(f"Weather model trained with accuracy = {best_score:.3f}")
        return results
    
    def make_prediction(self, model_name: str, features: pd.DataFrame) -> np.ndarray:
        """Make predictions using a trained model"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        model = self.models[model_name]
        metadata = self.model_metadata[model_name]
        
        # Select only the features used in training
        available_features = [col for col in metadata['features'] if col in features.columns]
        
        if len(available_features) != len(metadata['features']):
            missing_features = set(metadata['features']) - set(available_features)
            logger.warning(f"Missing features for {model_name}: {missing_features}")
        
        X = features[available_features]
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        return model.predict(X)
    
    def get_model_summary(self) -> Dict[str, Any]:
        """Get summary of all trained models"""
        summary = {
            'total_models': len(self.models),
            'models': {}
        }
        
        for name, metadata in self.model_metadata.items():
            summary['models'][name] = {
                'best_model': metadata['best_model'],
                'features_count': len(metadata['features']),
                'trained_date': metadata['trained_date'],
                'performance': metadata['performance']
            }
        
        return summary
    
    def save_models(self, filepath: str):
        """Save all models and metadata"""
        model_data = {
            'models': self.models,
            'metadata': self.model_metadata,
            'feature_importance': self.feature_importance
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Models saved to {filepath}")
    
    def load_models(self, filepath: str):
        """Load models and metadata"""
        model_data = joblib.load(filepath)
        
        self.models = model_data['models']
        self.model_metadata = model_data['metadata']
        self.feature_importance = model_data['feature_importance']
        
        logger.info(f"Models loaded from {filepath}")
    
    def train_all_models(self, processed_data: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, Any]]:
        """Train models for all available data types"""
        logger.info("Training models for all data types...")
        
        results = {}
        
        if 'covid' in processed_data:
            results['covid'] = self.train_covid_forecasting_model(processed_data['covid'])
        
        if 'stock' in processed_data:
            results['stock'] = self.train_stock_prediction_model(processed_data['stock'])
        
        if 'weather' in processed_data:
            results['weather'] = self.train_weather_classification_model(processed_data['weather'])
        
        logger.info(f"Trained models for {len(results)} data types")
        return results

if __name__ == "__main__":
    # Test the ML models
    ml = MLModels()
    
    # Create sample data for testing
    sample_data = pd.DataFrame({
        'cases': np.random.randint(1000, 10000, 50),
        'deaths': np.random.randint(10, 100, 50),
        'recovered': np.random.randint(500, 5000, 50),
        'new_cases': np.random.randint(100, 1000, 50),
        'day_of_year': np.random.randint(1, 365, 50),
        'month': np.random.randint(1, 13, 50)
    })
    
    results = ml.train_covid_forecasting_model(sample_data)
    print(f"COVID model results: {results}")
    
    summary = ml.get_model_summary()
    print(f"Model summary: {summary}") 