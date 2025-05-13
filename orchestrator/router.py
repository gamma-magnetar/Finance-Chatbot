"""
Agent Router for the Finance Assistant.
Routes queries to the appropriate agents based on intent.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class AgentRouter:
    """
    Router that directs queries to the appropriate agents based on intent analysis.
    """
    
    def __init__(self, api_agent, scraping_agent, retriever_agent, analysis_agent, language_agent, voice_agent):
        """
        Initialize the agent router.
        
        Args:
            api_agent: API agent instance
            scraping_agent: Scraping agent instance
            retriever_agent: Retriever agent instance
            analysis_agent: Analysis agent instance
            language_agent: Language agent instance
            voice_agent: Voice agent instance
        """
        self.api_agent = api_agent
        self.scraping_agent = scraping_agent
        self.retriever_agent = retriever_agent
        self.analysis_agent = analysis_agent
        self.language_agent = language_agent
        self.voice_agent = voice_agent
        
        # Define confidence threshold for retrieval
        self.retrieval_confidence_threshold = 0.6
    
    def route_query(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route a query to the appropriate agents based on intent.
        
        Args:
            query: User query
            intent: Intent analysis from language agent
            
        Returns:
            Response dictionary
        """
        try:
            # Extract intent information
            primary_intent = intent.get("primary_intent", "unknown")
            entities = intent.get("entities", [])
            confidence = intent.get("confidence", 0.0)
            
            logger.info(f"Routing query with intent: {primary_intent}, confidence: {confidence}")
            
            # Handle different intents
            if primary_intent == "market_info":
                return self._handle_market_info(query, entities)
            elif primary_intent == "portfolio_analysis":
                return self._handle_portfolio_analysis(query, entities)
            elif primary_intent == "risk_assessment":
                return self._handle_risk_assessment(query, entities)
            elif primary_intent == "stock_specific":
                return self._handle_stock_specific(query, entities)
            elif primary_intent == "economic_data":
                return self._handle_economic_data(query, entities)
            else:
                # Default to retrieval-based response
                return self._fallback_retrieval(query, confidence)
                
        except Exception as e:
            logger.error(f"Error routing query: {str(e)}")
            
            # Fallback to simple language model response
            response = self.language_agent.generate_response(query)
            
            return {
                "text": response,
                "source": "language_agent",
                "error": str(e)
            }
    
    def _handle_market_info(self, query: str, entities: List[str]) -> Dict[str, Any]:
        """
        Handle market information queries.
        
        Args:
            query: User query
            entities: Entities from intent analysis
            
        Returns:
            Response dictionary
        """
        try:
            # Get relevant data based on entities
            data = {}
            
            # Check for indices
            if any(entity in ["indices", "index", "market"] for entity in entities):
                data["indices"] = self.api_agent.get_market_indices()
                
            # Check for sectors
            if any("""
Router for the Finance Assistant.
Routes queries to the appropriate agents based on intent.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

class AgentRouter:
    """
    Routes queries to appropriate agents based on the query intent.
    """
    
    def __init__(self, api_agent, scraping_agent, retriever_agent, analysis_agent, language_agent, voice_agent):
        """
        Initialize the agent router.
        
        Args:
            api_agent: API agent instance
            scraping_agent: Scraping agent instance
            retriever_agent: Retriever agent instance
            analysis_agent: Analysis agent instance
            language_agent: Language agent instance
            voice_agent: Voice agent instance
        """
        self.api_agent = api_agent
        self.scraping_agent = scraping_agent
        self.retriever_agent = retriever_agent
        self.analysis_agent = analysis_agent
        self.language_agent = language_agent
        self.voice_agent = voice_agent
    
    def route_query(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route a query to the appropriate agents based on intent.
        
        Args:
            query: User query
            intent: Query intent analysis
            
        Returns:
            Response dictionary
        """
        primary_intent = intent.get("primary_intent", "unknown")
        entities = intent.get("entities", [])
        
        logger.info(f"Routing query with primary intent: {primary_intent}")
        
        # Get relevant context from retriever agent
        context = self.retriever_agent.retrieve(query, k=5)
        
        # Process based on intent
        if primary_intent == "market_info":
            return self._handle_market_info(query, entities, context)
            
        elif primary_intent == "portfolio_analysis":
            return self._handle_portfolio_analysis(query, entities, context)
            
        elif primary_intent == "risk_assessment":
            return self._handle_risk_assessment(query, entities, context)
            
        elif primary_intent == "stock_specific":
            return self._handle_stock_specific(query, entities, context)
            
        elif primary_intent == "economic_data":
            return self._handle_economic_data(query, entities, context)
            
        else:
            # Default handling for unknown intents
            return self._handle_default(query, context)
    
    def _handle_market_info(self, query: str, entities: List[str], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Handle market information queries.
        
        Args:
            query: User query
            entities: Entities in the query
            context: Context from retriever
            
        Returns:
            Response dictionary
        """
        # Get market indices
        indices = self.api_agent.get_market_indices()
        
        # Get sector performance
        sectors = self.api_agent.get_sector_performance()
        
        # Add this data to the context
        context.append({
            "content": f"Current market indices: {json.dumps(indices, indent=2)}",
            "metadata": {"type": "market_indices"}
        })
        
        context.append({
            "content": f"Current sector performance: {json.dumps(sectors, indent=2)}",
            "metadata": {"type": "sector_performance"}
        })
        
        # Generate response using language agent
        text = self.language_agent.generate_response(query, context)
        
        return {
            "text": text,
            "data": {
                "indices": indices,
                "sectors": sectors
            }
        }
    
    def _handle_portfolio_analysis(self, query: str, entities: List[str], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Handle portfolio analysis queries.
        
        Args:
            query: User query
            entities: Entities in the query
            context: Context from retriever
            
        Returns:
            Response dictionary
        """
        # Get portfolio data
        portfolio = self.api_agent.get_portfolio_data()
        
        # Add to context
        context.append({
            "content": f"Portfolio data: {json.dumps(portfolio, indent=2)}",
            "metadata": {"type": "portfolio_data"}
        })
        
        # Generate response
        text = self.language_agent.generate_response(query, context)
        
        return {
            "text": text,
            "data": portfolio
        }
    
    def _handle_risk_assessment(self, query: str, entities: List[str], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Handle risk assessment queries.
        
        Args:
            query: User query
            entities: Entities in the query
            context: Context from retriever
            
        Returns:
            Response dictionary
        """
        # Extract region and sector from entities
        region = None
        sector = None
        
        for entity in entities:
            if entity.lower() in ["asia", "europe", "north america", "emerging markets"]:
                region = entity
            elif entity.lower() in ["technology", "finance", "healthcare", "consumer", "energy"]:
                sector = entity
        
        # Default to Asia/Technology if not specified
        if not region:
            region = "Asia"
        if not sector and "tech" in query.lower():
            sector = "Technology"
        
        # Get risk exposure
        exposure = self.analysis_agent.analyze_risk_exposure(self.api_agent, region, sector)
        
        # Add to context
        context.append({
            "content": f"Risk exposure for {region}/{sector if sector else 'all sectors'}: {json.dumps(exposure, indent=2)}",
            "metadata": {"type": "risk_exposure"}
        })
        
        # If the query is specifically about Asia tech stocks
        if "asia" in query.lower() and "tech" in query.lower():
            asia_tech = self.api_agent.get_asia_tech_exposure()
            context.append({
                "content": f"Asia tech exposure: {json.dumps(asia_tech, indent=2)}",
                "metadata": {"type": "asia_tech_exposure"}
            })
        
        # Generate response
        text = self.language_agent.generate_response(query, context)
        
        return {
            "text": text,
            "data": exposure
        }
    
    def _handle_stock_specific(self, query: str, entities: List[str], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Handle stock-specific queries.
        
        Args:
            query: User query
            entities: Entities in the query
            context: Context from retriever
            
        Returns:
            Response dictionary
        """
        # Extract stock tickers from entities
        tickers = []
        for entity in entities:
            # Simple heuristic for identifying tickers
            if entity.isupper() and len(entity) <= 5:
                tickers.append(entity)
        
        # If no tickers found, extract from common stocks mentioned in query
        common_stocks = {
            "apple": "AAPL",
            "microsoft": "MSFT",
            "google": "GOOGL",
            "amazon": "AMZN",
            "tesla": "TSLA",
            "facebook": "META",
            "nvidia": "NVDA",
            "tsmc": "TSM",
            "samsung": "005930.KS",
            "alibaba": "BABA",
            "tencent": "0700.HK"
        }
        
        query_lower = query.lower()
        for name, ticker in common_stocks.items():
            if name in query_lower and ticker not in tickers:
                tickers.append(ticker)
        
        # Get stock data for each ticker
        stock_data = {}
        for ticker in tickers:
            try:
                data = self.api_agent.get_stock_data(ticker)
                if not data.empty:
                    latest_price = data['Close'].iloc[-1]
                    prev_price = data['Close'].iloc[-2] if len(data) > 1 else data['Close'].iloc[-1]
                    pct_change = ((latest_price - prev_price) / prev_price) * 100
                    
                    stock_data[ticker] = {
                        "price": latest_price,
                        "change_percent": pct_change
                    }
                    
                    # Add to context
                    context.append({
                        "content": f"Stock data for {ticker}: Price=${latest_price:.2f}, Change={pct_change:.2f}%",
                        "metadata": {"type": "stock_data", "ticker": ticker}
                    })
                    
                # Get news for the ticker
                news = self.api_agent.get_stock_news(ticker)
                if news:
                    news_text = f"Recent news for {ticker}:\n"
                    for item in news[:3]:  # Limit to 3 news items
                        news_text += f"- {item['title']} ({item['published']})\n"
                    
                    context.append({
                        "content": news_text,
                        "metadata": {"type": "stock_news", "ticker": ticker}
                    })
            except Exception as e:
                logger.error(f"Error getting data for {ticker}: {str(e)}")
        
        # Generate response
        text = self.language_agent.generate_response(query, context)
        
        return {
            "text": text,
            "data": {
                "stocks": stock_data
            }
        }
    
    def _handle_economic_data(self, query: str, entities: List[str], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Handle economic data queries.
        
        Args:
            query: User query
            entities: Entities in the query
            context: Context from retriever
            
        Returns:
            Response dictionary
        """
        # Get economic indicators
        indicators = self.api_agent.get_economic_indicators()
        
        # Add to context
        context.append({
            "content": f"Economic indicators: {json.dumps(indicators, indent=2)}",
            "metadata": {"type": "economic_indicators"}
        })
        
        # Generate response
        text = self.language_agent.generate_response(query, context)
        
        return {
            "text": text,
            "data": {
                "indicators": indicators
            }
        }
    
    def _handle_default(self, query: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Handle default/unknown queries.
        
        Args:
            query: User query
            context: Context from retriever
            
        Returns:
            Response dictionary
        """
        # Use the retriever to get context, then generate response
        text = self.language_agent.generate_response(query, context)
        
        return {
            "text": text,
            "data": {}
        }
