"""
Company Enrichment Tool - Enriches company data using web search and parsing.
Uses LLM to extract relevant information from web sources.
"""

import logging
from typing import Dict, Any, Optional, List
import httpx
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from ..models import Company, Lead
from ..config import Config

logger = logging.getLogger(__name__)


class CompanyEnrichmentInput(BaseModel):
    """Input for company enrichment."""
    
    company_name: str = Field(..., description="Company name to enrich")
    company_website: Optional[str] = Field(None, description="Company website URL")
    location: Optional[str] = Field(None, description="Company location")


class CompanyEnrichmentTool:
    """
    Enriches company information using:
    - Website content parsing
    - LLM-based information extraction
    - Public data sources
    
    This tool focuses on ethical, ToS-compliant enrichment.
    """
    
    def __init__(self):
        """Initialize the enrichment tool."""
        self.llm = ChatOpenAI(
            model_name=Config.OPENAI_MODEL,
            temperature=0.3,
            timeout=Config.LLM_TIMEOUT,
        )
        self.http_client = httpx.Client(timeout=Config.HTTP_TIMEOUT)
        self._setup_extraction_chain()
    
    def enrich_company(self, input_data: CompanyEnrichmentInput) -> Optional[Company]:
        """
        Enrich company data.
        
        Args:
            input_data: Company information to enrich
        
        Returns:
            Enriched Company object or None if enrichment fails
        """
        try:
            company_data = {
                "name": input_data.company_name,
                "location": input_data.location,
                "website": input_data.company_website,
            }
            
            # Try to fetch and parse website content
            if input_data.company_website:
                web_content = self._fetch_website_content(input_data.company_website)
                if web_content:
                    extracted = self._extract_company_info(web_content, input_data.company_name)
                    company_data.update(extracted)
            
            # Create Company object
            company = Company(
                name=input_data.company_name,
                website=input_data.company_website,
                location=input_data.location,
                description=company_data.get("description"),
                industry=company_data.get("industry"),
                company_size=company_data.get("company_size"),
                tech_stack=company_data.get("tech_stack", []),
            )
            
            logger.info(f"Successfully enriched company: {input_data.company_name}")
            return company
        
        except Exception as e:
            logger.error(f"Error enriching company {input_data.company_name}: {e}")
            return None
    
    def enrich_lead(self, lead: Lead) -> Lead:
        """
        Enrich a lead with company information.
        
        Args:
            lead: Lead to enrich
        
        Returns:
            Updated lead with enriched company data
        """
        try:
            enrichment_input = CompanyEnrichmentInput(
                company_name=lead.company_name,
                company_website=str(lead.company_website) if lead.company_website else None,
                location=lead.location,
            )
            
            enriched_company = self.enrich_company(enrichment_input)
            if enriched_company:
                lead.company = enriched_company
                if not lead.industry:
                    lead.industry = enriched_company.industry
                if not lead.location:
                    lead.location = enriched_company.location
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
            response = self.http_client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            # Extract text from HTML (basic extraction)
            html = response.text
            
            # Simple text extraction: remove common HTML tags
            import re
            text = re.sub("<[^>]+>", " ", html)
            text = re.sub(r"\s+", " ", text)
            text = text[:max_length]
            
            return text.strip()
        
        except Exception as e:
            logger.debug(f"Error fetching website {website_url}: {e}")
            return None
    
    def _setup_extraction_chain(self):
        """Setup LLM chain for information extraction."""
        prompt_template = """Extract company information from the following website content.
Return a JSON object with these fields (only include if found):
- industry: Main industry/vertical
- company_size: Size category (micro, small, mid, enterprise)
- description: Brief company description
- tech_stack: List of technologies used

Website content:
{content}

Return only valid JSON, no other text."""
        
        self.extraction_prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["content"],
        )
    
    def _extract_company_info(self, content: str, company_name: str) -> Dict[str, Any]:
        """Extract company info using LLM."""
        try:
            chain = LLMChain(llm=self.llm, prompt=self.extraction_prompt)
            response = chain.run(content=content)
            
            # Parse JSON response
            import json
            data = json.loads(response)
            
            return {
                "description": data.get("description"),
                "industry": data.get("industry"),
                "company_size": data.get("company_size"),
                "tech_stack": data.get("tech_stack", []),
            }
        
        except Exception as e:
            logger.debug(f"Error extracting company info: {e}")
            return {}
    
    def close(self):
        """Close HTTP client."""
        self.http_client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
