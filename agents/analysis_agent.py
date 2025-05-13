"""
Analysis Agent for the Finance Assistant.
Handles financial analysis, risk assessment, and metrics calculation.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AnalysisAgent:
    """
    Agent responsible for financial analysis and metrics calculation.
    """
    
    def __init__(self):
        """Initialize the analysis agent."""
        self.cache = {}
    
    def calculate_volatility(self, prices: pd.Series, window: int = 20) -> float:
        """
        Calculate volatility (standard deviation) of a price series.
        
        Args:
            prices: Series of prices
            window: Lookback window in days
            
        Returns:
            Volatility as decimal (e.g., 0.15 = 15%)
        """
        try:
            # Calculate daily returns
            returns = prices.pct_change().dropna()
            
            # Calculate rolling standard deviation
            if len(returns) < window:
                # Not enough data, use all available
                volatility = returns.std() * np.sqrt(252)  # Annualized
            else:
                # Use rolling window
                volatility = returns.iloc[-window:].std() * np.sqrt(252)  # Annualized
                
            return volatility
        except Exception as e:
            logger.error(f"Error calculating volatility: {str(e)}")
            return 0.0
    
    def calculate_beta(self, stock_prices: pd.Series, market_prices: pd.Series, window: int = 60) -> float:
        """
        Calculate beta of a stock relative to the market.
        
        Args:
            stock_prices: Series of stock prices
            market_prices: Series of market prices (e.g., S&P 500)
            window: Lookback window in days
            
        Returns:
            Beta value
        """
        try:
            # Calculate daily returns
            stock_returns = stock_prices.pct_change().dropna()
            market_returns = market_prices.pct_change().dropna()
            
            # Align the two series
            returns = pd.DataFrame({
                'stock': stock_returns,
                'market': market_returns
            }).dropna()
            
            # Use only the specified window
            if len(returns) > window:
                returns = returns.iloc[-window:]
                
            # Calculate covariance and variance
            covariance = returns.cov().iloc[0, 1]
            market_variance = returns['market'].var()
            
            # Calculate beta
            if market_variance == 0:
                return 1.0  # Default to market beta
                
            beta = covariance / market_variance
            
            return beta
        except Exception as e:
            logger.error(f"Error calculating beta: {str(e)}")
            return 1.0  # Default to market beta
    
    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.035, window: int = 252) -> float:
        """
        Calculate Sharpe ratio for a series of returns.
        
        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate
            window: Lookback window in days
            
        Returns:
            Sharpe ratio
        """
        try:
            # Use the specified window
            if len(returns) > window:
                returns = returns.iloc[-window:]
                
            # Calculate mean return and standard deviation
            mean_return = returns.mean() * 252  # Annualized
            std_dev = returns.std() * np.sqrt(252)  # Annualized
            
            # Calculate Sharpe ratio
            if std_dev == 0:
                return 0.0  # Avoid division by zero
                
            sharpe = (mean_return - risk_free_rate) / std_dev
            
            return sharpe
        except Exception as e:
            logger.error(f"Error calculating Sharpe ratio: {str(e)}")
            return 0.0
    
    def calculate_drawdown(self, prices: pd.Series) -> Dict[str, float]:
        """
        Calculate maximum drawdown for a price series.
        
        Args:
            prices: Series of prices
            
        Returns:
            Dictionary with maximum drawdown and duration
        """
        try:
            # Calculate running maximum
            running_max = prices.cummax()
            
            # Calculate drawdown
            drawdown = (prices / running_max - 1) * 100
            
            # Find maximum drawdown
            max_drawdown = drawdown.min()
            max_drawdown_idx = drawdown.idxmin()
            
            # Find the peak before the drawdown
            peak_idx = prices.iloc[:drawdown.idxmin()].idxmax()
            
            # Calculate duration in days
            if isinstance(peak_idx, pd.Timestamp) and isinstance(max_drawdown_idx, pd.Timestamp):
                duration = (max_drawdown_idx - peak_idx).days
            else:
                duration = 0
                
            return {
                'max_drawdown': max_drawdown,
                'duration': duration
            }
        except Exception as e:
            logger.error(f"Error calculating drawdown: {str(e)}")
            return {
                'max_drawdown': 0.0,
                'duration': 0
            }
    
    def calculate_var(self, returns: pd.Series, confidence: float = 0.95, window: int = 252) -> float:
        """
        Calculate Value at Risk (VaR) using historical method.
        
        Args:
            returns: Series of returns
            confidence: Confidence level (e.g., 0.95 for 95%)
            window: Lookback window in days
            
        Returns:
            VaR as a percentage of investment
        """
        try:
            # Use the specified window
            if len(returns) > window:
                returns = returns.iloc[-window:]
                
            # Calculate VaR
            var = returns.quantile(1 - confidence)
            
            return var * 100  # Convert to percentage
        except Exception as e:
            logger.error(f"Error calculating VaR: {str(e)}")
            return 0.0
    
    def analyze_portfolio(self, api_agent, portfolio_tickers: List[str], weights: List[float] = None) -> Dict[str, Any]:
        """
        Analyze a portfolio of stocks.
        
        Args:
            api_agent: API agent instance
            portfolio_tickers: List of stock tickers in the portfolio
            weights: Optional weights for each ticker (default: equal weighting)
            
        Returns:
            Dictionary with portfolio analysis
        """
        try:
            if weights is None:
                # Equal weighting
                weights = [1.0 / len(portfolio_tickers) for _ in portfolio_tickers]
                
            # Ensure weights sum to 1.0
            weights = [w / sum(weights) for w in weights]
            
            # Get market data (S&P 500 as benchmark)
            market_data = api_agent.get_stock_data("^GSPC", period="1y", interval="1d")
            
            # Get data for each stock
            stock_data = {}
            returns_data = {}
            portfolio_metrics = {
                'tickers': portfolio_tickers,
                'weights': weights,
                'individual_metrics': {},
                'portfolio_metrics': {}
            }
            
            for ticker in portfolio_tickers:
                try:
                    data = api_agent.get_stock_data(ticker, period="1y", interval="1d")
                    stock_data[ticker] = data
                    
                    # Calculate returns
                    returns = data['Close'].pct_change().dropna()
                    returns_data[ticker] = returns
                    
                    # Calculate individual metrics
                    volatility = self.calculate_volatility(data['Close'])
                    beta = self.calculate_beta(data['Close'], market_data['Close'])
                    sharpe = self.calculate_sharpe_ratio(returns)
                    drawdown = self.calculate_drawdown(data['Close'])
                    var = self.calculate_var(returns)
                    
                    portfolio_metrics['individual_metrics'][ticker] = {
                        'volatility': volatility * 100,  # Convert to percentage
                        'beta': beta,
                        'sharpe_ratio': sharpe,
                        'max_drawdown': drawdown['max_drawdown'],
                        'drawdown_duration': drawdown['duration'],
                        'var_95': var
                    }
                    
                except Exception as e:
                    logger.error(f"Error analyzing ticker {ticker}: {str(e)}")
                    portfolio_metrics['individual_metrics'][ticker] = {
                        'error': str(e)
                    }
            
            # Calculate portfolio returns
            portfolio_returns = pd.Series(0.0, index=next(iter(returns_data.values())).index)
            
            for ticker, weight in zip(portfolio_tickers, weights):
                if ticker in returns_data and returns_data[ticker] is not None:
                    # Align indices
                    portfolio_returns = portfolio_returns.add(returns_data[ticker] * weight, fill_value=0)
            
            # Calculate portfolio metrics
            portfolio_volatility = portfolio_returns.std() * np.sqrt(252)  # Annualized
            portfolio_sharpe = self.calculate_sharpe_ratio(portfolio_returns)
            portfolio_var = self.calculate_var(portfolio_returns)
            
            # Calculate correlation matrix
            returns_df = pd.DataFrame(returns_data)
            correlation_matrix = returns_df.corr().round(2)
            
            # Calculate portfolio beta
            portfolio_beta = 0.0
            for ticker, weight in zip(portfolio_tickers, weights):
                if ticker in portfolio_metrics['individual_metrics']:
                    portfolio_beta += portfolio_metrics['individual_metrics'][ticker].get('beta', 0) * weight
            
            # Calculate portfolio drawdown
            # Create portfolio value series
            portfolio_value = pd.Series(1.0, index=portfolio_returns.index)
            for i in range(1, len(portfolio_returns)):
                portfolio_value.iloc[i] = portfolio_value.iloc[i-1] * (1 + portfolio_returns.iloc[i])
            
            portfolio_drawdown = self.calculate_drawdown(portfolio_value)
            
            # Store portfolio-level metrics
            portfolio_metrics['portfolio_metrics'] = {
                'volatility': portfolio_volatility * 100,  # Convert to percentage
                'beta': portfolio_beta,
                'sharpe_ratio': portfolio_sharpe,
                'max_drawdown': portfolio_drawdown['max_drawdown'],
                'drawdown_duration': portfolio_drawdown['duration'],
                'var_95': portfolio_var,
                'correlation_matrix': correlation_matrix.to_dict()
            }
            
            return portfolio_metrics
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {str(e)}")
            return {
                'error': str(e)
            }
    
    def analyze_risk_exposure(self, api_agent, region: str, sector: str = None) -> Dict[str, Any]:
        """
        Analyze risk exposure for a specific region and sector.
        
        Args:
            api_agent: API agent instance
            region: Geographic region (e.g., 'Asia', 'Europe')
            sector: Optional sector (e.g., 'Technology', 'Finance')
            
        Returns:
            Dictionary with risk analysis
        """
        try:
            # Define stocks for the region
            region_mapping = {
                'Asia': {
                    'Technology': ['TSM', '005930.KS', '9988.HK', '0700.HK', '6758.T'],  # TSMC, Samsung, Alibaba, Tencent, Sony
                    'Finance': ['8306.T', '8316.T', '3988.HK', '1398.HK', '000001.SS'],  # Mitsubishi UFJ, Sumitomo Mitsui, BOC, ICBC, PINS
                    'Consumer': ['9633.T', '6758.T', '2330.TW', '1177.HK', '1211.HK'],  # Nintendo, Sony, LG, Chow Tai Fook, BYD
                    'Healthcare': ['4502.T', '4503.T', '1177.HK', '3320.HK', '1093.HK'],  # Takeda, Astellas, Sino Biopharm, China Bio, CSPC
                },
                'Europe': {
                    'Technology': ['ASML.AS', 'SAP.DE', 'CAP.PA', 'STM.PA', 'ERIC-B.ST'],  # ASML, SAP, Capgemini, STMicro, Ericsson
                    'Finance': ['HSBA.L', 'BNP.PA', 'SAN.MC', 'BBVA.MC', 'DBK.DE'],  # HSBC, BNP Paribas, Santander, BBVA, Deutsche Bank
                    'Consumer': ['MC.PA', 'OR.PA', 'NESN.SW', 'UL.AS', 'AIR.PA'],  # LVMH, L'Oreal, Nestle, Unilever, Airbus
                    'Healthcare': ['ROG.SW', 'SAN.PA', 'NOVN.SW', 'AZN.L', 'GSK.L'],  # Roche, Sanofi, Novartis, AstraZeneca, GSK
                },
                'North America': {
                    'Technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'],  # Apple, Microsoft, Alphabet, Amazon, Meta
                    'Finance': ['JPM', 'BAC', 'WFC', 'C', 'GS'],  # JPMorgan, Bank of America, Wells Fargo, Citigroup, Goldman Sachs
                    'Consumer': ['COST', 'WMT', 'HD', 'NKE', 'MCD'],  # Costco, Walmart, Home Depot, Nike, McDonald's
                    'Healthcare': ['JNJ', 'PFE', 'MRK', 'ABT', 'UNH'],  # Johnson & Johnson, Pfizer, Merck, Abbott, UnitedHealth
                }
            }
            
            # Get tickers for the region and sector
            if region not in region_mapping:
                return {'error': f"Region '{region}' not supported"}
                
            if sector and sector not in region_mapping[region]:
                return {'error': f"Sector '{sector}' not supported for region '{region}'"}
                
            if sector:
                tickers = region_mapping[region][sector]
            else:
                # Combine all sectors for the region
                tickers = []
                for sector_tickers in region_mapping[region].values():
                    tickers.extend(sector_tickers)
            
            # Get data for each ticker
            stock_data = {}
            for ticker in tickers:
                try:
                    data = api_agent.get_stock_data(ticker, period="1mo", interval="1d")
                    stock_data[ticker] = data
                except Exception as e:
                    logger.error(f"Error getting data for {ticker}: {str(e)}")
            
            # Calculate metrics
            exposure_metrics = {
                'region': region,
                'sector': sector,
                'tickers': tickers,
                'metrics': {}
            }
            
            # Calculate average metrics
            volatilities = []
            betas = []
            variances = []
            
            # Get market data
            market_data = api_agent.get_stock_data("^GSPC", period="1mo", interval="1d")
            
            for ticker, data in stock_data.items():
                if data is not None and not data.empty:
                    try:
                        # Calculate returns
                        returns = data['Close'].pct_change().dropna()
                        
                        # Calculate metrics
                        volatility = self.calculate_volatility(data['Close'])
                        beta = self.calculate_beta(data['Close'], market_data['Close'])
                        var = self.calculate_var(returns)
                        
                        # Store metrics
                        exposure_metrics['metrics'][ticker] = {
                            'volatility': volatility * 100,  # Convert to percentage
                            'beta': beta,
                            'var_95': var
                        }
                        
                        volatilities.append(volatility * 100)
                        betas.append(beta)
                        variances.append(var)
                        
                    except Exception as e:
                        logger.error(f"Error calculating metrics for {ticker}: {str(e)}")
            
            # Calculate average metrics
            exposure_metrics['average_metrics'] = {
                'volatility': np.mean(volatilities) if volatilities else 0,
                'beta': np.mean(betas) if betas else 0,
                'var_95': np.mean(variances) if variances else 0
            }
            
            # Determine risk level
            avg_volatility = exposure_metrics['average_metrics']['volatility']
            if avg_volatility > 30:
                risk_level = "Very High"
            elif avg_volatility > 20:
                risk_level = "High"
            elif avg_volatility > 15:
                risk_level = "Moderate to High"
            elif avg_volatility > 10:
                risk_level = "Moderate"
            else:
                risk_level = "Low"
                
            exposure_metrics['risk_level'] = risk_level
            
            # Get recent earnings surprises from api_agent
            earnings_surprises = {}
            asia_tech_exposure = api_agent.get_asia_tech_exposure()
            if 'earnings_surprises' in asia_tech_exposure:
                earnings_surprises = asia_tech_exposure['earnings_surprises']
            
            exposure_metrics['earnings_surprises'] = earnings_surprises
            
            # Get market sentiment if Asia region
            if region == 'Asia':
                exposure_metrics['sentiment'] = asia_tech_exposure.get('sentiment', 'neutral')
            
            return exposure_metrics
            
        except Exception as e:
            logger.error(f"Error analyzing risk exposure: {str(e)}")
            return {
                'error': str(e)
            }
    
    def generate_morning_brief(self, api_agent, region: str = 'Asia', sector: str = 'Technology') -> Dict[str, Any]:
        """
        Generate a comprehensive morning market brief.
        
        Args:
            api_agent: API agent instance
            region: Region to focus on
            sector: Sector to focus on
            
        Returns:
            Dictionary with morning brief data
        """
        try:
            # Get market indices
            indices = api_agent.get_market_indices()
            
            # Get specific region/sector exposure
            exposure = self.analyze_risk_exposure(api_agent, region, sector)
            
            # Get economic indicators
            indicators = api_agent.get_economic_indicators()
            
            # Get Asia tech exposure (contains earnings surprises)
            asia_tech = api_agent.get_asia_tech_exposure()
            
            # Compile morning brief
            brief = {
                'date': datetime.now().strftime("%Y-%m-%d"),
                'indices': indices,
                'economic_indicators': indicators,
                'region_exposure': exposure,
                'asia_tech': asia_tech
            }
            
            return brief
            
        except Exception as e:
            logger.error(f"Error generating morning brief: {str(e)}")
            return {
                'error': str(e),
                'date': datetime.now().strftime("%Y-%m-%d")
            }
