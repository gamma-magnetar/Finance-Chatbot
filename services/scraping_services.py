"""
Scraping Service for the Finance Assistant.
Provides access to the scraping agent functionality.
"""

import os
import requests
import logging
from typing import Dict, List, Any, Optional
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class ScrapingService:
    """
    Service class for accessing scraping agent functionality.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the scraping service.
        
        Args:
            base_url: Base URL for the orchestrator service
        """
        self.base_url = base_url
    
    async def get_financial_news(self) -> List[Dict[str, Any]]:
        """
        Get financial news.
        
        Returns:
            List of news articles
        """
        try:
            # This would ideally call a specific endpoint for financial news
            # For now, we'll use the process endpoint with a specific query
            url = f"{self.base_url}/process"
            payload = {
                "query": "What are the latest financial news headlines?"
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract news from the response if available
                if "data" in result and "news" in result["data"]:
                    return result["data"]["news"]
                else:
                    # Return the text response
                    return [{"title": "Financial News", "content": result.get("text", "")}]
            else:
                logger.error(f"Error getting financial news: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Error getting financial news")
        except Exception as e:
            logger.error(f"Error connecting to scraping service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to scraping service: {str(e)}")
    
    async def get_earnings_calendar(self) -> List[Dict[str, Any]]:
        """
        Get earnings calendar.
        
        Returns:
            List of upcoming earnings reports
        """
        try:
            # This would ideally call a specific endpoint for earnings calendar
            # For now, we'll use the process endpoint with a specific query
            url = f"{self.base_url}/process"
            payload = {
                "query": "What are the upcoming earnings reports this week?"
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract earnings from the response if available
                if "data" in result and "earnings" in result["data"]:
                    return result["data"]["earnings"]
                else:
                    # Return the text response
                    return [{"title": "Earnings Calendar", "content": result.get("text", "")}]
            else:
                logger.error(f"Error getting earnings calendar: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Error getting earnings calendar")
        except Exception as e:
            logger.error(f"Error connecting to scraping service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to scraping service: {str(e)}")
    
    async def get_market_sentiment(self, keyword: str) -> Dict[str, Any]:
        """
        Get market sentiment for a keyword.
        
        Args:
            keyword: Keyword to analyze sentiment for
            
        Returns:
            Dictionary with sentiment analysis
        """
        try:
            # This would ideally call a specific endpoint for market sentiment
            # For now, we'll use the process endpoint with a specific query
            url = f"{self.base_url}/process"
            payload = {
                "query": f"What is the current market sentiment for {keyword}?"
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract sentiment from the response if available
                if "data" in result and "sentiment" in result["data"]:
                    return result["data"]["sentiment"]
                else:
                    # Return the text response
                    return {"keyword": keyword, "sentiment": result.get("text", "")}
            else:
                logger.error(f"Error getting market sentiment: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Error getting market sentiment")
        except Exception as e:
            logger.error(f"Error connecting to scraping service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to scraping service: {str(e)}")
