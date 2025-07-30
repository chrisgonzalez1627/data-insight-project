"""
Data Processor Module
Handles data cleaning, transformation, and feature engineering
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class DataProcessor:
    """Main data processing class for cleaning and transforming data"""
    
    def __init__(self):
        self.scalers = {}
        self.label_encoders = {}
        self.imputers = {}
    
    def clean_covid_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and process COVID-19 data"""
        logger.info("Cleaning COVID-19 data...")
        
        if df.empty:
            return df
        
        # Create a copy to avoid modifying original
        df_clean = df.copy()
        
        # Handle missing values
        df_clean = df_clean.fillna(0)
        
        # Remove negative values (data errors)
        numeric_cols = ['cases', 'deaths', 'recovered', 'new_cases', 'new_deaths', 'new_recovered']
        for col in numeric_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].clip(lower=0)
        
        # Add derived features
        df_clean['case_fatality_rate'] = np.where(
            df_clean['cases'] > 0,
            df_clean['deaths'] / df_clean['cases'] * 100,
            0
        )
        
        df_clean['recovery_rate'] = np.where(
            df_clean['cases'] > 0,
            df_clean['recovered'] / df_clean['cases'] * 100,
            0
        )
        
        # Add rolling averages
        df_clean['cases_7d_avg'] = df_clean['cases'].rolling(window=7).mean()
        df_clean['deaths_7d_avg'] = df_clean['deaths'].rolling(window=7).mean()
        
        # Add growth rates
        df_clean['cases_growth_rate'] = df_clean['cases'].pct_change()
        df_clean['deaths_growth_rate'] = df_clean['deaths'].pct_change()
        
        logger.info(f"Cleaned COVID-19 data: {len(df_clean)} records")
        return df_clean
    
    def clean_weather_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and process weather data"""
        logger.info("Cleaning weather data...")
        
        if df.empty:
            return df
        
        df_clean = df.copy()
        
        # Handle missing values
        df_clean = df_clean.dropna()
        
        # Remove outliers using IQR method
        numeric_cols = ['temperature', 'humidity', 'pressure', 'wind_speed']
        for col in numeric_cols:
            if col in df_clean.columns:
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df_clean = df_clean[(df_clean[col] >= lower_bound) & (df_clean[col] <= upper_bound)]
        
        # Add derived features
        df_clean['temp_fahrenheit'] = df_clean['temperature'] * 9/5 + 32
        df_clean['feels_like'] = df_clean['temperature']  # Simplified calculation
        
        # Add time-based features
        df_clean['hour'] = df_clean['datetime'].dt.hour
        df_clean['day_of_week'] = df_clean['datetime'].dt.dayofweek
        df_clean['month'] = df_clean['datetime'].dt.month
        
        # Encode weather descriptions
        if 'description' in df_clean.columns:
            le = LabelEncoder()
            df_clean['weather_code'] = le.fit_transform(df_clean['description'])
            self.label_encoders['weather_description'] = le
        
        logger.info(f"Cleaned weather data: {len(df_clean)} records")
        return df_clean
    
    def clean_stock_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and process stock market data"""
        logger.info("Cleaning stock data...")
        
        if df.empty:
            return df
        
        df_clean = df.copy()
        
        # Handle missing values
        df_clean = df_clean.dropna()
        
        # Remove outliers (extreme price movements)
        df_clean = df_clean[df_clean['daily_return'].abs() < 0.5]  # Remove >50% daily moves
        
        # Add technical indicators
        df_clean['sma_5'] = df_clean['close'].rolling(window=5).mean()
        df_clean['sma_20'] = df_clean['close'].rolling(window=20).mean()
        df_clean['ema_12'] = df_clean['close'].ewm(span=12).mean()
        df_clean['ema_26'] = df_clean['close'].ewm(span=26).mean()
        
        # MACD
        df_clean['macd'] = df_clean['ema_12'] - df_clean['ema_26']
        df_clean['macd_signal'] = df_clean['macd'].ewm(span=9).mean()
        
        # RSI
        delta = df_clean['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df_clean['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df_clean['bb_middle'] = df_clean['close'].rolling(window=20).mean()
        bb_std = df_clean['close'].rolling(window=20).std()
        df_clean['bb_upper'] = df_clean['bb_middle'] + (bb_std * 2)
        df_clean['bb_lower'] = df_clean['bb_middle'] - (bb_std * 2)
        
        # Price momentum
        df_clean['momentum_5'] = df_clean['close'] / df_clean['close'].shift(5) - 1
        df_clean['momentum_10'] = df_clean['close'] / df_clean['close'].shift(10) - 1
        
        # Volume indicators
        df_clean['volume_sma'] = df_clean['volume'].rolling(window=20).mean()
        df_clean['volume_ratio'] = df_clean['volume'] / df_clean['volume_sma']
        
        logger.info(f"Cleaned stock data: {len(df_clean)} records")
        return df_clean
    
    def clean_public_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and process public data"""
        logger.info("Cleaning public data...")
        
        if df.empty:
            return df
        
        df_clean = df.copy()
        
        # Handle missing values
        df_clean = df_clean.dropna()
        
        # Remove rows with invalid population data
        df_clean = df_clean[df_clean['population'] > 0]
        
        # Add derived features
        df_clean['population_millions'] = df_clean['population'] / 1_000_000
        df_clean['log_population'] = np.log(df_clean['population'])
        
        # Add population categories
        df_clean['population_category'] = pd.cut(
            df_clean['population'],
            bins=[0, 10_000_000, 50_000_000, 100_000_000, float('inf')],
            labels=['Small', 'Medium', 'Large', 'Very Large']
        )
        
        logger.info(f"Cleaned public data: {len(df_clean)} records")
        return df_clean
    
    def create_features(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """Create additional features for machine learning"""
        logger.info(f"Creating features for {data_type} data...")
        
        df_features = df.copy()
        
        if data_type == 'covid':
            # Time-based features
            df_features['day_of_year'] = df_features['date'].dt.dayofyear
            df_features['week_of_year'] = df_features['date'].dt.isocalendar().week
            df_features['month'] = df_features['date'].dt.month
            
            # Lag features
            df_features['cases_lag_1'] = df_features['cases'].shift(1)
            df_features['cases_lag_7'] = df_features['cases'].shift(7)
            df_features['deaths_lag_1'] = df_features['deaths'].shift(1)
            
        elif data_type == 'stock':
            # Price change features
            df_features['price_change'] = df_features['close'] - df_features['open']
            df_features['price_change_pct'] = df_features['price_change'] / df_features['open']
            
            # Volatility features
            df_features['high_low_ratio'] = df_features['high'] / df_features['low']
            df_features['close_open_ratio'] = df_features['close'] / df_features['open']
            
            # Time-based features
            df_features['day_of_week'] = df_features['date'].dt.dayofweek
            df_features['month'] = df_features['date'].dt.month
            df_features['quarter'] = df_features['date'].dt.quarter
            
        elif data_type == 'weather':
            # Seasonal features
            df_features['is_summer'] = df_features['month'].isin([6, 7, 8]).astype(int)
            df_features['is_winter'] = df_features['month'].isin([12, 1, 2]).astype(int)
            df_features['is_weekend'] = df_features['day_of_week'].isin([5, 6]).astype(int)
            
            # Temperature categories
            df_features['temp_category'] = pd.cut(
                df_features['temperature'],
                bins=[-float('inf'), 0, 10, 20, 30, float('inf')],
                labels=['Freezing', 'Cold', 'Mild', 'Warm', 'Hot']
            )
        
        return df_features
    
    def prepare_ml_data(self, df: pd.DataFrame, target_col: str, 
                       feature_cols: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for machine learning"""
        logger.info("Preparing data for machine learning...")
        
        # Remove rows with missing target
        df_ml = df.dropna(subset=[target_col])
        
        # Select features and target
        X = df_ml[feature_cols].copy()
        y = df_ml[target_col]
        
        # Handle missing values in features
        imputer = SimpleImputer(strategy='mean')
        X_imputed = imputer.fit_transform(X)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_imputed)
        
        # Store scaler for later use
        self.scalers[f'{target_col}_scaler'] = scaler
        self.imputers[f'{target_col}_imputer'] = imputer
        
        logger.info(f"Prepared ML data: {X_scaled.shape[0]} samples, {X_scaled.shape[1]} features")
        return X_scaled, y.values
    
    def process_all_data(self, data_sources: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Process all data sources"""
        logger.info("Processing all data sources...")
        
        processed_data = {}
        
        for source_name, df in data_sources.items():
            if df.empty:
                continue
                
            if source_name == 'covid':
                processed_data[source_name] = self.clean_covid_data(df)
            elif source_name == 'weather':
                processed_data[source_name] = self.clean_weather_data(df)
            elif source_name == 'stock':
                processed_data[source_name] = self.clean_stock_data(df)
            elif source_name == 'public':
                processed_data[source_name] = self.clean_public_data(df)
            
            # Add features
            if source_name in processed_data:
                processed_data[source_name] = self.create_features(
                    processed_data[source_name], source_name
                )
        
        logger.info(f"Processed {len(processed_data)} data sources")
        return processed_data

if __name__ == "__main__":
    # Test the processor
    processor = DataProcessor()
    
    # Create sample data for testing
    sample_covid = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=30),
        'cases': np.random.randint(1000, 10000, 30),
        'deaths': np.random.randint(10, 100, 30),
        'recovered': np.random.randint(500, 5000, 30)
    })
    
    processed = processor.clean_covid_data(sample_covid)
    print(f"Processed COVID data shape: {processed.shape}")
    print(f"Features: {list(processed.columns)}") 