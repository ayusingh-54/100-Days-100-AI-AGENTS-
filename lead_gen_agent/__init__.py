"""
Initialize lead_gen_agent package.
"""

__version__ = "1.0.0"
__author__ = "Lead Gen AI Team"

from .models import Lead, Company, JobPosting, LeadScoreResult, ICPConfig, ScoringWeights
from .graph import run_lead_gen_workflow, build_lead_gen_graph

__all__ = [
    "Lead",
    "Company",
    "JobPosting",
    "LeadScoreResult",
    "ICPConfig",
    "ScoringWeights",
    "run_lead_gen_workflow",
    "build_lead_gen_graph",
]
