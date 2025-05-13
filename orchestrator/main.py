"""
Main Orchestrator for the Finance Assistant.
Coordinates the different agents and handles the main workflow.
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Optional, Union
import json
import os
from datetime import datetime

from fastapi import FastAPI, Request, File, UploadFile, Form, Body, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from agents.api_agent import APIAgent
from agents.scraping_agent import ScrapingAgent
from agents.retriever_agent import RetrieverAgent
from agents.analysis_agent import AnalysisAgent
from agents.language_agent import LanguageAgent
from agents.voice_agent import VoiceAgent
from utils.logger import setup_logger
from orchestrator.router import AgentRouter

# Setup logging
logger = setup_logger("orchestrator")

# Create FastAPI app
app = FastAPI(title="Finance Assistant Orchestrator")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
api_agent = APIAgent()
scraping_agent = ScrapingAgent()
retriever_agent = RetrieverAgent()
analysis_agent = AnalysisAgent()
language_agent = LanguageAgent()
voice_agent = VoiceAgent()

# Initialize router
router = AgentRouter(
    api_agent=api_agent,
    scraping_agent=scraping_agent,
    retriever_agent=retriever_agent,
    analysis_agent=analysis_agent,
    language_agent=language_agent,
    voice_agent=voice_agent
)

# Set up periodic data ingestion
last_data_ingestion = 0
DATA_INGESTION_INTERVAL = 3600  # 1 hour in seconds

async def ingest_data_periodically():
    """Periodically ingest data to keep the knowledge base updated."""
    global last_data_ingestion
    
    # Check if it's time to ingest data
    current_time = time.time()
    if current_time - last_data_ingestion > DATA_INGESTION_INTERVAL:
        logger.info("Starting periodic data ingestion")
        
        try:
            # Define key stocks to track
            asia_tech_stocks = ["TSM", "9988.HK", "005930.KS", "0700.HK", "6758.T"]
            
            # Ingest data from API agent
            retriever_agent.add_from_api_agent(api_agent, asia_tech_stocks)
            
            # Ingest data from scraping agent
            retriever_agent.add_from_scraping_agent(scraping_agent, asia_tech_stocks)
            
            last_data_ingestion = current_time
            logger.info("Periodic data ingestion completed")
            
        except Exception as e:
            logger.error(f"Error during periodic data ingestion: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Run tasks when the server starts."""
    # Initial data ingestion
    await ingest_data_periodically()

@app.post("/process")
async def process_query(request: Dict[str, Any] = Body(...), background_tasks: BackgroundTasks = None):
    """
    Process a user query through the appropriate agents.
    
    Args:
        request: Request body with query
        background_tasks: FastAPI background tasks
    
    Returns:
        JSON response with processed result
    """
    query = request.get("query", "")
    
    if not query:
        return JSONResponse(
            status_code=400,
            content={"error": "No query provided"}
        )
        
    try:
        # Analyze query intent
        intent = language_agent.analyze_query_intent(query)
        
        # Schedule periodic data ingestion
        if background_tasks:
            background_tasks.add_task(ingest_data_periodically)
        
        # Route the query to appropriate agents
        response = router.route_query(query, intent)
        
        return response
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error processing query: {str(e)}"}
        )

@app.post("/voice/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Transcribe audio to text.
    
    Args:
        audio: Audio file
    
    Returns:
        JSON response with transcription
    """
    try:
        # Save the audio file temporarily
        with open("temp_audio.wav", "wb") as temp_file:
            temp_file.write(await audio.read())
        
        # Transcribe the audio
        result = voice_agent.transcribe_audio("temp_audio.wav")
        
        # Clean up
        if os.path.exists("temp_audio.wav"):
            os.remove("temp_audio.wav")
        
        if result["success"]:
            return {"text": result["text"]}
        else:
            return JSONResponse(
                status_code=500,
                content={"error": result.get("error", "Unknown error")}
            )
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error transcribing audio: {str(e)}"}
        )

@app.post("/voice/synthesize")
async def synthesize_speech(request: Dict[str, Any] = Body(...)):
    """
    Convert text to speech.
    
    Args:
        request: Request body with text
    
    Returns:
        JSON response with audio
    """
    text = request.get("text", "")
    
    if not text:
        return JSONResponse(
            status_code=400,
            content={"error": "No text provided"}
        )
        
    try:
        # Convert text to speech
        result = voice_agent.text_to_speech(text)
        
        if result["success"]:
            return {"audio_base64": result["audio_base64"]}
        else:
            return JSONResponse(
                status_code=500,
                content={"error": result.get("error", "Unknown error")}
            )
    except Exception as e:
        logger.error(f"Error synthesizing speech: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error synthesizing speech: {str(e)}"}
        )

@app.get("/api/indices")
async def get_market_indices():
    """
    Get current market indices.
    
    Returns:
        JSON response with market indices
    """
    try:
        indices = api_agent.get_market_indices()
        return indices
    except Exception as e:
        logger.error(f"Error getting market indices: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error getting market indices: {str(e)}"}
        )

@app.get("/api/portfolio")
async def get_portfolio():
    """
    Get portfolio data.
    
    Returns:
        JSON response with portfolio data
    """
    try:
        portfolio = api_agent.get_portfolio_data()
        return portfolio
    except Exception as e:
        logger.error(f"Error getting portfolio data: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error getting portfolio data: {str(e)}"}
        )

@app.get("/api/sectors")
async def get_sector_performance():
    """
    Get sector performance.
    
    Returns:
        JSON response with sector performance
    """
    try:
        sectors = api_agent.get_sector_performance()
        return sectors
    except Exception as e:
        logger.error(f"Error getting sector performance: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error getting sector performance: {str(e)}"}
        )

@app.get("/api/asia_tech")
async def get_asia_tech():
    """
    Get Asia tech exposure.
    
    Returns:
        JSON response with Asia tech exposure
    """
    try:
        asia_tech = api_agent.get_asia_tech_exposure()
        return asia_tech
    except Exception as e:
        logger.error(f"Error getting Asia tech exposure: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error getting Asia tech exposure: {str(e)}"}
        )

@app.get("/morning_brief")
async def get_morning_brief():
    """
    Get morning market brief.
    
    Returns:
        JSON response with morning brief
    """
    try:
        # Generate brief data
        brief_data = analysis_agent.generate_morning_brief(api_agent)
        
        # Generate narrative
        narrative = language_agent.generate_morning_brief(brief_data)
        
        # Generate audio
        audio_result = voice_agent.speak_financial_summary(narrative)
        
        return {
            "text": narrative,
            "audio_base64": audio_result.get("audio_base64", ""),
            "data": brief_data
        }
    except Exception as e:
        logger.error(f"Error generating morning brief: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error generating morning brief: {str(e)}"}
        )

def start():
    """Start the FastAPI server."""
    uvicorn.run("orchestrator.main:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    start()
