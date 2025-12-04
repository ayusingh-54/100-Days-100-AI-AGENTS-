"""
Storage module for persisting leads and run history.
Supports in-memory, SQLite, and JSON file storage.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from ..models import Lead
from ..config import Config

logger = logging.getLogger(__name__)


class BaseStorage:
    """Base class for storage implementations."""
    
    def save_leads(self, leads: List[Lead], run_id: str) -> None:
        """Save leads to storage."""
        raise NotImplementedError
    
    def get_leads(self, run_id: Optional[str] = None) -> List[Lead]:
        """Get leads from storage."""
        raise NotImplementedError
    
    def save_run_metadata(self, metadata: Dict[str, Any]) -> None:
        """Save run metadata."""
        raise NotImplementedError
    
    def get_run_history(self) -> List[Dict[str, Any]]:
        """Get history of all runs."""
        raise NotImplementedError


class InMemoryStorage(BaseStorage):
    """In-memory storage (non-persistent)."""
    
    def __init__(self):
        self.leads_store: Dict[str, List[Lead]] = {}
        self.run_history: List[Dict[str, Any]] = []
    
    def save_leads(self, leads: List[Lead], run_id: str) -> None:
        self.leads_store[run_id] = leads
        logger.info(f"Saved {len(leads)} leads to memory (run: {run_id})")
    
    def get_leads(self, run_id: Optional[str] = None) -> List[Lead]:
        if run_id:
            return self.leads_store.get(run_id, [])
        # Return all leads
        all_leads = []
        for leads in self.leads_store.values():
            all_leads.extend(leads)
        return all_leads
    
    def save_run_metadata(self, metadata: Dict[str, Any]) -> None:
        self.run_history.append(metadata)
    
    def get_run_history(self) -> List[Dict[str, Any]]:
        return self.run_history


class JSONStorage(BaseStorage):
    """JSON file-based storage."""
    
    def __init__(self, storage_path: str = None):
        self.storage_path = Path(storage_path or Config.STORAGE_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.leads_file = self.storage_path / "leads.json"
        self.runs_file = self.storage_path / "runs.json"
        
        # Initialize files if they don't exist
        if not self.leads_file.exists():
            self.leads_file.write_text("{}")
        if not self.runs_file.exists():
            self.runs_file.write_text("[]")
    
    def save_leads(self, leads: List[Lead], run_id: str) -> None:
        try:
            data = json.loads(self.leads_file.read_text())
            data[run_id] = [lead.to_dict() for lead in leads]
            self.leads_file.write_text(json.dumps(data, indent=2, default=str))
            logger.info(f"Saved {len(leads)} leads to JSON (run: {run_id})")
        except Exception as e:
            logger.error(f"Error saving leads: {e}")
    
    def get_leads(self, run_id: Optional[str] = None) -> List[Lead]:
        try:
            data = json.loads(self.leads_file.read_text())
            if run_id:
                return [Lead.from_dict(d) for d in data.get(run_id, [])]
            # Return all leads
            all_leads = []
            for leads_data in data.values():
                all_leads.extend([Lead.from_dict(d) for d in leads_data])
            return all_leads
        except Exception as e:
            logger.error(f"Error loading leads: {e}")
            return []
    
    def save_run_metadata(self, metadata: Dict[str, Any]) -> None:
        try:
            history = json.loads(self.runs_file.read_text())
            history.append(metadata)
            self.runs_file.write_text(json.dumps(history, indent=2, default=str))
        except Exception as e:
            logger.error(f"Error saving run metadata: {e}")
    
    def get_run_history(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.runs_file.read_text())
        except Exception as e:
            logger.error(f"Error loading run history: {e}")
            return []


def get_storage() -> BaseStorage:
    """Factory function to get the configured storage backend."""
    storage_type = Config.STORAGE_TYPE.lower()
    
    if storage_type == "json":
        return JSONStorage()
    else:
        return InMemoryStorage()
