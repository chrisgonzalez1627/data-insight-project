"""
Data Collector Module
Handles data collection from multiple sources including APIs and web scraping
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time
import logging
from typing import Dict, List, Optional
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollector:
    """Main data collection class for multiple data sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def collect_covid_data(self) -> pd.DataFrame:
        """Collect COVID-19 data from multiple sources"""
        logger.info("Collecting COVID-19 data...")
        
        try:
            # COVID-19 API (free tier)
            url = "https://disease.sh/v3/covid-19/historical/all?lastdays=30"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df.index)
            df = df.reset_index(drop=True)
            
            # Add calculated columns
            df['new_cases'] = df['cases'].diff()
            df['new_deaths'] = df['deaths'].diff()
            df['new_recovered'] = df['recovered'].diff()
            
            logger.info(f"Collected {len(df)} COVID-19 records")
            return df
            
        except Exception as e:
            logger.error(f"Error collecting COVID-19 data: {e}")
            return pd.DataFrame()
    
    def collect_weather_data(self, city: str = "New York") -> pd.DataFrame:
        """Collect weather data using OpenWeatherMap API (free tier)"""
        logger.info(f"Collecting weather data for {city}...")
        
        try:
            # Using a free weather API
            url = f"https://api.openweathermap.org/data/2.5/forecast"
            params = {
                'q': city,
                'appid': 'demo',  # Replace with actual API key
                'units': 'metric'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract weather data
            weather_data = []
            for item in data.get('list', []):
                weather_data.append({
                    'datetime': pd.to_datetime(item['dt'], unit='s'),
                    'temperature': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'pressure': item['main']['pressure'],
                    'description': item['weather'][0]['description'],
                    'wind_speed': item['wind']['speed']
                })
            
            df = pd.DataFrame(weather_data)
            logger.info(f"Collected {len(df)} weather records")
            return df
            
        except Exception as e:
            logger.error(f"Error collecting weather data: {e}")
            return pd.DataFrame()
    
    def collect_stock_data(self, symbol: str = "AAPL") -> pd.DataFrame:
        """Collect stock market data using Alpha Vantage API"""
        logger.info(f"Collecting stock data for {symbol}...")
        
        try:
            # Using Alpha Vantage API (free tier)
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': 'demo',  # Replace with actual API key
                'outputsize': 'compact'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract time series data
            time_series = data.get('Time Series (Daily)', {})
            
            stock_data = []
            for date, values in time_series.items():
                stock_data.append({
                    'date': pd.to_datetime(date),
                    'open': float(values['1. open']),
                    'high': float(values['2. high']),
                    'low': float(values['3. low']),
                    'close': float(values['4. close']),
                    'volume': int(values['5. volume'])
                })
            
            df = pd.DataFrame(stock_data)
            df = df.sort_values('date').reset_index(drop=True)
            
            # Add technical indicators
            df['daily_return'] = df['close'].pct_change()
            df['volatility'] = df['daily_return'].rolling(window=5).std()
            
            logger.info(f"Collected {len(df)} stock records")
            return df
            
        except Exception as e:
            logger.error(f"Error collecting stock data: {e}")
            return pd.DataFrame()
    
    def scrape_public_data(self) -> pd.DataFrame:
        """Scrape additional public data from websites"""
        logger.info("Scraping public data...")
        
        try:
            # Example: Scraping population data from a public source
            url = "https://en.wikipedia.org/wiki/List_of_countries_by_population"
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the main table
            table = soup.find('table', {'class': 'wikitable'})
            if not table:
                return pd.DataFrame()
            
            # Extract data
            data = []
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows[:20]:  # Limit to first 20 countries
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 3:
                    try:
                        country = cols[1].get_text(strip=True)
                        population = cols[2].get_text(strip=True).replace(',', '')
                        population = int(population) if population.isdigit() else 0
                        
                        data.append({
                            'country': country,
                            'population': population,
                            'scraped_date': datetime.now()
                        })
                    except (ValueError, IndexError):
                        continue
            
            df = pd.DataFrame(data)
            logger.info(f"Scraped {len(df)} public records")
            return df
            
        except Exception as e:
            logger.error(f"Error scraping public data: {e}")
            return pd.DataFrame()
    
    def collect_all_data(self) -> Dict[str, pd.DataFrame]:
        """Collect data from all sources"""
        logger.info("Starting data collection from all sources...")
        
        data_sources = {}
        
        # Collect COVID-19 data
        covid_data = self.collect_covid_data()
        if not covid_data.empty:
            data_sources['covid'] = covid_data
        
        # Collect weather data
        weather_data = self.collect_weather_data()
        if not weather_data.empty:
            data_sources['weather'] = weather_data
        
        # Collect stock data
        stock_data = self.collect_stock_data()
        if not stock_data.empty:
            data_sources['stock'] = stock_data
        
        # Scrape public data
        public_data = self.scrape_public_data()
        if not public_data.empty:
            data_sources['public'] = public_data
        
        logger.info(f"Collected data from {len(data_sources)} sources")
        return data_sources

if __name__ == "__main__":
    collector = DataCollector()
    data = collector.collect_all_data()
    
    # Save data to files
    for source_name, df in data.items():
        if not df.empty:
            filename = f"../data/{source_name}_data_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(filename, index=False)
            print(f"Saved {source_name} data to {filename}") 