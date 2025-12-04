# 🎯 Lead Generation AI Agent

A production-ready, end-to-end lead generation system built with **LangChain**, **LangGraph**, and **Streamlit**. This agent automates the process of finding, enriching, and scoring B2B leads using AI and ethical web scraping.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![LangChain](https://img.shields.io/badge/LangChain-latest-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Features

### Lead Generation & Enrichment

- 🔍 **LinkedIn Job Scraping** - Find hiring companies and extract signals
- 📍 **Google Maps Business Discovery** - Discover local businesses
- 📄 **CSV Import** - Enrich existing lead lists
- 🏢 **Company Enrichment** - Enrich data using website parsing and LLM

### Intelligent Lead Scoring

- 🎯 **ICP-Based Scoring** - Score leads against your Ideal Customer Profile
- ⚖️ **Configurable Weights** - Adjust scoring weights for your needs
- 🏷️ **Priority Buckets** - Automatic HIGH/MEDIUM/LOW classification
- 📝 **Detailed Analysis** - LLM-generated explanations for each score

### Modern Dashboard

- 📊 **Interactive Analytics** - Charts and KPIs
- 🔎 **Advanced Filtering** - Filter by score, industry, location
- 📥 **Export Options** - Download JSON or CSV
- 📋 **Lead Management** - View and analyze individual leads

## 📁 Project Structure

```
lead_gen_agent/
├── app.py                 # Streamlit web UI
├── main.py                # CLI entry point
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
│
├── models/                # Data models (Pydantic)
│   ├── __init__.py
│   └── lead_models.py     # Lead, Company, JobPosting, etc.
│
├── tools/                 # LangChain tools
│   ├── __init__.py
│   ├── apify_scraper.py   # Generic Apify scraper
│   ├── linkedin_jobs.py   # LinkedIn jobs tool
│   ├── google_maps.py     # Google Maps search tool
│   ├── company_enrichment.py  # Company enrichment
│   └── lead_scoring.py    # LLM-based scoring
│
├── graph/                 # LangGraph workflow
│   ├── __init__.py
│   └── workflow.py        # Main workflow definition
│
├── cli/                   # Command-line interface
│   ├── __init__.py
│   └── main.py            # CLI commands
│
├── config/                # Configuration
│   └── __init__.py        # Config class
│
├── storage/               # Data persistence
│   └── __init__.py        # Storage backends
│
└── utils/                 # Utility functions
    └── __init__.py
```

## 🛠️ Installation

### Prerequisites

- Python 3.10 or higher
- OpenAI API key
- (Optional) Apify token for web scraping
- (Optional) Google Maps API key

### Setup

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/lead_gen_agent.git
cd lead_gen_agent
```

2. **Create virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:

```env
OPENAI_API_KEY=your-openai-api-key-here
APIFY_TOKEN=your-apify-token-here  # Optional
GOOGLE_MAPS_API_KEY=your-key-here  # Optional
```

## 🎮 Usage

### Web UI (Streamlit)

Run the interactive dashboard:

```bash
streamlit run app.py
```

This opens a browser with:

- ⚙️ Configuration sidebar
- 🚀 Run Agent tab
- 📋 Leads & Filters tab
- 📊 Analytics tab
- 📝 Logs tab

### Command-Line Interface (CLI)

**Search for leads:**

```bash
python main.py search --keywords "Data Engineer" --location "Bangalore" \
                      --sources linkedin --max-leads 50 \
                      --industries "SaaS" --output leads.json
```

**Enrich from CSV:**

```bash
python main.py enrich --csv-file companies.csv \
                      --industries "Enterprise Software" \
                      --output leads_scored.json
```

**Show configuration:**

```bash
python main.py config
```

### Programmatic Usage

```python
from lead_gen_agent import run_lead_gen_workflow, ICPConfig

# Define ICP
icp_config = ICPConfig(
    target_industries=["SaaS", "Enterprise Software"],
    target_company_sizes=["mid", "enterprise"],
    preferred_tech_stack=["Python", "AWS", "Kubernetes"],
    target_geographies=["North America"],
)

# Run workflow
result = run_lead_gen_workflow(
    search_keywords="Data Engineer",
    search_location="San Francisco",
    search_source=["linkedin", "google_maps"],
    max_leads=100,
    icp_config=icp_config,
)

# Access results
for lead in result.scored_leads[:10]:
    print(f"{lead.company_name}: {lead.lead_score:.1f} ({lead.priority.value})")
```

## 🔧 Configuration

### ICP Configuration

```python
icp_config = ICPConfig(
    target_company_sizes=["small", "mid", "enterprise"],
    target_industries=["SaaS", "FinTech", "Healthcare"],
    preferred_tech_stack=["Python", "AWS", "Docker", "Kubernetes"],
    target_geographies=["North America", "Europe"],
    target_roles=["CTO", "VP Engineering", "Director of Data"],
    min_company_headcount=50,
    max_company_headcount=1000,
)
```

### Scoring Weights

```python
scoring_weights = ScoringWeights(
    company_size_weight=0.15,
    industry_match_weight=0.20,
    tech_stack_match_weight=0.20,
    geography_weight=0.15,
    role_seniority_weight=0.15,
    hiring_signal_weight=0.15,
)
```

## 📊 Output Format

### JSON Output

```json
[
  {
    "company_name": "TechCorp Inc.",
    "name": "John Smith",
    "title": "Engineering Manager",
    "company_website": "https://techcorp.io",
    "location": "San Francisco, CA",
    "industry": "SaaS",
    "lead_score": 85.0,
    "priority": "HIGH",
    "reasons_for_score": "Strong ICP match: enterprise SaaS company...",
    "enrichment_sources": ["linkedin_jobs_scraper", "company_enrichment_tool"]
  }
]
```

### CSV Output

| company_name  | name       | title       | email | location      | industry | lead_score | priority |
| ------------- | ---------- | ----------- | ----- | ------------- | -------- | ---------- | -------- |
| TechCorp Inc. | John Smith | Eng Manager |       | San Francisco | SaaS     | 85.0       | HIGH     |

## 🏗️ Architecture

### LangGraph Workflow

```
┌─────────────────┐
│   input_node    │  Validate inputs
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ source_selection│  Choose data sources
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  scraping_node  │  Fetch from LinkedIn, Google Maps, CSV
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ enrichment_node │  Enrich company data
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  scoring_node   │  LLM-based scoring
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ filtering_node  │  Sort by score
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  output_node    │  Format results
└─────────────────┘
```

### Tools Overview

| Tool                           | Purpose                | Data Source             |
| ------------------------------ | ---------------------- | ----------------------- |
| `LinkedInJobsTool`             | Extract hiring signals | Apify LinkedIn actor    |
| `GoogleMapsBusinessSearchTool` | Find local businesses  | Apify/Google Places API |
| `CompanyEnrichmentTool`        | Enrich company data    | Website parsing + LLM   |
| `LeadScoringTool`              | Score leads vs ICP     | OpenAI LLM              |
| `ApifyScraperTool`             | Generic Apify runner   | Apify API               |

## ⚠️ Ethical & Legal Considerations

This tool is designed with ethics and ToS compliance in mind:

- ✅ **Uses official APIs** or compliant third-party services (Apify)
- ✅ **Respects robots.txt** and rate limits
- ❌ **Does NOT** bypass authentication or login
- ❌ **Does NOT** circumvent rate limits
- ❌ **Does NOT** scrape personal data without consent

**Important:** Before using in production:

1. Review and comply with LinkedIn, Google, and Apify ToS
2. Ensure GDPR/CCPA compliance for data handling
3. Only collect publicly available business information
4. Implement proper data retention policies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) - LLM orchestration
- [LangGraph](https://github.com/langchain-ai/langgraph) - Workflow graphs
- [Streamlit](https://streamlit.io/) - Web UI framework
- [OpenAI](https://openai.com/) - LLM provider
- [Apify](https://apify.com/) - Web scraping platform
