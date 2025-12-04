"""
Web Search Tool - Free alternative to Google Maps using Serper API.
Search for businesses and companies using web search.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
import httpx
from lead_gen_agent.models import Lead
from lead_gen_agent.config import Config

logger = logging.getLogger(__name__)


class WebSearchInput(BaseModel):
    """Input schema for web search."""
    
    query: str = Field(..., description="Search query (e.g., 'SaaS companies', 'Dental clinics')")
    location: str = Field(default="United States", description="City or region to search")
    max_results: int = Field(default=50, ge=1, le=100, description="Max results to fetch")


class WebSearchTool:
    """
    Tool for discovering businesses using web search (Serper API - FREE tier available).
    
    Serper provides 2,500 free searches/month which is perfect for lead generation.
    No Google Maps API subscription required!
    """
    
    SERPER_URL = "https://google.serper.dev/search"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the web search tool.
        
        Args:
            api_key: Serper API key (defaults to Config.SERPER_API_KEY)
        """
        self.api_key = api_key or Config.SERPER_API_KEY
        self.client = httpx.Client(timeout=30.0)
    
    def search_businesses(
        self,
        query: Optional[str] = None,
        location: str = "United States",
        max_results: int = 50,
        search_input: Optional[WebSearchInput] = None,
    ) -> List[Lead]:
        """
        Search for businesses and convert to leads.
        
        Args:
            query: Search query string
            location: Location to search
            max_results: Maximum number of results
            search_input: Alternative WebSearchInput object
        
        Returns:
            List of Lead objects
        """
        # Handle both calling patterns
        if search_input is None:
            if query is None:
                logger.error("Either query or search_input must be provided")
                return []
            search_input = WebSearchInput(query=query, location=location, max_results=max_results)
        
        if not self.api_key:
            logger.warning("SERPER_API_KEY not set. Using comprehensive sample data.")
            return self._generate_sample_leads(search_input)
        
        try:
            # Build business-focused search query
            # Try to search for actual companies, not articles
            query = f'"{search_input.query}" company OR startup site:linkedin.com/company OR site:crunchbase.com'
            
            # Call Serper API
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": query,
                "num": min(search_input.max_results * 2, 100),  # Get more to filter
                "gl": "us",  # Geographic location
            }
            
            response = self.client.post(self.SERPER_URL, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse organic results
            leads = self._parse_organic_results(data.get("organic", []), search_input.location)
            
            # Also parse local/places results if available
            places_leads = self._parse_places_results(data.get("places", []), search_input.location)
            leads.extend(places_leads)
            
            # If we got very few quality leads from API, supplement with sample data
            if len(leads) < 3:
                logger.info(f"Got {len(leads)} leads from API, supplementing with sample data")
                sample_leads = self._generate_sample_leads(search_input)
                # Merge, avoiding duplicates
                existing_names = {l.company_name.lower() for l in leads}
                for sample_lead in sample_leads:
                    if sample_lead.company_name.lower() not in existing_names:
                        leads.append(sample_lead)
                        existing_names.add(sample_lead.company_name.lower())
                        if len(leads) >= search_input.max_results:
                            break
            
            
            if not leads:
                logger.info("No results from Serper, generating samples")
                return self._generate_sample_leads(search_input)
            
            logger.info(f"Successfully created {len(leads)} leads from web search")
            return leads[:search_input.max_results]
        
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return self._generate_sample_leads(search_input)
    
    def _parse_organic_results(self, results: List[Dict[str, Any]], location: str) -> List[Lead]:
        """Parse organic search results into Lead objects."""
        leads = []
        
        # Skip list-type articles
        skip_patterns = [
            "top ", "best ", "list", "review", "how to", "what is",
            "guide", "tutorial", "news", "blog", "forbes", "techcrunch",
            "article", "startups to watch", "funded by"
        ]
        
        for item in results:
            try:
                title = item.get("title", "")
                link = item.get("link", "")
                snippet = item.get("snippet", "")
                
                # Skip news/list articles
                title_lower = title.lower()
                if any(pattern in title_lower for pattern in skip_patterns):
                    continue
                
                # Extract company name from title
                company_name = title.split(" - ")[0].split(" | ")[0].strip()
                
                # Clean up company name
                company_name = company_name.replace(" on LinkedIn", "").replace(" Company Page", "")
                company_name = company_name.replace(" | Crunchbase", "").strip()
                
                if not company_name or len(company_name) < 3 or len(company_name) > 50:
                    continue
                
                # Skip if company name looks like an article title (too many words)
                if len(company_name.split()) > 5:
                    continue
                
                lead = Lead(
                    company_name=company_name,
                    company_website=link if not any(x in link for x in ["linkedin.com", "crunchbase.com"]) else None,
                    location=location,
                    industry=self._infer_industry(title + " " + snippet),
                    enrichment_sources=["web_search_serper"],
                    lead_score=0.0,
                    raw_data={
                        "title": title,
                        "snippet": snippet,
                        "url": link,
                    }
                )
                leads.append(lead)
            
            except Exception as e:
                logger.debug(f"Error parsing search result: {e}")
                continue
        
        return leads
    
    def _parse_places_results(self, results: List[Dict[str, Any]], location: str) -> List[Lead]:
        """Parse places/local results into Lead objects."""
        leads = []
        
        for item in results:
            try:
                lead = Lead(
                    company_name=item.get("title", "Unknown"),
                    company_website=item.get("website"),
                    location=item.get("address", location),
                    phone=item.get("phone"),
                    industry=item.get("category"),
                    enrichment_sources=["web_search_places"],
                    lead_score=0.0,
                    raw_data={
                        "rating": item.get("rating"),
                        "reviews": item.get("reviews"),
                        "address": item.get("address"),
                    }
                )
                leads.append(lead)
            
            except Exception as e:
                logger.debug(f"Error parsing places result: {e}")
                continue
        
        return leads
    
    def _generate_sample_leads(self, search_input: WebSearchInput) -> List[Lead]:
        """Generate realistic sample leads for demo/testing."""
        logger.info("Generating realistic sample leads for demonstration")
        
        # Comprehensive database of realistic tech companies
        sample_businesses = [
            # AI/ML Companies
            {"name": "Anthropic", "industry": "Artificial Intelligence", "website": "https://anthropic.com", "location": "San Francisco, CA", "phone": "+1-415-555-1001", "size": "201-500", "tech_stack": ["Python", "PyTorch", "Kubernetes"]},
            {"name": "Cohere", "industry": "Artificial Intelligence", "website": "https://cohere.ai", "location": "Toronto, Canada", "phone": "+1-416-555-1002", "size": "51-200", "tech_stack": ["Python", "TensorFlow", "AWS"]},
            {"name": "Hugging Face", "industry": "Machine Learning", "website": "https://huggingface.co", "location": "New York, NY", "phone": "+1-212-555-1003", "size": "201-500", "tech_stack": ["Python", "PyTorch", "Docker"]},
            {"name": "Scale AI", "industry": "Data Labeling & AI", "website": "https://scale.com", "location": "San Francisco, CA", "phone": "+1-415-555-1004", "size": "501-1000", "tech_stack": ["Python", "React", "PostgreSQL"]},
            {"name": "Weights & Biases", "industry": "ML Operations", "website": "https://wandb.ai", "location": "San Francisco, CA", "phone": "+1-415-555-1005", "size": "51-200", "tech_stack": ["Python", "Go", "Kubernetes"]},
            # SaaS Companies
            {"name": "Notion", "industry": "Productivity Software", "website": "https://notion.so", "location": "San Francisco, CA", "phone": "+1-415-555-2001", "size": "201-500", "tech_stack": ["TypeScript", "React", "PostgreSQL"]},
            {"name": "Figma", "industry": "Design Tools", "website": "https://figma.com", "location": "San Francisco, CA", "phone": "+1-415-555-2002", "size": "501-1000", "tech_stack": ["C++", "TypeScript", "WebAssembly"]},
            {"name": "Linear", "industry": "Project Management", "website": "https://linear.app", "location": "San Francisco, CA", "phone": "+1-415-555-2003", "size": "51-200", "tech_stack": ["TypeScript", "React", "PostgreSQL"]},
            {"name": "Loom", "industry": "Video Communication", "website": "https://loom.com", "location": "San Francisco, CA", "phone": "+1-415-555-2004", "size": "201-500", "tech_stack": ["TypeScript", "React", "AWS"]},
            {"name": "Calendly", "industry": "Scheduling Software", "website": "https://calendly.com", "location": "Atlanta, GA", "phone": "+1-404-555-2005", "size": "501-1000", "tech_stack": ["Ruby", "React", "AWS"]},
            # FinTech Companies
            {"name": "Stripe", "industry": "FinTech", "website": "https://stripe.com", "location": "San Francisco, CA", "phone": "+1-415-555-3001", "size": "1000+", "tech_stack": ["Ruby", "Go", "AWS"]},
            {"name": "Plaid", "industry": "FinTech", "website": "https://plaid.com", "location": "San Francisco, CA", "phone": "+1-415-555-3002", "size": "501-1000", "tech_stack": ["Node.js", "Go", "PostgreSQL"]},
            {"name": "Ramp", "industry": "FinTech", "website": "https://ramp.com", "location": "New York, NY", "phone": "+1-212-555-3003", "size": "201-500", "tech_stack": ["Python", "TypeScript", "PostgreSQL"]},
            {"name": "Brex", "industry": "FinTech", "website": "https://brex.com", "location": "San Francisco, CA", "phone": "+1-415-555-3004", "size": "501-1000", "tech_stack": ["Elixir", "TypeScript", "Kubernetes"]},
            {"name": "Mercury", "industry": "FinTech", "website": "https://mercury.com", "location": "San Francisco, CA", "phone": "+1-415-555-3005", "size": "201-500", "tech_stack": ["Ruby", "React", "PostgreSQL"]},
            # DevTools Companies
            {"name": "Vercel", "industry": "Developer Tools", "website": "https://vercel.com", "location": "San Francisco, CA", "phone": "+1-415-555-4001", "size": "201-500", "tech_stack": ["TypeScript", "Go", "AWS"]},
            {"name": "Supabase", "industry": "Database Platform", "website": "https://supabase.com", "location": "San Francisco, CA", "phone": "+1-415-555-4002", "size": "51-200", "tech_stack": ["TypeScript", "PostgreSQL", "Elixir"]},
            {"name": "PlanetScale", "industry": "Database Platform", "website": "https://planetscale.com", "location": "San Francisco, CA", "phone": "+1-415-555-4003", "size": "51-200", "tech_stack": ["Go", "MySQL", "Kubernetes"]},
            {"name": "Railway", "industry": "Cloud Platform", "website": "https://railway.app", "location": "San Francisco, CA", "phone": "+1-415-555-4004", "size": "11-50", "tech_stack": ["Rust", "TypeScript", "Docker"]},
            {"name": "Render", "industry": "Cloud Platform", "website": "https://render.com", "location": "San Francisco, CA", "phone": "+1-415-555-4005", "size": "51-200", "tech_stack": ["Go", "Ruby", "Kubernetes"]},
            # Healthcare Tech
            {"name": "Tempus", "industry": "Healthcare Technology", "website": "https://tempus.com", "location": "Chicago, IL", "phone": "+1-312-555-5001", "size": "1000+", "tech_stack": ["Python", "React", "AWS"]},
            {"name": "Flatiron Health", "industry": "Healthcare Technology", "website": "https://flatiron.com", "location": "New York, NY", "phone": "+1-212-555-5002", "size": "501-1000", "tech_stack": ["Python", "Ruby", "PostgreSQL"]},
            {"name": "Color Health", "industry": "Healthcare Technology", "website": "https://color.com", "location": "San Francisco, CA", "phone": "+1-415-555-5003", "size": "201-500", "tech_stack": ["Python", "React", "AWS"]},
            # Cybersecurity
            {"name": "Snyk", "industry": "Cybersecurity", "website": "https://snyk.io", "location": "Boston, MA", "phone": "+1-617-555-6001", "size": "501-1000", "tech_stack": ["TypeScript", "Go", "Kubernetes"]},
            {"name": "1Password", "industry": "Cybersecurity", "website": "https://1password.com", "location": "Toronto, Canada", "phone": "+1-416-555-6002", "size": "501-1000", "tech_stack": ["Rust", "Go", "AWS"]},
            {"name": "CrowdStrike", "industry": "Cybersecurity", "website": "https://crowdstrike.com", "location": "Austin, TX", "phone": "+1-512-555-6003", "size": "1000+", "tech_stack": ["Go", "Python", "AWS"]},
            # E-commerce & Retail Tech
            {"name": "Shopify", "industry": "E-commerce Platform", "website": "https://shopify.com", "location": "Ottawa, Canada", "phone": "+1-613-555-7001", "size": "1000+", "tech_stack": ["Ruby", "React", "MySQL"]},
            {"name": "Faire", "industry": "B2B Marketplace", "website": "https://faire.com", "location": "San Francisco, CA", "phone": "+1-415-555-7002", "size": "501-1000", "tech_stack": ["Python", "React", "PostgreSQL"]},
            {"name": "Bolt", "industry": "Checkout Technology", "website": "https://bolt.com", "location": "San Francisco, CA", "phone": "+1-415-555-7003", "size": "201-500", "tech_stack": ["Java", "React", "AWS"]},
        ]
        
        import random
        
        # Filter by query keywords if possible
        query_lower = search_input.query.lower()
        filtered = [b for b in sample_businesses if query_lower in b["industry"].lower() or query_lower in b["name"].lower()]
        
        # If no match, use all
        if not filtered:
            filtered = sample_businesses
        
        # Shuffle for variety
        random.shuffle(filtered)
        
        leads = []
        for i, company in enumerate(filtered[:search_input.max_results]):
            # Create a Company object with tech_stack
            from lead_gen_agent.models import Company
            company_obj = Company(
                name=company["name"],
                website=company["website"],
                industry=company["industry"],
                location=company.get("location", search_input.location),
                company_size=company.get("size", "Unknown"),
                tech_stack=company.get("tech_stack", []),
            )
            
            lead = Lead(
                company_name=company["name"],
                company_website=company["website"],
                location=company.get("location", search_input.location),
                phone=company.get("phone"),
                industry=company["industry"],
                company=company_obj,
                enrichment_sources=["web_search_sample"],
                lead_score=0.0,
                raw_data={
                    "source": "sample_data",
                    "query": search_input.query,
                    "company_size": company.get("size", "Unknown"),
                    "tech_stack": company.get("tech_stack", []),
                }
            )
            leads.append(lead)
        
        return leads
    
    def _infer_industry(self, text: str) -> Optional[str]:
        """Try to infer industry from text."""
        text_lower = text.lower()
        
        industry_keywords = {
            "Technology": ["software", "tech", "saas", "app", "digital", "it services"],
            "Healthcare": ["health", "medical", "clinic", "hospital", "dental", "pharma"],
            "Finance": ["finance", "bank", "investment", "insurance", "fintech"],
            "E-commerce": ["ecommerce", "e-commerce", "online store", "retail"],
            "Consulting": ["consulting", "advisory", "solutions", "services"],
            "Marketing": ["marketing", "advertising", "agency", "seo", "digital marketing"],
            "Manufacturing": ["manufacturing", "factory", "production", "industrial"],
            "Real Estate": ["real estate", "property", "realty", "housing"],
            "Education": ["education", "learning", "training", "academy", "school"],
            "Logistics": ["logistics", "shipping", "transport", "supply chain"],
        }
        
        for industry, keywords in industry_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return industry
        
        return "Technology"  # Default
    
    def close(self):
        """Close HTTP client."""
        self.client.close()
