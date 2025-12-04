"""
================================================================================
APP.PY - Streamlit Frontend for Prompt Generation AI Agent
================================================================================

This is an advanced, dynamic Streamlit application that provides an intuitive
interface for the Prompt Generation AI Agent. It features:

- Modern, responsive UI with custom styling
- Real-time conversation with AI
- Session management and conversation history
- Export functionality for generated prompts
- Advanced features like conversation reset, history view, and analytics
- Dark/light mode support
- Interactive visualizations

Author: AI Agent Development Team
Version: 1.0.0
Date: October 2025
================================================================================
"""

import streamlit as st
import os
from datetime import datetime
from typing import List, Dict
import json

# Import backend
from backend import get_backend, PromptGenerationBackend


# ============================================================================
# PAGE CONFIGURATION - Must be the first Streamlit command
# ============================================================================

st.set_page_config(
    page_title="AI Prompt Generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-',
        'Report a bug': 'https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-/issues',
        'About': '# AI Prompt Generator\nPowered by LangChain & LangGraph'
    }
)


# ============================================================================
# CUSTOM CSS - Modern styling for the application
# ============================================================================

def load_custom_css():
    """
    Load custom CSS for enhanced UI styling.
    Provides modern design elements, animations, and responsive layout.
    """
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
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .header-title {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .header-subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        /* Chat message styling */
        .user-message {
            background-color: #e3f2fd;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border-left: 4px solid #2196f3;
        }
        
        .assistant-message {
            background-color: #f3e5f5;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border-left: 4px solid #9c27b0;
        }
        
        /* Sidebar styling */
        .sidebar-section {
            padding: 1rem;
            background-color: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        /* Metrics styling */
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin: 0.5rem 0;
        }
        
        /* Button styling */
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        /* Input styling */
        .stTextInput>div>div>input {
            border-radius: 8px;
        }
        
        /* Info boxes */
        .info-box {
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        .success-box {
            background-color: #d4edda;
            border-left: 4px solid #28a745;
        }
        
        .warning-box {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
        }
        
        .info-box-content {
            color: #333;
        }
        
        /* Animation for new messages */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .fade-in {
            animation: fadeIn 0.3s ease-in;
        }
        
        /* Phase indicator */
        .phase-indicator {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .phase-gathering {
            background-color: #fff3cd;
            color: #856404;
        }
        
        .phase-generating {
            background-color: #d4edda;
            color: #155724;
        }
        </style>
    """, unsafe_allow_html=True)


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state():
    """
    Initialize Streamlit session state variables.
    This ensures all necessary state is available throughout the app lifecycle.
    """
    # Backend instance
    if 'backend' not in st.session_state:
        st.session_state.backend = get_backend()
    
    # Session management
    if 'session_id' not in st.session_state:
        st.session_state.session_id = st.session_state.backend.create_session()
    
    # Conversation history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Phase tracking
    if 'current_phase' not in st.session_state:
        st.session_state.current_phase = "info_gathering"
    
    # Statistics
    if 'total_messages' not in st.session_state:
        st.session_state.total_messages = 0
    
    # Generated prompts history
    if 'generated_prompts' not in st.session_state:
        st.session_state.generated_prompts = []
    
    # UI state
    if 'show_history' not in st.session_state:
        st.session_state.show_history = False
    
    if 'show_analytics' not in st.session_state:
        st.session_state.show_analytics = False


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def reset_conversation():
    """
    Reset the current conversation and start a new session.
    Clears all messages and creates a fresh session ID.
    """
    # Reset backend session
    st.session_state.backend.reset_session(st.session_state.session_id)
    
    # Create new session
    st.session_state.session_id = st.session_state.backend.create_session()
    
    # Clear UI state
    st.session_state.messages = []
    st.session_state.current_phase = "info_gathering"
    
    st.success("✅ Conversation reset! Start a new prompt generation.")


def export_prompt(prompt_text: str, format: str = "txt"):
    """
    Export the generated prompt in various formats.
    
    Args:
        prompt_text: The prompt text to export
        format: Export format (txt, md, json)
    
    Returns:
        Formatted content for download
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == "txt":
        return prompt_text
    
    elif format == "md":
        return f"""# Generated Prompt
        
**Generated on:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Prompt Template

{prompt_text}

---

*Generated by AI Prompt Generator*
"""
    
    elif format == "json":
        return json.dumps({
            "prompt": prompt_text,
            "generated_at": datetime.now().isoformat(),
            "session_id": st.session_state.session_id
        }, indent=2)


def get_phase_badge(phase: str) -> str:
    """
    Get HTML badge for current phase.
    
    Args:
        phase: Current conversation phase
    
    Returns:
        HTML string for phase badge
    """
    if phase == "info_gathering":
        return '<span class="phase-indicator phase-gathering">📝 Gathering Requirements</span>'
    else:
        return '<span class="phase-indicator phase-generating">✨ Generating Prompt</span>'


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_header():
    """
    Render the application header with title and description.
    """
    st.markdown("""
        <div class="header-container">
            <div class="header-title">🤖 AI Prompt Generator</div>
            <div class="header-subtitle">
                Create professional prompt templates with AI assistance
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """
    Render the sidebar with controls, statistics, and information.
    """
    with st.sidebar:
        # Logo and branding
        st.markdown("### 🎯 Controls")
        
        # New conversation button
        if st.button("🔄 New Conversation", use_container_width=True):
            reset_conversation()
            st.rerun()
        
        st.markdown("---")
        
        # Session info
        st.markdown("### 📊 Session Info")
        
        metadata = st.session_state.backend.get_session_metadata(
            st.session_state.session_id
        )
        
        if metadata:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Messages", metadata.message_count)
            with col2:
                st.metric("Phase", "1️⃣" if metadata.phase == "info_gathering" else "2️⃣")
            
            st.caption(f"Started: {metadata.started_at.strftime('%H:%M:%S')}")
        
        st.markdown("---")
        
        # Features section
        st.markdown("### ✨ Features")
        
        # Toggle buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📜 History", use_container_width=True):
                st.session_state.show_history = not st.session_state.show_history
                st.rerun()
        
        with col2:
            if st.button("📈 Analytics", use_container_width=True):
                st.session_state.show_analytics = not st.session_state.show_analytics
                st.rerun()
        
        st.markdown("---")
        
        # How it works
        with st.expander("❓ How It Works"):
            st.markdown("""
            **Phase 1: Information Gathering**
            - Tell the AI what kind of prompt you need
            - It will ask clarifying questions about:
              - Objective
              - Variables needed
              - Constraints
              - Requirements
            
            **Phase 2: Prompt Generation**
            - AI generates a professional prompt template
            - Review and refine if needed
            - Export in multiple formats
            """)
        
        # Tips
        with st.expander("💡 Tips for Best Results"):
            st.markdown("""
            - **Be specific** about your use case
            - **List all variables** you'll need
            - **Define constraints** clearly
            - **Specify requirements** for quality output
            - **Provide examples** if helpful
            """)
        
        st.markdown("---")
        
        # Footer
        st.markdown("""
            <div style='text-align: center; color: #666; font-size: 0.8rem;'>
                <p>Powered by</p>
                <p><strong>LangChain + LangGraph</strong></p>
                <p>🌟 Part of 100 Days - 100 AI Agents</p>
            </div>
        """, unsafe_allow_html=True)


def render_chat_interface():
    """
    Render the main chat interface with conversation history.
    """
    # Phase indicator
    st.markdown(
        get_phase_badge(st.session_state.current_phase), 
        unsafe_allow_html=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display conversation history
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                    <div class="user-message fade-in">
                        <strong>👤 You:</strong><br>
                        {message["content"]}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="assistant-message fade-in">
                        <strong>🤖 AI Assistant:</strong><br>
                        {message["content"]}
                    </div>
                """, unsafe_allow_html=True)
    
    # Input area
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Chat input
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_input = st.text_input(
                "Type your message...",
                placeholder="Describe what kind of prompt you need...",
                label_visibility="collapsed"
            )
        
        with col2:
            submit_button = st.form_submit_button("Send 📤", use_container_width=True)
    
    # Process input
    if submit_button and user_input:
        process_user_message(user_input)
        st.rerun()


def render_history_panel():
    """
    Render the conversation history panel in an expandable section.
    """
    if st.session_state.show_history:
        st.markdown("### 📜 Conversation History")
        
        history = st.session_state.backend.get_conversation_history(
            st.session_state.session_id
        )
        
        if history:
            with st.expander("View Full History", expanded=True):
                for i, msg in enumerate(history, 1):
                    role = "👤 You" if msg["role"] == "user" else "🤖 AI"
                    st.markdown(f"**{i}. {role}:**")
                    st.text(msg["content"])
                    st.markdown("---")
        else:
            st.info("No conversation history yet. Start chatting!")


def render_analytics_panel():
    """
    Render analytics and statistics panel.
    """
    if st.session_state.show_analytics:
        st.markdown("### 📈 Analytics")
        
        metadata = st.session_state.backend.get_session_metadata(
            st.session_state.session_id
        )
        
        if metadata:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Messages",
                    metadata.message_count,
                    delta=None
                )
            
            with col2:
                duration = (metadata.last_updated - metadata.started_at).seconds
                st.metric(
                    "Duration (sec)",
                    duration,
                    delta=None
                )
            
            with col3:
                phase_display = "Phase 1" if metadata.phase == "info_gathering" else "Phase 2"
                st.metric(
                    "Current Phase",
                    phase_display,
                    delta=None
                )
            
            # Conversation timeline
            st.markdown("#### 📊 Session Timeline")
            st.markdown(f"""
            - **Started:** {metadata.started_at.strftime('%Y-%m-%d %H:%M:%S')}
            - **Last Updated:** {metadata.last_updated.strftime('%Y-%m-%d %H:%M:%S')}
            - **Status:** {'Gathering Info' if metadata.phase == 'info_gathering' else 'Generating Prompt'}
            """)


def render_export_section():
    """
    Render export options for generated prompts.
    """
    # Check if we have any generated prompts in conversation
    if st.session_state.messages:
        last_message = st.session_state.messages[-1]
        
        # If last message is from assistant and we're past info gathering
        if (last_message["role"] == "assistant" and 
            st.session_state.current_phase == "prompt_generation"):
            
            st.markdown("### 💾 Export Generated Prompt")
            
            col1, col2, col3 = st.columns(3)
            
            prompt_text = last_message["content"]
            
            with col1:
                st.download_button(
                    label="📄 Download as TXT",
                    data=export_prompt(prompt_text, "txt"),
                    file_name=f"prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                st.download_button(
                    label="📝 Download as MD",
                    data=export_prompt(prompt_text, "md"),
                    file_name=f"prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            
            with col3:
                st.download_button(
                    label="🔧 Download as JSON",
                    data=export_prompt(prompt_text, "json"),
                    file_name=f"prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )


# ============================================================================
# BUSINESS LOGIC
# ============================================================================

def process_user_message(user_input: str):
    """
    Process user message and get AI response.
    
    Args:
        user_input: User's message text
    """
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Show spinner while processing
    with st.spinner("🤔 AI is thinking..."):
        try:
            # Send message to backend
            response = st.session_state.backend.send_message(
                user_input,
                st.session_state.session_id
            )
            
            # Update phase
            st.session_state.current_phase = response["phase"]
            
            # Add AI response to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["response"]
            })
            
            # Update statistics
            st.session_state.total_messages += 2
            
            # Store generated prompt if in generation phase
            if response["phase"] == "prompt_generation":
                st.session_state.generated_prompts.append({
                    "prompt": response["response"],
                    "timestamp": datetime.now(),
                    "session_id": st.session_state.session_id
                })
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """
    Main application entry point.
    Orchestrates all UI components and application flow.
    """
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Create layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Main chat interface
        render_chat_interface()
        
        # Export section
        render_export_section()
    
    with col2:
        # History panel
        render_history_panel()
        
        # Analytics panel
        render_analytics_panel()
    
    # Render sidebar
    render_sidebar()
    
    # Welcome message if no conversation started
    if len(st.session_state.messages) == 0:
        st.markdown("""
            <div class="info-box success-box">
                <div class="info-box-content">
                    <h4>👋 Welcome to AI Prompt Generator!</h4>
                    <p>I'll help you create professional prompt templates for your AI applications.</p>
                    <p><strong>Get started by telling me:</strong></p>
                    <ul>
                        <li>What kind of prompt do you need?</li>
                        <li>What's the main objective?</li>
                        <li>What variables will you use?</li>
                    </ul>
                    <p>Let's create something amazing together! 🚀</p>
                </div>
            </div>
        """, unsafe_allow_html=True)


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()
