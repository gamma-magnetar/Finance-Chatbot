"""
Market Data Ingestion for the Finance Assistant.
Handles retrieval and processing of market data.
"""

import pandas as pd
import yfinance as yf
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class MarketDataIngestion:
    """
    Class for ingesting market data from various sources.
    Primary source is Yahoo Finance API.
    """
    
    def __init__(self):
        """Initialize the market data ingestion."""
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = 300  # Cache duration in seconds (5 minutes)
    
    def get_stock_data(self, ticker: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """
        Get historical stock data for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            DataFrame with stock data
        """
        cache_key = f"{ticker}_{period}_{interval}"
        
        # Check cache
        if cache_key in self.cache and self.cache_expiry.get(cache_key, 0) > time.time():
            logger.info(f"Using cached data for {ticker}")
            return self.cache[cache_key]
        
        try:
            logger.info(f"Fetching stock data for {ticker}")
            stock = yf.Ticker(ticker)
            data = stock.history(period=period, interval=interval)
            
            # Cache the result
            self.cache[cache_key] = data
            self.cache_expiry[cache_key] = time.time() + self.cache_duration
            
            return data
        except Exception as e:
            logger.error(f"Error fetching stock data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def get_market_indices(self) -> Dict[str, pd.DataFrame]:
        """
        Get data for major market indices.
        
        Returns:
            Dictionary with index data
        """
        indices = {
            "S&P 500": "^GSPC",
            "Dow Jones": "^DJI",
            "NASDAQ": "^IXIC",
            "FTSE 100": "^FTSE",
            "Nikkei 225": "^N225",
            "Hang Seng": "^HSI"
        }
        
        result = {}
        for name, ticker in indices.items():
            try:
                result[name] = self.get_stock_data(ticker)
            except Exception as e:
                logger.error(f"Error fetching index data for {name}: {str(e)}")
                result[name] = pd.DataFrame()
                
        return result
    
    def get_sector_performance(self) -> Dict[str, float]:
        """
        Get performance for major market sectors using ETFs.
        
        Returns:
            Dictionary with sector performance (percentage change)
        """
        # Sector ETFs
        sectors = {
            "Technology": "XLK",
            "Healthcare": "XLV",
            "Financial": "XLF",
            "Consumer Discretionary": "XLY",
            "Consumer Staples": "XLP",
            "Energy": "XLE",
            "Utilities": "XLU",
            "Materials": "XLB",
            "Industrial": "XLI",
            "Real Estate": "XLRE",
            "Communication": "XLC"
        }
        
        result = {}
        for sector, ticker in sectors.items():
            try:
                # Get 5-day performance
                data = self.get_stock_data(ticker, period="5d")
                
                if not data.empty:
                    # Calculate percentage change
                    first_close = data['Close'].iloc[0]
                    last_close = data['Close'].iloc[-1]
                    pct_change = (last_close - first_close) / first_close * 100
                    
                    result[sector] = round(pct_change, 2)
                else:
                    result[sector] = 0.0
                    
            except Exception as e:
                logger.error(f"Error calculating sector performance for {sector}: {str(e)}")
                result[sector] = 0.0
                
        return result
    
    def get_economic_indicators(self) -> Dict[str, float]:
        """
        Get key economic indicators.
        
        Returns:
            Dictionary with economic indicators
        """
        indicators = {
            "10-Year Treasury Yield": "^TNX",
            "30-Year Treasury Yield": "^TYX",
            "Crude Oil": "CL=F",
            "Gold": "GC=F",
            "VIX": "^VIX",
            "USD/EUR": "USDEUR=X",
            "USD/JPY": "USDJPY=X"
        }
        
        result = {}
        for name, ticker in indicators.items():
            try:
                data = self.get_stock_data(ticker, period="1d")
                
                if not data.empty:
                    result[name] = data['Close'].iloc[-1]
                else:
                    result[name] = 0.0
                    
            except Exception as e:
                logger.error(f"Error fetching indicator {name}: {str(e)}")
                result[name] = 0.0
                
        return result
    
    def get_earnings_calendar(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get upcoming earnings announcements.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of upcoming earnings announcements
        """
        try:
            # Define date range
            start_date = datetime.now().strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Use yfinance to get earnings calendar
            calendar = pd.read_html(f'https://finance.yahoo.com/calendar/earnings?from={start_date}&to={end_date}')
            
            if not calendar:
                return []
                
            earnings_df = calendar[0]
            
            # Convert to list of dictionaries
            earnings = []
            for _, row in earnings_df.iterrows():
                earnings.append({
                    'symbol': row['Symbol'],
                    'company': row['Company'],
                    'date': row['Earnings Date'],
                    'eps_estimate': row['EPS Estimate']
                })
                
            return earnings
                
        except Exception as e:
            logger.error(f"Error fetching earnings calendar: {str(e)}")
            return []
    
    def get_recent_ipos(self) -> List[Dict[str, Any]]:
        """
        Get recent IPOs.
        
        Returns:
            List of recent IPOs
        """
        try:
            # Use yfinance to get IPO calendar
            calendar = pd.read_html('https://finance.yahoo.com/calendar/ipo')
            
            if not calendar:
                return []
                
            ipo_df = calendar[0]
            
            # Convert to list of dictionaries
            ipos = []
            for _, row in ipo_df.iterrows():
                ipos.append({
                    'symbol': row['Symbol'],
                    'company': row['Company'],
                    'price_range': row['Price Range'],
                    'date': row['Date']
                })
                
            return ipos
                
        except Exception as e:
            logger.error(f"Error fetching recent IPOs: {str(e)}")
            return []
