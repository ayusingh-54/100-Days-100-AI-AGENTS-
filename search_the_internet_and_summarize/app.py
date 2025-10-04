"""
AI-Powered Web Research Tool - Streamlit Frontend
=================================================
A beautiful and intuitive web interface for searching and summarizing web content.

Features:
- 🔍 Smart web search with DuckDuckGo
- 🤖 AI-powered summarization with OpenAI
- 🎯 Site-specific search capability
- 📊 Search history tracking
- 💾 Export results in multiple formats
- 🎨 Beautiful, responsive UI
- ⚡ Fast caching mechanism

Author: AI Assistant
Date: October 2025
"""

import streamlit as st
from datetime import datetime
import time
from typing import Optional
import sys
import os

# Import backend modules
from backend import SearchManager, Config, validate_url, format_timestamp


# ============================================================================
# Page Configuration
# ============================================================================

def configure_page():
    """Configure Streamlit page settings and styling."""
    st.set_page_config(
        page_title="AI Web Research Assistant",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com',
            'Report a bug': 'https://github.com',
            'About': "AI-Powered Web Research Tool v1.0"
        }
    )
    
    # Custom CSS for better UI
    st.markdown("""
        <style>
        /* Main container styling */
        .main {
            padding: 2rem;
        }
        
        /* Header styling */
        .header-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
        }
        
        /* Card styling */
        .result-card {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Button styling */
        .stButton>button {
            width: 100%;
            border-radius: 5px;
            height: 3em;
            background-color: #667eea;
            color: white;
            font-weight: 600;
        }
        
        .stButton>button:hover {
            background-color: #764ba2;
            border-color: #764ba2;
        }
        
        /* Sidebar styling */
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        
        /* Success message */
        .success-message {
            padding: 1rem;
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            border-radius: 5px;
            margin: 1rem 0;
        }
        
        /* Error message */
        .error-message {
            padding: 1rem;
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
            border-radius: 5px;
            margin: 1rem 0;
        }
        
        /* Stats container */
        .stats-container {
            display: flex;
            justify-content: space-around;
            padding: 1rem;
            background-color: #e9ecef;
            border-radius: 10px;
            margin: 1rem 0;
        }
        
        .stat-item {
            text-align: center;
        }
        
        /* Animation for loading */
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .loading {
            animation: pulse 1.5s ease-in-out infinite;
        }
        </style>
    """, unsafe_allow_html=True)


# ============================================================================
# Session State Management
# ============================================================================

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'search_manager' not in st.session_state:
        st.session_state.search_manager = None
    
    if 'current_results' not in st.session_state:
        st.session_state.current_results = None
    
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    
    if 'settings' not in st.session_state:
        st.session_state.settings = {
            'summary_style': 'bullet',
            'max_results': 3,
            'max_points': 2,
            'temperature': 0.7
        }
    
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False


def initialize_backend():
    """Initialize backend components."""
    try:
        if not st.session_state.initialized:
            with st.spinner("🔧 Initializing AI backend..."):
                config = Config()
                st.session_state.search_manager = SearchManager(config)
                st.session_state.initialized = True
            st.success("✅ Backend initialized successfully!")
            time.sleep(1)
            st.rerun()
    except Exception as e:
        st.error(f"❌ Failed to initialize backend: {str(e)}")
        st.info("💡 Make sure your .env file contains OPENAI_API_KEY")
        st.stop()


# ============================================================================
# UI Components
# ============================================================================

def render_header():
    """Render the application header."""
    st.markdown("""
        <div class="header-container">
            <h1>🔍 AI Web Research Assistant</h1>
            <p style="font-size: 1.2em; margin-top: 0.5rem;">
                Search the web and get AI-powered summaries instantly
            </p>
        </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with settings and options."""
    with st.sidebar:
        st.title("⚙️ Settings")
        
        # Search Settings Section
        st.subheader("🔍 Search Settings")
        
        max_results = st.slider(
            "Maximum Results",
            min_value=1,
            max_value=10,
            value=st.session_state.settings['max_results'],
            help="Number of search results to retrieve and summarize"
        )
        st.session_state.settings['max_results'] = max_results
        
        # Summarization Settings Section
        st.subheader("📝 Summarization Settings")
        
        summary_style = st.selectbox(
            "Summary Style",
            options=['bullet', 'paragraph', 'brief'],
            index=['bullet', 'paragraph', 'brief'].index(st.session_state.settings['summary_style']),
            help="Choose how summaries should be formatted"
        )
        st.session_state.settings['summary_style'] = summary_style
        
        if summary_style == 'bullet':
            max_points = st.slider(
                "Bullet Points",
                min_value=1,
                max_value=5,
                value=st.session_state.settings['max_points'],
                help="Number of bullet points per summary"
            )
            st.session_state.settings['max_points'] = max_points
        
        st.divider()
        
        # Statistics Section
        st.subheader("📊 Statistics")
        if st.session_state.search_manager:
            history = st.session_state.search_manager.get_search_history()
            st.metric("Total Searches", len(history))
            if st.session_state.current_results:
                st.metric("Last Search Results", 
                         len(st.session_state.current_results.get('summaries', [])))
        
        st.divider()
        
        # Action Buttons Section
        st.subheader("🛠️ Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Cache", use_container_width=True):
                if st.session_state.search_manager:
                    st.session_state.search_manager.clear_cache()
                    st.success("Cache cleared!")
        
        with col2:
            if st.button("📜 Clear History", use_container_width=True):
                if st.session_state.search_manager:
                    st.session_state.search_manager.clear_history()
                    st.session_state.search_history = []
                    st.success("History cleared!")
        
        # History Display
        if st.session_state.search_manager:
            history = st.session_state.search_manager.get_search_history()
            if history:
                st.divider()
                st.subheader("📜 Recent Searches")
                for i, item in enumerate(reversed(history[-5:])):  # Show last 5
                    with st.expander(f"🔍 {item['query'][:30]}..."):
                        st.text(f"Query: {item['query']}")
                        st.text(f"Site: {item.get('site', 'All websites')}")
                        st.text(f"Results: {item['result_count']}")
                        st.text(f"Time: {format_timestamp(item['timestamp'])}")


def render_search_interface():
    """Render the main search interface."""
    st.subheader("🔎 Search & Summarize")
    
    # Create two columns for layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Enter your search query",
            placeholder="e.g., Latest advancements in quantum computing",
            help="Enter any topic you want to research",
            key="search_query"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        search_button = st.button("🚀 Search", type="primary", use_container_width=True)
    
    # Optional site-specific search
    with st.expander("🎯 Advanced: Search Specific Website"):
        specific_site = st.text_input(
            "Website URL (optional)",
            placeholder="e.g., https://www.nature.com",
            help="Leave empty to search all websites, or specify a site for focused results",
            key="specific_site"
        )
        
        if specific_site and not validate_url(specific_site):
            st.warning("⚠️ Please enter a valid URL (including http:// or https://)")
    
    return query, specific_site if specific_site else None, search_button


def render_results(results: dict):
    """
    Render search results in a beautiful format.
    
    Args:
        results (dict): Results dictionary from backend
    """
    if not results['success']:
        st.error(f"❌ {results['message']}")
        return
    
    # Display metadata
    st.success(f"✅ {results['message']}")
    
    # Info bar
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"📅 **Date:** {format_timestamp(results['timestamp'])}")
    with col2:
        st.info(f"🌐 **Source:** {results.get('specific_site', 'All websites')}")
    with col3:
        st.info(f"📊 **Results:** {len(results['summaries'])}")
    
    st.divider()
    
    # Display summaries
    st.subheader("📋 Summaries")
    
    if not results['summaries']:
        st.warning("No summaries available.")
        return
    
    for idx, summary in enumerate(results['summaries'], 1):
        with st.container():
            st.markdown(f"### Result {idx}")
            
            # Parse and display summary content
            lines = summary.split('\n')
            for line in lines:
                if line.startswith('📌 **Source:**'):
                    st.markdown(line)
                elif line.startswith('🔗 **Link:**'):
                    st.markdown(line)
                elif line.startswith('📝 **Summary:**'):
                    st.markdown(line)
                elif line.strip() and not line.startswith('-' * 10):
                    st.markdown(line)
            
            st.divider()


def render_export_section(results: dict):
    """
    Render export options for results.
    
    Args:
        results (dict): Results to export
    """
    if not results or not results.get('success'):
        return
    
    st.subheader("💾 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export as TXT", use_container_width=True):
            export_data = st.session_state.search_manager.export_results(results, format="txt")
            st.download_button(
                label="⬇️ Download TXT",
                data=export_data,
                file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    with col2:
        if st.button("📋 Export as Markdown", use_container_width=True):
            export_data = st.session_state.search_manager.export_results(results, format="md")
            st.download_button(
                label="⬇️ Download MD",
                data=export_data,
                file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    with col3:
        if st.button("📊 Export as JSON", use_container_width=True):
            export_data = st.session_state.search_manager.export_results(results, format="json")
            st.download_button(
                label="⬇️ Download JSON",
                data=export_data,
                file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )


# ============================================================================
# Main Application Logic
# ============================================================================

def perform_search(query: str, specific_site: Optional[str]):
    """
    Perform search and display results.
    
    Args:
        query (str): Search query
        specific_site (Optional[str]): Specific site to search
    """
    if not query.strip():
        st.warning("⚠️ Please enter a search query")
        return
    
    # Display loading animation
    with st.spinner("🔍 Searching and generating summaries..."):
        # Add progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🌐 Searching the web...")
        progress_bar.progress(30)
        time.sleep(0.5)
        
        status_text.text("🤖 Generating AI summaries...")
        progress_bar.progress(60)
        
        # Perform actual search
        results = st.session_state.search_manager.search_and_summarize(
            query=query,
            specific_site=specific_site,
            max_results=st.session_state.settings['max_results'],
            summary_style=st.session_state.settings['summary_style'],
            max_points=st.session_state.settings['max_points']
        )
        
        progress_bar.progress(100)
        status_text.text("✅ Complete!")
        time.sleep(0.5)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
    
    # Store results
    st.session_state.current_results = results
    
    # Display results
    render_results(results)
    
    # Export section
    if results.get('success'):
        st.divider()
        render_export_section(results)


def main():
    """Main application entry point."""
    # Configure page
    configure_page()
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize backend if needed
    if not st.session_state.initialized:
        initialize_backend()
    
    # Render UI components
    render_header()
    render_sidebar()
    
    # Main content area
    query, specific_site, search_button = render_search_interface()
    
    # Handle search button click
    if search_button:
        perform_search(query, specific_site)
    
    # Display current results if available
    elif st.session_state.current_results:
        st.divider()
        st.subheader("📋 Previous Results")
        render_results(st.session_state.current_results)
        render_export_section(st.session_state.current_results)
    
    # Footer
    st.divider()
    st.markdown("""
        <div style="text-align: center; color: #666; padding: 2rem;">
            <p>🤖 Powered by OpenAI GPT-4 & DuckDuckGo Search</p>
            <p>Made with ❤️ using Streamlit</p>
        </div>
    """, unsafe_allow_html=True)


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    main()
