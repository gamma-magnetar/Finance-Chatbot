import streamlit as st
from datetime import datetime
import random

# Set page title and layout
st.set_page_config(
    page_title="Financial Market Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_current_date():
    """Get the current date formatted for display."""
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
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
    
    # Sample responses for demo purposes
    sample_responses = [
        "Your exposure to Asia tech stocks is currently 15% of your portfolio. Recent earnings surprises include TSMC beating expectations by 8.3% and Samsung Electronics missing projections by 2.1%.",
        "Top performing sectors this week are Technology (+3.2%), Healthcare (+2.1%), and Consumer Discretionary (+1.6%). Energy is the worst performer, down 1.8%.",
        "Semiconductor stocks are showing strong performance after recent earnings. The sector is up 4.5% over the past week, led by TSMC (+7.2%) and AMD (+6.5%).",
        "Current treasury yields are: 2-Year: 3.82%, 5-Year: 3.56%, 10-Year: 3.81%, 30-Year: 4.14%. The yield curve remains inverted.",
        "Market sentiment towards AI stocks is currently bullish with moderate optimism. The AI sector has seen inflows of $1.2B in the past month, though valuations remain a concern for some analysts."
    ]
    
    for i, query in enumerate(example_queries):
        if st.button(query, key=f"example_{i}"):
            st.session_state.messages.append({"role": "user", "content": query})
            response = sample_responses[i]
            st.session_state.messages.append({"role": "assistant", "content": response})

    # Text input for questions
    st.subheader("Ask a Question")
    query = st.text_input("Enter your financial query:")
    if st.button("Submit") and query:
        st.session_state.messages.append({"role": "user", "content": query})
        # Generate a random response for demonstration purposes
        responses = [
            "Based on current market analysis, Asia tech stocks are showing moderate strength with potential for growth in the semiconductor sector.",
            "Our financial models suggest maintaining your current allocation to technology stocks, with a slight increase in exposure to Taiwan and South Korea-based manufacturers.",
            "The market is showing positive momentum, with major indices trending upward over the past week. Consider this a favorable environment for growth-oriented positions.",
            "Current risk assessment for your portfolio is moderate. Consider diversifying further into defensive sectors as a hedge against potential volatility.",
            "Analysis of recent earnings reports from major tech companies indicates stronger-than-expected performance in the semiconductor and cloud computing segments."
        ]
        st.session_state.messages.append({"role": "assistant", "content": random.choice(responses)})

# Main content area with market data and chat
with col_main:
    # Market Overview Section
    st.header("Market Overview")

    # Create two columns for market data
    market_col1, market_col2 = st.columns(2)

    with market_col1:
        st.subheader("Major Indices")
        # Sample indices data for demonstration
        indices = {
            "S&P 500": {"price": 4735.42, "change_percent": 0.61},
            "Nasdaq": {"price": 16573.68, "change_percent": 0.83},
            "Dow Jones": {"price": 38157.94, "change_percent": 0.32},
            "Nikkei 225": {"price": 38789.56, "change_percent": -0.22},
            "Shanghai": {"price": 3112.05, "change_percent": 0.54}
        }
        
        for idx, data in indices.items():
            delta = data.get("change_percent", 0)
            st.metric(
                label=idx, 
                value=f"{data.get('price', 0):.2f}", 
                delta=f"{delta:.2f}%"
            )

    with market_col2:
        st.subheader("Your Portfolio Summary")
        # Sample portfolio data for demonstration
        portfolio = {
            "total_value": 1250350.75,
            "daily_change_percent": 0.45,
            "allocation": {
                "regions": {
                    "North America": 42,
                    "Europe": 23,
                    "Asia": 28,
                    "Other": 7
                }
            }
        }
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

    # Chat interface
    st.header("Financial Assistant Chat")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Footer
    st.divider()
    st.caption("Financial Market Assistant © 2025")
