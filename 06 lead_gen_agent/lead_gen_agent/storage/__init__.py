"""
Lead Generation Agent Storage Module.
Provides in-memory and file-based persistence.
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from lead_gen_agent.models import Lead, PriorityBucket

logger = logging.getLogger(__name__)


class LeadStorage:
    """
    Storage layer for leads with multiple backend options.
    Supports in-memory, JSON file, and SQLite storage.
    """
    
    def __init__(self, storage_type: str = "memory", storage_path: Optional[str] = None):
        """
        Initialize storage.
        
        Args:
            storage_type: "memory", "json", or "sqlite"
            storage_path: Path for file-based storage
        """
        self.storage_type = storage_type
        self.storage_path = Path(storage_path) if storage_path else Path("data/leads")
        self._leads: Dict[str, Lead] = {}
        self._db_conn: Optional[sqlite3.Connection] = None
        
        # Initialize storage backend
        if storage_type == "json":
            self._init_json_storage()
        elif storage_type == "sqlite":
            self._init_sqlite_storage()
    
    def _init_json_storage(self):
        """Initialize JSON file storage."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._json_file = self.storage_path / "leads.json"
        if self._json_file.exists():
            try:
                with open(self._json_file, "r") as f:
                    data = json.load(f)
                    for lead_id, lead_data in data.items():
                        self._leads[lead_id] = Lead(**lead_data)
                logger.info(f"Loaded {len(self._leads)} leads from JSON")
            except Exception as e:
                logger.error(f"Error loading JSON storage: {e}")
    
    def _init_sqlite_storage(self):
        """Initialize SQLite storage."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        db_file = self.storage_path / "leads.db"
        self._db_conn = sqlite3.connect(str(db_file), check_same_thread=False)
        self._create_tables()
        self._load_from_sqlite()
    
    def _create_tables(self):
        """Create SQLite tables."""
        if not self._db_conn:
            return
        
        cursor = self._db_conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                company_name TEXT NOT NULL,
                name TEXT,
                email TEXT,
                phone TEXT,
                linkedin_url TEXT,
                company_website TEXT,
                location TEXT,
                industry TEXT,
                lead_score REAL,
                priority TEXT,
                reasons_for_score TEXT,
                created_at TEXT,
                data_json TEXT
            )
        """)
        self._db_conn.commit()
    
    def _load_from_sqlite(self):
        """Load leads from SQLite."""
        if not self._db_conn:
            return
        
        cursor = self._db_conn.cursor()
        cursor.execute("SELECT id, data_json FROM leads")
        for row in cursor.fetchall():
            try:
                lead_data = json.loads(row[1])
                self._leads[row[0]] = Lead(**lead_data)
            except Exception as e:
                logger.error(f"Error loading lead {row[0]}: {e}")
        
        logger.info(f"Loaded {len(self._leads)} leads from SQLite")
    
    def _generate_lead_id(self, lead: Lead) -> str:
        """Generate unique ID for a lead."""
        base = f"{lead.company_name}_{lead.name or 'unknown'}"
        return f"lead_{hash(base) % 100000}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def add_lead(self, lead: Lead) -> str:
        """
        Add a lead to storage.
        
        Args:
            lead: Lead to add
        
        Returns:
            Lead ID
        """
        lead_id = self._generate_lead_id(lead)
        self._leads[lead_id] = lead
        
        # Persist based on storage type
        if self.storage_type == "json":
            self._save_to_json()
        elif self.storage_type == "sqlite":
            self._save_lead_to_sqlite(lead_id, lead)
        
        logger.info(f"Added lead: {lead_id}")
        return lead_id
    
    def add_leads(self, leads: List[Lead]) -> List[str]:
        """Add multiple leads."""
        ids = []
        for lead in leads:
            lead_id = self.add_lead(lead)
            ids.append(lead_id)
        return ids
    
    def get_lead(self, lead_id: str) -> Optional[Lead]:
        """Get a lead by ID."""
        return self._leads.get(lead_id)
    
    def get_all_leads(self) -> List[Lead]:
        """Get all leads."""
        return list(self._leads.values())
    
    def get_leads_by_priority(self, priority: PriorityBucket) -> List[Lead]:
        """Get leads by priority level."""
        return [lead for lead in self._leads.values() if lead.priority == priority]
    
    def get_leads_by_score(self, min_score: float, max_score: float = 100.0) -> List[Lead]:
        """Get leads within a score range."""
        return [
            lead for lead in self._leads.values()
            if lead.lead_score is not None and min_score <= lead.lead_score <= max_score
        ]
    
    def search_leads(self, query: str) -> List[Lead]:
        """Search leads by company name, industry, or location."""
        query_lower = query.lower()
        results = []
        for lead in self._leads.values():
            if (query_lower in (lead.company_name or "").lower() or
                query_lower in (lead.industry or "").lower() or
                query_lower in (lead.location or "").lower() or
                query_lower in (lead.name or "").lower()):
                results.append(lead)
        return results
    
    def update_lead(self, lead_id: str, updates: Dict[str, Any]) -> bool:
        """Update a lead."""
        if lead_id not in self._leads:
            return False
        
        lead = self._leads[lead_id]
        for key, value in updates.items():
            if hasattr(lead, key):
                setattr(lead, key, value)
        
        if self.storage_type == "json":
            self._save_to_json()
        elif self.storage_type == "sqlite":
            self._save_lead_to_sqlite(lead_id, lead)
        
        return True
    
    def delete_lead(self, lead_id: str) -> bool:
        """Delete a lead."""
        if lead_id not in self._leads:
            return False
        
        del self._leads[lead_id]
        
        if self.storage_type == "json":
            self._save_to_json()
        elif self.storage_type == "sqlite":
            self._delete_from_sqlite(lead_id)
        
        return True
    
    def clear_all(self):
        """Clear all leads."""
        self._leads.clear()
        
        if self.storage_type == "json":
            self._save_to_json()
        elif self.storage_type == "sqlite":
            if self._db_conn:
                cursor = self._db_conn.cursor()
                cursor.execute("DELETE FROM leads")
                self._db_conn.commit()
    
    def _save_to_json(self):
        """Save all leads to JSON file."""
        try:
            data = {
                lead_id: lead.model_dump(mode="json")
                for lead_id, lead in self._leads.items()
            }
            with open(self._json_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
    
    def _save_lead_to_sqlite(self, lead_id: str, lead: Lead):
        """Save a lead to SQLite."""
        if not self._db_conn:
            return
        
        try:
            cursor = self._db_conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO leads 
                (id, company_name, name, email, phone, linkedin_url, company_website, 
                 location, industry, lead_score, priority, reasons_for_score, created_at, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lead_id,
                lead.company_name,
                lead.name,
                lead.email,
                lead.phone,
                lead.linkedin_url,
                lead.company_website,
                lead.location,
                lead.industry,
                lead.lead_score,
                lead.priority.value if lead.priority else None,
                lead.reasons_for_score,
                lead.created_at.isoformat() if lead.created_at else None,
                json.dumps(lead.model_dump(mode="json"), default=str)
            ))
            self._db_conn.commit()
        except Exception as e:
            logger.error(f"Error saving to SQLite: {e}")
    
    def _delete_from_sqlite(self, lead_id: str):
        """Delete a lead from SQLite."""
        if not self._db_conn:
            return
        
        cursor = self._db_conn.cursor()
        cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
        self._db_conn.commit()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics."""
        total = len(self._leads)
        by_priority = {
            "HIGH": len(self.get_leads_by_priority(PriorityBucket.HIGH)),
            "MEDIUM": len(self.get_leads_by_priority(PriorityBucket.MEDIUM)),
            "LOW": len(self.get_leads_by_priority(PriorityBucket.LOW)),
        }
        
        scores = [l.lead_score for l in self._leads.values() if l.lead_score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return {
            "total_leads": total,
            "by_priority": by_priority,
            "average_score": round(avg_score, 2),
            "storage_type": self.storage_type,
        }
    
    def export_to_csv(self, filepath: str) -> bool:
        """Export leads to CSV."""
        import csv
        
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # Header
                writer.writerow([
                    "Company", "Name", "Email", "Phone", "LinkedIn", "Website",
                    "Location", "Industry", "Score", "Priority", "Analysis"
                ])
                # Data
                for lead in self._leads.values():
                    writer.writerow([
                        lead.company_name,
                        lead.name or "",
                        lead.email or "",
                        lead.phone or "",
                        lead.linkedin_url or "",
                        lead.company_website or "",
                        lead.location or "",
                        lead.industry or "",
                        lead.lead_score or "",
                        lead.priority.value if lead.priority else "",
                        lead.reasons_for_score or ""
                    ])
            return True
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
    
    def close(self):
        """Close storage connections."""
        if self._db_conn:
            self._db_conn.close()
            self._db_conn = None


# Global storage instance
_storage: Optional[LeadStorage] = None


def get_storage(storage_type: str = "memory", storage_path: Optional[str] = None) -> LeadStorage:
    """Get or create the global storage instance."""
    global _storage
    if _storage is None:
        _storage = LeadStorage(storage_type, storage_path)
    return _storage
