"""
Analysis Service for the Finance Assistant.
Provides access to the analysis agent functionality.
"""

import os
import requests
import logging
from typing import Dict, List, Any, Optional
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class AnalysisService:
    """
    Service class for accessing analysis agent functionality.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the analysis service.
        
        Args:
            base_url: Base URL for the orchestrator service
        """
        self.base_url = base_url
    
    async def analyze_portfolio(self) -> Dict[str, Any]:
        """
        Analyze portfolio.
        
        Returns:
            Dictionary with portfolio analysis
        """
        try:
            # This would ideally call a specific endpoint for portfolio analysis
            # For now, we'll use the process endpoint with a specific query
            url = f"{self.base_url}/process"
            payload = {
                "query": "Analyze my current portfolio performance and risk metrics"
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract portfolio analysis if available
                if "data" in result:
                    return result
                else:
                    # Return the text response
                    return {"analysis": result.get("text", "")}
            else:
                logger.error(f"Error analyzing portfolio: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Error analyzing portfolio")
        except Exception as e:
            logger.error(f"Error connecting to analysis service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to analysis service: {str(e)}")
    
    async def analyze_risk_exposure(self, region: str, sector: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze risk exposure for a region and sector.
        
        Args:
            region: Geographic region
            sector: Optional sector
            
        Returns:
            Dictionary with risk analysis
        """
        try:
            # Craft query based on region and sector
            if sector:
                query = f"What is our risk exposure in {region} {sector} stocks today?"
            else:
                query = f"What is our risk exposure in {region} stocks today?"
                
            # Call process endpoint
            url = f"{self.base_url}/process"
            payload = {
                "query": query
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract risk analysis if available
                if "data" in result:
                    return result
                else:
                    # Return the text response
                    return {
                        "region": region,
                        "sector": sector,
                        "analysis": result.get("text", "")
                    }
            else:
                logger.error(f"Error analyzing risk exposure: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Error analyzing risk exposure")
        except Exception as e:
            logger.error(f"Error connecting to analysis service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to analysis service: {str(e)}")
    
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
            logger.error(f"Error connecting to analysis service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to analysis service: {str(e)}")
