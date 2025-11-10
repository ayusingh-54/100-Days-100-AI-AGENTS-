# 👗 Vibe Matcher - Interactive Streamlit App

An AI-powered fashion recommender that matches your style vibes with perfect product recommendations using OpenAI embeddings and cosine similarity.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-Embeddings-green.svg)

---

## 🌟 Features

### 🔍 **Smart Search**

- Natural language vibe queries
- Real-time AI-powered matching
- Quick suggestion buttons
- Intelligent query validation

### 📊 **Rich Visualizations**

- Interactive score distribution charts
- Latency tracking over time
- Performance metrics dashboard
- Beautiful product cards

### 📚 **Catalog Browser**

- Filter by vibe tags
- Search by product name
- Full product details
- Expandable product cards

### 📈 **Analytics Dashboard**

- Search statistics
- Score distribution analysis
- Latency performance tracking
- Fallback rate monitoring

### 📜 **Search History**

- Complete search log
- Repeat previous searches
- Performance metrics per search
- Clear history option

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager
- OpenAI API key (optional - synthetic embeddings work offline)

### Installation

```powershell
# 1. Navigate to project directory
cd c:\Users\ayusi\Desktop\AGENTS\aa

# 2. Activate virtual environment
..\\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set OpenAI API key (optional)
$env:OPENAI_API_KEY = 'sk-...'

# 5. Run the app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 🎯 How to Use

### 1. **Search by Vibe**

- Enter your style vibe in natural language
- Examples:
  - "energetic urban chic"
  - "soft cozy loungewear"
  - "boho festival earthy"
- Click **Search** or use quick suggestions

### 2. **View Results**

- See top-ranked products
- Check similarity scores
- Explore vibe tags
- Read full descriptions

### 3. **Browse Catalog**

- Filter by vibe tags
- Search by name
- Explore all products

### 4. **Analyze Performance**

- View search statistics
- Track score distributions
- Monitor latency trends

### 5. **Review History**

- See past searches
- Repeat successful queries
- Track your preferences

---

## 🎨 App Structure

### Main Tabs

#### 🔍 **Search Tab**

- Main search interface
- Quick suggestion buttons
- Real-time results with metrics
- Score visualization

#### 📚 **Catalog Browser Tab**

- Full product listing
- Multi-select vibe filters
- Name search
- Detailed product cards

#### 📊 **Analytics Tab**

- Performance metrics
- Score distribution histogram
- Latency trends
- Recent searches table

#### 📜 **History Tab**

- Complete search log
- Repeat search functionality
- Performance per search
- Clear history button

---

## ⚙️ Configuration

### Sidebar Settings

**Display Options:**

- Show/hide similarity scores
- Show/hide full descriptions
- Adjust number of results (1-10)

**Statistics:**

- Total products in catalog
- Total searches performed
- Unique vibe tags

**Thresholds:**

- Good Hit: ≥ 0.7
- Fallback: < 0.35

---

## 📁 File Structure

```
aa/
├── app.py                          # Main Streamlit application
├── vibe_matcher_backend.py         # Core backend logic
├── requirements.txt                # Python dependencies
├── data/
│   └── embeddings_cache.json       # Cached embeddings (auto-generated)
├── notebooks/
│   └── vibe_matcher.ipynb          # Jupyter notebook version
└── src/                            # Original utility modules
    ├── embeddings.py
    ├── search.py
    └── utils.py
```

---

## 🎯 Key Components

### Backend (`vibe_matcher_backend.py`)

**Functions:**

- `initialize_embeddings()` - Load catalog and generate embeddings
- `search_vibes()` - Complete search pipeline
- `rank_by_similarity()` - Cosine similarity ranking
- `validate_query()` - Input validation
- `get_metrics_summary()` - Calculate performance metrics

**Data Structures:**

- `RankedResult` - Dataclass for search results
- Product catalog with 10 fashion items
- Vibe tags for each product

### Frontend (`app.py`)

**Features:**

- Custom CSS styling
- Session state management
- Multiple tabs with rich content
- Interactive visualizations (Plotly)
- Real-time search
- History tracking

---

## 💡 Usage Examples

### Example 1: Urban Streetwear

**Query:** `"energetic urban chic"`

**Expected Results:**

1. Urban Streetwear Bomber (Score: ~0.52)
2. Tech Wear Cargo Pants (Score: ~0.51)
3. Vintage Denim Jacket (Score: ~0.50)

**Vibes:** urban, streetwear, bold, edgy, energetic

---

### Example 2: Cozy Comfort

**Query:** `"soft cozy loungewear comfort"`

**Expected Results:**

1. Cozy Loungewear Bundle (Score: ~0.53)
2. Minimalist Cashmere Sweater (Score: ~0.51)
3. Sustainable Linen Set (Score: ~0.49)

**Vibes:** cozy, soft, comfortable, relaxed

---

### Example 3: Bohemian Festival

**Query:** `"boho festival earthy tribal"`

**Expected Results:**

1. Boho Maxi Dress (Score: ~0.54)
2. Festival Fringe Top (Score: ~0.52)
3. Sustainable Linen Set (Score: ~0.48)

**Vibes:** boho, festival, earthy, tribal

---

## 🔧 Customization

### Add More Products

Edit `vibe_matcher_backend.py` in the `get_product_catalog()` function:

```python
{
    "id": 11,
    "name": "Your Product Name",
    "desc": "Detailed description...",
    "vibes": ["vibe1", "vibe2", "vibe3"]
}
```

### Adjust Thresholds

In `vibe_matcher_backend.py`:

```python
FALLBACK_THRESHOLD = 0.35  # Minimum acceptable score
GOOD_HIT_THRESHOLD = 0.7   # High-quality match threshold
TOP_K = 3                  # Default number of results
```

### Modify UI Colors

In `app.py`, edit the CSS in the `st.markdown()` section:

```css
background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
```

---

## 📊 Performance

### Typical Metrics

- **Average Latency:** 25-50ms (with caching)
- **First Query:** ~100ms (cold start)
- **Cached Queries:** < 10ms
- **Embedding Generation:** ~500ms per batch (OpenAI API)

### Optimization Tips

1. **Use Caching:** Embeddings are cached automatically
2. **Batch Queries:** Pre-generate embeddings for common queries
3. **Adjust TOP_K:** Fewer results = faster rendering
4. **Synthetic Mode:** Use without API key for instant responses

---

## 🐛 Troubleshooting

### Issue: "No module named 'streamlit'"

**Solution:**

```powershell
pip install -r requirements.txt
```

### Issue: "No module named 'plotly'"

**Solution:**

```powershell
pip install plotly
```

### Issue: Low similarity scores

**Cause:** Using synthetic embeddings (no API key)

**Solution:** Set `OPENAI_API_KEY` environment variable:

```powershell
$env:OPENAI_API_KEY = 'sk-...'
```

### Issue: App not loading

**Solution:**

```powershell
# Check if streamlit is installed
streamlit --version

# Re-run with verbose output
streamlit run app.py --logger.level=debug
```

---

## 🌐 Deployment

### Deploy to Streamlit Cloud

1. **Push to GitHub:**

   ```bash
   git add .
   git commit -m "Add Vibe Matcher Streamlit app"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud:**

   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repo
   - Select `aa/app.py` as main file
   - Add `OPENAI_API_KEY` in Secrets

3. **Secrets Configuration:**
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```

### Deploy to Heroku

1. **Create `Procfile`:**

   ```
   web: streamlit run aa/app.py --server.port=$PORT
   ```

2. **Deploy:**
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

---

## 🔐 Security

### API Key Management

**Never commit API keys to GitHub!**

**Local Development:**

```powershell
# Use environment variable
$env:OPENAI_API_KEY = 'sk-...'
```

**Production:**

- Use Streamlit Secrets
- Use environment variables
- Use secret management services

---

## 📈 Future Enhancements

### Planned Features

- [ ] Multi-modal search (text + images)
- [ ] User accounts and preferences
- [ ] Favorites/Wishlist functionality
- [ ] Product comparison tool
- [ ] Style quiz for recommendations
- [ ] Integration with e-commerce APIs
- [ ] Export recommendations to PDF
- [ ] Social sharing features
- [ ] Advanced filtering options
- [ ] Personalized recommendations

### Technical Improvements

- [ ] Migrate to Pinecone/FAISS for vector DB
- [ ] Implement hybrid search (tags + embeddings)
- [ ] Add LLM-based reranking
- [ ] Query expansion with GPT
- [ ] A/B testing framework
- [ ] Performance monitoring
- [ ] User feedback loop
- [ ] Batch embedding pipeline

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

This project is part of the 100 Days - 100 AI Agents Challenge.

---

## 👨‍💻 Author

**Ayush Singh**

- GitHub: [@ayusingh-54](https://github.com/ayusingh-54)
- LinkedIn: [@ayush-singh54](https://www.linkedin.com/in/ayush-singh54/)

---

## 🙏 Acknowledgments

- **OpenAI** - Embedding API
- **Streamlit** - Web framework
- **Plotly** - Interactive visualizations
- **scikit-learn** - Cosine similarity

---

## 📞 Support

For issues or questions:

- Open an issue on GitHub
- Check the troubleshooting section
- Review the documentation

---

**Built with ❤️ for Nexora AI - Where prototypes become products, fast.**

_Last Updated: November 10, 2025_
