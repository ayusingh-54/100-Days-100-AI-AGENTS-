"""
Google Maps Business Search Tool - Find businesses locally and create leads.
Uses Apify or Google Places API for ToS-compliant scraping.
"""

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from .apify_scraper import ApifyScraperTool, ApifyScraperConfig
from ..models import Lead
from ..config import Config
from ..utils import parse_company_size

logger = logging.getLogger(__name__)


class GoogleMapsSearchInput(BaseModel):
    """Input schema for Google Maps search."""
    
    query: str = Field(..., description="Search query (e.g., 'SaaS companies', 'Dental clinics')")
    location: str = Field(..., description="City or region to search")
    max_results: int = Field(default=50, ge=1, le=500, description="Max results to fetch")
    location_type: Optional[str] = Field(None, description="Type of location filter")


class GoogleMapsBusinessSearchTool:
    """
    Tool for discovering local businesses and converting them to leads.
    
    Respects ToS by using official APIs:
    - Prefers Google Places API when available
    - Falls back to Apify Google Maps scraper for broader scraping
    
    Important: Always respect rate limits and local laws when scraping contact info.
    """
    
    def __init__(self, token: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the Google Maps search tool.
        
        Args:
            token: Apify token (for scraping fallback)
            api_key: Google Maps API key (for official API)
        """
        self.apify_token = token or Config.APIFY_TOKEN
        self.google_api_key = api_key or Config.GOOGLE_MAPS_API_KEY
    
    def search_businesses(self, search_input: GoogleMapsSearchInput) -> List[Lead]:
        """
        Search for businesses and convert to leads.
        
        Args:
            search_input: Search parameters
        
        Returns:
            List of Lead objects
        """
        try:
            # Try official Google Places API first
            if self.google_api_key:
                leads = self._search_via_google_places_api(search_input)
                if leads:
                    return leads
            
            # Fall back to Apify
            if self.apify_token:
                leads = self._search_via_apify(search_input)
                return leads
            
            logger.error("No API key or Apify token configured for Google Maps search")
            return []
        
        except Exception as e:
            logger.error(f"Error searching Google Maps: {e}")
            return []
    
    def _search_via_google_places_api(self, search_input: GoogleMapsSearchInput) -> List[Lead]:
        """Search using official Google Places API."""
        # Implementation would require google-maps-services library
        # This is a placeholder showing the pattern
        logger.info("Google Places API not fully implemented. Falling back to Apify.")
        return []
    
    def _search_via_apify(self, search_input: GoogleMapsSearchInput) -> List[Lead]:
        """Search using Apify Google Maps actor."""
        try:
            actor_input = self._build_actor_input(search_input)
            
            config = ApifyScraperConfig(
                actor_id=Config.APIFY_ACTOR_IDS.get("google_maps", "apify/google-maps-scraper"),
                token=self.apify_token,
                timeout=Config.APIFY_DEFAULT_TIMEOUT,
                poll_interval=Config.APIFY_POLL_INTERVAL,
            )
            
            scraper = ApifyScraperTool(config)
            result = scraper.run(actor_input)
            scraper.close()
            
            if not result.get("success"):
                logger.error(f"Failed to search Google Maps: {result.get('error')}")
                return []
            
            # Parse results into Lead objects
            leads = self._parse_results(result.get("results", []), search_input.location)
            logger.info(f"Successfully created {len(leads)} leads from Google Maps search")
            
            return leads
        
        except Exception as e:
            logger.error(f"Error searching via Apify: {e}")
            return []
    
    def _build_actor_input(self, search_input: GoogleMapsSearchInput) -> Dict[str, Any]:
        """Build input for Apify Google Maps actor."""
        return {
            "searchStringsArray": [search_input.query],
            "locations": [search_input.location],
            "maxResults": search_input.max_results,
            "includeWebsites": True,
            "includePhoneNumbers": True,
        }
    
    def _parse_results(self, results: List[Dict[str, Any]], location: str) -> List[Lead]:
        """Parse search results into Lead objects."""
        leads = []
        
        for item in results:
            try:
                company_size = None
                if "numberOfReviews" in item:
                    reviews = item.get("numberOfReviews", 0)
                    if reviews > 500:
                        company_size = "enterprise"
                    elif reviews > 100:
                        company_size = "mid"
                    elif reviews > 20:
                        company_size = "small"
                    else:
                        company_size = "micro"
                
                lead = Lead(
                    company_name=item.get("title") or item.get("name") or "Unknown",
                    company_website=item.get("website"),
                    location=location,
                    phone=item.get("phone"),
                    industry=self._infer_industry(item),
                    enrichment_sources=["google_maps_scraper"],
                    lead_score=0.0,
                    raw_data={
                        "address": item.get("address"),
                        "rating": item.get("rating"),
                        "reviews": item.get("numberOfReviews"),
                        "type": item.get("type"),
                        "google_maps_url": item.get("url"),
                        "company_size": company_size,
                    }
                )
                leads.append(lead)
            
            except Exception as e:
                logger.debug(f"Error parsing Google Maps result: {e}")
                continue
        
        return leads
    
    def _infer_industry(self, item: Dict[str, Any]) -> Optional[str]:
        """Try to infer industry from business data."""
        item_type = (item.get("type") or "").lower()
        
        # Map common business types to industries
        type_mapping = {
            "software": "Technology",
            "saas": "Technology",
            "consulting": "Consulting",
            "agency": "Consulting",
            "dental": "Healthcare",
            "healthcare": "Healthcare",
            "medical": "Healthcare",
            "finance": "Financial Services",
            "bank": "Financial Services",
            "real estate": "Real Estate",
            "retail": "Retail",
            "restaurant": "Hospitality",
            "hotel": "Hospitality",
            "manufacturing": "Manufacturing",
        }
        
        for key, industry in type_mapping.items():
            if key in item_type:
                return industry
        
        return None
