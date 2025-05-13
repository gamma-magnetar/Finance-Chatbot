"""
Scraping Agent for the Finance Assistant.
Handles crawling financial filings and news from various sources.
"""

import requests
import logging
import trafilatura
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import random
import os

logger = logging.getLogger(__name__)

class ScrapingAgent:
    """
    Agent responsible for scraping financial data from various sources.
    """
    
    def __init__(self):
        """Initialize the scraping agent."""
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = 3600  # 1 hour in seconds
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_sec_filings(self, ticker: str, filing_type: str = "10-K") -> List[Dict[str, Any]]:
        """
        Get SEC filings for a company.
        
        Args:
            ticker: Stock ticker symbol
            filing_type: SEC filing type (10-K, 10-Q, 8-K, etc.)
            
        Returns:
            List of filing information
        """
        cache_key = f"filings_{ticker}_{filing_type}"
        
        # Check cache
        if cache_key in self.cache and self.cache_expiry.get(cache_key, 0) > datetime.now().timestamp():
            logger.info(f"Using cached data for {cache_key}")
            return self.cache[cache_key]
        
        try:
            # Using SEC EDGAR API
            base_url = "https://data.sec.gov/submissions/CIK"
            
            # Generate CIK with leading zeros
            resp = requests.get(f"https://www.sec.gov/include/ticker.txt")
            ticker_to_cik = {}
            for line in resp.text.split('\n'):
                if ':' in line:
                    ticker_part, cik_part = line.strip().split(':')
                    ticker_to_cik[ticker_part.upper()] = cik_part.strip()
            
            cik = ticker_to_cik.get(ticker.upper())
            if not cik:
                logger.error(f"CIK not found for ticker {ticker}")
                return []
            
            # Format CIK with leading zeros
            cik_formatted = cik.zfill(10)
            
            # Get company submissions
            url = f"{base_url}{cik_formatted}.json"
            logger.info(f"Fetching SEC data from {url}")
            
            # Use cached headers with appropriate user agent
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                logger.error(f"Failed to fetch SEC data: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            
            # Find relevant filings
            filings = []
            for idx, form in enumerate(data.get('filings', {}).get('recent', {}).get('form', [])):
                if form == filing_type:
                    filing_date = data['filings']['recent']['filingDate'][idx]
                    accession_number = data['filings']['recent']['accessionNumber'][idx]
                    
                    filings.append({
                        'form': form,
                        'filing_date': filing_date,
                        'accession_number': accession_number,
                        'link': f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number.replace('-', '')}/{accession_number}.txt"
                    })
            
            # Cache results
            self.cache[cache_key] = filings
            self.cache_expiry[cache_key] = datetime.now().timestamp() + self.cache_duration
            
            return filings
            
        except Exception as e:
            logger.error(f"Error retrieving SEC filings for {ticker}: {str(e)}")
            return []
    
    def get_filing_content(self, filing_url: str) -> str:
        """
        Get the content of a specific SEC filing.
        
        Args:
            filing_url: URL to the filing
            
        Returns:
            Text content of the filing
        """
        cache_key = f"filing_content_{filing_url}"
        
        # Check cache
        if cache_key in self.cache and self.cache_expiry.get(cache_key, 0) > datetime.now().timestamp():
            logger.info(f"Using cached filing content")
            return self.cache[cache_key]
        
        try:
            # Download the file content
            response = requests.get(filing_url, headers=self.headers)
            if response.status_code != 200:
                logger.error(f"Failed to download filing: {response.status_code}")
                return ""
            
            # Extract the text content
            html_content = response.text
            
            # Use trafilatura to extract clean text
            text = trafilatura.extract(html_content)
            
            if not text:
                # Fallback to BeautifulSoup if trafilatura fails
                soup = BeautifulSoup(html_content, 'html.parser')
                text = soup.get_text()
            
            # Cache result
            self.cache[cache_key] = text
            self.cache_expiry[cache_key] = datetime.now().timestamp() + self.cache_duration
            
            return text
            
        except Exception as e:
            logger.error(f"Error retrieving filing content from {filing_url}: {str(e)}")
            return ""
    
    def get_financial_news(self, sources: List[str] = None) -> List[Dict[str, Any]]:
        """
        Scrape financial news from various sources.
        
        Args:
            sources: List of news sources to scrape
            
        Returns:
            List of news items with source, title, summary, and URL
        """
        if sources is None:
            sources = ["yahoo_finance", "cnbc", "bloomberg"]
        
        cache_key = f"financial_news_{'-'.join(sources)}"
        
        # Check cache
        if cache_key in self.cache and self.cache_expiry.get(cache_key, 0) > datetime.now().timestamp():
            logger.info(f"Using cached news data")
            return self.cache[cache_key]
        
        news_items = []
        
        try:
            if "yahoo_finance" in sources:
                # Scrape Yahoo Finance
                url = "https://finance.yahoo.com/news/"
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    articles = soup.find_all('h3')
                    
                    for article in articles[:10]:  # Limit to 10 articles
                        link_tag = article.find('a')
                        if link_tag and link_tag.has_attr('href'):
                            href = link_tag['href']
                            if href.startswith('/'):
                                href = f"https://finance.yahoo.com{href}"
                            
                            news_items.append({
                                'source': 'Yahoo Finance',
                                'title': article.text.strip(),
                                'url': href,
                                'published': datetime.now().strftime("%Y-%m-%d")  # Actual date would be scraped
                            })
                            
            if "cnbc" in sources:
                # Scrape CNBC
                url = "https://www.cnbc.com/markets/"
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    articles = soup.find_all('div', class_='Card-titleContainer')
                    
                    for article in articles[:10]:  # Limit to 10 articles
                        title_tag = article.find('a')
                        if title_tag:
                            title = title_tag.text.strip()
                            href = title_tag.get('href', '')
                            
                            news_items.append({
                                'source': 'CNBC',
                                'title': title,
                                'url': href,
                                'published': datetime.now().strftime("%Y-%m-%d")
                            })
                            
            if "bloomberg" in sources:
                # Scrape Bloomberg
                url = "https://www.bloomberg.com/markets"
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    articles = soup.find_all('h3', class_='story-package-module__headline')
                    
                    for article in articles[:10]:  # Limit to 10 articles
                        link_tag = article.find('a')
                        if link_tag:
                            title = link_tag.text.strip()
                            href = link_tag.get('href', '')
                            if not href.startswith('http'):
                                href = f"https://www.bloomberg.com{href}"
                            
                            news_items.append({
                                'source': 'Bloomberg',
                                'title': title,
                                'url': href,
                                'published': datetime.now().strftime("%Y-%m-%d")
                            })
            
            # Cache results
            self.cache[cache_key] = news_items
            self.cache_expiry[cache_key] = datetime.now().timestamp() + self.cache_duration
            
            return news_items
            
        except Exception as e:
            logger.error(f"Error scraping financial news: {str(e)}")
            return []
    
    def get_earnings_calendar(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Scrape upcoming earnings reports.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of upcoming earnings reports
        """
        cache_key = f"earnings_calendar_{days}"
        
        # Check cache
        if cache_key in self.cache and self.cache_expiry.get(cache_key, 0) > datetime.now().timestamp():
            logger.info(f"Using cached earnings calendar")
            return self.cache[cache_key]
        
        try:
            # Yahoo Finance earnings calendar
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days)
            
            # Format dates for Yahoo Finance URL
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
            
            url = f"https://finance.yahoo.com/calendar/earnings?from={start_str}&to={end_str}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to get earnings calendar: {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table')
            
            if not table:
                logger.error("No earnings table found")
                return []
                
            rows = table.find_all('tr')[1:]  # Skip header row
            
            earnings = []
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 6:
                    symbol = cells[0].text.strip()
                    company = cells[1].text.strip()
                    earnings_date = cells[2].text.strip()
                    eps_estimate = cells[3].text.strip()
                    
                    earnings.append({
                        'symbol': symbol,
                        'company': company,
                        'date': earnings_date,
                        'eps_estimate': eps_estimate
                    })
            
            # Cache results
            self.cache[cache_key] = earnings
            self.cache_expiry[cache_key] = datetime.now().timestamp() + self.cache_duration
            
            return earnings
            
        except Exception as e:
            logger.error(f"Error retrieving earnings calendar: {str(e)}")
            return []
    
    def get_market_sentiment(self, keyword: str = "market") -> Dict[str, Any]:
        """
        Analyze market sentiment for a keyword by scraping news headlines.
        
        Args:
            keyword: Keyword to analyze sentiment for
            
        Returns:
            Dictionary with sentiment analysis
        """
        cache_key = f"sentiment_{keyword}"
        
        # Check cache
        if cache_key in self.cache and self.cache_expiry.get(cache_key, 0) > datetime.now().timestamp():
            logger.info(f"Using cached sentiment data for {keyword}")
            return self.cache[cache_key]
        
        try:
            # Get news from multiple sources
            news = self.get_financial_news()
            
            # Filter for relevant news
            relevant_news = [item for item in news if keyword.lower() in item['title'].lower()]
            
            # Basic sentiment analysis based on keywords
            positive_words = ['gain', 'rise', 'up', 'surge', 'jump', 'boost', 'rally', 'bullish', 'optimistic', 'growth']
            negative_words = ['drop', 'fall', 'down', 'plunge', 'decline', 'lose', 'loss', 'bearish', 'pessimistic', 'crash']
            
            positive_count = 0
            negative_count = 0
            
            for item in relevant_news:
                title = item['title'].lower()
                
                for word in positive_words:
                    if word in title:
                        positive_count += 1
                        
                for word in negative_words:
                    if word in title:
                        negative_count += 1
            
            # Calculate sentiment score
            total = positive_count + negative_count
            
            if total == 0:
                sentiment_score = 0
            else:
                sentiment_score = (positive_count - negative_count) / total
            
            # Determine sentiment category
            if sentiment_score > 0.3:
                sentiment = "bullish"
            elif sentiment_score > 0.1:
                sentiment = "slightly bullish"
            elif sentiment_score > -0.1:
                sentiment = "neutral"
            elif sentiment_score > -0.3:
                sentiment = "slightly bearish"
            else:
                sentiment = "bearish"
                
            result = {
                'keyword': keyword,
                'sentiment': sentiment,
                'sentiment_score': round(sentiment_score, 2),
                'positive_mentions': positive_count,
                'negative_mentions': negative_count,
                'total_relevant_articles': len(relevant_news),
                'articles': relevant_news[:5]  # Include top 5 relevant articles
            }
            
            # Cache result
            self.cache[cache_key] = result
            self.cache_expiry[cache_key] = datetime.now().timestamp() + self.cache_duration
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment for {keyword}: {str(e)}")
            return {
                'keyword': keyword,
                'sentiment': 'neutral',
                'error': str(e)
            }
