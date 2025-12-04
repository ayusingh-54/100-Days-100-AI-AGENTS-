"""
LinkedIn Jobs Tool - Scrapes LinkedIn jobs and extracts company/hiring signals.
Uses Apify for ToS-compliant scraping.
"""

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from .apify_scraper import ApifyScraperTool, ApifyScraperConfig
from ..models import JobPosting, Lead
from ..config import Config

logger = logging.getLogger(__name__)


class LinkedInJobsInput(BaseModel):
    """Input schema for LinkedIn jobs search."""
    
    keywords: str = Field(..., description="Job keywords/titles to search")
    location: str = Field(..., description="Geographic location")
    company_name: Optional[str] = Field(None, description="Optional: specific company name")
    experience_level: Optional[str] = Field(None, description="Experience level (entry, mid-level, senior, executive)")
    max_results: int = Field(default=50, ge=1, le=500, description="Max results to fetch")


class LinkedInJobsTool:
    """
    Tool for scraping LinkedIn job postings to identify hiring companies and create leads.
    
    Important: This tool respects LinkedIn's ToS by using Apify, which provides
    compliant scraping through their actors.
    
    For production use, you should:
    1. Use LinkedIn's official API (if you have access)
    2. Or use Apify's official LinkedIn actor
    3. Never implement custom login/automation that bypasses LinkedIn's authentication
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the LinkedIn jobs tool.
        
        Args:
            token: Apify token (defaults to Config.APIFY_TOKEN)
        """
        self.token = token or Config.APIFY_TOKEN
        if not self.token:
            logger.warning("APIFY_TOKEN not configured. LinkedIn scraping will not work.")
    
    def search_jobs(self, search_input: LinkedInJobsInput) -> List[JobPosting]:
        """
        Search for job postings on LinkedIn.
        
        Args:
            search_input: Search parameters
        
        Returns:
            List of JobPosting objects
        """
        if not self.token:
            logger.error("APIFY_TOKEN not set. Cannot scrape LinkedIn jobs.")
            return []
        
        try:
            # Prepare Apify actor input
            actor_input = self._build_actor_input(search_input)
            
            # Run the scraper
            config = ApifyScraperConfig(
                actor_id=Config.APIFY_ACTOR_IDS.get("linkedin_jobs", "apify/linkedin-jobs-scraper"),
                token=self.token,
                timeout=Config.APIFY_DEFAULT_TIMEOUT,
                poll_interval=Config.APIFY_POLL_INTERVAL,
            )
            
            scraper = ApifyScraperTool(config)
            result = scraper.run(actor_input)
            scraper.close()
            
            if not result.get("success"):
                logger.error(f"Failed to scrape LinkedIn jobs: {result.get('error')}")
                return []
            
            # Parse results into JobPosting objects
            job_postings = self._parse_results(result.get("results", []))
            logger.info(f"Successfully parsed {len(job_postings)} job postings from LinkedIn")
            
            return job_postings
        
        except Exception as e:
            logger.error(f"Error searching LinkedIn jobs: {e}")
            return []
    
    def create_leads_from_jobs(self, job_postings: List[JobPosting]) -> List[Lead]:
        """
        Convert job postings into leads based on hiring signals.
        
        Args:
            job_postings: List of job postings
        
        Returns:
            List of Lead objects with hiring company information
        """
        leads = []
        
        for job in job_postings:
            # Create a lead for each hiring company
            lead = Lead(
                company_name=job.company_name,
                company_website=job.company_website,
                location=job.location,
                source_job_posting=job,
                enrichment_sources=["linkedin_jobs_scraper"],
                lead_score=0.0,  # Will be scored by LeadScoringTool
                raw_data={
                    "job_title": job.title,
                    "job_url": str(job.job_url) if job.job_url else None,
                    "seniority": job.seniority_level,
                    "technologies": job.technologies,
                }
            )
            leads.append(lead)
        
        return leads
    
    def _build_actor_input(self, search_input: LinkedInJobsInput) -> Dict[str, Any]:
        """Build input for Apify LinkedIn actor."""
        actor_input = {
            "searchStrings": [search_input.keywords],
            "locations": [search_input.location],
            "maxResults": search_input.max_results,
        }
        
        if search_input.company_name:
            actor_input["companies"] = [search_input.company_name]
        
        if search_input.experience_level:
            actor_input["experienceLevels"] = [search_input.experience_level]
        
        return actor_input
    
    def _parse_results(self, results: List[Dict[str, Any]]) -> List[JobPosting]:
        """Parse Apify results into JobPosting objects."""
        job_postings = []
        
        for item in results:
            try:
                job = JobPosting(
                    job_id=item.get("id") or item.get("position_id") or str(len(job_postings)),
                    title=item.get("title") or item.get("position_name") or "Unknown",
                    company_name=item.get("company") or item.get("company_name") or "Unknown",
                    company_website=item.get("company_url"),
                    location=item.get("location") or item.get("geo_location") or "",
                    job_url=item.get("url") or item.get("link"),
                    description=item.get("description") or item.get("job_description") or "",
                    seniority_level=item.get("seniority_level") or self._extract_seniority(item),
                    employment_type=item.get("employment_type"),
                    skills_required=item.get("skills", []),
                    technologies=item.get("technologies", []) or self._extract_technologies(item),
                    posted_date=None,  # Apify may not always provide this
                )
                job_postings.append(job)
            except Exception as e:
                logger.debug(f"Error parsing job result: {e}")
                continue
        
        return job_postings
    
    def _extract_seniority(self, item: Dict[str, Any]) -> Optional[str]:
        """Try to extract seniority level from description."""
        description = (item.get("description") or "").lower()
        
        if any(x in description for x in ["entry", "junior", "internship"]):
            return "entry"
        elif any(x in description for x in ["mid-level", "mid-career", "intermediate"]):
            return "mid"
        elif any(x in description for x in ["senior", "lead", "principal"]):
            return "senior"
        elif any(x in description for x in ["manager", "director", "vp", "c-level"]):
            return "executive"
        
        return None
    
    def _extract_technologies(self, item: Dict[str, Any]) -> List[str]:
        """Extract technologies from job description."""
        description = (item.get("description") or "").lower()
        
        # Common tech keywords
        tech_keywords = {
            "python": ["python"],
            "javascript": ["javascript", "js", "node.js", "nodejs"],
            "java": ["java"],
            "golang": ["go", "golang"],
            "rust": ["rust"],
            "csharp": ["c#", "csharp", ".net"],
            "react": ["react", "reactjs"],
            "vue": ["vue", "vuejs"],
            "angular": ["angular"],
            "aws": ["aws", "amazon web services"],
            "gcp": ["gcp", "google cloud"],
            "azure": ["azure", "microsoft azure"],
            "kubernetes": ["kubernetes", "k8s"],
            "docker": ["docker"],
            "sql": ["sql", "postgres", "mysql", "postgresql"],
            "nosql": ["mongodb", "dynamodb", "cassandra"],
            "ai/ml": ["machine learning", "deep learning", "ai", "llm", "gpt"],
        }
        
        found_techs = []
        for tech, keywords in tech_keywords.items():
            if any(kw in description for kw in keywords):
                found_techs.append(tech)
        
        return found_techs
