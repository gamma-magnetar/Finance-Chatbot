"""
Retriever Service for the Finance Assistant.
Provides access to the retriever agent functionality.
"""

import os
import requests
import logging
from typing import Dict, List, Any, Optional
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class RetrieverService:
    """
    Service class for accessing retriever agent functionality.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the retriever service.
        
        Args:
            base_url: Base URL for the orchestrator service
        """
        self.base_url = base_url
    
    async def retrieve_for_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Retrieve relevant information for a query.
        
        Args:
            query: User query
            
        Returns:
            List of retrieved documents
        """
        try:
            # This would ideally call a specific endpoint for retrieval
            # For now, we'll use the process endpoint and extract relevant information
            url = f"{self.base_url}/process"
            payload = {
                "query": query
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract retrieved documents if available
                if "data" in result and "retrieved_documents" in result["data"]:
                    return result["data"]["retrieved_documents"]
                else:
                    # No explicit retrieval, return empty list
                    return []
            else:
                logger.error(f"Error retrieving information: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Error retrieving information")
        except Exception as e:
            logger.error(f"Error connecting to retriever service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to retriever service: {str(e)}")
    
    async def retrieve_by_topic(self, topic: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieve information for a specific topic.
        
        Args:
            topic: Topic to retrieve information for
            
        Returns:
            Dictionary with retrieved information for the topic
        """
        try:
            # This would ideally call a specific endpoint for topic retrieval
            # For now, we'll use the process endpoint with a specific query
            url = f"{self.base_url}/process"
            payload = {
                "query": f"Tell me about {topic}"
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract retrieved documents if available
                if "data" in result:
                    return {"topic": topic, "result": result}
                else:
                    # No data, return text response
                    return {"topic": topic, "text": result.get("text", "")}
            else:
                logger.error(f"Error retrieving topic information: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Error retrieving topic information")
        except Exception as e:
            logger.error(f"Error connecting to retriever service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to retriever service: {str(e)}")
    
    async def get_document_by_id(self, doc_id: str) -> Dict[str, Any]:
        """
        Get a specific document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document content and metadata
        """
        try:
            # This would ideally call a specific endpoint for document retrieval
            # For demonstration, we'll return a dummy response since this API doesn't exist yet
            logger.warning("Document retrieval by ID not implemented in the backend")
            
            return {
                "content": "Document content not available",
                "metadata": {"id": doc_id, "type": "unknown"}
            }
        except Exception as e:
            logger.error(f"Error retrieving document: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")
