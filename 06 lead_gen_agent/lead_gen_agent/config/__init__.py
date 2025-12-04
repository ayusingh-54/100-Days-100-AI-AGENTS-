"""
Configuration module for the Lead Generation Agent.
Loads environment variables and provides centralized configuration.
"""

import os
from typing import Optional
from pathlib import Path
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Central configuration class."""
    
    # ==================== API Keys & Credentials ====================
    # Load from environment variables - NEVER hardcode secrets!
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Use a cost-effective model by default
    OPENAI_MODEL_ADVANCED: str = os.getenv("OPENAI_MODEL_ADVANCED", "gpt-4o")  # For complex reasoning
    
    APIFY_TOKEN: str = os.getenv("APIFY_TOKEN", "")
    APIFY_DEFAULT_TIMEOUT: int = int(os.getenv("APIFY_DEFAULT_TIMEOUT", "300"))
    APIFY_POLL_INTERVAL: int = int(os.getenv("APIFY_POLL_INTERVAL", "5"))
    
    # Example actor IDs for common scraping tasks
    APIFY_ACTOR_IDS = {
        "linkedin_jobs": os.getenv("APIFY_ACTOR_LINKEDIN_JOBS", "hMvNSpz3JnHgl5jkh"),
        "google_maps": os.getenv("APIFY_ACTOR_GOOGLE_MAPS", "nwua9Gu5YrADL7ZDj"),
        "website_scraper": os.getenv("APIFY_ACTOR_WEBSITE", "YrQuEkowkNCLdmGCs"),
    }
    
    # Optional APIs - Serper is FREE alternative to Google Maps
    GOOGLE_MAPS_API_KEY: Optional[str] = os.getenv("GOOGLE_MAPS_API_KEY") or None
    SERPER_API_KEY: Optional[str] = os.getenv("SERPER_API_KEY") or None
    
    # ==================== LLM Configuration ====================
    
    LLM_TEMPERATURE: float = 0.3  # Lower temperature for more deterministic responses
    LLM_MAX_TOKENS: int = 1024
    LLM_TIMEOUT: int = 60
    
    # ==================== Application Settings ====================
    
    # Maximum number of leads to fetch in a single run
    MAX_LEADS_PER_RUN: int = int(os.getenv("MAX_LEADS_PER_RUN", "100"))
    
    # Enable/disable verbose logging
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Storage settings
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "memory")  # Options: memory, sqlite, json
    STORAGE_PATH: str = os.getenv("STORAGE_PATH", "./data")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./lead_gen.db")
    
    # ==================== Scraping & Enrichment Settings ====================
    
    # Request timeout for HTTP calls
    HTTP_TIMEOUT: int = 30
    
    # Maximum retries for failed API calls
    MAX_RETRIES: int = 3
    RETRY_BACKOFF_FACTOR: float = 2.0
    
    # User agent for HTTP requests (be respectful!)
    USER_AGENT: str = "LeadGenAI-Agent/1.0"
    
    # Respect robots.txt and rate limits
    RESPECT_ROBOTS_TXT: bool = True
    REQUEST_DELAY: float = 1.0  # Seconds between requests to the same domain
    
    # ==================== LangGraph & Workflow Settings ====================
    
    # Number of parallel workers for enrichment
    PARALLEL_WORKERS: int = int(os.getenv("PARALLEL_WORKERS", "3"))
    
    # Node timeout in seconds
    NODE_TIMEOUT: int = 60
    
    # ==================== Validation & Helpers ====================
    
    @classmethod
    def validate(cls) -> dict:
        """Validate that required environment variables are set."""
        status = {
            "openai": bool(cls.OPENAI_API_KEY),
            "apify": bool(cls.APIFY_TOKEN),
            "serper": bool(cls.SERPER_API_KEY),
            "google_maps": bool(cls.GOOGLE_MAPS_API_KEY),
        }
        
        if not cls.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set. LLM features will not work.")
        
        if not cls.APIFY_TOKEN:
            logger.warning("APIFY_TOKEN not set. Apify-based scraping will not work.")
        
        if not cls.SERPER_API_KEY:
            logger.info("SERPER_API_KEY not set. Web search features limited.")
        
        return status
    
    @classmethod
    def to_dict(cls) -> dict:
        """Return configuration as dictionary (excluding secrets)."""
        return {
            "OPENAI_MODEL": cls.OPENAI_MODEL,
            "OPENAI_MODEL_ADVANCED": cls.OPENAI_MODEL_ADVANCED,
            "MAX_LEADS_PER_RUN": cls.MAX_LEADS_PER_RUN,
            "DEBUG": cls.DEBUG,
            "STORAGE_TYPE": cls.STORAGE_TYPE,
            "PARALLEL_WORKERS": cls.PARALLEL_WORKERS,
            "APIFY_ACTORS": cls.APIFY_ACTOR_IDS,
            "HAS_OPENAI": bool(cls.OPENAI_API_KEY),
            "HAS_APIFY": bool(cls.APIFY_TOKEN),
            "HAS_SERPER": bool(cls.SERPER_API_KEY),
        }


# Create data directory if it doesn't exist
Path(Config.STORAGE_PATH).mkdir(parents=True, exist_ok=True)
