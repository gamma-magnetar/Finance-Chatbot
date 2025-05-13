"""
API Service for the Finance Assistant.
Provides access to the API agent functionality.
"""

import os
import requests
import logging
from typing import Dict, List, Any, Optional
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class APIService:
    """
    Service class for accessing API agent functionality.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the API service.
        
        Args:
            base_url: Base URL for the orchestrator service
        """
        self.base_url = base_url
    
    async def get_market_indices(self) -> Dict[str, Any]:
        """
        Get current market indices.
        
        Returns:
            Dictionary with market indices
        """
        try:
            url = f"{self.base_url}/api/indices"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting market indices: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Error getting market indices")
        except Exception as e:
            logger.error(f"Error connecting to API service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to API service: {str(e)}")
    
    async def get_portfolio(self) -> Dict[str, Any]:
        """
        Get portfolio data.
        
        Returns:
            Dictionary with portfolio data
        """
        try:
            url = f"{self.base_url}/api/portfolio"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting portfolio data: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Error getting portfolio data")
        except Exception as e:
            logger.error(f"Error connecting to API service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to API service: {str(e)}")
    
    async def get_sector_performance(self) -> Dict[str, float]:
        """
        Get sector performance.
        
        Returns:
            Dictionary with sector performance
        """
        try:
            url = f"{self.base_url}/api/sectors"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting sector performance: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Error getting sector performance")
        except Exception as e:
            logger.error(f"Error connecting to API service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to API service: {str(e)}")
    
    async def get_asia_tech_exposure(self) -> Dict[str, Any]:
        """
        Get Asia tech exposure.
        
        Returns:
            Dictionary with Asia tech exposure
        """
        try:
            url = f"{self.base_url}/api/asia_tech"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting Asia tech exposure: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Error getting Asia tech exposure")
        except Exception as e:
            logger.error(f"Error connecting to API service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to API service: {str(e)}")
    
    async def get_morning_brief(self) -> Dict[str, Any]:
        """
        Get morning market brief.
        
        Returns:
            Dictionary with morning brief
        """
        try:
            url = f"{self.base_url}/morning_brief"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting morning brief: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Error getting morning brief")
        except Exception as e:
            logger.error(f"Error connecting to API service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to API service: {str(e)}")
