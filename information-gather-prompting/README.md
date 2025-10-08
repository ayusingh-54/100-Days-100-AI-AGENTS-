# 🤖 AI Prompt Generator - Backend & Frontend

A professional, production-ready application for generating AI prompt templates using LangChain, LangGraph, and Streamlit.

## 📁 Project Structure

```
information-gather-prompting/
├── backend.py                 # Backend logic with LangChain/LangGraph
├── app.py                     # Streamlit frontend application
├── information-gather-prompting.ipynb  # Jupyter notebook version
├── README.md                  # This file
└── requirements.txt           # Python dependencies (in parent folder)
```

## 🎯 Features

### Backend (`backend.py`)

- **Modular Architecture**: Clean separation of concerns with type-safe code
- **State Management**: LangGraph-based workflow with checkpointing
- **Session Handling**: Multi-session support with conversation tracking
- **Tool Integration**: Pydantic models for structured information extraction
- **Two-Phase System**:
  1. **Information Gathering**: Collects requirements through natural conversation
  2. **Prompt Generation**: Creates professional prompt templates

### Frontend (`app.py`)

- **Modern UI**: Beautiful, responsive interface with custom CSS
- **Real-time Chat**: Interactive conversation with AI agent
- **Session Management**: Create, reset, and track multiple sessions
- **Export Options**: Download prompts in TXT, MD, or JSON format
- **Analytics Dashboard**: View conversation statistics and metrics
- **History View**: Full conversation history with easy navigation
- **Phase Tracking**: Visual indicators for current workflow phase

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8 or higher
python --version

# OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

### Installation

1. **Clone the repository** (if you haven't):

```bash
git clone https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-.git
cd 100-Days-100-AI-AGENTS-/information-gather-prompting
```

2. **Install dependencies**:

```bash
pip install -r ../requirements.txt

# Additional dependencies for this project:
pip install langchain langchain-openai langgraph streamlit python-dotenv pydantic typing-extensions
```

3. **Set up environment variables**:

```bash
# Create .env file in the parent directory
echo "OPENAI_API_KEY=your-api-key-here" > ../.env
```

### Running the Application

#### Option 1: Streamlit Frontend (Recommended)

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

#### Option 2: Backend Testing

```bash
python backend.py
```

This runs a test conversation to verify the backend is working.

#### Option 3: Jupyter Notebook

```bash
jupyter notebook information-gather-prompting.ipynb
```

## 📖 Usage Guide

### Using the Streamlit App

1. **Start a Conversation**:

   - Type your message in the input box
   - Example: "I need a prompt for code review"

2. **Answer Questions**:

   - The AI will ask about:
     - Main objective
     - Variables needed
     - Constraints (what NOT to do)
     - Requirements (what MUST be done)

3. **Get Your Prompt**:

   - Once all info is gathered, AI generates your prompt
   - Review the generated template
   - Export in your preferred format

4. **Manage Sessions**:
   - **New Conversation**: Click "🔄 New Conversation" in sidebar
   - **View History**: Click "📜 History" to see full conversation
   - **Analytics**: Click "📈 Analytics" for session metrics

### Using the Backend API

```python
from backend import get_backend

# Initialize backend
backend = get_backend()

# Create a session
session_id = backend.create_session()

# Send messages
response = backend.send_message(
    "I want to create a prompt for data analysis",
    session_id
)

print(response['response'])

# Get conversation history
history = backend.get_conversation_history(session_id)

# Reset session
backend.reset_session(session_id)
```

## 🏗️ Architecture

### Backend Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PromptGenerationBackend                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────┐    ┌───────────────┐    ┌────────────┐ │
│  │ Configuration │    │  Data Models  │    │   LLM      │ │
│  │  - Templates  │    │  - PromptInfo │    │  - GPT-4   │ │
│  │  - Constants  │    │  - State      │    │  - Temp=0  │ │
│  └───────────────┘    └───────────────┘    └────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              LangGraph Workflow                       │ │
│  │                                                       │ │
│  │   START → info_gathering → [Conditional]             │ │
│  │                              ├─→ add_tool_message    │ │
│  │                              │   → prompt_generation │ │
│  │                              │   → END               │ │
│  │                              ├─→ info (loop)         │ │
│  │                              └─→ END                 │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────┐    ┌───────────────┐    ┌────────────┐ │
│  │ Helper Funcs  │    │     Nodes     │    │  Session   │ │
│  │  - Message    │    │  - Info Node  │    │ Management │ │
│  │    Processing │    │  - Prompt Node│    │            │ │
│  └───────────────┘    └───────────────┘    └────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Frontend Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Streamlit Application                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌──────────────┐   │
│  │   Header    │    │   Sidebar   │    │ Main Content │   │
│  │  - Title    │    │  - Controls │    │  - Chat UI   │   │
│  │  - Branding │    │  - Metrics  │    │  - Messages  │   │
│  └─────────────┘    │  - Features │    │  - Input     │   │
│                     └─────────────┘    └──────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Session State Management               │   │
│  │  - Backend instance                                 │   │
│  │  - Session ID                                       │   │
│  │  - Message history                                  │   │
│  │  - Current phase                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ History  │  │Analytics │  │  Export  │  │  Themes  │   │
│  │  Panel   │  │  Panel   │  │ Options  │  │ & Styles │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Configuration

### Backend Configuration

Edit `backend.py` to customize:

```python
# Change LLM model
backend = PromptGenerationBackend(
    model="gpt-3.5-turbo",  # Use GPT-3.5 for faster/cheaper
    temperature=0.3          # Add creativity
)

# Modify system prompts
INFO_GATHERING_TEMPLATE = """Your custom instructions..."""
PROMPT_GENERATION_TEMPLATE = """Your custom template..."""
```

### Frontend Configuration

Edit `app.py` to customize:

```python
# Page configuration
st.set_page_config(
    page_title="Your Title",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS in load_custom_css() function
```

## 📊 API Reference

### Backend API

#### `PromptGenerationBackend`

**Methods:**

- `create_session() -> str`

  - Creates a new conversation session
  - Returns: Session ID

- `send_message(message: str, session_id: str) -> Dict`

  - Sends a message and gets AI response
  - Returns: Dictionary with response, phase, and metadata

- `get_conversation_history(session_id: str) -> List[Dict]`

  - Retrieves full conversation history
  - Returns: List of message dictionaries

- `reset_session(session_id: str) -> None`

  - Resets a session and clears history

- `get_session_metadata(session_id: str) -> ConversationMetadata`
  - Gets metadata for a session
  - Returns: Metadata object with statistics

### Frontend Components

#### Main Functions

- `initialize_session_state()`: Initialize Streamlit session variables
- `render_header()`: Render application header
- `render_sidebar()`: Render sidebar with controls
- `render_chat_interface()`: Render main chat interface
- `process_user_message(message)`: Process user input
- `export_prompt(text, format)`: Export prompt in various formats

## 💡 Use Cases

### 1. Code Review Prompts

```
Objective: Review code for best practices
Variables: code_snippet, language, focus_areas
Constraints: Don't suggest major refactoring
Requirements: Provide line numbers and explanations
```

### 2. Content Generation

```
Objective: Generate SEO-optimized blog posts
Variables: topic, keywords, target_audience, word_count
Constraints: Avoid controversial topics
Requirements: Include meta description
```

### 3. Data Analysis

```
Objective: Analyze datasets and provide insights
Variables: dataset, metrics, business_questions
Constraints: Don't make unfounded assumptions
Requirements: Include visualizations and statistics
```

### 4. Translation

```
Objective: Translate text with context preservation
Variables: text, source_lang, target_lang, domain
Constraints: Maintain formatting
Requirements: Cultural adaptation
```

## 🎨 Customization Guide

### Adding New Export Formats

Edit `app.py`:

```python
def export_prompt(prompt_text: str, format: str = "txt"):
    # Add your custom format
    elif format == "yaml":
        import yaml
        return yaml.dump({"prompt": prompt_text})
```

### Custom Styling

Edit CSS in `load_custom_css()`:

```python
st.markdown("""
    <style>
    .your-custom-class {
        /* Your styles */
    }
    </style>
""", unsafe_allow_html=True)
```

### Adding Analytics

Extend the `render_analytics_panel()` function:

```python
def render_analytics_panel():
    # Add charts with plotly or matplotlib
    import plotly.express as px
    fig = px.line(data)
    st.plotly_chart(fig)
```

## 🐛 Troubleshooting

### Common Issues

**Issue 1: Import Error**

```bash
ModuleNotFoundError: No module named 'langchain'
```

**Solution**: Install dependencies

```bash
pip install -r ../requirements.txt
```

**Issue 2: OpenAI API Error**

```bash
OpenAIError: The api_key client option must be set
```

**Solution**: Set environment variable

```bash
export OPENAI_API_KEY="your-key"
# Or create .env file
```

**Issue 3: Streamlit Connection Error**

```bash
Error: Unable to connect to Streamlit server
```

**Solution**: Check port availability

```bash
streamlit run app.py --server.port 8502
```

## 📈 Performance Optimization

### Backend Optimization

1. **Use GPT-3.5 for faster responses**:

```python
backend = PromptGenerationBackend(model="gpt-3.5-turbo")
```

2. **Implement caching**:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_generation(prompt_key):
    # Your logic
```

3. **Batch processing**:

```python
# Process multiple prompts in parallel
```

### Frontend Optimization

1. **Use Streamlit caching**:

```python
@st.cache_data
def load_data():
    # Expensive operation
```

2. **Lazy loading**:

```python
# Load components only when needed
if st.session_state.show_analytics:
    render_analytics_panel()
```

## 🧪 Testing

### Backend Testing

```bash
# Run backend tests
python backend.py

# Expected output:
# ✅ Backend initialized
# ✅ Session created
# 👤 User: [test messages]
# 🤖 Agent: [responses]
```

### Frontend Testing

```bash
# Run Streamlit app
streamlit run app.py

# Manual testing checklist:
# ✅ Chat interface loads
# ✅ Messages send/receive
# ✅ Phase transitions work
# ✅ Export functions work
# ✅ Session reset works
```

## 📝 Code Quality

### Type Safety

- ✅ Full type hints throughout both files
- ✅ Pydantic models for data validation
- ✅ TypedDict for state management

### Documentation

- ✅ Comprehensive docstrings for all functions
- ✅ Inline comments explaining complex logic
- ✅ Architecture diagrams and flowcharts

### Best Practices

- ✅ Single Responsibility Principle
- ✅ DRY (Don't Repeat Yourself)
- ✅ Error handling and validation
- ✅ Modular code structure

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper comments
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the "100 Days - 100 AI Agents" initiative.

## 🙏 Acknowledgments

- **LangChain**: For the amazing LLM framework
- **LangGraph**: For state-based workflow orchestration
- **Streamlit**: For the beautiful UI framework
- **OpenAI**: For GPT-4 API

## 📞 Support

- **GitHub Issues**: [Report bugs](https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-/issues)
- **Documentation**: See this README and inline code comments
- **Examples**: Check `backend.py` main section for usage examples

---

**Made with ❤️ as part of 100 Days - 100 AI Agents Challenge**

🌟 **Star this repo if you find it helpful!**
