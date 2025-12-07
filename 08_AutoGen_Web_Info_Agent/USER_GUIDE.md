# 📖 Complete User Guide - AutoGen Web Info Agent v2.0

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Features Overview](#features-overview)
4. [UI Guide](#ui-guide)
5. [Task Types](#task-types)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Usage](#advanced-usage)

---

## Installation

### System Requirements

- Windows/Mac/Linux
- Python 3.8 or higher
- 4GB RAM minimum
- Internet connection
- OpenAI API key

### Step-by-Step Installation

#### 1. Navigate to Project Directory

```bash
cd "C:\Users\ayusi\Desktop\AGENTS\07"
```

#### 2. Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. Run Quick Start Setup

```bash
python quickstart.py
```

This will:

- Check Python version
- Create `.env` from template
- Install dependencies
- Verify installation
- Create work directory
- Validate configuration

#### 4. Add Your API Key

```bash
# Edit the .env file
notepad .env

# Add your OpenAI API key:
# OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
```

#### 5. Start the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

---

## Quick Start

### 30-Second Setup

1. **Initialize Agent**

   - Click "🚀 Initialize Agent" in sidebar
   - Wait for ✅ Agent Ready

2. **Choose Task**

   - Select from tabs: Paper, Stock, Research, Custom
   - Enter your input
   - Click execute button

3. **View Results**
   - See conversation in real-time
   - Review extracted findings
   - Export results if needed

---

## Features Overview

### 🎯 Core Features

| Feature            | Purpose                 | Access          |
| ------------------ | ----------------------- | --------------- |
| **Paper Analysis** | Analyze research papers | Papers tab      |
| **Stock Market**   | Financial analysis      | Market tab      |
| **Web Research**   | General web research    | Research tab    |
| **Custom Tasks**   | Any custom task         | Custom tab      |
| **Export**         | Save conversations      | Results section |
| **Statistics**     | View metrics            | Stats section   |
| **History**        | Conversation log        | History viewer  |
| **Configuration**  | Adjust settings         | Sidebar panel   |

### 🔒 Security Features

- ✅ Input validation
- ✅ Sanitization
- ✅ API key encryption
- ✅ Docker isolation option
- ✅ Error filtering

### 📊 Monitoring Features

- ✅ Performance tracking
- ✅ Operation timing
- ✅ Success rates
- ✅ Metrics dashboard
- ✅ Export statistics

---

## UI Guide

### Main Interface Layout

```
┌─────────────────────────────────────────────────────────┐
│                      HEADER                              │
│           🤖 AutoGen Web Info Agent                      │
│              Agent Status: ✅ Ready                      │
└─────────────────────────────────────────────────────────┘
         │                                    │
         │                                    │
    SIDEBAR                              MAIN CONTENT
  ┌──────────┐                         ┌──────────────┐
  │ Config   │                         │ Task Tabs    │
  │ Settings │                         │ - Paper      │
  │ Init Btn │                         │ - Market     │
  │ Help     │                         │ - Research   │
  │ About    │                         │ - Custom     │
  └──────────┘                         └──────────────┘
                                       ┌──────────────┐
                                       │ Results      │
                                       │ - Conv View  │
                                       │ - History    │
                                       │ - Export     │
                                       └──────────────┘
                                       ┌──────────────┐
                                       │ Statistics   │
                                       │ - Metrics    │
                                       │ - Charts     │
                                       └──────────────┘
```

### Sidebar Controls

#### Initialization Section

```
🚀 Initialize Agent
   └─ Click to initialize agents

🔄 Reset
   └─ Clear history and reset state
```

#### Settings Section

```
□ Use Docker for Code Execution
   └─ Toggle Docker isolation

⚙️ Max Agent Retries
   └─ Slider: 1-20 (default: 10)

🌡️ Temperature
   └─ Slider: 0.0-2.0 (default: 0.0)
```

#### Information Section

```
ℹ️ About this Agent
   └─ Feature overview

🔧 How It Works
   └─ Step-by-step guide
```

### Main Content Tabs

#### Paper Analysis Tab

```
📄 Analyze Research Paper

[URL Input Field]
Placeholder: https://arxiv.org/abs/2308.08155

☐ Summary & Key Contributions
☐ Target Audience
☐ Methodology & Results
☐ Limitations & Future Work
☐ Practical Applications

[🚀 Analyze Paper] Button
```

#### Stock Market Tab

```
📈 Stock Market Analysis

[Query Text Area]
Placeholder: Show me YTD gain of top 10 tech companies...

Select Query Type:
┌─────────────────────┐
│ Stock Performance   │
│ Market Trends      │
│ Sector Analysis    │
│ Custom Query       │
└─────────────────────┘

[📊 Analyze Market] Button
```

#### Web Research Tab

```
🔍 Web Research

[Topic Text Area]
Placeholder: Research latest developments in AI safety...

Select Research Depth:
┌──────────────────────────┐
│ Quick Overview           │
│ Moderate Detail          │
│ Deep Analysis            │
└──────────────────────────┘

[🔍 Start Research] Button
```

#### Custom Task Tab

```
⚙️ Custom Task

[Task Description Area]
Placeholder: Enter your custom task description...

[⚙️ Execute Task] Button
```

---

## Task Types

### 1. Paper Analysis 📄

**What it does:**

- Reads research papers from URLs
- Provides intelligent analysis
- Extracts key findings
- Recommends audience

**How to use:**

1. Click "Paper Analysis" tab
2. Enter arxiv URL or paper URL
3. Select analysis aspects
4. Click "Analyze Paper"

**Example:**

```
URL: https://arxiv.org/abs/2308.08155
Aspects: Summary, Target Audience, Applications
```

**Output:**

- Summary of the paper
- Target reader profile
- Key contributions
- Practical applications

### 2. Stock Market Analysis 📈

**What it does:**

- Analyzes market trends
- Gets stock performance data
- Provides financial insights
- Shows sector analysis

**How to use:**

1. Click "Stock Market" tab
2. Enter your market question
3. Select query type
4. Click "Analyze Market"

**Example:**

```
Query: What are the top performing tech stocks?
Type: Stock Performance
```

**Output:**

- Current market data
- Performance metrics
- Trend analysis
- Predictions

### 3. Web Research 🔍

**What it does:**

- Researches any topic
- Gathers information from web
- Synthesizes findings
- Provides comprehensive overview

**How to use:**

1. Click "Web Research" tab
2. Enter research topic
3. Select depth (Quick/Moderate/Deep)
4. Click "Start Research"

**Example:**

```
Topic: Latest developments in quantum computing
Depth: Deep Analysis
```

**Output:**

- Comprehensive overview
- Key findings
- Recent developments
- Future trends

### 4. Custom Task ⚙️

**What it does:**

- Executes any custom task
- Full flexibility
- Agent interprets naturally
- Custom execution logic

**How to use:**

1. Click "Custom Task" tab
2. Describe your task
3. Click "Execute Task"
4. Wait for results

**Example:**

```
Task: Compare Python and Golang for backend development
```

---

## Configuration

### Environment Variables

Create `.env` file with:

```env
# Required
OPENAI_API_KEY=your_key_here

# Optional (defaults shown)
API_TIMEOUT=600
CACHE_SEED=42
LLM_TEMPERATURE=0.0
MAX_CONSECUTIVE_AUTO_REPLY=10
USE_DOCKER=False
WORK_DIR=./work_dir
LOG_LEVEL=INFO
LOG_FILE=agent.log
```

### Sidebar Settings

#### Docker Execution

```
□ Use Docker for Code Execution

When checked:
- Code runs in isolated Docker container
- Safer execution
- Requires Docker to be installed and running
- Slower but more secure
```

#### Max Agent Retries

```
⊣─────⊢
1         10         20

Default: 10
Higher value = more time for complex tasks
Lower value = faster, may fail on complex tasks
```

#### Temperature

```
⊣─────⊢
0.0      0.5        2.0

Default: 0.0
- 0.0 = Deterministic, consistent responses
- 0.7 = Balanced, slight randomness
- 2.0 = Creative, highly random
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: "Agent Not Initialized"

```
Error: Agent Not Initialized

Solution:
1. Click "🚀 Initialize Agent" in sidebar
2. Wait for ✅ message
3. Try again
```

#### Issue: "OPENAI_API_KEY not configured"

```
Error: OpenAI API key not configured

Solution:
1. Edit .env file
2. Add: OPENAI_API_KEY=your_key_here
3. Save file
4. Restart application
5. Try initialization again
```

#### Issue: Task Execution Timeout

```
Error: Request took too long

Solution:
1. Increase API_TIMEOUT in .env
2. Change: API_TIMEOUT=900
3. Restart application
4. Try again with simpler query
```

#### Issue: Code Execution Errors

```
Error: Code execution failed

Solution:
1. Enable Docker in sidebar
2. Or disable Docker and try again
3. Check work_dir permissions
4. Review agent.log for details
```

#### Issue: Memory Usage High

```
High Memory Consumption

Solution:
1. Click "Clear History" button
2. Restart application
3. Use shorter queries
4. Enable Docker isolation
```

#### Issue: API Rate Limit

```
Error: Rate limit exceeded

Solution:
1. Wait 60 seconds
2. Try with simpler query
3. Check API quota
4. Use smaller context
```

### Debugging

#### Enable Debug Logging

```env
LOG_LEVEL=DEBUG
```

This provides detailed logs in:

- Console output
- `agent.log` file

#### Check Logs

```bash
# View last 50 lines of log
tail -50 agent.log

# View all logs
type agent.log
```

#### Validate Configuration

```python
from config import Config
is_valid, error = Config.validate_config()
if not is_valid:
    print(f"Error: {error}")
```

#### Test Agent Connection

```python
from backend import initialize_agent_manager
success = initialize_agent_manager()
print(f"Agent initialized: {success}")
```

---

## Advanced Usage

### Custom Task Formatting

#### For Better Results

**Good task description:**

```
Analyze the Top 10 Python frameworks for web development.
For each framework, provide:
1. Key features
2. Use cases
3. Performance metrics
4. Community size
5. Learning curve
```

**Poor task description:**

```
Tell me about Python frameworks
```

### Exporting Conversations

#### Download as JSON

```
1. Execute a task
2. Click "Export as JSON" button
3. Click "Download JSON"
4. Save conversation_history.json
```

#### JSON Structure

```json
{
  "metadata": {
    "total_messages": 5,
    "start_time": "2024-12-07T14:23:45",
    "duration_seconds": 45.23,
    "senders": ["user", "assistant"]
  },
  "conversation": [
    {
      "timestamp": "2024-12-07T14:23:45",
      "sender": "user",
      "content": "Your query...",
      "type": "task"
    },
    ...
  ]
}
```

### Performance Optimization

#### For Faster Responses

```env
# Reduce timeout (for simple tasks)
API_TIMEOUT=300

# Reduce retries
MAX_CONSECUTIVE_AUTO_REPLY=5

# Use simpler model
# (modify in config.py)
```

#### For Better Quality

```env
# Increase timeout
API_TIMEOUT=900

# Allow more retries
MAX_CONSECUTIVE_AUTO_REPLY=15

# Keep temperature at 0.0 for consistency
LLM_TEMPERATURE=0.0
```

### Adding Custom Validators

In `utils.py`, add:

```python
class TaskValidator:
    @staticmethod
    def validate_custom(input_str):
        # Your validation logic
        if not valid:
            return False, "Error message"
        return True, None
```

### Adding New Task Types

1. **Update config.py:**

```python
TASK_TEMPLATES = {
    "my_task": {
        "name": "My Task",
        "description": "My description",
        "placeholder": "Example input..."
    }
}
```

2. **Update backend.py:**

```python
class TaskExecutor:
    def execute_my_task(self, param):
        message = f"Do something with {param}"
        return self.agent_manager.initiate_chat(message)
```

3. **Update app.py:**

```python
with tab_my_task:
    st.markdown("### My Task")
    input_val = st.text_input("Input", placeholder="...")
    if st.button("Execute"):
        # Handle execution
```

---

## Performance Tips

### 1. Query Optimization

```
Good: "Analyze Python for web development"
Bad: "python"

Good: "Compare A vs B for use case X"
Bad: "Compare A and B"
```

### 2. Reduce Load

```
- Use shorter queries
- Avoid very long URLs
- Limit to one task at a time
- Clear history regularly
```

### 3. Configure Appropriately

```
- Set timeout based on task complexity
- Adjust retries for task type
- Use Docker for isolation
- Enable caching
```

---

## Best Practices

### ✅ DO:

- Initialize agent before starting tasks
- Use clear, specific queries
- Check configuration before running
- Review logs for errors
- Export important results
- Clear history periodically
- Enable Docker for production
- Monitor performance metrics

### ❌ DON'T:

- Run multiple tasks simultaneously
- Use very long queries (>2000 chars)
- Hardcode API keys in code
- Ignore error messages
- Leave tasks hanging
- Use same agent for different users
- Disable validation/sanitization
- Run without error handling

---

## Support Resources

### Documentation Files

- `README.md` - Full documentation
- `IMPROVEMENTS.md` - Technical details
- `ARCHITECTURE.md` - System design
- `PROJECT_SUMMARY.md` - Overview
- `.env.template` - Configuration options

### Getting Help

1. Check relevant documentation
2. Review error logs
3. Verify `.env` configuration
4. Test API connectivity
5. Run `quickstart.py` again

### Key Files

```
app.py          - User interface
backend.py      - Agent management
config.py       - Configuration
utils.py        - Helper functions
agent.log       - Application logs
.env            - Environment variables
```

---

## Keyboard Shortcuts

| Action      | Key                    |
| ----------- | ---------------------- |
| Refresh UI  | F5                     |
| Clear Cache | Ctrl+Shift+Delete      |
| View Source | F12 (in browser)       |
| Focus Input | Tab                    |
| Submit      | Enter (in most fields) |

---

## Frequently Asked Questions

**Q: How long should tasks take?**
A: Usually 30-120 seconds depending on complexity.

**Q: Can I use the app offline?**
A: No, it requires internet for API calls.

**Q: Can I use free OpenAI tier?**
A: Yes, but with rate limits.

**Q: How do I change models?**
A: Edit `DEFAULT_MODELS` in `config.py`.

**Q: Can I use Azure OpenAI?**
A: Yes, configure `OAI_CONFIG_LIST` for Azure.

**Q: How do I increase memory limit?**
A: Clear history or restart application.

**Q: Can I run multiple instances?**
A: Yes, on different ports via `streamlit run app.py --server.port 8502`

**Q: How do I backup conversations?**
A: Use the JSON export feature.

---

## Final Checklist

Before starting:

- [ ] Python 3.8+ installed
- [ ] Dependencies installed
- [ ] `.env` file created
- [ ] API key added to `.env`
- [ ] `streamlit run app.py` works
- [ ] Browser opens successfully

When using:

- [ ] Initialize agent first
- [ ] Validate input format
- [ ] Check API connectivity
- [ ] Monitor logs for errors
- [ ] Export results if needed

---

**Happy Analyzing! 🚀**

For more details, see the comprehensive documentation in the project directory.
