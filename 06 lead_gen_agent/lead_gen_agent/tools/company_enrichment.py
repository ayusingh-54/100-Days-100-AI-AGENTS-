"""
Company Enrichment Tool - Enriches company data using web search and LLM.
"""

import logging
import re
from typing import Dict, Any, Optional
import httpx
from lead_gen_agent.models import Company, Lead
from lead_gen_agent.config import Config

logger = logging.getLogger(__name__)


class CompanyEnrichmentTool:
    """
    Enriches company information using:
    - Website content parsing
    - LLM-based information extraction
    
    This tool focuses on ethical, ToS-compliant enrichment.
    """
    
    def __init__(self):
        """Initialize the enrichment tool."""
        self.http_client = httpx.Client(timeout=Config.HTTP_TIMEOUT, follow_redirects=True)
        self.llm = None
        self._init_llm()
    
    def _init_llm(self):
        """Initialize LLM for extraction."""
        try:
            if Config.OPENAI_API_KEY:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    model_name=Config.OPENAI_MODEL,
                    temperature=0.3,
                    timeout=Config.LLM_TIMEOUT,
                    api_key=Config.OPENAI_API_KEY,
                )
        except Exception as e:
            logger.warning(f"Could not initialize LLM: {e}")
            self.llm = None
    
    def enrich_company(self, company_name: str, company_website: Optional[str] = None, location: Optional[str] = None) -> Optional[Company]:
        """
        Enrich company data.
        
        Args:
            company_name: Company name
            company_website: Company website URL
            location: Company location
        
        Returns:
            Enriched Company object or None if enrichment fails
        """
        try:
            company_data = {
                "name": company_name,
                "location": location,
                "website": company_website,
            }
            
            # Try to fetch and parse website content
            if company_website:
                web_content = self._fetch_website_content(company_website)
                if web_content:
                    extracted = self._extract_company_info(web_content, company_name)
                    company_data.update(extracted)
            
            # Create Company object
            company = Company(
                name=company_name,
                website=company_website,
                location=location or company_data.get("location"),
                description=company_data.get("description"),
                industry=company_data.get("industry"),
                company_size=company_data.get("company_size"),
                tech_stack=company_data.get("tech_stack", []),
            )
            
            logger.info(f"Successfully enriched company: {company_name}")
            return company
        
        except Exception as e:
            logger.error(f"Error enriching company {company_name}: {e}")
            return Company(name=company_name, website=company_website, location=location)
    
    def enrich_lead(self, lead: Lead) -> Lead:
        """
        Enrich a lead with company information.
        
        Args:
            lead: Lead to enrich
        
        Returns:
            Updated lead with enriched company data
        """
        try:
            enriched_company = self.enrich_company(
                company_name=lead.company_name,
                company_website=str(lead.company_website) if lead.company_website else None,
                location=lead.location,
            )
            
            if enriched_company:
                lead.company = enriched_company
                if not lead.industry and enriched_company.industry:
                    lead.industry = enriched_company.industry
                if not lead.location and enriched_company.location:
                    lead.location = enriched_company.location
                if "company_enrichment_tool" not in lead.enrichment_sources:
                    lead.enrichment_sources.append("company_enrichment_tool")
            
            return lead
        
        except Exception as e:
            logger.error(f"Error enriching lead: {e}")
            return lead
    
    def _fetch_website_content(self, website_url: str, max_length: int = 5000) -> Optional[str]:
        """Fetch and extract text from website."""
        try:
            # Build proper URL if needed
            url = website_url if website_url.startswith("http") else f"https://{website_url}"
            
            # Fetch page
            headers = {"User-Agent": Config.USER_AGENT}
            response = self.http_client.get(url, headers=headers)
            
            if response.status_code != 200:
                return None
            
            html = response.text
            
            # Simple text extraction: remove HTML tags
            text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            text = text[:max_length]
            
            return text.strip()
        
        except Exception as e:
            logger.debug(f"Error fetching website {website_url}: {e}")
            return None
    
    def _extract_company_info(self, content: str, company_name: str) -> Dict[str, Any]:
        """Extract company info using LLM or heuristics."""
        result = {
            "description": None,
            "industry": None,
            "company_size": None,
            "tech_stack": [],
        }
        
        # Try LLM extraction
        if self.llm:
            try:
                prompt = f"""Extract company information from this website content for {company_name}.
Return ONLY a JSON object with these fields (use null if not found):
- industry: Main industry/vertical (string)
- company_size: Size category - micro, small, mid, or enterprise (string)
- description: Brief description in 1-2 sentences (string)
- tech_stack: List of technologies mentioned (array of strings)

Website content:
{content[:3000]}

Return only valid JSON, nothing else."""

                response = self.llm.invoke(prompt)
                response_text = response.content if hasattr(response, 'content') else str(response)
                
                # Parse JSON from response
                import json
                # Try to find JSON in response
                json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    result.update({k: v for k, v in data.items() if v is not None})
            except Exception as e:
                logger.debug(f"LLM extraction failed: {e}")
        
        # Fallback: Use heuristics
        if not result["industry"]:
            result["industry"] = self._detect_industry_heuristic(content)
        
        if not result["tech_stack"]:
            result["tech_stack"] = self._detect_tech_stack_heuristic(content)
        
        return result
    
    def _detect_industry_heuristic(self, content: str) -> Optional[str]:
        """Detect industry using keyword matching."""
        content_lower = content.lower()
        
        industry_keywords = {
            "Technology": ["software", "saas", "tech", "platform", "cloud", "digital"],
            "Healthcare": ["health", "medical", "patient", "clinic", "hospital"],
            "Finance": ["finance", "banking", "investment", "insurance", "fintech"],
            "E-commerce": ["ecommerce", "online store", "shopping", "retail"],
            "Consulting": ["consulting", "advisory", "solutions"],
            "Marketing": ["marketing", "advertising", "agency"],
            "Manufacturing": ["manufacturing", "production", "factory"],
            "Education": ["education", "learning", "training", "courses"],
        }
        
        for industry, keywords in industry_keywords.items():
            if any(kw in content_lower for kw in keywords):
                return industry
        
        return "Technology"
    
    def _detect_tech_stack_heuristic(self, content: str) -> list:
        """Detect tech stack using keyword matching."""
        content_lower = content.lower()
        
        techs = {
            "Python": ["python"],
            "JavaScript": ["javascript", "node.js", "react", "vue", "angular"],
            "AWS": ["aws", "amazon web services"],
            "Azure": ["azure", "microsoft azure"],
            "Docker": ["docker", "container"],
            "Kubernetes": ["kubernetes", "k8s"],
            "AI/ML": ["machine learning", "ai", "artificial intelligence", "deep learning"],
        }
        
        found = []
        for tech, keywords in techs.items():
            if any(kw in content_lower for kw in keywords):
                found.append(tech)
        
        return found if found else ["Cloud", "SaaS"]
    
    def close(self):
        """Close HTTP client."""
        self.http_client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
