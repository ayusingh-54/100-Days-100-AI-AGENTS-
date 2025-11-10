# Vibe Matcher – Mini Recommender Prototype

A compact prototype that matches a short text “vibe” query to fashion products using OpenAI embeddings and cosine similarity. It's designed to be Colab-friendly and runnable locally.

Repository structure

```
.
├── README.md
├── requirements.txt
├── notebooks/
│   └── vibe_matcher.ipynb
├── data/                # created at runtime; embeddings_cache.json will be saved here
└── src/
    ├── embeddings.py
    ├── search.py
    └── utils.py
```

Quick overview

- Input: short vibe query (e.g. "energetic urban chic").
- Products: small mock catalog (8–10 fashion items) with descriptions and manual vibe tags.
- Embeddings: OpenAI `text-embedding-ada-002` used to embed product descriptions and queries.
- Matching: cosine similarity (scikit-learn). Top-3 returned. Similarity values transformed to 0–1 range.
- Thresholds: fallback threshold = 0.35, good hit threshold = 0.7 (constants in the notebook).

Why AI at Nexora?

AI at Nexora excites me because it's about applied ML that ships: small, explainable prototypes can rapidly inform product decisions, close the loop with user feedback, and turn ideas into measurable impact. A tiny system like Vibe Matcher demonstrates how rapid experimentation (embeddings + similarity search) yields fast, interpretable results that are easy to iterate on—exactly the product-focused, outcome-driven approach Nexora values.

How to run

Local (recommended):

1. Create a Python 3.10+ venv and activate it.
2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Set your OpenAI API key (PowerShell):

```powershell
$env:OPENAI_API_KEY = 'sk-...'
```

Colab: open the notebook `notebooks/vibe_matcher.ipynb` in Colab and run the first cells; set the key with `os.environ['OPENAI_API_KEY']='sk-...'`.

Notes and limits

- The notebook will attempt to call OpenAI. If `OPENAI_API_KEY` is not set, the notebook includes a deterministic synthetic-embedding fallback so you can still run end-to-end tests locally without incurring API calls.
- Caching: embeddings are cached to `data/embeddings_cache.json` to avoid repeated API calls.
- Future work: Pinecone/FAISS for production vector DB, hybrid tag+vector retrieval, LLM-based reranking.

Contact

This prototype was generated as part of a mini-project. For changes, edit files under `src/` and re-run the notebook.
# 🤖 100 Days - 100 AI Agents Challenge

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Open Source Love](https://img.shields.io/badge/Open%20Source-%E2%9D%A4-red.svg)](https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-)

> A comprehensive collection of AI-powered agents built with cutting-edge technologies like LangChain, LangGraph, OpenAI, and more. One agent every 2 days for 100 days!

---

## 🌟 Project Vision

Welcome to the **100 Days - 100 AI Agents Challenge**! This is an open-source initiative to create a diverse collection of production-ready AI agents that solve real-world problems. Each agent is:

- ✅ **Fully Functional**: Ready to use out of the box
- ✅ **Well Documented**: Clear explanations and examples
- ✅ **Modular Design**: Easy to understand and modify
- ✅ **Open Source**: Free for everyone to use and contribute

### 🎯 Mission

To democratize AI agent development by providing:

- Pre-built, tested AI agents for various use cases
- Learning resources for AI development
- A collaborative platform for the AI community
- Production-ready code that saves development time

---

## 📊 Project Status

| Metric                 | Status                  |
| ---------------------- | ----------------------- |
| **Total Agents**       | 3/100 🚀                |
| **Last Updated**       | October 7, 2025         |
| **Active Development** | ✅ Yes                  |
| **Release Schedule**   | One agent every 2 days  |
| **Contributors**       | Open for contributions! |

---

## 🤖 Available Agents

### Quick Access Table

| #   | Agent Name                        | Category    | Tech Stack                    | Status   | Quick Links                                                                                         |
| --- | --------------------------------- | ----------- | ----------------------------- | -------- | --------------------------------------------------------------------------------------------------- |
| 1   | **Customer Support Agent**        | 💬 Chatbot  | LangGraph, LangChain, OpenAI  | ✅ Ready | [Notebook](customer_support_agent_langgraph/) \| [Docs](customer_support_agent_langgraph/README.md) |
| 2   | **Web Search & Summarizer**       | 🔍 Research | DuckDuckGo, OpenAI, Streamlit | ✅ Ready | [Code](search_the_internet_and_summarize/) \| [Docs](search_the_internet_and_summarize/README.md)   |
| 3   | **Chatbot Simulator & Evaluator** | 🧪 Testing  | LangGraph, Streamlit, OpenAI  | ✅ Ready | [App](03_chatbot-simulation-evaluation/) \| [Docs](03_chatbot-simulation-evaluation/README.md)      |

---

## 📚 Detailed Agent Directory

### 1. 💬 Customer Support Agent (LangGraph)

**Location**: `customer_support_agent_langgraph/`

A sophisticated customer support chatbot built with LangGraph for managing complex conversation flows.

#### Features:

- ✅ Multi-turn conversation handling
- ✅ Context-aware responses
- ✅ State management with LangGraph
- ✅ Customizable personality and tone
- ✅ Integration-ready API

#### Tech Stack:

- LangGraph for workflow orchestration
- LangChain for LLM integration
- OpenAI GPT models
- Python 3.8+

#### Use Cases:

- Customer service automation
- FAQ handling
- Support ticket management
- Interactive help systems

#### Quick Start:

```bash
cd customer_support_agent_langgraph
pip install -r requirements.txt
# Follow instructions in README.md
```

---

### 2. 🔍 Web Search & Summarize Agent

**Location**: `search_the_internet_and_summarize/`

An intelligent research assistant that searches the web and generates concise, AI-powered summaries.

#### Features:

- ✅ DuckDuckGo search integration
- ✅ AI-powered summarization
- ✅ Site-specific search capability
- ✅ Multiple summary styles (bullet, paragraph, brief)
- ✅ Beautiful Streamlit UI
- ✅ Export in multiple formats (TXT, MD, JSON)
- ✅ Search history tracking
- ✅ Result caching for faster performance

#### Tech Stack:

- Streamlit for web interface
- DuckDuckGo Search API
- OpenAI GPT for summarization
- LangChain for LLM orchestration
- Python-dotenv for configuration

#### Use Cases:

- Research and information gathering
- News aggregation and summarization
- Competitive analysis
- Academic research assistance
- Market research
- Technical documentation review

#### Quick Start:

```bash
cd search_the_internet_and_summarize
pip install -r requirements.txt
echo "OPENAI_API_KEY=your_key_here" > .env
streamlit run app.py
```

#### Application Structure:

- `backend.py` - Core search and summarization logic
- `app.py` - Streamlit frontend interface
- `README.md` - Detailed documentation

---

### 3. 🧪 Chatbot Simulator & Evaluator

**Location**: `03_chatbot-simulation-evaluation/`

A comprehensive testing platform for evaluating chatbot performance using AI-powered simulated users.

#### Features:

- ✅ Automated chatbot testing
- ✅ AI-powered virtual customers
- ✅ 5+ predefined test scenarios
- ✅ Real-time conversation analysis
- ✅ Conversation statistics and metrics
- ✅ Export capabilities (TXT, MD, JSON)
- ✅ Beautiful analytics dashboard
- ✅ History tracking
- ✅ Customizable test scenarios

#### Tech Stack:

- LangGraph for conversation flow
- LangChain for LLM integration
- Streamlit for web interface
- OpenAI GPT models
- Python typing for type safety

#### Use Cases:

- Chatbot quality assurance
- Pre-deployment testing
- Regression testing after updates
- Performance benchmarking
- Training data generation
- Conversation flow optimization

#### Predefined Scenarios:

1. 🔄 Refund Request
2. ⏰ Flight Delay Complaint
3. 🧳 Lost Baggage Issue
4. ✈️ Seat Upgrade Request
5. 💳 Booking Payment Problem

#### Quick Start:

```bash
cd 03_chatbot-simulation-evaluation
pip install -r requirements.txt
echo "OPENAI_API_KEY=your_key_here" > .env
streamlit run app.py
```

#### Application Structure:

- `backend.py` - Core simulation engine
- `app.py` - Streamlit frontend
- `agent-simulation-evaluation.ipynb` - Jupyter notebook version
- `README.md` - Complete documentation

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager
- OpenAI API key ([Get one here](https://platform.openai.com/))
- Git

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-.git
cd 100-Days-100-AI-AGENTS-
```

2. **Create a virtual environment** (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Choose an agent and navigate to its directory**

```bash
cd <agent-directory>
```

4. **Install dependencies**

```bash
pip install -r requirements.txt
```

5. **Set up environment variables**

```bash
# Create .env file in the agent directory
echo "OPENAI_API_KEY=your_key_here" > .env
```

6. **Run the agent**

```bash
# For Streamlit apps
streamlit run app.py

# For Jupyter notebooks
jupyter notebook

# For Python scripts
python app.py
```

---

## 🛠️ Tech Stack Overview

### Core Technologies

- **Python 3.8+** - Primary programming language
- **LangChain** - LLM application framework
- **LangGraph** - Agent workflow orchestration
- **OpenAI GPT** - Large language models

### Frameworks & Libraries

- **Streamlit** - Web application framework
- **Jupyter** - Interactive development environment
- **DuckDuckGo Search** - Privacy-focused search API
- **Python-dotenv** - Environment configuration
- **Pydantic** - Data validation

### Development Tools

- **Git** - Version control
- **Virtual Environment** - Dependency isolation
- **pip** - Package management

---

## 📖 Documentation

Each agent includes:

- 📄 **README.md** - Complete setup and usage guide
- 💻 **Source Code** - Well-commented, modular code
- 📓 **Jupyter Notebooks** - Interactive examples (where applicable)
- 🎨 **UI Screenshots** - Visual guides
- 🔧 **Configuration Examples** - Sample .env files

---

## 🤝 Contributing

We **love** contributions! This project thrives on community involvement.

### How to Contribute

#### 1. **Report Issues**

Found a bug? Have a suggestion? [Open an issue](https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-/issues)

#### 2. **Submit Pull Requests**

**Process:**

1. Fork the repository
2. Create a feature branch
   ```bash
   git checkout -b feature/AmazingAgent
   ```
3. Make your changes
4. Commit with clear messages
   ```bash
   git commit -m "Add amazing new agent for [use case]"
   ```
5. Push to your fork
   ```bash
   git push origin feature/AmazingAgent
   ```
6. Open a Pull Request

#### 3. **Create New Agents**

**Want to contribute a new agent?** Follow this structure:

```
your-agent-name/
├── README.md                 # Detailed documentation
├── requirements.txt          # Python dependencies
├── .env.example             # Example configuration
├── backend.py               # Core logic (if applicable)
├── app.py                   # Main application
└── examples/                # Usage examples
    └── example.ipynb        # Jupyter notebook demo
```

**Agent Guidelines:**

- ✅ Clear, descriptive naming
- ✅ Modular, well-commented code
- ✅ Comprehensive README with:
  - Purpose and use cases
  - Installation instructions
  - Usage examples
  - Tech stack details
  - Troubleshooting guide
- ✅ requirements.txt with all dependencies
- ✅ .env.example for configuration
- ✅ Error handling and validation
- ✅ Type hints where appropriate

#### 4. **Improve Documentation**

- Fix typos
- Add examples
- Clarify instructions
- Translate to other languages

#### 5. **Share Your Experience**

- Write blog posts
- Create video tutorials
- Share on social media
- Give feedback

### Contribution Areas

| Area             | Description                | Difficulty   |
| ---------------- | -------------------------- | ------------ |
| 🐛 Bug Fixes     | Fix existing issues        | Beginner     |
| 📝 Documentation | Improve guides and docs    | Beginner     |
| ✨ New Features  | Add features to agents     | Intermediate |
| 🤖 New Agents    | Create entirely new agents | Intermediate |
| 🎨 UI/UX         | Improve interfaces         | Intermediate |
| ⚡ Performance   | Optimize code              | Advanced     |
| 🔐 Security      | Security improvements      | Advanced     |

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write descriptive comments
- Keep functions focused and small
- Use meaningful variable names

---

## 📅 Development Roadmap

### Current Focus (Days 1-10)

- ✅ Customer Support Agent
- ✅ Web Search & Summarize
- ✅ Chatbot Simulator
- 🚧 Email Assistant Agent (Coming Oct 9)
- 📋 Task Management Agent (Coming Oct 11)

### Upcoming Categories (Days 11-50)

#### 💼 Business Agents

- Sales Lead Qualifier
- Meeting Scheduler
- Invoice Processor
- Report Generator

#### 📊 Data Agents

- Data Analyzer
- SQL Query Generator
- CSV Processor
- API Data Fetcher

#### 🎨 Creative Agents

- Content Writer
- Image Caption Generator
- Social Media Manager
- Blog Post Creator

#### 🔧 Developer Agents

- Code Reviewer
- Documentation Generator
- Bug Reporter
- Test Case Generator

### Future (Days 51-100)

- Multi-agent systems
- Voice-enabled agents
- Image processing agents
- Video analysis agents
- Real-time monitoring agents
- Integration agents (Slack, Discord, etc.)

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### What This Means:

- ✅ Free to use for personal and commercial projects
- ✅ Modify and distribute as you wish
- ✅ No warranty provided
- ✅ Attribution appreciated but not required

---

## 🌐 Community & Support

### Get Help

- 📖 [Read the Documentation](https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-)
- 💬 [Open an Issue](https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-/issues)
- 📧 Contact: [Your Email]
- 🐦 Twitter: [@YourHandle]

### Stay Updated

- ⭐ Star this repository
- 👁️ Watch for updates
- 🔔 Enable notifications
- 📰 Follow the project

### Connect

- 💼 LinkedIn: [@ayush-singh54](https://www.linkedin.com/in/ayush-singh54/)
- 🐱 GitHub: [@ayusingh-54](https://github.com/ayusingh-54)


---

## 🎓 Learning Resources

### For Beginners

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Tutorial](https://langchain-ai.github.io/langgraph/)
- [OpenAI API Guide](https://platform.openai.com/docs/)
- [Streamlit Docs](https://docs.streamlit.io/)

### Advanced Topics

- [Agent Design Patterns](https://python.langchain.com/docs/modules/agents/)
- [Prompt Engineering](https://platform.openai.com/docs/guides/prompt-engineering)
- [LLM Best Practices](https://python.langchain.com/docs/guides/)

---

## 📊 Project Statistics

```
Total Lines of Code: 5000+
Total Agents: 3 (and growing!)
Programming Languages: Python
Frameworks: 5+
Contributors: Open for contributions
Stars: ⭐ (Star this repo!)
```

---

## 🙏 Acknowledgments

### Special Thanks To:

- **OpenAI** - For powerful language models
- **LangChain Team** - For the amazing framework
- **Streamlit** - For the beautiful UI framework
- **Open Source Community** - For inspiration and support
- **Contributors** - Everyone who helps improve this project

---

## 💡 Use Cases by Industry

### 🏢 Enterprise

- Customer support automation
- Internal knowledge bases
- Employee assistance
- Document processing

### 🎓 Education

- Tutoring systems
- Assignment helpers
- Research assistants
- Study guides

### 💻 Technology

- Code assistance
- Documentation generation
- Testing automation
- DevOps support

### 🛍️ E-commerce

- Product recommendations
- Customer service
- Order tracking
- Review analysis

### 🏥 Healthcare

- Patient assistance (non-medical)
- Appointment scheduling
- Information retrieval
- Administrative support

---

## ⚠️ Disclaimer

These agents are provided as-is for educational and development purposes. Always:

- Review and test thoroughly before production use
- Implement proper security measures
- Handle sensitive data appropriately
- Comply with relevant regulations
- Monitor usage and costs
- Keep API keys secure

---

## 🔮 Future Vision

By the end of 100 days, this repository will contain:

- ✨ 100 unique AI agents
- 📚 Comprehensive documentation
- 🎥 Video tutorials
- 🌍 Multi-language support
- 🔌 Integration templates
- 📱 Mobile-ready interfaces
- ☁️ Deployment guides
- 🧪 Testing frameworks

---

## 📈 How to Support

### Ways to Help:

1. ⭐ **Star** this repository
2. 🔀 **Fork** and contribute
3. 🐛 **Report** bugs and issues
4. 💡 **Suggest** new agent ideas
5. 📢 **Share** with your network
6. 📝 **Write** about your experience
7. 💬 **Provide** feedback
8. 🤝 **Collaborate** on features

---

## 📞 Contact & Feedback

We'd love to hear from you!

- **Found a bug?** [Open an issue](https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-/issues)
- **Have a suggestion?** [Start a discussion](https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-/discussions)
- **Want to collaborate?** [Contact me](mailto:your.email@example.com)
- **Need help?** Check the docs or ask in issues

---

## 🎯 Quick Links

| Resource         | Link                                                                           |
| ---------------- | ------------------------------------------------------------------------------ |
| 🏠 Home          | [Repository](https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-)           |
| 📖 Documentation | [Docs](https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-/tree/main)       |
| 🐛 Issues        | [Report Issues](https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-/issues) |
| 🤝 Contributing  | [Contribution Guide](#contributing)                                            |
| 📜 License       | [MIT License](LICENSE)                                                         |
| ⭐ Star History  | [Star History](https://star-history.com/#ayusingh-54/100-Days-100-AI-AGENTS-)  |

---

<div align="center">

### Made with ❤️ by [Ayu Singh](https://github.com/ayusingh-54)

### ⭐ Star this repo if you find it helpful!

**Building the future of AI, one agent at a time.**

[⬆ Back to Top](#-100-days---100-ai-agents-challenge)

</div>

---

**Last Updated:** October 7, 2025  
**Version:** 1.0.0  
**Status:** 🟢 Active Development
