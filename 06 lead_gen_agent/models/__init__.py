"""
Data models for the Lead Generation Agent.
Includes Lead, Company, JobPosting, and LeadScoreResult models.
"""

from .lead_models import (
    Lead,
    Company,
    JobPosting,
    LeadScoreResult,
    ICPConfig,
    ScoringWeights,
)

__all__ = [
    "Lead",
    "Company",
    "JobPosting",
    "LeadScoreResult",
    "ICPConfig",
    "ScoringWeights",
]
