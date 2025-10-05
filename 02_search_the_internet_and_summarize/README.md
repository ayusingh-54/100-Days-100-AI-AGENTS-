# 🔍 AI-Powered Web Research Assistant

A sophisticated web application that combines intelligent web searching with AI-powered summarization to help you research any topic quickly and efficiently.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## 🌟 Features

### Core Features

- 🔍 **Smart Web Search**: Powered by DuckDuckGo for privacy-focused searching
- 🤖 **AI Summarization**: Utilizes OpenAI's GPT-4 for intelligent text summarization
- 🎯 **Site-Specific Search**: Focus your research on specific websites
- 📊 **Multiple Summary Styles**: Choose from bullet points, paragraphs, or brief summaries
- ⚡ **Fast Caching**: Results are cached for instant retrieval

### Advanced Features

- 📜 **Search History**: Track all your previous searches
- 💾 **Multi-Format Export**: Export results as TXT, Markdown, or JSON
- 📈 **Statistics Dashboard**: Monitor your research activity
- 🎨 **Beautiful UI**: Clean, responsive, and intuitive interface
- ⚙️ **Customizable Settings**: Adjust search and summarization parameters

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Internet connection

## 🚀 Installation

### 1. Clone the Repository

```bash
cd search_the_internet_and_summarize
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

Create a `.env` file in the project directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

**How to get an OpenAI API key:**

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste it into your `.env` file

## 📦 Dependencies

Create a `requirements.txt` file with:

```
streamlit>=1.28.0
langchain>=0.1.0
langchain-openai>=0.0.2
python-dotenv>=1.0.0
duckduckgo-search>=3.9.0
nltk>=3.8.1
```

## 💻 Usage

### Running the Application

1. **Start the Streamlit app:**

```bash
streamlit run app.py
```

2. **Open your browser:**
   - The app will automatically open at `http://localhost:8501`
   - If not, navigate to the URL shown in your terminal

### Using the Application

#### Basic Search

1. Enter your search query in the main text box
2. Click the "🚀 Search" button
3. View AI-generated summaries with source links

#### Advanced Search (Site-Specific)

1. Expand the "🎯 Advanced: Search Specific Website" section
2. Enter a website URL (e.g., `https://www.nature.com`)
3. Enter your search query
4. Click "🚀 Search"

#### Customize Settings

Use the sidebar to adjust:

- **Maximum Results**: Number of results to retrieve (1-10)
- **Summary Style**: Choose bullet, paragraph, or brief format
- **Bullet Points**: Number of points per summary (for bullet style)

#### Export Results

After a search, use the export section to:

- Download as TXT file
- Download as Markdown file
- Download as JSON file

## 🏗️ Project Structure

```
search_the_internet_and_summarize/
│
├── app.py                                    # Streamlit frontend application
├── backend.py                                # Core backend logic
├── README.md                                 # This file
├── requirements.txt                          # Python dependencies
├── .env                                      # Environment variables (create this)
│
└── search_the_internet_and_summarize.ipynb  # Original Jupyter notebook
```

## 🔧 Architecture

### Backend Components (`backend.py`)

#### 1. **Config Class**

- Manages application configuration
- Loads environment variables
- Validates API keys

#### 2. **SearchEngine Class**

- Handles DuckDuckGo search operations
- Parses search results
- Maintains search history
- Supports site-specific searches

#### 3. **SummarizationEngine Class**

- Interfaces with OpenAI GPT models
- Generates summaries in multiple styles
- Formats results with source attribution
- Supports batch processing

#### 4. **SearchManager Class**

- Main orchestrator
- Combines search and summarization
- Manages caching
- Handles result export

### Frontend Components (`app.py`)

#### 1. **Page Configuration**

- Custom CSS styling
- Responsive layout
- Brand colors and themes

#### 2. **Session State Management**

- Persistent search history
- Settings preservation
- Results caching

#### 3. **UI Components**

- Header with branding
- Search interface
- Results display
- Export functionality
- Settings sidebar

## 🎨 Customization

### Changing AI Model

Edit in `backend.py`:

```python
self.default_model = "gpt-4"  # or "gpt-3.5-turbo"
```

### Adjusting Temperature

Modify creativity level (0.0-1.0):

```python
self.default_temperature = 0.7
```

### Custom Styling

Edit CSS in `app.py` under `configure_page()` function.

## 🔍 How It Works

### Search Process

1. **Query Input**: User enters search query
2. **Web Search**: DuckDuckGo API retrieves relevant results
3. **Parsing**: Raw results are structured into snippets, titles, and links
4. **Caching Check**: System checks if results are cached

### Summarization Process

1. **Text Extraction**: Relevant snippets are extracted from search results
2. **AI Processing**: OpenAI GPT model generates concise summaries
3. **Formatting**: Summaries are formatted with source attribution
4. **Display**: Results are presented in clean, readable format

### Data Flow

```
User Input → SearchEngine → DuckDuckGo API → Parse Results
    ↓
SummarizationEngine → OpenAI API → Format Summaries
    ↓
SearchManager → Cache Results → Display to User
```

## 📊 Example Use Cases

### 1. Academic Research

```
Query: "Recent breakthroughs in quantum computing"
Site: https://arxiv.org
```

### 2. News Aggregation

```
Query: "Latest developments in renewable energy"
Site: None (all sources)
```

### 3. Technical Documentation

```
Query: "Python asyncio best practices"
Site: https://docs.python.org
```

### 4. Market Research

```
Query: "AI startup trends 2025"
Site: None (all sources)
```

## 🛡️ Security & Privacy

- ✅ Uses DuckDuckGo for privacy-focused searching
- ✅ API keys stored securely in `.env` file
- ✅ No personal data collected or stored
- ✅ Local session management
- ⚠️ Never commit `.env` file to version control

## 🐛 Troubleshooting

### API Key Issues

```
Error: OPENAI_API_KEY not found
Solution: Ensure .env file exists with valid API key
```

### Import Errors

```
Error: No module named 'streamlit'
Solution: Run pip install -r requirements.txt
```

### Search Not Working

```
Error: No results found
Solution: Check internet connection and try different query
```

### Slow Performance

```
Issue: Summaries taking too long
Solution: Reduce max_results or use gpt-3.5-turbo model
```

## 🚀 Future Enhancements

- [ ] Support for multiple search engines (Google, Bing)
- [ ] PDF and Word document export
- [ ] Search result comparison
- [ ] Collaborative research features
- [ ] Custom prompt templates
- [ ] Image and video search integration
- [ ] Multi-language support
- [ ] Database storage for search history
- [ ] User authentication and profiles
- [ ] API endpoint for programmatic access

## 📝 Code Quality

### Backend Features

- ✅ Modular class-based architecture
- ✅ Type hints for better code clarity
- ✅ Comprehensive error handling
- ✅ Detailed docstrings
- ✅ Clean code principles

### Frontend Features

- ✅ Component-based UI structure
- ✅ Responsive design
- ✅ User-friendly interface
- ✅ Real-time feedback
- ✅ Accessibility considerations

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT models
- **DuckDuckGo** for search API
- **Streamlit** for the amazing web framework
- **LangChain** for LLM integration tools

## 📧 Support

For questions or issues:

- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

## 🎓 Learning Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [LangChain Documentation](https://python.langchain.com/)
- [DuckDuckGo Search API](https://github.com/deedy5/duckduckgo_search)

## 📈 Version History

### v1.0.0 (Current)

- Initial release
- Core search and summarization features
- Beautiful Streamlit UI
- Export functionality
- Search history tracking

---

**Made with ❤️ using Python, Streamlit, and OpenAI**

_Happy Researching! 🚀_
