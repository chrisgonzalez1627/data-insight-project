"""
Main ETL Pipeline
Orchestrates data collection, processing, and model training
"""

import sys
import os
import logging
from datetime import datetime
import pandas as pd
import json
import numpy as np

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.data_collector import DataCollector
from etl.data_processor import DataProcessor
from models.ml_models import MLModels

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ETLPipeline:
    """Main ETL pipeline class"""
    
    def __init__(self):
        self.collector = DataCollector()
        self.processor = DataProcessor()
        self.ml_models = MLModels()
        
        # Create data directory if it doesn't exist
        os.makedirs('../data', exist_ok=True)
        os.makedirs('../models', exist_ok=True)
    
    def run_full_pipeline(self) -> dict:
        """Run the complete ETL pipeline"""
        logger.info("Starting full ETL pipeline...")
        
        pipeline_results = {
            'timestamp': datetime.now().isoformat(),
            'status': 'completed',
            'data_sources': {},
            'models_trained': {},
            'errors': []
        }
        
        try:
            # Step 1: Collect data
            logger.info("Step 1: Collecting data from all sources...")
            raw_data = self.collector.collect_all_data()
            
            for source_name, df in raw_data.items():
                pipeline_results['data_sources'][source_name] = {
                    'records': len(df),
                    'columns': list(df.columns),
                    'collected_at': datetime.now().isoformat()
                }
                
                # Save raw data
                if not df.empty:
                    raw_filepath = f"../data/raw_{source_name}_{datetime.now().strftime('%Y%m%d')}.csv"
                    df.to_csv(raw_filepath, index=False)
                    logger.info(f"Saved raw {source_name} data: {len(df)} records")
            
            # Step 2: Process and clean data
            logger.info("Step 2: Processing and cleaning data...")
            processed_data = self.processor.process_all_data(raw_data)
            
            for source_name, df in processed_data.items():
                if not df.empty:
                    processed_filepath = f"../data/processed_{source_name}_{datetime.now().strftime('%Y%m%d')}.csv"
                    df.to_csv(processed_filepath, index=False)
                    logger.info(f"Saved processed {source_name} data: {len(df)} records")
            
            # Step 3: Train machine learning models
            logger.info("Step 3: Training machine learning models...")
            model_results = self.ml_models.train_all_models(processed_data)
            
            for model_name, results in model_results.items():
                if results:  # If models were successfully trained
                    pipeline_results['models_trained'][model_name] = results
                    logger.info(f"Trained {model_name} models successfully")
            
            # Step 4: Save models
            if self.ml_models.models:
                model_filepath = f"../models/trained_models_{datetime.now().strftime('%Y%m%d')}.joblib"
                self.ml_models.save_models(model_filepath)
                logger.info(f"Saved trained models to {model_filepath}")
            
            # Step 5: Generate insights and statistics
            logger.info("Step 5: Generating insights and statistics...")
            insights = self.generate_insights(processed_data)
            pipeline_results['insights'] = insights
            
            # Step 6: Save pipeline results
            results_filepath = f"../data/pipeline_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_filepath, 'w') as f:
                json.dump(pipeline_results, f, indent=2, default=str)
            
            logger.info("ETL pipeline completed successfully!")
            
        except Exception as e:
            logger.error(f"Error in ETL pipeline: {e}")
            pipeline_results['status'] = 'failed'
            pipeline_results['errors'].append(str(e))
        
        return pipeline_results
    
    def generate_insights(self, processed_data: dict) -> dict:
        """Generate insights and statistics from processed data"""
        insights = {}
        
        for source_name, df in processed_data.items():
            if df.empty:
                continue
            
            source_insights = {
                'total_records': len(df),
                'date_range': {
                    'start': df.select_dtypes(include=['datetime64']).min().min().isoformat() if df.select_dtypes(include=['datetime64']).shape[1] > 0 else None,
                    'end': df.select_dtypes(include=['datetime64']).max().max().isoformat() if df.select_dtypes(include=['datetime64']).shape[1] > 0 else None
                },
                'numeric_summary': {},
                'missing_values': {}
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
            
            # Missing values
            for col in df.columns:
                missing_count = df[col].isnull().sum()
                if missing_count > 0:
                    source_insights['missing_values'][col] = {
                        'count': int(missing_count),
                        'percentage': float(missing_count / len(df) * 100)
                    }
            
            # Source-specific insights
            if source_name == 'covid':
                if 'cases' in df.columns and 'deaths' in df.columns:
                    latest_cases = df['cases'].iloc[-1] if len(df) > 0 else 0
                    latest_deaths = df['deaths'].iloc[-1] if len(df) > 0 else 0
                    source_insights['latest_stats'] = {
                        'total_cases': int(latest_cases),
                        'total_deaths': int(latest_deaths),
                        'fatality_rate': float(latest_deaths / latest_cases * 100) if latest_cases > 0 else 0
                    }
            
            elif source_name == 'stock':
                if 'close' in df.columns:
                    latest_price = df['close'].iloc[-1] if len(df) > 0 else 0
                    price_change = df['close'].pct_change().iloc[-1] if len(df) > 1 else 0
                    source_insights['latest_stats'] = {
                        'latest_price': float(latest_price),
                        'daily_change': float(price_change * 100),
                        'volatility': float(df['daily_return'].std() * 100) if 'daily_return' in df.columns else 0
                    }
            
            elif source_name == 'weather':
                if 'temperature' in df.columns:
                    avg_temp = df['temperature'].mean()
                    temp_range = df['temperature'].max() - df['temperature'].min()
                    source_insights['latest_stats'] = {
                        'average_temperature': float(avg_temp),
                        'temperature_range': float(temp_range),
                        'temperature_unit': 'Celsius'
                    }
            
            insights[source_name] = source_insights
        
        return insights
    
    def run_data_collection_only(self) -> dict:
        """Run only the data collection step"""
        logger.info("Running data collection only...")
        
        try:
            raw_data = self.collector.collect_all_data()
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'status': 'completed',
                'data_sources': {}
            }
            
            for source_name, df in raw_data.items():
                results['data_sources'][source_name] = {
                    'records': len(df),
                    'columns': list(df.columns)
                }
                
                if not df.empty:
                    filepath = f"../data/raw_{source_name}_{datetime.now().strftime('%Y%m%d')}.csv"
                    df.to_csv(filepath, index=False)
                    logger.info(f"Saved {source_name} data: {len(df)} records")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in data collection: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def run_model_training_only(self) -> dict:
        """Run only the model training step using existing processed data"""
        logger.info("Running model training only...")
        
        try:
            # Load latest processed data
            processed_data = {}
            data_dir = '../data'
            
            for filename in os.listdir(data_dir):
                if filename.startswith('processed_') and filename.endswith('.csv'):
                    source_name = filename.replace('processed_', '').replace('.csv', '').split('_')[0]
                    filepath = os.path.join(data_dir, filename)
                    df = pd.read_csv(filepath)
                    
                    # Convert date columns
                    date_cols = ['date', 'datetime']
                    for col in date_cols:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col])
                    
                    processed_data[source_name] = df
            
            if not processed_data:
                logger.warning("No processed data found for model training")
                return {'status': 'failed', 'error': 'No processed data found'}
            
            # Train models
            model_results = self.ml_models.train_all_models(processed_data)
            
            # Save models
            if self.ml_models.models:
                model_filepath = f"../models/trained_models_{datetime.now().strftime('%Y%m%d')}.joblib"
                self.ml_models.save_models(model_filepath)
                logger.info(f"Saved trained models to {model_filepath}")
            
            return {
                'status': 'completed',
                'models_trained': model_results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in model training: {e}")
            return {'status': 'failed', 'error': str(e)}

def main():
    """Main function to run the ETL pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ETL Pipeline for Data Science Project')
    parser.add_argument('--mode', choices=['full', 'collect', 'train'], 
                       default='full', help='Pipeline mode to run')
    
    args = parser.parse_args()
    
    pipeline = ETLPipeline()
    
    if args.mode == 'full':
        results = pipeline.run_full_pipeline()
    elif args.mode == 'collect':
        results = pipeline.run_data_collection_only()
    elif args.mode == 'train':
        results = pipeline.run_model_training_only()
    
    print(f"Pipeline completed with status: {results.get('status', 'unknown')}")
    
    if results.get('status') == 'failed':
        print(f"Errors: {results.get('errors', results.get('error', 'Unknown error'))}")
        sys.exit(1)

if __name__ == "__main__":
    main() 