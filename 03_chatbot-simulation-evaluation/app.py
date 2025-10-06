"""
Chatbot Simulation Streamlit Application
=========================================
A beautiful web interface for simulating and evaluating chatbot conversations.

Features:
- 🤖 AI-powered chatbot simulation
- 👤 Virtual customer testing
- 📊 Conversation analysis
- 💾 Export capabilities
- 🎯 Predefined scenarios
- 📈 Real-time visualization

Author: AI Assistant
Date: October 2025
"""

import streamlit as st
import os
from pathlib import Path
from datetime import datetime
import time

# Import backend modules
from backend import (
    SimulationManager,
    Scenarios,
    Config,
    format_conversation_for_display,
    export_conversation
)


# ============================================================================
# Page Configuration
# ============================================================================

def configure_page():
    """Configure Streamlit page settings and styling."""
    st.set_page_config(
        page_title="Chatbot Simulator & Evaluator",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com',
            'Report a bug': 'https://github.com',
            'About': "Chatbot Simulation & Evaluation Tool v1.0"
        }
    )
    
    # Custom CSS styling
    st.markdown("""
        <style>
        /* Main container */
        .main {
            padding: 2rem;
        }
        
        /* Header styling */
        .header-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2.5rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        /* Message cards */
        .bot-message {
            background-color: #e3f2fd;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #2196F3;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .customer-message {
            background-color: #f3e5f5;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #9C27B0;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Stats boxes */
        .stat-box {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            font-size: 1rem;
            color: #666;
            margin-top: 0.5rem;
        }
        
        /* Button styling */
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* Scenario cards */
        .scenario-card {
            background-color: #fff;
            padding: 1rem;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            margin: 0.5rem 0;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .scenario-card:hover {
            border-color: #667eea;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
        }
        
        /* Progress bar */
        .stProgress > div > div {
            background-color: #667eea;
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 1rem 2rem;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)


# ============================================================================
# Session State Management
# ============================================================================

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'simulation_manager' not in st.session_state:
        st.session_state.simulation_manager = None
    
    if 'current_conversation' not in st.session_state:
        st.session_state.current_conversation = None
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'api_key_loaded' not in st.session_state:
        st.session_state.api_key_loaded = False
    
    if 'settings' not in st.session_state:
        st.session_state.settings = {
            'max_turns': Config.MAX_CONVERSATION_TURNS,
            'model': Config.DEFAULT_MODEL,
            'bot_prompt': Config.SUPPORT_BOT_SYSTEM_PROMPT
        }


def load_api_key() -> str:
    """
    Load OpenAI API key from environment or .env file.
    
    Returns:
        str: API key or None
    """
    # Check environment first
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        # Try loading from .env file
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        if key.strip() == 'OPENAI_API_KEY':
                            api_key = value.strip().strip("'").strip('"')
                            os.environ["OPENAI_API_KEY"] = api_key
                            break
    
    return api_key


# ============================================================================
# UI Components
# ============================================================================

def render_header():
    """Render the application header."""
    st.markdown("""
        <div class="header-container">
            <h1>🤖 Chatbot Simulator & Evaluator</h1>
            <p style="font-size: 1.2em; margin-top: 1rem;">
                Test and evaluate your chatbot with AI-powered simulated users
            </p>
        </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with settings and scenarios."""
    with st.sidebar:
        st.title("⚙️ Configuration")
        
        # API Key Status
        st.subheader("🔑 API Status")
        api_key = load_api_key()
        if api_key:
            st.success("✅ API Key Loaded")
            st.session_state.api_key_loaded = True
        else:
            st.error("❌ API Key Not Found")
            st.info("💡 Add OPENAI_API_KEY to your .env file")
            st.session_state.api_key_loaded = False
        
        st.divider()
        
        # Simulation Settings
        st.subheader("🎛️ Simulation Settings")
        
        max_turns = st.slider(
            "Maximum Conversation Turns",
            min_value=4,
            max_value=20,
            value=st.session_state.settings['max_turns'],
            help="Maximum number of message exchanges"
        )
        st.session_state.settings['max_turns'] = max_turns
        
        model = st.selectbox(
            "OpenAI Model",
            options=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            index=0,
            help="AI model to use for simulation"
        )
        st.session_state.settings['model'] = model
        
        st.divider()
        
        # Predefined Scenarios
        st.subheader("📋 Quick Scenarios")
        
        scenarios = {
            "🔄 Refund Request": Scenarios.REFUND_REQUEST,
            "⏰ Flight Delay": Scenarios.FLIGHT_DELAY,
            "🧳 Lost Baggage": Scenarios.BAGGAGE_LOST,
            "✈️ Seat Upgrade": Scenarios.SEAT_UPGRADE,
            "💳 Booking Issue": Scenarios.BOOKING_ISSUE
        }
        
        for name, instructions in scenarios.items():
            if st.button(name, use_container_width=True):
                st.session_state.selected_scenario = instructions
                st.rerun()
        
        st.divider()
        
        # Statistics
        st.subheader("📊 Statistics")
        st.metric("Simulations Run", len(st.session_state.conversation_history))
        
        if st.session_state.current_conversation:
            st.metric("Current Turns", len(st.session_state.current_conversation))
        
        # Clear History
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.conversation_history = []
            st.session_state.current_conversation = None
            st.success("History cleared!")
            time.sleep(1)
            st.rerun()


def render_scenario_configuration():
    """Render the scenario configuration section."""
    st.subheader("🎯 Configure Simulation Scenario")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Bot System Prompt
        bot_prompt = st.text_area(
            "Chatbot System Prompt",
            value=st.session_state.settings['bot_prompt'],
            height=100,
            help="Define the chatbot's role and behavior"
        )
        st.session_state.settings['bot_prompt'] = bot_prompt
    
    with col2:
        st.info("""
        **💡 Tips:**
        - Define clear bot persona
        - Specify expertise areas
        - Set tone and style
        - Include policies
        """)
    
    # Customer Instructions
    st.write("")
    customer_instructions = st.text_area(
        "Customer Scenario Instructions",
        value=st.session_state.get('selected_scenario', Scenarios.REFUND_REQUEST),
        height=150,
        help="Define the customer's situation, goals, and behavior"
    )
    
    return bot_prompt, customer_instructions


def render_simulation_results(conversation: list):
    """
    Render the simulation results with formatted messages.
    
    Args:
        conversation (list): List of conversation turns
    """
    st.subheader("💬 Conversation History")
    
    # Create a scrollable container
    for turn in conversation:
        if turn["speaker"] == "Bot":
            st.markdown(f"""
                <div class="bot-message">
                    <strong>🤖 Support Bot</strong>
                    <p style="margin-top: 0.5rem;">{turn['message']}</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="customer-message">
                    <strong>👤 Customer</strong>
                    <p style="margin-top: 0.5rem;">{turn['message']}</p>
                </div>
            """, unsafe_allow_html=True)


def render_analysis_section(conversation: list):
    """
    Render conversation analysis and statistics.
    
    Args:
        conversation (list): List of conversation turns
    """
    st.subheader("📈 Conversation Analysis")
    
    # Calculate statistics
    total_turns = len(conversation)
    bot_turns = sum(1 for c in conversation if c["speaker"] == "Bot")
    customer_turns = sum(1 for c in conversation if c["speaker"] == "Customer")
    
    completed = any(
        Config.FINISH_KEYWORD in c["message"] 
        for c in conversation
    )
    
    # Display stats in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="stat-box">
                <div class="stat-value">{}</div>
                <div class="stat-label">Total Turns</div>
            </div>
        """.format(total_turns), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="stat-box">
                <div class="stat-value">{}</div>
                <div class="stat-label">Bot Messages</div>
            </div>
        """.format(bot_turns), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="stat-box">
                <div class="stat-value">{}</div>
                <div class="stat-label">Customer Messages</div>
            </div>
        """.format(customer_turns), unsafe_allow_html=True)
    
    with col4:
        status = "✅ Yes" if completed else "❌ No"
        st.markdown("""
            <div class="stat-box">
                <div class="stat-value" style="font-size: 2rem;">{}</div>
                <div class="stat-label">Completed</div>
            </div>
        """.format(status), unsafe_allow_html=True)
    
    # Message length analysis
    st.write("")
    st.write("**📊 Message Length Analysis**")
    
    bot_lengths = [len(c["message"]) for c in conversation if c["speaker"] == "Bot"]
    customer_lengths = [len(c["message"]) for c in conversation if c["speaker"] == "Customer"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        if bot_lengths:
            avg_bot = sum(bot_lengths) / len(bot_lengths)
            st.metric("Avg. Bot Message Length", f"{avg_bot:.0f} chars")
    
    with col2:
        if customer_lengths:
            avg_customer = sum(customer_lengths) / len(customer_lengths)
            st.metric("Avg. Customer Message Length", f"{avg_customer:.0f} chars")


def render_export_section(conversation: list):
    """
    Render export options for conversation data.
    
    Args:
        conversation (list): List of conversation turns
    """
    st.subheader("💾 Export Conversation")
    
    col1, col2, col3 = st.columns(3)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with col1:
        txt_export = export_conversation(conversation, format="txt")
        st.download_button(
            label="📄 Download as TXT",
            data=txt_export,
            file_name=f"chatbot_simulation_{timestamp}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        md_export = export_conversation(conversation, format="md")
        st.download_button(
            label="📋 Download as Markdown",
            data=md_export,
            file_name=f"chatbot_simulation_{timestamp}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with col3:
        json_export = export_conversation(conversation, format="json")
        st.download_button(
            label="📊 Download as JSON",
            data=json_export,
            file_name=f"chatbot_simulation_{timestamp}.json",
            mime="application/json",
            use_container_width=True
        )


# ============================================================================
# Main Application Logic
# ============================================================================

def run_simulation(bot_prompt: str, customer_instructions: str):
    """
    Execute the chatbot simulation.
    
    Args:
        bot_prompt (str): System prompt for the chatbot
        customer_instructions (str): Instructions for the simulated user
    """
    if not st.session_state.api_key_loaded:
        st.error("❌ Cannot run simulation: API key not loaded")
        return
    
    # Get API key
    api_key = load_api_key()
    
    # Create simulation manager
    with st.spinner("🔧 Initializing simulation..."):
        manager = SimulationManager(
            api_key=api_key,
            customer_instructions=customer_instructions,
            bot_system_prompt=bot_prompt,
            max_turns=st.session_state.settings['max_turns'],
            model=st.session_state.settings['model']
        )
        
        manager.build_workflow()
    
    # Run simulation with progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("🚀 Starting simulation...")
    progress_bar.progress(20)
    time.sleep(0.5)
    
    status_text.text("💬 Generating conversation...")
    progress_bar.progress(40)
    
    try:
        conversation = manager.run_simulation()
        
        progress_bar.progress(80)
        status_text.text("✅ Processing results...")
        time.sleep(0.5)
        
        progress_bar.progress(100)
        status_text.text("✅ Simulation complete!")
        time.sleep(0.5)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Store results
        st.session_state.current_conversation = conversation
        st.session_state.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'conversation': conversation
        })
        
        st.success("✅ Simulation completed successfully!")
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Simulation failed: {str(e)}")


def main():
    """Main application entry point."""
    # Configure page
    configure_page()
    
    # Initialize session state
    initialize_session_state()
    
    # Render UI components
    render_header()
    render_sidebar()
    
    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Run Simulation", "📊 Analysis", "📚 History"])
    
    with tab1:
        # Scenario configuration
        bot_prompt, customer_instructions = render_scenario_configuration()
        
        st.write("")
        
        # Run simulation button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Run Simulation", type="primary", use_container_width=True):
                run_simulation(bot_prompt, customer_instructions)
        
        st.divider()
        
        # Display results if available
        if st.session_state.current_conversation:
            render_simulation_results(st.session_state.current_conversation)
    
    with tab2:
        st.subheader("📈 Analysis Dashboard")
        
        if st.session_state.current_conversation:
            render_analysis_section(st.session_state.current_conversation)
            st.divider()
            render_export_section(st.session_state.current_conversation)
        else:
            st.info("👈 Run a simulation first to see analysis")
    
    with tab3:
        st.subheader("📚 Simulation History")
        
        if st.session_state.conversation_history:
            st.write(f"**Total Simulations:** {len(st.session_state.conversation_history)}")
            
            for idx, record in enumerate(reversed(st.session_state.conversation_history), 1):
                timestamp = datetime.fromisoformat(record['timestamp'])
                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                
                with st.expander(f"🔍 Simulation {idx} - {formatted_time}"):
                    conversation = record['conversation']
                    
                    # Mini stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Turns", len(conversation))
                    with col2:
                        bot_msgs = sum(1 for c in conversation if c["speaker"] == "Bot")
                        st.metric("Bot Messages", bot_msgs)
                    with col3:
                        completed = any(Config.FINISH_KEYWORD in c["message"] for c in conversation)
                        st.metric("Completed", "Yes" if completed else "No")
                    
                    # View conversation button
                    if st.button(f"View Full Conversation", key=f"view_{idx}"):
                        st.session_state.current_conversation = conversation
                        st.rerun()
        else:
            st.info("📭 No simulation history yet. Run your first simulation!")
    
    # Footer
    st.divider()
    st.markdown("""
        <div style="text-align: center; color: #666; padding: 2rem;">
            <p>🤖 Powered by OpenAI GPT & LangGraph</p>
            <p>Built with ❤️ using Streamlit</p>
        </div>
    """, unsafe_allow_html=True)


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    main()
