"""
Language Service for the Finance Assistant.
Provides access to the language agent functionality.
"""

import os
import requests
import logging
import json
from typing import Dict, List, Any, Optional
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class LanguageService:
    """
    Service class for accessing language agent functionality.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the language service.
        
        Args:
            base_url: Base URL for the orchestrator service
        """
        self.base_url = base_url
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query.
        
        Args:
            query: User query
            
        Returns:
            Dictionary with processed response
        """
        try:
            # Call process endpoint
            url = f"{self.base_url}/process"
            payload = {
                "query": query
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error processing query: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Error processing query")
        except Exception as e:
            logger.error(f"Error connecting to language service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to language service: {str(e)}")
    
    async def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Analyze the intent of a user query.
        
        Args:
            query: User query
            
        Returns:
            Dictionary with query intent analysis
        """
        try:
            # This would ideally call a specific endpoint for intent analysis
            # For demonstration, we'll return a simplified intent analysis
            
            # Simple keywords to intents mapping
            intents = {
                "portfolio": "portfolio_analysis",
                "risk": "risk_assessment",
                "exposure": "risk_assessment",
                "market": "market_info",
                "indices": "market_info",
                "sector": "market_info",
                "stock": "stock_specific",
                "price": "stock_specific",
                "economic": "economic_data",
                "treasury": "economic_data",
                "yield": "economic_data",
                "earnings": "stock_specific"
            }
            
            # Simple keywords to entities mapping
            entities = {
                "asia": "Asia",
                "europe": "Europe",
                "america": "North America",
                "tech": "Technology",
                "technology": "Technology",
                "financial": "Finance",
                "finance": "Finance",
                "healthcare": "Healthcare",
                "consumer": "Consumer",
                "energy": "Energy"
            }
            
            # Determine primary intent
            query_lower = query.lower()
            primary_intent = "unknown"
            max_count = 0
            
            for keyword, intent in intents.items():
                if keyword in query_lower:
                    count = query_lower.count(keyword)
                    if count > max_count:
                        max_count = count
                        primary_intent = intent
            
            # Extract entities
            found_entities = []
            for keyword, entity in entities.items():
                if keyword in query_lower and entity not in found_entities:
                    found_entities.append(entity)
            
            # Add any stock tickers (simple heuristic: uppercase 1-5 letters)
            for word in query.split():
                if word.isupper() and 1 <= len(word) <= 5 and word not in found_entities:
                    found_entities.append(word)
            
            # Determine timeframe
            timeframe = "current"
            if "today" in query_lower:
                timeframe = "today"
            elif "week" in query_lower:
                timeframe = "week"
            elif "month" in query_lower:
                timeframe = "month"
            elif "year" in query_lower:
                timeframe = "year"
            
            # Determine if numeric data is required
            requires_numeric_data = any(keyword in query_lower for keyword in ["price", "percent", "change", "value", "number", "amount", "how much", "how many"])
            
            # Return intent analysis
            return {
                "primary_intent": primary_intent,
                "entities": found_entities,
                "timeframe": timeframe,
                "requires_numeric_data": requires_numeric_data,
                "confidence": 0.8  # Fixed confidence for this simplified implementation
            }
            
        except Exception as e:
            logger.error(f"Error analyzing query intent: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error analyzing query intent: {str(e)}")
    
    async def summarize_document(self, document: str) -> str:
        """
        Summarize a financial document.
        
        Args:
            document: Document text
            
        Returns:
            Summarized document
        """
        try:
            # This would ideally call a specific endpoint for document summarization
            # For demonstration, we'll use the process endpoint with a specific query
            url = f"{self.base_url}/process"
            
            # Limit document length for the request
            if len(document) > 5000:
                document_preview = document[:5000] + "... [truncated]"
            else:
                document_preview = document
                
            payload = {
                "query": f"Summarize the following financial document: {document_preview}"
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("text", "")
            else:
                logger.error(f"Error summarizing document: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Error summarizing document")
        except Exception as e:
            logger.error(f"Error connecting to language service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to language service: {str(e)}")
