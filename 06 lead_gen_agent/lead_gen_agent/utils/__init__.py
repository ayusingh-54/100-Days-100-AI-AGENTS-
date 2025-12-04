"""
Utility functions and helpers.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib


logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def generate_id(prefix: str, data: Dict[str, Any]) -> str:
    """Generate a unique ID based on prefix and data."""
    hash_input = json.dumps(data, sort_keys=True, default=str)
    hash_val = hashlib.md5(hash_input.encode()).hexdigest()[:8]
    return f"{prefix}_{hash_val}_{int(datetime.now().timestamp())}"


def format_json(obj: Any) -> str:
    """Format object as pretty JSON."""
    return json.dumps(obj, indent=2, default=str)


def truncate_text(text: Optional[str], max_length: int = 100) -> str:
    """Truncate text to max length."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def deduplicate_leads(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate leads based on company_name and name."""
    seen = set()
    unique = []
    for lead in leads:
        key = (lead.get("company_name", "").lower(), lead.get("name", "").lower())
        if key not in seen:
            seen.add(key)
            unique.append(lead)
    return unique


def normalize_location(location: str) -> str:
    """Normalize location string."""
    if not location:
        return ""
    return location.strip().title()


def parse_company_size(size_str: Optional[str]) -> Optional[str]:
    """Parse and normalize company size."""
    if not size_str:
        return None
    
    size_lower = size_str.lower()
    
    if any(x in size_lower for x in ["1-10", "1-50", "micro", "freelancer"]):
        return "micro"
    elif any(x in size_lower for x in ["11-50", "50-200", "small"]):
        return "small"
    elif any(x in size_lower for x in ["51-200", "201-500", "500-1000", "mid", "medium"]):
        return "mid"
    elif any(x in size_lower for x in ["1000+", "enterprise", "large", "5001+"]):
        return "enterprise"
    
    return None


def safe_get(data: Dict, *keys, default=None):
    """Safely get nested dictionary values."""
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key, default)
        else:
            return default
    return result if result is not None else default
