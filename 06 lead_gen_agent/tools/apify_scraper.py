"""
Apify Scraper Tool - Generic abstraction for Apify-based scraping.
Handles API communication, polling, and result fetching.
"""

import logging
import time
import json
from typing import Dict, Any, Optional, List
import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ApifyScraperConfig(BaseModel):
    """Configuration for Apify scraper."""
    
    actor_id: str = Field(..., description="Apify actor ID")
    token: str = Field(..., description="Apify token")
    timeout: int = Field(default=300, description="Timeout in seconds")
    poll_interval: int = Field(default=5, description="Polling interval in seconds")


class ApifyScraperTool:
    """
    Generic tool for running Apify actors and collecting results.
    
    Usage:
        config = ApifyScraperConfig(actor_id="...", token="...")
        scraper = ApifyScraperTool(config)
        results = scraper.run(input_data={"keywords": "...", "country": "..."})
    """
    
    BASE_URL = "https://api.apify.com/v2"
    
    def __init__(self, config: ApifyScraperConfig):
        """Initialize the Apify scraper."""
        self.config = config
        self.client = httpx.Client(timeout=config.timeout)
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run an Apify actor and return results.
        
        Args:
            input_data: Input parameters for the actor
        
        Returns:
            Dictionary with results or error information
        """
        try:
            # Start the actor run
            run_id = self._start_run(input_data)
            logger.info(f"Started Apify run: {run_id}")
            
            # Wait for completion
            run_data = self._wait_for_completion(run_id)
            
            if run_data.get("status") != "SUCCEEDED":
                logger.error(f"Run failed with status: {run_data.get('status')}")
                return {
                    "success": False,
                    "error": f"Run failed: {run_data.get('status')}",
                    "results": []
                }
            
            # Fetch results
            results = self._fetch_results(run_id)
            
            logger.info(f"Successfully retrieved {len(results)} results from Apify")
            
            return {
                "success": True,
                "run_id": run_id,
                "results": results,
            }
        
        except Exception as e:
            logger.error(f"Apify scraper error: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    def _start_run(self, input_data: Dict[str, Any]) -> str:
        """Start an Apify actor run."""
        url = f"{self.BASE_URL}/acts/{self.config.actor_id}/runs"
        params = {"token": self.config.token}
        
        response = self.client.post(url, json=input_data, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get("data", {}).get("id")
    
    def _wait_for_completion(self, run_id: str, max_attempts: Optional[int] = None) -> Dict[str, Any]:
        """Poll run status until completion or timeout."""
        url = f"{self.BASE_URL}/actor-runs/{run_id}"
        params = {"token": self.config.token}
        
        start_time = time.time()
        attempts = 0
        max_attempts = max_attempts or (self.config.timeout // self.config.poll_interval)
        
        while attempts < max_attempts:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            
            run_data = response.json().get("data", {})
            status = run_data.get("status")
            
            if status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
                return run_data
            
            logger.debug(f"Run {run_id} status: {status}, waiting...")
            time.sleep(self.config.poll_interval)
            attempts += 1
        
        raise TimeoutError(f"Apify run timed out after {self.config.timeout}s")
    
    def _fetch_results(self, run_id: str, limit: int = 10000) -> List[Dict[str, Any]]:
        """Fetch results from a completed run."""
        url = f"{self.BASE_URL}/actor-runs/{run_id}/dataset/items"
        params = {
            "token": self.config.token,
            "limit": limit,
            "format": "json"
        }
        
        response = self.client.get(url, params=params)
        response.raise_for_status()
        
        # Response is a list of items
        return response.json()
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
