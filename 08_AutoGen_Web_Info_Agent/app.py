"""
Advanced Interactive Streamlit UI for AutoGen Web Info Agent
"""
import streamlit as st
import json
from datetime import datetime
from typing import Dict, Any
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from backend import get_agent_manager, initialize_agent_manager, TaskExecutor
from utils import Logger

# Configure Streamlit page
st.set_page_config(
    page_title=Config.PAGE_TITLE,
    page_icon=Config.PAGE_ICON,
    layout=Config.LAYOUT,
    initial_sidebar_state=Config.INITIAL_SIDEBAR_STATE,
)

# Setup logger
logger = Logger.setup(__name__, Config.LOG_LEVEL)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding-top: 2rem;
    }
    
    /* Card styling */
    .info-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77e2;
        margin: 1rem 0;
    }
    
    .success-card {
        background-color: #d4f1d4;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    
    .error-card {
        background-color: #f8d7da;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
    }
    
    .warning-card {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    
    /* Metrics styling */
    .metric-container {
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        margin: 2rem 0;
    }
    
    /* Conversation styling */
    .message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        word-wrap: break-word;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
    }
    
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #666;
    }
    
    .system-message {
        background-color: #fff9c4;
        border-left: 4px solid #f57f17;
    }
    
    /* Header styling */
    h1 {
        color: #1f77e2;
        border-bottom: 3px solid #1f77e2;
        padding-bottom: 1rem;
    }
    
    h2 {
        color: #2c5aa0;
        margin-top: 2rem;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #1f77e2;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #1557a8;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Sidebar styling */
    .sidebar-section {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        background-color: #f9f9f9;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def initialize_session_state():
    """Initialize session state variables"""
    if "agent_manager" not in st.session_state:
        st.session_state.agent_manager = None
    
    if "agent_initialized" not in st.session_state:
        st.session_state.agent_initialized = False
    
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    if "current_task" not in st.session_state:
        st.session_state.current_task = None
    
    if "execution_in_progress" not in st.session_state:
        st.session_state.execution_in_progress = False
    
    if "performance_stats" not in st.session_state:
        st.session_state.performance_stats = {}


# Initialize on first run
initialize_session_state()


def render_header():
    """Render main header"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("# 🤖 AutoGen Web Info Agent")
        st.markdown("*Powered by AutoGen - Intelligent Multi-Agent Conversation Framework*")
    
    with col2:
        if st.session_state.agent_initialized:
            st.success("✅ Agent Ready")
        else:
            st.warning("⚠️ Agent Not Ready")


def render_sidebar():
    """Render sidebar with configuration and controls"""
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # Status indicator
        st.markdown("### Status")
        if st.session_state.agent_initialized:
            st.success("Agent Initialized")
        else:
            st.info("Agent Not Initialized")
        
        # Initialize button
        st.markdown("### Initialization")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Initialize Agent", key="init_btn"):
                with st.spinner("Initializing agent..."):
                    try:
                        if initialize_agent_manager():
                            st.session_state.agent_manager = get_agent_manager()
                            st.session_state.agent_initialized = True
                            st.success("✅ Agent initialized successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to initialize agent")
                    except Exception as e:
                        st.error(f"❌ Initialization error: {str(e)}")
        
        with col2:
            if st.button("🔄 Reset", key="reset_btn"):
                if st.session_state.agent_manager:
                    st.session_state.agent_manager.reset()
                st.session_state.conversation_history = []
                st.session_state.current_task = None
                st.success("✅ Reset complete")
                st.rerun()
        
        # Settings
        st.markdown("### Settings")
        
        use_docker = st.checkbox(
            "Use Docker for Code Execution",
            value=Config.USE_DOCKER,
            help="Safer code execution in isolated Docker containers"
        )
        
        max_retries = st.slider(
            "Max Agent Retries",
            min_value=1,
            max_value=20,
            value=Config.MAX_CONSECUTIVE_AUTO_REPLY,
            help="Maximum number of times agent can retry"
        )
        
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=Config.LLM_TEMPERATURE,
            step=0.1,
            help="Controls randomness: higher = more random"
        )
        
        # Information section
        st.markdown("---")
        st.markdown("### 📚 Information")
        
        with st.expander("About this Agent"):
            st.markdown("""
            This is an advanced AutoGen Web Info Agent that can:
            
            - 📄 **Analyze Research Papers** - Read and discuss papers from URLs
            - 📈 **Stock Market Analysis** - Get market insights and financial data
            - 🔍 **Web Research** - Research any topic on the web
            - ⚙️ **Custom Tasks** - Execute any custom task
            
            The agent uses intelligent multi-agent conversation to solve complex tasks.
            """)
        
        with st.expander("🔧 How It Works"):
            st.markdown("""
            1. **Initialize the Agent** - Set up the assistant and user proxy agents
            2. **Choose a Task Type** - Select from predefined tasks or create custom ones
            3. **Provide Input** - Enter the details (URL, query, etc.)
            4. **Execute** - The agents will work together to solve your task
            5. **Review Results** - Examine the conversation and findings
            
            The agents communicate intelligently, writing code when needed and executing it safely.
            """)


def render_task_selection():
    """Render task selection interface"""
    st.markdown("## 📋 Task Selection")
    
    # Create tabs for different task categories
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Paper Analysis",
        "📈 Stock Market",
        "🔍 Web Research",
        "⚙️ Custom Task"
    ])
    
    with tab1:
        st.markdown("### Analyze Research Paper")
        
        # Template for paper analysis
        paper_url = st.text_input(
            "Paper URL",
            placeholder="https://arxiv.org/abs/2308.08155",
            key="paper_url",
            help="Enter the URL of the research paper you want to analyze"
        )
        
        analysis_aspects = st.multiselect(
            "What aspects would you like analyzed?",
            options=[
                "Summary & Key Contributions",
                "Target Audience",
                "Methodology & Results",
                "Limitations & Future Work",
                "Practical Applications"
            ],
            default=["Summary & Key Contributions", "Target Audience"]
        )
        
        if st.button("🚀 Analyze Paper", key="analyze_paper"):
            if not paper_url:
                st.error("❌ Please enter a paper URL")
            elif not st.session_state.agent_initialized:
                st.error("❌ Please initialize the agent first")
            else:
                st.session_state.current_task = {
                    "type": "paper_analysis",
                    "url": paper_url,
                    "aspects": analysis_aspects
                }
                st.session_state.execution_in_progress = True
    
    with tab2:
        st.markdown("### Stock Market Analysis")
        
        market_query = st.text_area(
            "Market Query",
            placeholder="Show me the YTD gain of 10 largest technology companies as of today",
            key="market_query",
            help="Enter your stock market query"
        )
        
        query_type = st.selectbox(
            "Query Type",
            options=[
                "Stock Performance",
                "Market Trends",
                "Sector Analysis",
                "Custom Query"
            ],
            key="query_type"
        )
        
        if st.button("📊 Analyze Market", key="analyze_market"):
            if not market_query:
                st.error("❌ Please enter a market query")
            elif not st.session_state.agent_initialized:
                st.error("❌ Please initialize the agent first")
            else:
                st.session_state.current_task = {
                    "type": "stock_market",
                    "query": market_query,
                    "query_type": query_type
                }
                st.session_state.execution_in_progress = True
    
    with tab3:
        st.markdown("### Web Research")
        
        research_topic = st.text_area(
            "Research Topic",
            placeholder="Research the latest developments in AI safety",
            key="research_topic",
            help="Enter the topic you want to research"
        )
        
        research_depth = st.select_slider(
            "Research Depth",
            options=["Quick Overview", "Moderate Detail", "Deep Analysis"],
            value="Moderate Detail",
            key="research_depth"
        )
        
        if st.button("🔍 Start Research", key="start_research"):
            if not research_topic:
                st.error("❌ Please enter a research topic")
            elif not st.session_state.agent_initialized:
                st.error("❌ Please initialize the agent first")
            else:
                st.session_state.current_task = {
                    "type": "web_research",
                    "topic": research_topic,
                    "depth": research_depth
                }
                st.session_state.execution_in_progress = True
    
    with tab4:
        st.markdown("### Custom Task")
        
        custom_task = st.text_area(
            "Your Custom Task",
            placeholder="Enter your custom task description...",
            key="custom_task",
            height=150,
            help="Describe any custom task for the agents to execute"
        )
        
        if st.button("⚙️ Execute Task", key="execute_custom"):
            if not custom_task:
                st.error("❌ Please enter a task description")
            elif not st.session_state.agent_initialized:
                st.error("❌ Please initialize the agent first")
            else:
                st.session_state.current_task = {
                    "type": "custom",
                    "task": custom_task
                }
                st.session_state.execution_in_progress = True


def execute_task(task: Dict[str, Any]):
    """Execute the selected task"""
    try:
        agent_manager = st.session_state.agent_manager
        if not agent_manager:
            st.error("❌ Agent manager not available")
            return
        
        task_executor = TaskExecutor(agent_manager)
        
        with st.spinner("Executing task... This may take a moment."):
            if task["type"] == "paper_analysis":
                result = task_executor.execute_paper_analysis(task["url"])
            
            elif task["type"] == "stock_market":
                result = task_executor.execute_stock_market_analysis(task["query"])
            
            elif task["type"] == "web_research":
                result = task_executor.execute_web_research(task["topic"])
            
            elif task["type"] == "custom":
                result = task_executor.execute_custom_task(task["task"])
            
            else:
                result = "❌ Unknown task type"
        
        return result
    
    except Exception as e:
        return f"❌ Error executing task: {str(e)}"


def render_conversation_view():
    """Render conversation history and results"""
    if not st.session_state.current_task:
        return
    
    st.markdown("## 💬 Conversation & Results")
    
    # Task details
    with st.expander("📋 Task Details", expanded=True):
        st.json(st.session_state.current_task)
    
    # Execute task if in progress
    if st.session_state.execution_in_progress:
        result = execute_task(st.session_state.current_task)
        
        if result:
            st.markdown("### Response")
            
            if "❌" in result:
                st.error(result)
            elif "✅" in result:
                st.success(result)
            else:
                # Display result with formatting
                st.markdown(result)
            
            # Store in history
            st.session_state.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "task": st.session_state.current_task,
                "result": result
            })
        
        st.session_state.execution_in_progress = False
    
    # Conversation history
    if st.session_state.conversation_history:
        st.markdown("### 📜 History")
        
        for i, item in enumerate(st.session_state.conversation_history, 1):
            with st.expander(f"Conversation {i} - {item['timestamp'][:19]}"):
                st.markdown("**Task:**")
                st.json(item["task"])
                st.markdown("**Result:**")
                st.markdown(item["result"])
        
        # Export options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Export as JSON"):
                json_data = json.dumps(st.session_state.conversation_history, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name="conversation_history.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("🗑️ Clear History"):
                st.session_state.conversation_history = []
                if st.session_state.agent_manager:
                    st.session_state.agent_manager.clear_history()
                st.success("✅ History cleared")
                st.rerun()
        
        with col3:
            if st.button("📊 View Statistics"):
                st.session_state.show_stats = True


def render_statistics():
    """Render performance statistics"""
    st.markdown("## 📊 Statistics")
    
    if st.session_state.agent_manager:
        stats = st.session_state.agent_manager.get_performance_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Operations", stats.get("total_operations", 0))
        
        with col2:
            st.metric(
                "Avg Duration (ms)",
                f"{stats.get('average_duration_ms', 0):.2f}"
            )
        
        with col3:
            st.metric(
                "Total Duration (ms)",
                f"{stats.get('total_duration_ms', 0):.2f}"
            )
        
        with col4:
            st.metric(
                "Success Rate",
                f"{stats.get('success_rate', 0):.1f}%"
            )
    
    # Conversation summary
    if st.session_state.agent_manager:
        summary = st.session_state.agent_manager.get_conversation_summary()
        
        st.markdown("### Conversation Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Messages", summary.get("total_messages", 0))
        
        with col2:
            st.metric("Duration (seconds)", f"{summary.get('duration_seconds', 0):.2f}")
        
        with col3:
            st.metric("Participants", len(summary.get("senders", [])))


def main():
    """Main application logic"""
    render_header()
    render_sidebar()
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    if not st.session_state.agent_initialized:
        st.warning("""
        ### ⚠️ Agent Not Initialized
        
        Please click the **Initialize Agent** button in the sidebar to get started.
        The agent needs to be initialized before you can execute tasks.
        """)
        return
    
    # Display main interface
    render_task_selection()
    render_conversation_view()
    render_statistics()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        <p>🤖 AutoGen Web Info Agent | Enhanced with Advanced Interactive UI</p>
        <p>Powered by AutoGen & Streamlit</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
