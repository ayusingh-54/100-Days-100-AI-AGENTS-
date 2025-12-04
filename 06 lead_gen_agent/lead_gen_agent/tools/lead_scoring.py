"""
Lead Scoring Tool - LLM-based lead scoring and analysis.
Scores leads against an Ideal Customer Profile (ICP).
"""

import logging
import json
import re
from typing import Dict, Any, Optional
from lead_gen_agent.models import Lead, LeadScoreResult, PriorityBucket, ICPConfig, ScoringWeights
from lead_gen_agent.config import Config

logger = logging.getLogger(__name__)


class LeadScoringTool:
    """
    Scores leads using LLM-powered analysis against an ICP.
    
    Scoring factors:
    - Company size match
    - Industry alignment
    - Technology stack match
    - Geography alignment
    - Role seniority
    - Hiring signals
    """
    
    def __init__(self):
        """Initialize the scoring tool."""
        self.llm = None
        self._init_llm()
    
    def _init_llm(self):
        """Initialize LLM for scoring."""
        try:
            if Config.OPENAI_API_KEY:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    model_name=Config.OPENAI_MODEL,
                    temperature=0.2,
                    timeout=Config.LLM_TIMEOUT,
                    api_key=Config.OPENAI_API_KEY,
                )
        except Exception as e:
            logger.warning(f"Could not initialize LLM for scoring: {e}")
            self.llm = None
    
    def score_lead(self, lead: Lead, icp_config: ICPConfig, scoring_weights: Optional[ScoringWeights] = None) -> LeadScoreResult:
        """
        Score a lead against ICP.
        
        Args:
            lead: Lead to score
            icp_config: ICP configuration
            scoring_weights: Scoring weights configuration
        
        Returns:
            LeadScoreResult with score and analysis
        """
        try:
            weights = scoring_weights or ScoringWeights()
            
            # Use LLM scoring if available
            if self.llm:
                return self._score_with_llm(lead, icp_config, weights)
            else:
                return self._score_with_heuristics(lead, icp_config, weights)
        
        except Exception as e:
            logger.error(f"Error scoring lead: {e}")
            return self._create_default_result(lead, str(e))
    
    def _score_with_llm(self, lead: Lead, icp_config: ICPConfig, weights: ScoringWeights) -> LeadScoreResult:
        """Score using LLM analysis."""
        try:
            # Build ICP description
            icp_parts = []
            if icp_config.target_company_sizes:
                icp_parts.append(f"Target sizes: {', '.join(icp_config.target_company_sizes)}")
            if icp_config.target_industries:
                icp_parts.append(f"Target industries: {', '.join(icp_config.target_industries)}")
            if icp_config.preferred_tech_stack:
                icp_parts.append(f"Preferred tech: {', '.join(icp_config.preferred_tech_stack)}")
            if icp_config.target_geographies:
                icp_parts.append(f"Target regions: {', '.join(icp_config.target_geographies)}")
            
            icp_desc = "\n".join(icp_parts) if icp_parts else "General B2B companies"
            
            # Build lead description
            tech_stack = []
            if lead.company and lead.company.tech_stack:
                tech_stack.extend(lead.company.tech_stack)
            if lead.source_job_posting and lead.source_job_posting.technologies:
                tech_stack.extend(lead.source_job_posting.technologies)
            
            hiring_signals = "None"
            if lead.source_job_posting:
                hiring_signals = f"Hiring for: {lead.source_job_posting.title}"
            
            prompt = f"""Score this lead against the ICP on a scale of 0-100.

ICP (Ideal Customer Profile):
{icp_desc}

Lead Information:
- Company: {lead.company_name}
- Industry: {lead.industry or 'Unknown'}
- Location: {lead.location or 'Unknown'}
- Tech Stack: {', '.join(set(tech_stack)) if tech_stack else 'Unknown'}
- Hiring Signals: {hiring_signals}

Return ONLY a JSON object with:
- score: number between 0-100
- priority: "HIGH", "MEDIUM", or "LOW"
- analysis: brief explanation (2-3 sentences)

Return only valid JSON."""

            response = self.llm.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse response
            json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                score = float(data.get("score", 50))
                score = max(0, min(100, score))
                priority_str = data.get("priority", "MEDIUM").upper()
                priority = PriorityBucket(priority_str) if priority_str in ["HIGH", "MEDIUM", "LOW"] else PriorityBucket.MEDIUM
                analysis = data.get("analysis", "Scored by AI analysis.")
            else:
                # Fallback to heuristics
                return self._score_with_heuristics(lead, icp_config, weights)
            
            # Update lead
            lead.lead_score = score
            lead.priority = priority
            lead.reasons_for_score = analysis
            
            return LeadScoreResult(
                lead_id=f"lead_{lead.company_name}_{hash(str(lead.name)) % 1000}",
                company_name=lead.company_name,
                lead_score=score,
                priority=priority,
                analysis=analysis,
            )
        
        except Exception as e:
            logger.error(f"LLM scoring failed: {e}")
            return self._score_with_heuristics(lead, icp_config, weights)
    
    def _score_with_heuristics(self, lead: Lead, icp_config: ICPConfig, weights: ScoringWeights) -> LeadScoreResult:
        """Score using rule-based heuristics."""
        score = 50.0  # Base score
        reasons = []
        
        # Industry match
        if lead.industry and icp_config.target_industries:
            if any(ind.lower() in lead.industry.lower() for ind in icp_config.target_industries):
                score += 20
                reasons.append(f"Industry match: {lead.industry}")
            else:
                score -= 10
        
        # Location match
        if lead.location and icp_config.target_geographies:
            if any(geo.lower() in lead.location.lower() for geo in icp_config.target_geographies):
                score += 15
                reasons.append(f"Location match: {lead.location}")
        
        # Tech stack match
        lead_tech = []
        if lead.company and lead.company.tech_stack:
            lead_tech.extend(lead.company.tech_stack)
        if lead.source_job_posting and lead.source_job_posting.technologies:
            lead_tech.extend(lead.source_job_posting.technologies)
        
        if lead_tech and icp_config.preferred_tech_stack:
            matches = sum(1 for t in lead_tech if any(p.lower() in t.lower() for p in icp_config.preferred_tech_stack))
            if matches > 0:
                score += min(matches * 5, 20)
                reasons.append(f"Tech match: {matches} technologies")
        
        # Hiring signals (positive indicator)
        if lead.source_job_posting:
            score += 15
            reasons.append("Active hiring signal detected")
        
        # Normalize score
        score = max(0, min(100, score))
        
        # Determine priority
        if score >= 70:
            priority = PriorityBucket.HIGH
        elif score >= 40:
            priority = PriorityBucket.MEDIUM
        else:
            priority = PriorityBucket.LOW
        
        analysis = ". ".join(reasons) if reasons else "Basic scoring applied."
        
        # Update lead
        lead.lead_score = score
        lead.priority = priority
        lead.reasons_for_score = analysis
        
        return LeadScoreResult(
            lead_id=f"lead_{lead.company_name}_{hash(str(lead.name)) % 1000}",
            company_name=lead.company_name,
            lead_score=score,
            priority=priority,
            analysis=analysis,
        )
    
    def _create_default_result(self, lead: Lead, error_msg: str) -> LeadScoreResult:
        """Create a default result when scoring fails."""
        lead.lead_score = 50.0
        lead.priority = PriorityBucket.MEDIUM
        lead.reasons_for_score = f"Default score assigned: {error_msg}"
        
        return LeadScoreResult(
            lead_id=f"lead_{lead.company_name}_{hash(str(lead.name)) % 1000}",
            company_name=lead.company_name,
            lead_score=50.0,
            priority=PriorityBucket.MEDIUM,
            analysis=f"Default score assigned due to: {error_msg}",
        )
