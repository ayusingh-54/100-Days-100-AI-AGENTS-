"""
Streamlit App for Customer Support Agent
This is the main application file for the customer support agent interface.
"""

import streamlit as st
from backend import CustomerSupportAgent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Customer Support Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .query-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .response-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    .escalation-box {
        background-color: #ffe6e6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #ff4444;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []


def get_sentiment_emoji(sentiment: str) -> str:
    """Get emoji based on sentiment."""
    sentiment_lower = sentiment.lower()
    if 'positive' in sentiment_lower:
        return "😊"
    elif 'negative' in sentiment_lower:
        return "😠"
    else:
        return "😐"


def get_category_emoji(category: str) -> str:
    """Get emoji based on category."""
    category_lower = category.lower()
    if 'technical' in category_lower:
        return "🔧"
    elif 'billing' in category_lower:
        return "💰"
    else:
        return "📋"


def main():
    """Main application function."""
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Customer Support Agent</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Welcome to the AI-powered Customer Support Agent! This intelligent system uses LangGraph 
    to categorize queries, analyze sentiment, and provide appropriate responses or escalate 
    issues when necessary.
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key", 
            type="password",
            value=os.getenv('OPENAI_API_KEY', ''),
            help="Enter your OpenAI API key"
        )
        
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        # Temperature slider
        temperature = st.slider(
            "Model Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.1,
            help="Controls randomness in responses. Lower values are more focused and deterministic."
        )
        
        # Initialize agent button
        if st.button("🚀 Initialize Agent", type="primary"):
            if not api_key:
                st.error("Please enter your OpenAI API key!")
            else:
                with st.spinner("Initializing agent..."):
                    try:
                        st.session_state.agent = CustomerSupportAgent(temperature=temperature)
                        st.success("✅ Agent initialized successfully!")
                    except Exception as e:
                        st.error(f"Error initializing agent: {str(e)}")
        
        st.divider()
        
        # Workflow visualization
        st.header("📊 Workflow Graph")
        if st.session_state.agent:
            try:
                with st.spinner("Generating workflow graph..."):
                    graph_image = st.session_state.agent.get_graph_image()
                    st.image(graph_image, caption="LangGraph Workflow")
            except Exception as e:
                st.info("Graph visualization unavailable")
        else:
            st.info("Initialize the agent to see the workflow graph")
        
        st.divider()
        
        # Query history
        st.header("📜 Query History")
        if st.session_state.query_history:
            st.metric("Total Queries", len(st.session_state.query_history))
        else:
            st.info("No queries yet")
    
    # Main content area
    if not st.session_state.agent:
        st.warning("⚠️ Please initialize the agent using the sidebar configuration.")
        
        # Show example queries
        st.subheader("📝 Example Queries")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("**Technical Query**\n\n'My internet connection keeps dropping. Can you help?'")
            st.info("**Billing Query**\n\n'Where can I find my receipt?'")
        
        with col2:
            st.info("**General Query**\n\n'What are your business hours?'")
            st.info("**Escalation Example**\n\n'I'm very frustrated with your service!'")
    
    else:
        # Query input
        st.subheader("💬 Enter Your Query")
        
        # Text area for query
        query = st.text_area(
            "Customer Query",
            height=100,
            placeholder="Type your customer support query here...",
            help="Enter the customer's question or concern"
        )
        
        # Submit button
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            submit_button = st.button("🔍 Process Query", type="primary")
        
        with col2:
            clear_button = st.button("🗑️ Clear")
        
        if clear_button:
            st.rerun()
        
        # Process query
        if submit_button and query:
            with st.spinner("Processing your query..."):
                try:
                    result = st.session_state.agent.process_query(query)
                    
                    # Add to history
                    st.session_state.query_history.append({
                        "query": query,
                        "result": result
                    })
                    
                    # Display results
                    st.divider()
                    st.subheader("📊 Analysis Results")
                    
                    # Metrics row
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.metric(
                            "Category",
                            f"{get_category_emoji(result['category'])} {result['category']}"
                        )
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.metric(
                            "Sentiment",
                            f"{get_sentiment_emoji(result['sentiment'])} {result['sentiment']}"
                        )
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        is_escalated = "escalated" in result['response'].lower()
                        st.metric(
                            "Status",
                            "🚨 Escalated" if is_escalated else "✅ Resolved"
                        )
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.divider()
                    
                    # Query display
                    st.markdown("**Original Query:**")
                    st.markdown(f'<div class="query-box">{query}</div>', unsafe_allow_html=True)
                    
                    # Response display
                    st.markdown("**Response:**")
                    if "escalated" in result['response'].lower():
                        st.markdown(f'<div class="escalation-box">{result["response"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="response-box">{result["response"]}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ Error processing query: {str(e)}")
        
        elif submit_button:
            st.warning("⚠️ Please enter a query to process.")
        
        # Display query history
        if st.session_state.query_history:
            st.divider()
            st.subheader("📜 Recent Queries")
            
            with st.expander("View Query History", expanded=False):
                for idx, item in enumerate(reversed(st.session_state.query_history[-5:])):
                    st.markdown(f"**Query {len(st.session_state.query_history) - idx}:**")
                    st.text(item['query'])
                    st.markdown(f"*Category:* {item['result']['category']} | "
                              f"*Sentiment:* {item['result']['sentiment']}")
                    st.markdown("---")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>Built with LangGraph, LangChain, and Streamlit | Powered by OpenAI</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
