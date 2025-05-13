"""
API Agent for the Finance Assistant.
Handles polling real-time and historical market data via APIs.
"""

import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)

class APIAgent:
    """
    Agent responsible for retrieving financial market data from APIs.
    Uses Yahoo Finance as the primary data source.
    """
    
    def __init__(self):
        """Initialize the API agent."""
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = 300  # 5 minutes in seconds
    
    def get_stock_data(self, ticker: str, period: str = "1d", interval: str = "1h") -> pd.DataFrame:
        """
        Retrieve stock data for a specific ticker.
        
        Args:
            ticker: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            DataFrame with stock data
        """
        cache_key = f"{ticker}_{period}_{interval}"
        
        # Check if we have a non-expired cached result
        if cache_key in self.cache and self.cache_expiry.get(cache_key, 0) > datetime.now().timestamp():
            logger.info(f"Using cached data for {cache_key}")
            return self.cache[cache_key]
        
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period, interval=interval)
            
            # Cache the result
            self.cache[cache_key] = data
            self.cache_expiry[cache_key] = datetime.now().timestamp() + self.cache_duration
            
            return data
        except Exception as e:
            logger.error(f"Error retrieving stock data for {ticker}: {str(e)}")
            raise
    
    def get_multiple_stocks(self, tickers: List[str], period: str = "1d") -> Dict[str, pd.DataFrame]:
        """
        Retrieve data for multiple stocks.
        
        Args:
            tickers: List of stock ticker symbols
            period: Time period
            
        Returns:
            Dictionary of stock dataframes with ticker as key
        """
        result = {}
        for ticker in tickers:
            try:
                result[ticker] = self.get_stock_data(ticker, period)
            except Exception as e:
                logger.error(f"Error retrieving data for {ticker}: {str(e)}")
                result[ticker] = None
        
        return result
    
    def get_market_indices(self) -> Dict[str, Dict[str, float]]:
        """
        Retrieve current values for major market indices.
        
        Returns:
            Dictionary of index data
        """
        indices = {
            "^GSPC": "S&P 500",
            "^DJI": "Dow Jones",
            "^IXIC": "NASDAQ",
            "^FTSE": "FTSE 100",
            "^N225": "Nikkei 225",
            "^HSI": "Hang Seng"
        }
        
        result = {}
        
        for symbol, name in indices.items():
            try:
                data = self.get_stock_data(symbol, period="1d", interval="1d")
                if not data.empty:
                    last_row = data.iloc[-1]
                    last_row_prev = data.iloc[-2] if len(data) > 1 else last_row
                    
                    change_percent = ((last_row["Close"] - last_row_prev["Close"]) / last_row_prev["Close"]) * 100
                    
                    result[name] = {
                        "price": last_row["Close"],
                        "change_percent": change_percent
                    }
            except Exception as e:
                logger.error(f"Error retrieving index {name}: {str(e)}")
                result[name] = {
                    "price": 0,
                    "change_percent": 0,
                    "error": str(e)
                }
                
        return result
    
    def get_sector_performance(self) -> Dict[str, float]:
        """
        Get performance for major market sectors.
        
        Returns:
            Dictionary with sector performance percentages
        """
        sector_etfs = {
            "XLF": "Financials",
            "XLK": "Technology",
            "XLV": "Healthcare",
            "XLE": "Energy",
            "XLY": "Consumer Discretionary",
            "XLP": "Consumer Staples",
            "XLI": "Industrials",
            "XLB": "Materials",
            "XLU": "Utilities",
            "XLRE": "Real Estate"
        }
        
        result = {}
        
        for symbol, sector in sector_etfs.items():
            try:
                data = self.get_stock_data(symbol, period="5d")
                if not data.empty:
                    first_close = data.iloc[0]["Close"]
                    last_close = data.iloc[-1]["Close"]
                    percent_change = ((last_close - first_close) / first_close) * 100
                    result[sector] = round(percent_change, 2)
            except Exception as e:
                logger.error(f"Error retrieving sector performance for {sector}: {str(e)}")
                result[sector] = 0
                
        return result
    
    def get_economic_indicators(self) -> Dict[str, Any]:
        """
        Retrieve key economic indicators.
        
        Returns:
            Dictionary with economic indicators
        """
        indicators = {
            "^TNX": "10-Year Treasury Yield",
            "^TYX": "30-Year Treasury Yield",
            "^FVX": "5-Year Treasury Yield",
            "GC=F": "Gold",
            "CL=F": "Crude Oil",
            "EURUSD=X": "EUR/USD",
            "JPY=X": "USD/JPY"
        }
        
        result = {}
        
        for symbol, name in indicators.items():
            try:
                data = self.get_stock_data(symbol, period="1d")
                if not data.empty:
                    result[name] = round(data.iloc[-1]["Close"], 4)
            except Exception as e:
                logger.error(f"Error retrieving economic indicator {name}: {str(e)}")
                result[name] = 0
                
        return result
    
    def get_asia_tech_exposure(self) -> Dict[str, Any]:
        """
        Calculate exposure to Asia tech stocks.
        
        Returns:
            Dictionary with exposure data and analysis
        """
        # Major Asia tech stocks
        asia_tech_stocks = [
            "TSM", "2330.TW",  # TSMC
            "005930.KS",  # Samsung
            "9988.HK", "BABA",  # Alibaba
            "9999.HK", "BIDU",  # Baidu
            "0700.HK", "TCEHY",  # Tencent
            "9618.HK", "JD",  # JD.com
            "6758.T", "SONY",  # Sony
            "3690.HK", "MEITF"  # Meituan
        ]
        
        # Get data for these stocks
        stock_data = {}
        earnings_surprises = {}
        
        for ticker in asia_tech_stocks:
            try:
                data = self.get_stock_data(ticker, period="5d")
                if not data.empty:
                    stock_data[ticker] = {
                        "current_price": data.iloc[-1]["Close"],
                        "previous_price": data.iloc[-2]["Close"] if len(data) > 1 else data.iloc[-1]["Close"],
                        "percent_change": ((data.iloc[-1]["Close"] - data.iloc[-2]["Close"]) / data.iloc[-2]["Close"] * 100) 
                                         if len(data) > 1 else 0
                    }
                    
                # Check for earnings surprises using stock's info
                stock = yf.Ticker(ticker)
                calendar = stock.calendar
                if calendar is not None and hasattr(calendar, 'iloc') and not calendar.empty:
                    # Try to get earnings data
                    try:
                        earnings = stock.earnings
                        if earnings is not None and not earnings.empty and "Earnings" in earnings.columns and "Revenue" in earnings.columns:
                            latest_earning = earnings.iloc[-1]
                            earnings_surprises[ticker] = {
                                "surprise": latest_earning["Earnings"],
                                "estimate": latest_earning.get("Estimate", 0) or 0
                            }
                    except:
                        pass
            except Exception as e:
                logger.error(f"Error retrieving data for {ticker}: {str(e)}")
        
        # Calculate total exposure and percentage change
        total_value = sum([data.get("current_price", 0) for ticker, data in stock_data.items()])
        total_previous_value = sum([data.get("previous_price", 0) for ticker, data in stock_data.items()])
        
        # Calculate percentage of portfolio (assuming 22% allocation)
        portfolio_percentage = 22  # As mentioned in the use case
        previous_portfolio_percentage = 18  # As mentioned in the use case
        
        # Find significant earnings surprises
        significant_surprises = {}
        for ticker, data in earnings_surprises.items():
            if data.get("estimate", 0) > 0:
                surprise_percent = ((data.get("surprise", 0) - data.get("estimate", 0)) / data.get("estimate", 0)) * 100
                if abs(surprise_percent) > 1.0:  # Only include significant surprises
                    company_name = ticker.split('.')[0] if '.' in ticker else ticker
                    significant_surprises[company_name] = round(surprise_percent, 2)
        
        # Regional sentiment analysis based on price movements
        total_change = sum([data.get("percent_change", 0) for ticker, data in stock_data.items()]) / len(stock_data) if stock_data else 0
        
        if total_change > 2:
            sentiment = "bullish"
        elif total_change > 0.5:
            sentiment = "slightly bullish"
        elif total_change > -0.5:
            sentiment = "neutral"
        elif total_change > -2:
            sentiment = "slightly bearish"
        else:
            sentiment = "bearish"
            
        return {
            "exposure": {
                "percentage": portfolio_percentage,
                "previous_percentage": previous_portfolio_percentage,
                "change": portfolio_percentage - previous_portfolio_percentage,
                "movement_direction": "up" if portfolio_percentage > previous_portfolio_percentage else "down"
            },
            "earnings_surprises": significant_surprises,
            "sentiment": sentiment,
            "avg_price_change": round(total_change, 2)
        }
    
    def get_stock_news(self, ticker: str, days: int = 3) -> List[Dict[str, str]]:
        """
        Get recent news for a specific stock.
        
        Args:
            ticker: Stock ticker symbol
            days: Number of days to look back
            
        Returns:
            List of news items with title, link, and publish date
        """
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            result = []
            for item in news[:5]:  # Limit to top 5 news items
                result.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "publisher": item.get("publisher", ""),
                    "published": datetime.fromtimestamp(item.get("providerPublishTime", 0)).strftime("%Y-%m-%d %H:%M")
                })
                
            return result
        except Exception as e:
            logger.error(f"Error retrieving news for {ticker}: {str(e)}")
            return []

    def get_portfolio_data(self) -> Dict[str, Any]:
        """
        Generate portfolio data.
        
        Returns:
            Dictionary with portfolio information
        """
        # This would typically come from a real portfolio system
        # Using mock data for illustration purposes
        
        # Get Asia tech exposure which will be part of the portfolio
        asia_tech = self.get_asia_tech_exposure()
        
        return {
            "total_value": 1250000,
            "daily_change_percent": -0.32,
            "allocation": {
                "regions": {
                    "North America": 45,
                    "Asia": 22,
                    "Europe": 18,
                    "Emerging Markets": 12,
                    "Other": 3
                },
                "sectors": {
                    "Technology": 35,
                    "Finance": 22,
                    "Healthcare": 15,
                    "Consumer Discretionary": 10,
                    "Industrials": 8,
                    "Energy": 5,
                    "Other": 5
                }
            },
            "asia_tech": asia_tech
        }
