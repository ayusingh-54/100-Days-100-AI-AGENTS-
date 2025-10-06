# 🤖 Chatbot Simulator & Evaluator

A comprehensive Streamlit application for simulating and evaluating chatbot conversations using AI-powered virtual users. Test your chatbots before deployment with realistic customer interactions powered by LangChain and LangGraph.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![LangChain](https://img.shields.io/badge/langchain-latest-green.svg)
![LangGraph](https://img.shields.io/badge/langgraph-latest-orange.svg)

## 🌟 Features

### Core Capabilities

- 🤖 **AI-Powered Chatbot Simulation**: Test customer support bots with realistic interactions
- 👤 **Virtual Customer**: Simulated users with customizable behaviors and scenarios
- 🔄 **Automated Testing**: Run multiple conversation scenarios automatically
- 📊 **Conversation Analysis**: Detailed statistics and insights
- 💾 **Export Options**: Save conversations in TXT, Markdown, or JSON formats
- 📈 **History Tracking**: Keep track of all simulation runs

### Advanced Features

- 🎯 **Predefined Scenarios**: 5+ ready-to-use customer scenarios
- ⚙️ **Customizable Settings**: Adjust conversation length, AI models, and prompts
- 🎨 **Beautiful UI**: Modern, responsive interface with real-time updates
- 📱 **Mobile Friendly**: Works on desktop, tablet, and mobile devices
- 🔍 **Detailed Analysis**: Message length, turn counts, completion status

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Internet connection

## 🚀 Installation

### 1. Navigate to the Directory

```bash
cd 03_chatbot-simulation-evaluation
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

**Get your OpenAI API key:**

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key
5. Copy and paste into `.env` file

## 📦 Dependencies

Create a `requirements.txt` file:

```
streamlit>=1.28.0
langchain>=0.1.0
langchain-core>=0.1.0
langchain-community>=0.0.20
langchain-openai>=0.0.5
langgraph>=0.0.30
openai>=1.0.0
python-dotenv>=1.0.0
typing-extensions>=4.5.0
```

## 💻 Usage

### Running the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Using the Interface

#### 1. **Configure Scenario**

- Choose a predefined scenario from the sidebar
- Or write custom customer instructions
- Modify the chatbot's system prompt if needed

#### 2. **Adjust Settings**

- Set maximum conversation turns (4-20)
- Select AI model (GPT-3.5-turbo, GPT-4, etc.)
- Configure other parameters

#### 3. **Run Simulation**

- Click "🚀 Run Simulation" button
- Watch the conversation unfold in real-time
- View results immediately

#### 4. **Analyze Results**

- Switch to "📊 Analysis" tab
- View conversation statistics
- Export results in multiple formats

#### 5. **Review History**

- Check "📚 History" tab
- View all past simulations
- Compare different runs

## 🏗️ Project Structure

```
03_chatbot-simulation-evaluation/
│
├── app.py                                    # Streamlit frontend
├── backend.py                                # Core simulation logic
├── .env                                      # Environment variables (create this)
├── requirements.txt                          # Python dependencies
├── README.md                                 # This file
│
└── agent-simulation-evaluation.ipynb        # Original Jupyter notebook
```

## 🔧 Architecture

### Backend Components (`backend.py`)

#### 1. **ChatBot Class**

- Handles customer support responses
- Uses OpenAI API for generation
- Customizable system prompts

#### 2. **SimulatedUser Class**

- Generates realistic customer behavior
- Built with LangChain
- Configurable scenarios and personalities

#### 3. **SimulationManager Class**

- Orchestrates the complete workflow
- Manages LangGraph execution
- Provides conversation analysis

#### 4. **LangGraph Workflow**

- Node-based conversation flow
- Automatic turn management
- Conditional conversation ending

### Frontend Components (`app.py`)

#### 1. **Configuration Interface**

- Scenario selection
- Settings adjustment
- API key management

#### 2. **Simulation Runner**

- Progress visualization
- Real-time updates
- Error handling

#### 3. **Results Display**

- Formatted message cards
- Statistics dashboard
- Export functionality

#### 4. **History Management**

- Persistent storage
- Past simulations review
- Comparison tools

## 🎯 Predefined Scenarios

### 1. 🔄 Refund Request

Customer wants a full refund for a 5-year-old trip to Alaska.

### 2. ⏰ Flight Delay

Customer's flight was delayed 8 hours, missed important meeting.

### 3. 🧳 Lost Baggage

Airline lost baggage with important documents and medication.

### 4. ✈️ Seat Upgrade

Customer wants to upgrade to business class for long flight.

### 5. 💳 Booking Issue

Payment failed but card was charged, needs resolution.

## 📊 Analysis Features

### Conversation Statistics

- Total conversation turns
- Bot vs. customer message count
- Completion status
- Average message lengths

### Export Formats

#### **TXT Format**

Plain text report with conversation history

#### **Markdown Format**

Formatted document with headers and structure

#### **JSON Format**

Structured data for programmatic analysis

## 🎨 Customization

### Custom Chatbot Behavior

```python
# In app.py or directly in UI
bot_prompt = """You are a customer support agent for [COMPANY].
Your role is to [ROLE_DESCRIPTION].
You should [BEHAVIOR_GUIDELINES].
"""
```

### Custom Customer Scenarios

```python
# In backend.py or UI
custom_scenario = """Your name is [NAME].
You are [SITUATION].
Your goal is to [OBJECTIVE].
Additional details: [CONTEXT]
"""
```

### Adjust Conversation Length

```python
# In settings sidebar
max_turns = 12  # Adjust as needed (4-20)
```

### Change AI Model

```python
# In settings sidebar
model = "gpt-4"  # or "gpt-3.5-turbo", "gpt-4-turbo"
```

## 🔍 How It Works

### Conversation Flow

```
START
  ↓
Chatbot initiates conversation
  ↓
Customer responds (AI-generated based on scenario)
  ↓
Chatbot replies (based on system prompt)
  ↓
[Loop continues until:]
  - Customer says "FINISHED"
  - Maximum turns reached
  ↓
END
```

### Message Role Swapping

Both chatbot and simulated user use LLMs that output AI messages. The system automatically swaps roles to maintain proper conversation flow:

```python
AIMessage (Bot) → Displayed as Bot → Converted to HumanMessage for User
HumanMessage (User input) → Processed by User LLM → Returns as AIMessage
```

### State Management

LangGraph manages conversation state using a typed dictionary:

```python
class ConversationState(TypedDict):
    messages: Annotated[list, add_messages]
```

The `add_messages` annotation automatically:

- Appends new messages
- Maintains conversation history
- Prevents duplicates

## 🎓 Use Cases

### 1. **Chatbot Development**

- Test bot responses before deployment
- Identify edge cases and issues
- Refine conversation flows

### 2. **Quality Assurance**

- Automated testing of customer support bots
- Regression testing after updates
- Performance benchmarking

### 3. **Training & Education**

- Demonstrate chatbot capabilities
- Train support staff on scenarios
- Educational demonstrations

### 4. **Research & Development**

- Study conversation patterns
- Analyze customer interactions
- Develop better prompts

## 📈 Best Practices

### ✅ Do:

- Test multiple scenarios regularly
- Review conversation analysis
- Export and document results
- Iterate on bot prompts
- Use realistic customer scenarios

### ❌ Don't:

- Use in production without human review
- Rely solely on automated testing
- Ignore failed conversations
- Skip analysis of results
- Hardcode sensitive information

## 🐛 Troubleshooting

### API Key Issues

```
Error: API key not loaded
Solution: Check .env file format (no quotes, no spaces)
```

### Import Errors

```
Error: Module not found
Solution: pip install -r requirements.txt
```

### Simulation Hangs

```
Issue: Conversation not ending
Solution: Reduce max_turns or check customer instructions
```

### Memory Issues

```
Issue: Application slow/crashes
Solution: Clear history, reduce conversation length
```

## 🔐 Security & Privacy

- ✅ API keys stored securely in `.env` file
- ✅ No conversation data sent to external servers (except OpenAI)
- ✅ Local session management
- ✅ Conversation history stored locally
- ⚠️ Never commit `.env` file to version control

## 🚀 Advanced Features

### Batch Testing

Run multiple scenarios programmatically:

```python
from backend import SimulationManager, Scenarios

scenarios = [
    Scenarios.REFUND_REQUEST,
    Scenarios.FLIGHT_DELAY,
    Scenarios.BAGGAGE_LOST
]

for scenario in scenarios:
    manager = SimulationManager(api_key, scenario)
    conversation = manager.run_simulation()
    # Analyze results
```

### Custom Analysis

Add custom metrics in `backend.py`:

```python
def custom_analysis(conversation):
    # Sentiment analysis
    # Response time metrics
    # Customer satisfaction indicators
    pass
```

## 📚 Learning Resources

- **LangChain**: [https://python.langchain.com/](https://python.langchain.com/)
- **LangGraph**: [https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/)
- **Streamlit**: [https://docs.streamlit.io/](https://docs.streamlit.io/)
- **OpenAI API**: [https://platform.openai.com/docs/](https://platform.openai.com/docs/)

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional predefined scenarios
- More analysis metrics
- Integration with other LLM providers
- Multi-language support
- Voice/audio simulation

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **OpenAI** for GPT models
- **LangChain** for LLM framework
- **LangGraph** for workflow orchestration
- **Streamlit** for the amazing web framework

## 📧 Support

For issues or questions:

- Check the troubleshooting section
- Review the Jupyter notebook for examples
- Open an issue on GitHub

---

## 🎯 Quick Start Guide

### Fastest Way to Get Started:

1. **Install dependencies:**

   ```bash
   pip install streamlit langchain langchain-openai langgraph openai python-dotenv langchain-community
   ```

2. **Create `.env` file:**

   ```bash
   OPENAI_API_KEY=your_key_here
   ```

3. **Run the app:**

   ```bash
   streamlit run app.py
   ```

4. **Select a scenario and click "Run Simulation"!**

---

**Made with ❤️ using Python, Streamlit, LangChain & LangGraph**

_Happy Testing! 🚀_
