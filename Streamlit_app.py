import streamlit as st
import requests
import os
from datetime import datetime

# Set page title and layout
st.set_page_config(
    page_title="Financial Market Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set up API endpoints
#ORCHESTRATOR_URL = "http://localhost:8000"
ORCHESTRATOR_URL = "http://0.0.0.0:8000"

def get_current_date():
    """Get the current date formatted for display."""
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y")

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

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🏦 Financial Market Assistant")
    st.markdown(f"Today is {get_current_date()}")

# Main layout    
col_sidebar, col_main = st.columns([1, 2])

# Sidebar with example queries
with col_sidebar:
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

    # Text input for questions
    st.subheader("Ask a Question")
    query = st.text_input("Enter your financial query:")
    if st.button("Submit") and query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.spinner("Processing..."):
            response = process_query(query)
            if response:
                st.session_state.messages.append({"role": "assistant", "content": response.get("text", "")})

# Main content area with market data and chat
with col_main:
    # Market Overview Section
    st.header("Market Overview")

    # Create two columns for market data
    market_col1, market_col2 = st.columns(2)

    with market_col1:
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

    with market_col2:
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

    # Chat interface
    st.header("Financial Assistant Chat")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Footer
    st.divider()
    st.caption("Financial Market Assistant © 2023")
