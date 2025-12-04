"""
Core data models using Pydantic v2 for type safety and validation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class PriorityBucket(str, Enum):
    """Priority buckets for lead classification."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Company(BaseModel):
    """Represents a company with enriched data."""
    
    name: str = Field(..., description="Company name")
    website: Optional[str] = Field(None, description="Company website URL")
    industry: Optional[str] = Field(None, description="Industry vertical")
    company_size: Optional[str] = Field(None, description="Company size (e.g., micro, small, mid, enterprise)")
    estimated_revenue: Optional[str] = Field(None, description="Estimated annual revenue")
    location: Optional[str] = Field(None, description="Company headquarters location")
    description: Optional[str] = Field(None, description="Company description")
    founded_year: Optional[int] = Field(None, description="Year company was founded")
    employee_count: Optional[int] = Field(None, description="Number of employees")
    tech_stack: Optional[List[str]] = Field(default_factory=list, description="Detected technologies")
    
    class Config:
        populate_by_name = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump(exclude_none=True)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Company":
        """Create from dictionary."""
        return cls(**data)


class JobPosting(BaseModel):
    """Represents a job posting."""
    
    job_id: str = Field(..., description="Unique job ID")
    title: str = Field(..., description="Job title")
    company_name: str = Field(..., description="Hiring company")
    company_website: Optional[str] = Field(None, description="Company website")
    location: Optional[str] = Field(None, description="Job location")
    job_url: Optional[str] = Field(None, description="Job posting URL")
    description: Optional[str] = Field(None, description="Job description")
    seniority_level: Optional[str] = Field(None, description="Seniority level (e.g., junior, mid, senior)")
    employment_type: Optional[str] = Field(None, description="Employment type (full-time, contract, etc.)")
    skills_required: Optional[List[str]] = Field(default_factory=list, description="Required skills")
    technologies: Optional[List[str]] = Field(default_factory=list, description="Required technologies")
    posted_date: Optional[datetime] = Field(None, description="When the job was posted")
    
    class Config:
        populate_by_name = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = self.model_dump(exclude_none=True)
        if 'posted_date' in data and data['posted_date']:
            data['posted_date'] = data['posted_date'].isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JobPosting":
        """Create from dictionary."""
        return cls(**data)


class Lead(BaseModel):
    """
    Represents an enriched lead with all relevant information.
    This is the unified lead object containing prospect and company data.
    """
    
    # Prospect information
    name: Optional[str] = Field(None, description="Prospect's full name")
    title: Optional[str] = Field(None, description="Prospect's job title")
    email: Optional[str] = Field(None, description="Prospect's email (if ethically obtainable)")
    phone: Optional[str] = Field(None, description="Prospect's phone number")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    
    # Company information
    company_name: str = Field(..., description="Company name")
    company_website: Optional[str] = Field(None, description="Company website URL")
    company: Optional[Company] = Field(None, description="Enriched company object")
    
    # Location
    location: Optional[str] = Field(None, description="Geographic location")
    
    # Industry and vertical
    industry: Optional[str] = Field(None, description="Industry classification")
    
    # Lead scoring
    lead_score: float = Field(default=0.0, ge=0, le=100, description="Lead score (0-100)")
    priority: PriorityBucket = Field(default=PriorityBucket.MEDIUM, description="Priority bucket")
    reasons_for_score: Optional[str] = Field(None, description="Explanation of scoring decision")
    
    # Enrichment metadata
    enrichment_sources: List[str] = Field(default_factory=list, description="Sources used for enrichment")
    source_job_posting: Optional[JobPosting] = Field(None, description="Associated job posting if from job scrape")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now, description="When lead was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw enrichment data for reference")
    
    class Config:
        populate_by_name = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = self.model_dump(exclude_none=True)
        # Convert datetime to strings
        if 'created_at' in data:
            data['created_at'] = data['created_at'].isoformat()
        if 'updated_at' in data:
            data['updated_at'] = data['updated_at'].isoformat()
        # Convert priority to string
        if 'priority' in data:
            data['priority'] = data['priority'] if isinstance(data['priority'], str) else data['priority'].value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Lead":
        """Create from dictionary."""
        # Handle priority enum
        if 'priority' in data and isinstance(data['priority'], str):
            data['priority'] = PriorityBucket(data['priority'])
        return cls(**data)


class ScoringWeights(BaseModel):
    """Configurable weights for lead scoring."""
    
    company_size_weight: float = Field(default=0.15, ge=0, le=1)
    industry_match_weight: float = Field(default=0.20, ge=0, le=1)
    tech_stack_match_weight: float = Field(default=0.20, ge=0, le=1)
    geography_weight: float = Field(default=0.15, ge=0, le=1)
    role_seniority_weight: float = Field(default=0.15, ge=0, le=1)
    hiring_signal_weight: float = Field(default=0.15, ge=0, le=1)
    
    class Config:
        populate_by_name = True


class ICPConfig(BaseModel):
    """Ideal Customer Profile (ICP) configuration."""
    
    target_company_sizes: List[str] = Field(default_factory=lambda: ["small", "mid", "enterprise"], description="Target company sizes")
    target_industries: List[str] = Field(default_factory=list, description="Target industries")
    preferred_tech_stack: List[str] = Field(default_factory=list, description="Preferred technologies")
    target_geographies: List[str] = Field(default_factory=list, description="Target geographic regions")
    target_roles: List[str] = Field(default_factory=list, description="Target job roles")
    min_company_headcount: Optional[int] = Field(None, description="Minimum company headcount")
    max_company_headcount: Optional[int] = Field(None, description="Maximum company headcount")
    
    class Config:
        populate_by_name = True


class LeadScoreResult(BaseModel):
    """Result of lead scoring analysis."""
    
    lead_id: str = Field(..., description="Lead identifier")
    company_name: str = Field(..., description="Company name")
    lead_score: float = Field(..., ge=0, le=100, description="Score (0-100)")
    priority: PriorityBucket = Field(..., description="Priority bucket")
    analysis: str = Field(..., description="Detailed scoring analysis")
    scoring_timestamp: datetime = Field(default_factory=datetime.now, description="When scoring occurred")
    
    class Config:
        populate_by_name = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = self.model_dump(exclude_none=True)
        if 'scoring_timestamp' in data:
            data['scoring_timestamp'] = data['scoring_timestamp'].isoformat()
        if 'priority' in data:
            data['priority'] = data['priority'] if isinstance(data['priority'], str) else data['priority'].value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LeadScoreResult":
        """Create from dictionary."""
        if 'priority' in data and isinstance(data['priority'], str):
            data['priority'] = PriorityBucket(data['priority'])
        return cls(**data)
