# 🤖 AutoGen Web Info Agent - Improved & Enhanced

An advanced interactive agent system built with **AutoGen** and **Streamlit** that can intelligently perform complex tasks requiring web information acquisition, analysis, and synthesis.

## ✨ Features

### Core Capabilities

- 📄 **Research Paper Analysis** - Analyze academic papers from URLs with intelligent insights
- 📈 **Stock Market Analysis** - Get real-time market data and financial insights
- 🔍 **Web Research** - Research any topic comprehensively on the web
- ⚙️ **Custom Tasks** - Execute any custom task using intelligent agents
- 💬 **Multi-Agent Conversation** - Agents collaborate to solve complex problems

### Advanced Improvements

- **Robust Error Handling** - Comprehensive exception management with retry logic
- **Input Validation** - Sanitization and validation of all user inputs
- **Performance Monitoring** - Track operation metrics and performance statistics
- **Conversation History** - Full audit trail of all conversations
- **Docker Support** - Safe code execution in isolated containers
- **Logging & Debugging** - Detailed logging for troubleshooting
- **State Management** - Persistent session state management

### Interactive UI Features

- **Advanced Streamlit Interface** - Beautiful, responsive design with multiple tabs
- **Real-time Status Updates** - Live feedback during task execution
- **Conversation Export** - Export conversations as JSON for documentation
- **Performance Dashboard** - Visual metrics and statistics
- **Task Templates** - Pre-configured templates for common tasks
- **Configuration Panel** - Easy adjustment of agent parameters

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key or valid OAI_CONFIG_LIST configuration

### Installation

1. **Navigate to the project directory:**

```bash
cd "C:\Users\ayusi\Desktop\AGENTS\07"
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**

```bash
# Create a .env file
cp .env.template .env

# Edit .env and add your configuration
notepad .env
```

4. **Run the Streamlit application:**

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## 📋 Configuration

### Environment Variables

Create a `.env` file in the project directory:

```env
# API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OAI_CONFIG_LIST=path_to_config_json_or_json_string

# Agent Configuration
API_TIMEOUT=600
CACHE_SEED=42
LLM_TEMPERATURE=0.0
MAX_CONSECUTIVE_AUTO_REPLY=10

# Execution Configuration
USE_DOCKER=False
WORK_DIR=./work_dir

# Logging
LOG_LEVEL=INFO
LOG_FILE=agent.log
```

### Configuration Options

| Variable                     | Default | Description                                     |
| ---------------------------- | ------- | ----------------------------------------------- |
| `API_TIMEOUT`                | 600     | API request timeout in seconds                  |
| `CACHE_SEED`                 | 42      | Cache seed for reproducible results             |
| `LLM_TEMPERATURE`            | 0.0     | Controls randomness (0=deterministic, 2=random) |
| `MAX_CONSECUTIVE_AUTO_REPLY` | 10      | Max agent retry attempts                        |
| `USE_DOCKER`                 | False   | Use Docker for safe code execution              |
| `LOG_LEVEL`                  | INFO    | Logging level (DEBUG, INFO, WARNING, ERROR)     |

## 📖 Usage Guide

### 1. Initialize the Agent

Click the **🚀 Initialize Agent** button in the sidebar. This will:

- Load your API configuration
- Create the Assistant Agent (LLM-based)
- Create the User Proxy Agent (code executor)
- Verify all connections

### 2. Select a Task Type

Choose from predefined task types:

#### Paper Analysis

- Provide a research paper URL (e.g., ArXiv)
- Select analysis aspects
- The agent will read and analyze the paper

#### Stock Market Analysis

- Enter your market query
- Select query type (performance, trends, etc.)
- Get comprehensive market analysis

#### Web Research

- Enter your research topic
- Select research depth
- Get detailed research findings

#### Custom Task

- Describe any custom task
- The agent will work to solve it

### 3. Execute & Review

- Click the execution button to start
- Monitor progress in real-time
- View conversation history
- Review extracted findings

### 4. Export Results

- Download conversation as JSON
- Export for documentation or further analysis
- View performance statistics

## 🏗️ Architecture

### Project Structure

```
07/
├── app.py                    # Main Streamlit application
├── backend.py                # Agent management and task execution
├── config.py                 # Configuration management
├── utils.py                  # Utility functions and helpers
├── requirements.txt          # Python dependencies
├── .env.template             # Environment variable template
└── README.md                 # This file
```

### Core Components

#### `config.py` - Configuration Management

- Centralized configuration
- Environment variable handling
- Task templates
- Configuration validation

#### `utils.py` - Utility Modules

- **Logger** - Structured logging
- **MessageProcessor** - Message parsing and formatting
- **ConversationManager** - History management
- **ErrorHandler** - Error handling and recovery
- **TaskValidator** - Input validation
- **PerformanceMonitor** - Performance tracking

#### `backend.py` - Agent Management

- **AutoGenAgentManager** - Main agent orchestration
- **TaskExecutor** - Task-specific execution
- Agent initialization and setup
- Error handling and recovery
- Performance monitoring

#### `app.py` - Streamlit UI

- Interactive interface
- Task selection and configuration
- Conversation display
- Performance dashboard
- Export functionality

## 🔧 Advanced Features

### Error Handling & Recovery

The system includes robust error handling:

```python
# Automatic retry on transient errors
# User-friendly error messages
# Detailed logging for debugging
# Graceful degradation
```

### Input Validation

All user inputs are validated:

```python
# URL format validation
# Query length validation
# Input sanitization (prevents injection)
# File size limits
```

### Performance Monitoring

Track performance metrics:

```python
# Operation timing
# Success rates
# Resource usage
# Cache efficiency
```

### Conversation Management

Full conversation tracking:

```python
# Message history
# Conversation summaries
# JSON export
# Timestamp tracking
```

## 🔐 Security Features

- **Input Sanitization** - Removes potentially dangerous patterns
- **Docker Isolation** - Optional Docker container execution
- **API Key Management** - Secure key handling
- **Error Message Filtering** - No sensitive data in error messages
- **File Access Control** - Limited work directory access

## 📊 Performance Optimization

The system includes several optimizations:

1. **Caching** - Configurable LLM response caching
2. **Connection Pooling** - Reused HTTP connections
3. **Async Operations** - Non-blocking where possible
4. **Resource Management** - Proper cleanup of resources
5. **Memory Efficiency** - Streaming for large responses

## 🐛 Troubleshooting

### Agent Fails to Initialize

**Problem**: Agent initialization fails
**Solution**:

1. Verify API key in `.env`
2. Check internet connectivity
3. Ensure OPENAI_API_KEY or OAI_CONFIG_LIST is set
4. Check logs for detailed error message

### Task Execution Times Out

**Problem**: Tasks take too long or timeout
**Solution**:

1. Increase `API_TIMEOUT` in config
2. Try simpler queries first
3. Check internet connectivity
4. Verify API quota/limits

### Code Execution Errors

**Problem**: Code execution fails
**Solution**:

1. Enable Docker for safer execution
2. Check `USE_DOCKER=True` in config
3. Verify Docker is running
4. Check logs for stack traces

### Memory Issues

**Problem**: High memory usage
**Solution**:

1. Clear conversation history
2. Reduce context window
3. Use Docker isolation
4. Restart the application

## 📚 Examples

### Example 1: Analyze a Research Paper

1. Click **Paper Analysis** tab
2. Enter: `https://arxiv.org/abs/2308.08155`
3. Select aspects to analyze
4. Click **Analyze Paper**

### Example 2: Stock Market Analysis

1. Click **Stock Market** tab
2. Enter: `What are the top performing tech stocks in 2024?`
3. Select **Stock Performance** as query type
4. Click **Analyze Market**

### Example 3: Web Research

1. Click **Web Research** tab
2. Enter: `Latest developments in quantum computing`
3. Select **Deep Analysis** depth
4. Click **Start Research**

## 🔄 Advanced Configuration

### Using Docker for Execution

For safer code execution in isolated containers:

```env
USE_DOCKER=True
```

Requires Docker to be installed and running on your system.

### Custom Model Selection

Modify `Config.DEFAULT_MODELS` in `config.py`:

```python
DEFAULT_MODELS = ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo-16k"]
```

### Adjusting Agent Behavior

Modify LLM config in `config.py`:

```python
LLM_TEMPERATURE=0.7  # More creative responses
API_TIMEOUT=900      # Longer timeout
MAX_CONSECUTIVE_AUTO_REPLY=15  # More retries
```

## 📈 Performance Metrics

The application tracks:

- **Total Operations** - Number of agent operations
- **Average Duration** - Average operation time
- **Total Duration** - Cumulative operation time
- **Success Rate** - Percentage of successful operations
- **Conversation Stats** - Message counts and duration

## 🤝 Contributing

To extend the system:

1. **Add New Task Types** - Update `Config.TASK_TEMPLATES`
2. **Custom Validators** - Add to `TaskValidator` class
3. **New Utilities** - Extend `utils.py`
4. **UI Enhancements** - Modify `app.py`

## 📝 Logging

Logs are written to:

- Console output (real-time)
- `agent.log` file (persistent)

Log level controlled by `LOG_LEVEL` environment variable:

- `DEBUG` - Detailed debugging information
- `INFO` - General information
- `WARNING` - Warning messages
- `ERROR` - Error messages

## 🎯 Best Practices

1. **Initialize Agent First** - Always click "Initialize Agent" before running tasks
2. **Validate Inputs** - Use proper URLs and clear queries
3. **Monitor Performance** - Check statistics regularly
4. **Export Results** - Save important conversations
5. **Review Logs** - Check logs for troubleshooting
6. **Use Docker** - Enable for production environments

## 📄 License

This project is part of the 100 Days 100 AI Agents initiative.

## 🙏 Acknowledgments

Built with:

- **AutoGen** - Multi-agent conversation framework by Microsoft
- **Streamlit** - Interactive web framework
- **OpenAI** - Language models and APIs

## 📞 Support

For issues or questions:

1. Check the troubleshooting section
2. Review logs in `agent.log`
3. Verify configuration in `.env`
4. Check internet connectivity

---

**Last Updated**: December 2024
**Version**: 2.0.0 (Enhanced & Improved)
