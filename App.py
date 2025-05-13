import streamlit as st
import requests
import io
import base64
import time
import os
import numpy as np
import tempfile
from datetime import datetime

# Set page title and layout
st.set_page_config(
    page_title="Financial Market Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set up API endpoints
ORCHESTRATOR_URL = "http://localhost:8000"

def get_current_date():
    """Get the current date formatted for display."""
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y")

def record_audio():
    """Record audio from the user's microphone."""
    audio_bytes = st.session_state.get("audio_recording", None)
    
    if not audio_bytes:
        st.warning("No audio recorded. Please record your question.")
        return None
    
    return audio_bytes

def save_audio_to_file(audio_bytes):
    """Save audio bytes to a temporary file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
        f.write(audio_bytes)
        return f.name

def transcribe_audio(audio_file):
    """Send audio to voice service for transcription."""
    try:
        files = {'audio': open(audio_file, 'rb')}
        response = requests.post(f"{ORCHESTRATOR_URL}/voice/transcribe", files=files)
        if response.status_code == 200:
            return response.json().get("text", "")
        else:
            st.error(f"Error transcribing audio: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None
    finally:
        # Clean up temp file
        if os.path.exists(audio_file):
            os.remove(audio_file)

def process_query(query):
    """Send the query to the orchestrator and get a response."""
    try:
        response = requests.post(
            f"{ORCHESTRATOR_URL}/process",
            json={"query": query}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error processing query: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to orchestrator: {str(e)}")
        return None

def text_to_speech(text):
    """Convert text to speech and return audio bytes."""
    try:
        response = requests.post(
            f"{ORCHESTRATOR_URL}/voice/synthesize",
            json={"text": text}
        )
        if response.status_code == 200:
            return base64.b64decode(response.json().get("audio_base64", ""))
        else:
            st.error(f"Error synthesizing speech: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to voice service: {str(e)}")
        return None

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "audio_recording" not in st.session_state:
    st.session_state.audio_recording = None

# Header
st.title("🏦 Financial Market Assistant")
st.markdown(f"### Today is {get_current_date()}")

# Sidebar
with st.sidebar:
    st.header("Options")
    
    # Example queries
    st.subheader("Example Queries")
    example_queries = [
        "What's our risk exposure in Asia tech stocks today, and highlight any earnings surprises?",
        "What are the top performing sectors this week?",
        "How are semiconductor stocks performing after recent earnings?",
        "What are the current treasury yields?",
        "What's the market sentiment towards AI stocks?"
    ]
    
    for query in example_queries:
        if st.button(query):
            st.session_state.messages.append({"role": "user", "content": query})
            with st.spinner("Processing..."):
                response = process_query(query)
                if response:
                    st.session_state.messages.append({"role": "assistant", "content": response.get("text", "")})
                    audio_bytes = text_to_speech(response.get("text", ""))
                    if audio_bytes:
                        st.session_state.audio_playback = audio_bytes
    
    st.divider()
    
    # Voice Recording
    st.subheader("Voice Input")
    
    audio_bytes = st.audio_recorder(pause_threshold=3.0)
    if audio_bytes:
        st.session_state.audio_recording = audio_bytes
        st.audio(audio_bytes, format="audio/wav")
        
    if st.session_state.get("audio_recording") is not None:
        if st.button("Submit Voice Query"):
            with st.spinner("Transcribing..."):
                audio_file = save_audio_to_file(st.session_state.audio_recording)
                transcription = transcribe_audio(audio_file)
                if transcription:
                    st.session_state.messages.append({"role": "user", "content": transcription})
                    with st.spinner("Processing..."):
                        response = process_query(transcription)
                        if response:
                            st.session_state.messages.append({"role": "assistant", "content": response.get("text", "")})
                            audio_bytes = text_to_speech(response.get("text", ""))
                            if audio_bytes:
                                st.session_state.audio_playback = audio_bytes
                    
                    # Reset recording
                    st.session_state.audio_recording = None

# Main content area - Chat interface
st.header("Financial Assistant Chat")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        # Play audio for assistant responses
        if message["role"] == "assistant" and st.session_state.get("audio_playback") is not None:
            st.audio(st.session_state.audio_playback, format="audio/wav")
            st.session_state.audio_playback = None

# Text input for chat
query = st.chat_input("Ask about financial markets...")
if query:
    st.session_state.messages.append({"role": "user", "content": query})
    
    with st.spinner("Processing..."):
        response = process_query(query)
        if response:
            st.session_state.messages.append({"role": "assistant", "content": response.get("text", "")})
            audio_bytes = text_to_speech(response.get("text", ""))
            if audio_bytes:
                st.session_state.audio_playback = audio_bytes
                
    # Force a rerun to update the UI
    st.rerun()

# Market Overview Section
st.header("Market Overview")

# Create two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Major Indices")
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/api/indices")
        if response.status_code == 200:
            indices = response.json()
            for idx, data in indices.items():
                delta = data.get("change_percent", 0)
                st.metric(
                    label=idx, 
                    value=f"{data.get('price', 0):.2f}", 
                    delta=f"{delta:.2f}%"
                )
        else:
            st.error("Failed to load market indices")
    except Exception as e:
        st.error(f"Error: {str(e)}")

with col2:
    st.subheader("Your Portfolio Summary")
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/api/portfolio")
        if response.status_code == 200:
            portfolio = response.json()
            st.metric(
                label="Total Value", 
                value=f"${portfolio.get('total_value', 0):,.2f}", 
                delta=f"{portfolio.get('daily_change_percent', 0):.2f}%"
            )
            
            # Show allocation
            st.caption("Allocation by Region")
            regions = portfolio.get("allocation", {}).get("regions", {})
            for region, percentage in regions.items():
                st.progress(percentage / 100, text=f"{region}: {percentage}%")
                
        else:
            st.error("Failed to load portfolio data")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Footer
st.divider()
st.caption("Financial Market Assistant © 2023")
