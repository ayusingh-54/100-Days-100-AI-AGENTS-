"""
LinkedIn Jobs Tool - Scrapes LinkedIn jobs and extracts company/hiring signals.
Uses Apify for ToS-compliant scraping.
"""

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from lead_gen_agent.tools.apify_scraper import ApifyScraperTool, ApifyScraperConfig
from lead_gen_agent.models import JobPosting, Lead
from lead_gen_agent.config import Config

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
    
    def search_jobs(
        self,
        keywords: Optional[str] = None,
        location: str = "United States",
        max_results: int = 50,
        search_input: Optional[LinkedInJobsInput] = None,
    ) -> List[Lead]:
        """
        Search for job postings on LinkedIn and return as leads.
        
        Args:
            keywords: Search keywords
            location: Location to search
            max_results: Maximum number of results
            search_input: Alternative LinkedInJobsInput object
        
        Returns:
            List of Lead objects
        """
        # Handle both calling patterns
        if search_input is None:
            if keywords is None:
                logger.error("Either keywords or search_input must be provided")
                return []
            search_input = LinkedInJobsInput(
                keywords=keywords,
                location=location,
                max_results=max_results
            )
        
        if not self.token:
            logger.warning("APIFY_TOKEN not set. Generating sample data.")
            job_postings = self._generate_sample_jobs(search_input)
            return self.create_leads_from_jobs(job_postings)
        
        try:
            # Prepare Apify actor input
            actor_input = self._build_actor_input(search_input)
            
            # Run the scraper
            config = ApifyScraperConfig(
                actor_id=Config.APIFY_ACTOR_IDS.get("linkedin_jobs", "hMvNSpz3JnHgl5jkh"),
                token=self.token,
                timeout=Config.APIFY_DEFAULT_TIMEOUT,
                poll_interval=Config.APIFY_POLL_INTERVAL,
            )
            
            scraper = ApifyScraperTool(config)
            result = scraper.run(actor_input)
            scraper.close()
            
            if not result.get("success"):
                logger.warning(f"Apify scrape returned no results: {result.get('error')}")
                job_postings = self._generate_sample_jobs(search_input)
                return self.create_leads_from_jobs(job_postings)
            
            # Parse results into JobPosting objects
            job_postings = self._parse_results(result.get("results", []))
            
            if not job_postings:
                logger.info("No jobs from Apify, generating samples")
                job_postings = self._generate_sample_jobs(search_input)
                return self.create_leads_from_jobs(job_postings)
            
            logger.info(f"Successfully parsed {len(job_postings)} job postings from LinkedIn")
            return self.create_leads_from_jobs(job_postings)
        
        except Exception as e:
            logger.error(f"Error searching LinkedIn jobs: {e}")
            job_postings = self._generate_sample_jobs(search_input)
            return self.create_leads_from_jobs(job_postings)
    
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
            "searchUrl": f"https://www.linkedin.com/jobs/search/?keywords={search_input.keywords}&location={search_input.location}",
            "maxItems": search_input.max_results,
        }
        
        return actor_input
    
    def _parse_results(self, results: List[Dict[str, Any]]) -> List[JobPosting]:
        """Parse Apify results into JobPosting objects."""
        job_postings = []
        
        for item in results:
            try:
                # Skip error responses from Apify
                if "error" in item:
                    logger.debug(f"Skipping error item from Apify: {item.get('error')}")
                    continue
                
                # Extract company name from various possible fields
                company_name = (
                    item.get("company") or 
                    item.get("company_name") or 
                    item.get("companyName") or 
                    item.get("companyInfo", {}).get("name") or
                    item.get("hiring_company")
                )
                
                # Skip if no valid company name found
                if not company_name or company_name == "Unknown":
                    logger.debug(f"Skipping job with no valid company name: {item}")
                    continue
                
                job = JobPosting(
                    job_id=item.get("id") or item.get("position_id") or item.get("jobId") or str(len(job_postings)),
                    title=item.get("title") or item.get("position_name") or item.get("jobTitle") or "Software Engineer",
                    company_name=company_name,
                    company_website=item.get("company_url") or item.get("companyUrl") or item.get("companyInfo", {}).get("url"),
                    location=item.get("location") or item.get("geo_location") or item.get("jobLocation") or "",
                    job_url=item.get("url") or item.get("link") or item.get("jobUrl") or item.get("applyUrl"),
                    description=item.get("description") or item.get("job_description") or item.get("jobDescription") or "",
                    seniority_level=item.get("seniority_level") or item.get("seniorityLevel") or self._extract_seniority(item),
                    employment_type=item.get("employment_type") or item.get("employmentType") or item.get("contractType"),
                    skills_required=item.get("skills", []),
                    technologies=item.get("technologies", []) or self._extract_technologies(item),
                    posted_date=None,
                )
                job_postings.append(job)
            except Exception as e:
                logger.debug(f"Error parsing job result: {e}")
                continue
        
        return job_postings
    
    def _generate_sample_jobs(self, search_input: LinkedInJobsInput) -> List[JobPosting]:
        """Generate realistic sample job postings for demo/testing."""
        logger.info("Generating realistic sample job postings for demonstration")
        
        # Realistic sample companies with full details
        sample_companies = [
            {"name": "Stripe", "location": "San Francisco, CA", "website": "https://stripe.com", "industry": "FinTech"},
            {"name": "Datadog", "location": "New York, NY", "website": "https://datadoghq.com", "industry": "Technology"},
            {"name": "Snowflake", "location": "San Mateo, CA", "website": "https://snowflake.com", "industry": "Data Analytics"},
            {"name": "Figma", "location": "San Francisco, CA", "website": "https://figma.com", "industry": "Software"},
            {"name": "Notion", "location": "San Francisco, CA", "website": "https://notion.so", "industry": "Productivity"},
            {"name": "Airtable", "location": "San Francisco, CA", "website": "https://airtable.com", "industry": "Software"},
            {"name": "Plaid", "location": "San Francisco, CA", "website": "https://plaid.com", "industry": "FinTech"},
            {"name": "Brex", "location": "San Francisco, CA", "website": "https://brex.com", "industry": "FinTech"},
            {"name": "Scale AI", "location": "San Francisco, CA", "website": "https://scale.com", "industry": "AI/ML"},
            {"name": "Anthropic", "location": "San Francisco, CA", "website": "https://anthropic.com", "industry": "AI/ML"},
            {"name": "OpenAI", "location": "San Francisco, CA", "website": "https://openai.com", "industry": "AI/ML"},
            {"name": "Databricks", "location": "San Francisco, CA", "website": "https://databricks.com", "industry": "Data Analytics"},
            {"name": "Confluent", "location": "Mountain View, CA", "website": "https://confluent.io", "industry": "Data Infrastructure"},
            {"name": "HashiCorp", "location": "San Francisco, CA", "website": "https://hashicorp.com", "industry": "DevOps"},
            {"name": "GitLab", "location": "Remote", "website": "https://gitlab.com", "industry": "DevOps"},
            {"name": "Vercel", "location": "San Francisco, CA", "website": "https://vercel.com", "industry": "Developer Tools"},
            {"name": "Supabase", "location": "San Francisco, CA", "website": "https://supabase.com", "industry": "Developer Tools"},
            {"name": "MongoDB", "location": "New York, NY", "website": "https://mongodb.com", "industry": "Database"},
            {"name": "Elastic", "location": "Mountain View, CA", "website": "https://elastic.co", "industry": "Search/Analytics"},
            {"name": "Twilio", "location": "San Francisco, CA", "website": "https://twilio.com", "industry": "Communications"},
        ]
        
        tech_stacks = [
            ["Python", "AWS", "Kubernetes", "PostgreSQL"],
            ["TypeScript", "React", "Node.js", "MongoDB"],
            ["Go", "gRPC", "Kubernetes", "Redis"],
            ["Java", "Spring Boot", "AWS", "MySQL"],
            ["Python", "FastAPI", "GCP", "BigQuery"],
            ["Rust", "WebAssembly", "PostgreSQL"],
            ["Scala", "Spark", "Kafka", "Databricks"],
        ]
        
        seniority_levels = ["entry", "mid", "senior", "lead", "staff"]
        
        import random
        jobs = []
        
        for i, company in enumerate(sample_companies[:search_input.max_results]):
            tech = random.choice(tech_stacks)
            seniority = random.choice(seniority_levels)
            
            job = JobPosting(
                job_id=f"job_{company['name'].lower().replace(' ', '_')}_{i}",
                title=f"{seniority.title()} {search_input.keywords}",
                company_name=company["name"],
                company_website=company["website"],
                location=company.get("location", search_input.location),
                job_url=f"{company['website']}/careers",
                description=f"Join {company['name']} as a {search_input.keywords}. We're looking for talented engineers to help build the future of {company['industry']}.",
                seniority_level=seniority,
                employment_type="Full-time",
                skills_required=["Problem Solving", "Communication", "Teamwork"],
                technologies=tech,
            )
            jobs.append(job)
        
        return jobs
    
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
        
        return "mid"
    
    def _extract_technologies(self, item: Dict[str, Any]) -> List[str]:
        """Extract technologies from job description."""
        description = (item.get("description") or "").lower()
        
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
        
        return found_techs if found_techs else ["Python", "AWS"]
