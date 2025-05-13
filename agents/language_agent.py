"""
Language Agent for the Finance Assistant.
Handles natural language processing and generation using LLMs.
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional
import time
from openai import OpenAI

logger = logging.getLogger(__name__)

class LanguageAgent:
    """
    Agent responsible for natural language processing and generation.
    Uses OpenAI API for language tasks.
    """
    
    def __init__(self):
        """Initialize the language agent."""
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
        self.max_tokens = 2000
        self.temperature = 0.3
        self.cache = {}
    
    def generate_response(self, query: str, context: List[Dict[str, Any]] = None) -> str:
        """
        Generate a natural language response to a query.
        
        Args:
            query: User query
            context: Optional context from retriever
            
        Returns:
            Generated response
        """
        try:
            # Prepare context
            context_text = ""
            if context:
                context_text = "Context information:\n"
                for i, item in enumerate(context):
                    context_text += f"[{i+1}] {item['content']}\n\n"
            
            # Prepare system message
            system_message = """You are a professional financial advisor who specializes in market analysis. 
            When responding to queries, use the provided context to give accurate and detailed information.
            Always maintain a formal, professional tone. For financial data, provide specific numbers and percentages.
            If answering questions about risk or investment advice, emphasize that these are analyses, not recommendations.
            Format currency values with appropriate symbols and use two decimal places for percentages.
            Keep responses concise, factual, and focused on the query."""
            
            # Prepare messages
            messages = [
                {"role": "system", "content": system_message},
            ]
            
            if context_text:
                messages.append({"role": "user", "content": f"{context_text}\n\nBased on this context, please answer: {query}"})
            else:
                messages.append({"role": "user", "content": query})
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I apologize, but I encountered an error processing your request. Please try again later. Error: {str(e)}"
    
    def generate_morning_brief(self, brief_data: Dict[str, Any]) -> str:
        """
        Generate a morning market brief narrative.
        
        Args:
            brief_data: Data for the morning brief
            
        Returns:
            Generated brief narrative
        """
        try:
            # Extract key data
            date = brief_data.get('date', 'today')
            
            # Extract indices data
            indices_text = ""
            indices = brief_data.get('indices', {})
            for name, data in indices.items():
                price = data.get('price', 0)
                change = data.get('change_percent', 0)
                direction = "up" if change > 0 else "down"
                indices_text += f"The {name} is at {price:.2f}, {direction} {abs(change):.2f}%. "
            
            # Extract asia tech exposure
            asia_tech = brief_data.get('asia_tech', {})
            exposure = asia_tech.get('exposure', {})
            exposure_percentage = exposure.get('percentage', 0)
            previous_percentage = exposure.get('previous_percentage', 0)
            exposure_change = exposure.get('change', 0)
            exposure_direction = exposure.get('movement_direction', 'unchanged')
            
            # Extract earnings surprises
            surprises_text = ""
            earnings_surprises = asia_tech.get('earnings_surprises', {})
            for company, surprise in earnings_surprises.items():
                direction = "beat" if surprise > 0 else "missed"
                surprises_text += f"{company} {direction} estimates by {abs(surprise):.1f}%. "
            
            if not surprises_text:
                surprises_text = "No significant earnings surprises to report. "
                
            # Extract sentiment
            sentiment = asia_tech.get('sentiment', 'neutral')
            
            # Extract region exposure
            region_exposure = brief_data.get('region_exposure', {})
            risk_level = region_exposure.get('risk_level', 'moderate')
            
            # Prepare system message
            system_message = """You are a professional financial advisor delivering a morning market brief. 
            Your briefing should sound like a professional financial analyst summarizing key market information.
            Focus on being concise, informative, and insightful. Use a formal, authoritative tone.
            Explain what the data means for the client in practical terms."""
            
            # Prepare prompt
            prompt = f"""Generate a brief morning market update based on the following data:

Date: {date}

Market Indices:
{indices_text}

Asia Tech Exposure:
- Current allocation: {exposure_percentage}% of AUM
- Previous allocation: {previous_percentage}% of AUM
- Change: {exposure_direction} {abs(exposure_change)}%

Earnings Surprises:
{surprises_text}

Market Sentiment:
- Regional sentiment: {sentiment}

Risk Assessment:
- Risk level: {risk_level}

Please create a concise, professional morning brief that a financial advisor would deliver to a client. 
Focus specifically on the Asia tech stock exposure and any earnings surprises. Mention the change in allocation.
The brief should be about 3-4 sentences, direct and informative."""

            # Call OpenAI API
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating morning brief: {str(e)}")
            return f"I apologize, but I couldn't generate the morning brief due to an error. Please try again later. Error: {str(e)}"
    
    def summarize_financial_document(self, document: str, max_length: int = 500) -> str:
        """
        Summarize a financial document or filing.
        
        Args:
            document: Document text to summarize
            max_length: Maximum length of summary in characters
            
        Returns:
            Document summary
        """
        try:
            # Prepare system message
            system_message = """You are a financial analyst tasked with summarizing complex financial documents.
            Create a concise, fact-based summary that captures the most important information.
            Focus on key financial metrics, risk factors, and material changes or events.
            Use a professional, neutral tone and avoid any subjective judgments or recommendations."""
            
            # Limit document length to avoid token limits
            if len(document) > 15000:
                document = document[:15000] + "... [document truncated]"
            
            # Prepare prompt
            prompt = f"""Please summarize the following financial document in a concise way (no more than {max_length} characters).
            Focus on the key points, important financial data, and any significant information an investor should know.

            Document:
            {document}"""
            
            # Call OpenAI API
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error summarizing document: {str(e)}")
            return f"Error summarizing document: {str(e)}"
    
    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Analyze the intent of a user query to determine required information.
        
        Args:
            query: User query
            
        Returns:
            Dictionary with query intent analysis
        """
        try:
            # Prepare system message
            system_message = """You are a financial assistant that analyzes user queries to determine their intent.
            Respond with a JSON object containing the following fields:
            - primary_intent: The main category of the query (market_info, portfolio_analysis, risk_assessment, stock_specific, economic_data)
            - entities: Any specific entities mentioned (e.g., company names, indices, regions, sectors)
            - timeframe: The relevant timeframe for the query (e.g., today, week, month, year)
            - requires_numeric_data: Boolean indicating if the query needs specific numeric data
            - confidence: Your confidence in this analysis (0-1)"""
            
            # Prepare messages
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Analyze the intent of this query: {query}"}
            ]
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Parse JSON response
            intent_analysis = json.loads(response.choices[0].message.content)
            
            return intent_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing query intent: {str(e)}")
            return {
                "primary_intent": "unknown",
                "entities": [],
                "timeframe": "current",
                "requires_numeric_data": True,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def extract_key_points(self, text: str, max_points: int = 5) -> List[str]:
        """
        Extract key points from a longer text.
        
        Args:
            text: Text to analyze
            max_points: Maximum number of key points to extract
            
        Returns:
            List of key points
        """
        try:
            # Prepare system message
            system_message = """You are a financial analyst tasked with extracting the most important points from financial text.
            Identify the key facts, figures, and insights that would be most relevant to an investor.
            Focus on concrete data points, trends, and significant information.
            Provide each key point as a separate item in a list."""
            
            # Limit text length to avoid token limits
            if len(text) > 8000:
                text = text[:8000] + "... [text truncated]"
            
            # Prepare prompt
            prompt = f"""Extract the {max_points} most important key points from the following text.
            Each point should be concise, informative, and focused on financial information.
            Format each point as a separate item in a JSON array.

            Text:
            {text}"""
            
            # Call OpenAI API
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Parse JSON response
            result = json.loads(response.choices[0].message.content)
            
            # Extract key points from the response
            key_points = result.get("key_points", [])
            if not key_points and isinstance(result, list):
                key_points = result
                
            # Limit to requested number of points
            return key_points[:max_points]
            
        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            return [f"Error extracting key points: {str(e)}"]
