# 🤖 100 Days - 100 AI Agents & AI Automation Projects

![GitHub Repo](https://img.shields.io/badge/Repository-100--Days--100--AI--AGENTS-blue?style=flat-square&logo=github)
![License](https://img.shields.io/badge/License-Apache%202.0-green?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![OpenAI](https://img.shields.io/badge/OpenAI-Latest-412991?style=flat-square&logo=openai)
![LangChain](https://img.shields.io/badge/LangChain-Latest-darkblue?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?style=flat-square)

---

## 📌 About This Repository

This is a **comprehensive open-source collection** of **AI agents**, **automation projects**, and **intelligent systems** built as part of the **"100 Days - 100 AI Agents"** challenge. Each project demonstrates practical applications of modern AI technologies including LLMs, embeddings, multi-agent systems, and retrieval-augmented generation (RAG).

The repository showcases real-world implementations of cutting-edge AI/ML techniques with a focus on:

- 🔄 **Multi-Agent Orchestration** (LangGraph, LangChain)
- 🧠 **Large Language Models** (OpenAI GPT)
- 📊 **Vector Embeddings & Search** (Semantic similarity)
- 🎯 **Intelligent Routing & Decision-Making**
- 🌐 **Interactive Web Applications** (Streamlit)
- ⚡ **Real-time Processing & Evaluation**

---

## 👨‍💻 Author

**Ayush Singh**

- 📧 Email: [ayusingh693@gmail.com](mailto:ayusingh693@gmail.com)
- 🔗 GitHub: [@ayusingh-54](https://github.com/ayusingh-54)
- 💼 LinkedIn: [@ayush-singh54](https://www.linkedin.com/in/ayush-singh54/)

---

## 📚 Projects Overview

### 1. 🛎️ Customer Support Agent with LangGraph

**`01_customer_support_agent_langgraph/`**

A sophisticated multi-agent customer support system that intelligently handles, analyzes, and routes customer queries.

**Key Features:**

- Query categorization (Technical, Billing, General)
- Sentiment analysis (Positive, Neutral, Negative)
- Intelligent routing to specialized handlers
- Automatic escalation for critical issues
- Interactive Streamlit dashboard
- Complete workflow visualization

**Technologies:**

- LangGraph (Multi-agent orchestration)
- LangChain (LLM integration)
- OpenAI GPT (NLP & reasoning)
- Streamlit (Web interface)
- Python (Core logic)

**Quick Start:**

```bash
cd 01_customer_support_agent_langgraph
pip install -r requirements.txt
export OPENAI_API_KEY="your-api-key"
streamlit run app.py
```

**Use Cases:**

- Enterprise customer service automation
- Support ticket routing
- Quality assurance for customer interactions
- 24/7 automated first-response system

---

### 2. 🔍 Search the Internet and Summarize

**`02_search_the_internet_and_summarize/`**

An intelligent web search and summarization agent that searches the internet for information and provides concise, relevant summaries.

**Key Features:**

- Real-time internet search capabilities
- Multi-source information gathering
- Intelligent text summarization
- Key insights extraction
- Citation tracking
- Interactive search interface
- Search history management

**Technologies:**

- DuckDuckGo Search API (Web search)
- OpenAI GPT (Summarization & extraction)
- LangChain (Agent orchestration)
- Streamlit (Web UI)
- BeautifulSoup (Web scraping)

**Quick Start:**

```bash
cd 02_search_the_internet_and_summarize
pip install -r requirements.txt
streamlit run app.py
```

**Use Cases:**

- Research automation
- Market intelligence gathering
- News aggregation and summarization
- Competitive analysis
- Real-time information synthesis

---

### 3. 🤖 Chatbot Simulation & Evaluation

**`03_chatbot-simulation-evaluation/`**

A comprehensive framework for simulating conversations between multiple chatbots and evaluating their performance across various metrics.

**Key Features:**

- Multi-bot conversation simulation
- Automated evaluation metrics
- Performance benchmarking
- Response quality analysis
- Conversation flow tracking
- Detailed analytics dashboard
- Export & reporting capabilities

**Technologies:**

- LangChain (Bot frameworks)
- OpenAI GPT (Conversation logic)
- Pandas (Data analysis)
- Plotly (Visualizations)
- Jupyter Notebooks (Interactive development)

**Quick Start:**

```bash
cd 03_chatbot-simulation-evaluation
jupyter notebook agent-simulation-evaluation.ipynb
```

**Use Cases:**

- Chatbot performance comparison
- Quality assurance testing
- Response consistency evaluation
- Model benchmarking
- Development and testing

---

### 4. 📝 Information Gathering with Prompting

**`information-gather-prompting/`**

An advanced system for extracting structured information from unstructured data using intelligent prompting strategies.

**Key Features:**

- Prompt engineering framework
- Information extraction pipeline
- Structured data generation
- Context-aware questioning
- Multi-step reasoning chains
- Output validation & verification

**Technologies:**

- OpenAI GPT (Core LLM)
- Prompt engineering techniques
- Chain-of-thought prompting
- Streamlit (Interface)
- JSON schema validation

**Quick Start:**

```bash
cd information-gather-prompting
pip install -r requirements.txt
streamlit run app.py
```

**Use Cases:**

- Data extraction from documents
- Structured knowledge base creation
- Report generation
- Information normalization
- Data cleaning automation

---

### 5. 👗 Vibe Matcher - AI-Powered Fashion Recommender

**`vibe-matcher-app/`**

An innovative AI-powered recommendation engine that matches style vibes to fashion products using embeddings and semantic similarity.

**Key Features:**

- Natural language vibe search
- Semantic product matching
- AI-powered embeddings (OpenAI)
- Cosine similarity ranking
- Real-time analytics dashboard
- Search history tracking
- Interactive product browser
- Performance metrics visualization

**Technologies:**

- OpenAI text-embedding-ada-002 (1536-dim embeddings)
- scikit-learn (Cosine similarity)
- Streamlit (Web application)
- Plotly (Interactive charts)
- Pandas & NumPy (Data manipulation)

**Quick Start:**

```bash
cd vibe-matcher-app
pip install -r requirements.txt
export OPENAI_API_KEY="your-api-key"
streamlit run app.py
```

**Live Demo:**

- 🌐 Deployed on Streamlit Cloud
- Search for style vibes like: "energetic urban chic", "soft cozy loungewear"
- Get instant product recommendations

**Use Cases:**

- E-commerce product recommendation
- Style personalization
- Fashion AI assistant
- Customer engagement tool
- Conversion optimization

---

## 🏗️ Project Architecture

```
100-Days-100-AI-AGENTS/
│
├── 01_customer_support_agent_langgraph/
│   ├── app.py                          # Streamlit interface
│   ├── backend.py                      # Agent logic
│   ├── customer_support_agent_langgraph.ipynb
│   ├── requirements.txt
│   └── README.md
│
├── 02_search_the_internet_and_summarize/
│   ├── app.py                          # Main app
│   ├── backend.py                      # Search & summarize logic
│   ├── search_the_internet_and_summarize.ipynb
│   ├── requirements.txt
│   └── README.md
│
├── 03_chatbot-simulation-evaluation/
│   ├── agent-simulation-evaluation.ipynb
│   ├── app.py                          # Interface
│   ├── backend.py                      # Simulation logic
│   ├── requirements.txt
│   └── README.md
│
├── information-gather-prompting/
│   ├── app.py                          # Streamlit UI
│   ├── backend.py                      # Prompt & extraction logic
│   ├── information-gather-prompting.ipynb
│   ├── requirements.txt
│   └── README.md
│
├── Vibe Matcher/
│   ├── notebooks/
│   │   └── vibe_matcher.ipynb          # Notebook prototype
│   ├── src/
│   │   ├── embeddings.py               # Embedding utilities
│   │   ├── search.py                   # Search logic
│   │   └── utils.py                    # Helper functions
│   ├── data/
│   │   └── embeddings_cache.json       # Cached embeddings
│   ├── README.md
│   └── requirements.txt
│
├── vibe-matcher-app/
│   ├── app.py                          # Streamlit app (deployed)
│   ├── vibe_matcher_backend.py         # Backend logic
│   ├── requirements.txt                # Clean dependencies
│   ├── README.md                       # Complete documentation
│   ├── DEPLOYMENT_GUIDE.md             # Deployment instructions
│   ├── data/
│   │   └── .gitkeep
│   └── DEPLOYMENT_GUIDE.md
│
├── README.md                           # This file
├── LICENSE                             # Apache 2.0
└── .gitignore
```

---

## 🚀 Getting Started

### Prerequisites

- **Python** 3.10 or higher
- **pip** (Python package manager)
- **Virtual Environment** (recommended)
- **OpenAI API Key** (for some projects)

### Installation

1. **Clone the Repository**

```bash
git clone https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-.git
cd 100-Days-100-AI-AGENTS-
```

2. **Create Virtual Environment**

```bash
# Windows
python -m venv venv
venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies (for all projects)**

```bash
pip install pandas numpy scikit-learn openai streamlit plotly langchain langgraph jupyter
```

4. **Set Up Environment Variables**

```bash
# Create .env file
cp .env.example .env

# Add your OpenAI API key
export OPENAI_API_KEY="sk-your-actual-key-here"
```

### Running Individual Projects

Each project can be run independently:

```bash
# Customer Support Agent
cd 01_customer_support_agent_langgraph
streamlit run app.py

# Search & Summarize
cd 02_search_the_internet_and_summarize
streamlit run app.py

# Vibe Matcher
cd vibe-matcher-app
streamlit run app.py
```

---

## 🛠️ Technology Stack

### Core Technologies

| Technology       | Version | Purpose                    |
| ---------------- | ------- | -------------------------- |
| **Python**       | 3.10+   | Core programming language  |
| **OpenAI**       | Latest  | LLM and embeddings         |
| **LangChain**    | 0.0.x+  | LLM framework & chains     |
| **LangGraph**    | Latest  | Multi-agent orchestration  |
| **Streamlit**    | 1.28+   | Web application framework  |
| **Pandas**       | 2.0+    | Data manipulation          |
| **NumPy**        | 1.23+   | Numerical computing        |
| **Scikit-learn** | 1.1+    | ML algorithms              |
| **Plotly**       | 5.14+   | Interactive visualizations |

### Key Libraries

```python
# LLM & NLP
openai>=0.27.0
langchain>=0.0.200
langgraph>=0.0.1

# Data & ML
pandas>=1.5.0
numpy>=1.23.0
scikit-learn>=1.1.0

# Web & UI
streamlit>=1.28.0
plotly>=5.14.0

# Utilities
python-dotenv>=0.19.0
requests>=2.28.0
```

---

## 📊 Feature Comparison

| Feature              | Project 1 | Project 2 | Project 3 | Project 4 | Project 5 |
| -------------------- | --------- | --------- | --------- | --------- | --------- |
| **Multi-Agent**      | ✅        | ✅        | ✅        | ❌        | ❌        |
| **LLM Powered**      | ✅        | ✅        | ✅        | ✅        | ❌\*      |
| **Web UI**           | ✅        | ✅        | ✅        | ✅        | ✅        |
| **Real-time**        | ✅        | ✅        | ❌        | ✅        | ✅        |
| **Analytics**        | ✅        | ✅        | ✅        | ✅        | ✅        |
| **Deployment Ready** | ✅        | ✅        | ✅        | ✅        | ✅        |

\*Project 5 uses embeddings instead of LLM reasoning

---

## 🎯 Use Cases & Applications

### Enterprise Solutions

- **Customer Support Automation** - Multi-tier customer service with intelligent routing
- **Knowledge Management** - Automated information extraction and organization
- **Research & Analysis** - Real-time intelligence gathering and summarization
- **Quality Assurance** - Bot simulation and performance evaluation

### E-Commerce & Retail

- **Product Recommendations** - AI-powered style matching
- **Customer Engagement** - Conversational shopping assistants
- **Inventory Intelligence** - Smart product discovery
- **Personalization** - User preference learning

### Content & Publishing

- **News Aggregation** - Automated summary generation
- **Research Synthesis** - Multi-source information compilation
- **Report Generation** - Structured data extraction
- **Competitive Analysis** - Market intelligence

---

## 📖 Documentation

Each project includes comprehensive documentation:

- **Individual README.md** - Project-specific setup & usage
- **Jupyter Notebooks** - Interactive examples & tutorials
- **Inline Code Comments** - Detailed explanations
- **Deployment Guides** - Production deployment instructions
- **API Documentation** - Function references

---

## 🔐 Security & Best Practices

### API Key Management

```bash
# Never commit API keys!
# Use environment variables:
export OPENAI_API_KEY="your-key-here"

# Or use .env file (add to .gitignore)
OPENAI_API_KEY=sk-...
SEARCH_API_KEY=...
```

### Rate Limiting

- Implement exponential backoff for API calls
- Cache embeddings and results
- Monitor quota usage
- Use local fallbacks when available

### Data Privacy

- No sensitive data in logs
- Encrypt cached data
- Clean up temporary files
- Respect user privacy

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Steps to Contribute

1. **Fork the Repository**

```bash
git clone https://github.com/your-username/100-Days-100-AI-AGENTS-.git
```

2. **Create Feature Branch**

```bash
git checkout -b feature/your-feature-name
```

3. **Make Changes**

- Write clean, documented code
- Follow PEP 8 style guide
- Add tests where applicable

4. **Commit Changes**

```bash
git commit -m "Add: Description of changes"
git push origin feature/your-feature-name
```

5. **Create Pull Request**

- Describe changes clearly
- Link relevant issues
- Request review

### Contribution Guidelines

- ✅ Follow PEP 8 style guide
- ✅ Add docstrings to functions
- ✅ Include type hints
- ✅ Write meaningful commit messages
- ✅ Update documentation
- ✅ Test your code

---

## 📝 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

### Apache 2.0 Summary

- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed
- ⚠️ Must include license and copyright
- ⚠️ Must state changes made
- ⚠️ Patent indemnification

---

## 🌟 Star History & Acknowledgments

If you find this repository helpful, please consider:

- ⭐ Starring the repository
- 🔗 Sharing with others
- 🤝 Contributing improvements
- 💬 Providing feedback

### Technologies We Use

- **OpenAI** - Leading LLM provider
- **LangChain** - Excellent LLM framework
- **Streamlit** - Fast web app development
- **Python Community** - Amazing open-source ecosystem

---

## 📞 Support & Contact

### Get Help

- 📧 Email: [ayusingh693@gmail.com](mailto:ayusingh693@gmail.com)
- 🐛 Issues: [GitHub Issues](https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-/discussions)
- 🔗 LinkedIn: [@ayush-singh54](https://www.linkedin.com/in/ayush-singh54/)

### FAQ

**Q: Do I need an OpenAI API key?**
A: For most projects yes, but some have synthetic/fallback modes for testing.

**Q: Can I run this locally?**
A: Absolutely! All projects are designed to run locally with proper setup.

**Q: How can I deploy these projects?**
A: Check individual DEPLOYMENT_GUIDE.md files for platform-specific instructions.

**Q: Can I use these for commercial purposes?**
A: Yes! Under Apache 2.0 license with proper attribution.

**Q: How often are projects updated?**
A: Regularly! Follow for latest updates and features.

---

## 🗺️ Roadmap

### Upcoming Features

- [ ] Advanced multi-modal agents
- [ ] Vector database integration (Pinecone, Weaviate)
- [ ] Enhanced performance analytics
- [ ] Advanced caching strategies
- [ ] Mobile app versions
- [ ] API service layer
- [ ] Docker containerization
- [ ] Kubernetes deployment guides

### New Projects Planned

- [ ] Image-based recommendation system
- [ ] Voice-based customer support
- [ ] Real-time sentiment analysis
- [ ] Predictive analytics engine
- [ ] Autonomous task execution

---

## 📊 Statistics

| Metric              | Value      |
| ------------------- | ---------- |
| Total Projects      | 5+         |
| Lines of Code       | 5000+      |
| Jupyter Notebooks   | 5          |
| Streamlit Apps      | 4          |
| Supported Platforms | 3+         |
| Python Version      | 3.10+      |
| Open Source License | Apache 2.0 |

---

## 🎓 Learning Resources

### For Beginners

- [LangChain Documentation](https://python.langchain.com/)
- [Streamlit Getting Started](https://docs.streamlit.io/)
- [OpenAI API Guide](https://platform.openai.com/docs/)

### Intermediate

- [LangGraph Guide](https://python.langchain.com/docs/langgraph)
- [Advanced Prompting](https://platform.openai.com/docs/guides/prompt-engineering)
- [RAG Pattern](https://python.langchain.com/docs/use_cases/question_answering/)

### Advanced

- [Multi-Agent Systems](https://arxiv.org/abs/2308.00352)
- [Vector Embeddings](https://openai.com/blog/introducing-text-and-code-embeddings/)
- [LLM Fine-tuning](https://platform.openai.com/docs/guides/fine-tuning)

---

## 🎉 Success Stories

This repository has been used by:

- ✅ AI/ML enthusiasts learning agent development
- ✅ Startups building AI products
- ✅ Enterprises automating customer service
- ✅ Researchers prototyping new agents
- ✅ Students in ML courses

---

## 📢 Updates & Announcements

Follow for latest updates:

- 🐙 GitHub: [@ayusingh-54](https://github.com/ayusingh-54)
- 💼 LinkedIn: [@ayush-singh54](https://www.linkedin.com/in/ayush-singh54/)
- 📧 Email: [ayusingh693@gmail.com](mailto:ayusingh693@gmail.com)

---

## 🏆 Badges & Recognition

![AI Agents](https://img.shields.io/badge/AI-Agents-blue?style=for-the-badge)
![Open Source](https://img.shields.io/badge/Open-Source-green?style=for-the-badge)
![100%Practical](https://img.shields.io/badge/100%25-Practical-orange?style=for-the-badge)
![Production Ready](https://img.shields.io/badge/Production-Ready-brightgreen?style=for-the-badge)

---

## 📋 Checklist for Using This Repository

Before getting started:

- [ ] Clone the repository
- [ ] Create a virtual environment
- [ ] Install dependencies
- [ ] Set up OpenAI API key
- [ ] Review project README
- [ ] Run example projects
- [ ] Explore Jupyter notebooks
- [ ] Check out deployment guides
- [ ] Star the repository ⭐

---

## 💡 Tips & Best Practices

### Performance Optimization

- Cache embeddings to reduce API calls
- Use batch processing for multiple queries
- Implement request throttling
- Monitor API usage and costs

### Code Quality

- Write clear, self-documenting code
- Use type hints throughout
- Add comprehensive docstrings
- Write unit tests
- Follow PEP 8 style

### Deployment

- Use environment variables for secrets
- Implement proper error handling
- Add logging for debugging
- Monitor application health
- Set up alerting

---

## 🚀 Quick Links

- [GitHub Repository](https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-)
- [Open Issues](https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-/issues)
- [Discussion Forum](https://github.com/ayusingh-54/100-Days-100-AI-AGENTS-/discussions)
- [Author's GitHub](https://github.com/ayusingh-54)
- [Author's LinkedIn](https://www.linkedin.com/in/ayush-singh54/)

---

<div align="center">

### 🌟 Show Your Support! 🌟

If this repository helped you, consider giving it a ⭐ and sharing it with others!

**Happy Coding & Building Amazing AI Agents!** 🤖✨

---

**Made with ❤️ by [Ayush Singh](mailto:ayusingh693@gmail.com)**

_100 Days - 100 AI Agents | Building the Future of AI Automation_

_Last Updated: December 5, 2025_

</div>

---

## 📚 Additional Resources

### Books

- "Building Intelligent Systems" - Geoff Hulten
- "Designing Machine Learning Systems" - Chip Huyen
- "LLM Engineering" - Various authors

### Courses

- DeepLearning.AI LangChain courses
- OpenAI API documentation courses
- Streamlit official tutorials

### Papers & Research

- "Generalist Agent" - DeepMind
- "In-Context Learning" - OpenAI
- "ReAct: Synergizing Reasoning and Acting" - Princeton

---

**Version:** 2.0.0  
**Last Updated:** December 5, 2025  
**Maintainer:** [Ayush Singh](mailto:ayusingh693@gmail.com)
