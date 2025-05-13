"""
Main entry point for the Finance Assistant application.
Starts the FastAPI orchestrator and Streamlit frontend.
"""

import os
import subprocess
import threading
import time
import logging
import signal
import sys
from utils.logger import setup_logger

# Setup logging
logger = setup_logger("run", log_level="INFO", log_file="logs/app.log")

def start_orchestrator():
    """Start the FastAPI orchestrator service."""
    logger.info("Starting orchestrator service...")
    try:
        # Run the FastAPI server
        subprocess.run([
            "python", "-m", "uvicorn", 
            "orchestrator.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except Exception as e:
        logger.error(f"Error starting orchestrator: {str(e)}")
        sys.exit(1)

def start_streamlit():
"""Start the Streamlit frontend."""
    logger.info("Starting Streamlit frontend...")
    try:
        # Run the Streamlit app
        # Run the Streamlit app - using streamlit_app.py instead of app.py to avoid audio_recorder issues
        subprocess.run([
            "streamlit", "run", 
            "app.py",
            "streamlit_app.py",
            "--server.port", "5000",
            "--server.address", "0.0.0.0"
        ])
    except Exception as e:
        logger.error(f"Error starting Streamlit: {str(e)}")
        sys.exit(1)

def handle_exit(signum, frame):
    """Handle exit signals."""
    logger.info("Shutting down Finance Assistant...")
    sys.exit(0)

def main():
    """Main entry point."""
    # Register signal handlers
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Create data directory if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Start orchestrator in a separate thread
    orchestrator_thread = threading.Thread(target=start_orchestrator)
    orchestrator_thread.daemon = True
    orchestrator_thread.start()
    
    # Wait for orchestrator to start
    logger.info("Waiting for orchestrator to start...")
    time.sleep(5)
    
    # Start Streamlit
    start_streamlit()

if __name__ == "__main__":
    main()
