"""
Lead Scoring Tool - LLM-based lead scoring and analysis.
Scores leads against an Ideal Customer Profile (ICP).
"""

import logging
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from ..models import Lead, LeadScoreResult, PriorityBucket, ICPConfig, ScoringWeights
from ..config import Config

logger = logging.getLogger(__name__)


class LeadScoringInput(BaseModel):
    """Input for lead scoring."""
    
    lead: Lead = Field(..., description="Lead to score")
    icp_config: ICPConfig = Field(..., description="ICP configuration")
    scoring_weights: Optional[ScoringWeights] = Field(None, description="Scoring weights")


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
        self.llm = ChatOpenAI(
            model_name=Config.OPENAI_MODEL_ADVANCED,  # Use better model for reasoning
            temperature=0.2,  # Low temperature for consistent scoring
            timeout=Config.LLM_TIMEOUT,
        )
        self._setup_scoring_chain()
    
    def score_lead(self, input_data: LeadScoringInput) -> LeadScoreResult:
        """
        Score a lead against ICP.
        
        Args:
            input_data: Scoring input with lead and ICP
        
        Returns:
            LeadScoreResult with score and analysis
        """
        try:
            weights = input_data.scoring_weights or ScoringWeights()
            
            # Build scoring context
            context = self._build_scoring_context(
                input_data.lead,
                input_data.icp_config,
                weights
            )
            
            # Use LLM to analyze and score
            analysis = self._analyze_lead(context)
            
            # Parse score from analysis
            score = self._extract_score(analysis)
            priority = self._determine_priority(score)
            
            result = LeadScoreResult(
                lead_id=f"lead_{input_data.lead.company_name}_{hash(str(input_data.lead.name)) % 1000}",
                company_name=input_data.lead.company_name,
                lead_score=score,
                priority=priority,
                analysis=analysis,
            )
            
            # Update the lead with score
            input_data.lead.lead_score = score
            input_data.lead.priority = priority
            input_data.lead.reasons_for_score = analysis
            
            logger.info(f"Scored lead {input_data.lead.company_name}: {score} ({priority})")
            
            return result
        
        except Exception as e:
            logger.error(f"Error scoring lead: {e}")
            # Return a default low score on error
            return LeadScoreResult(
                lead_id="unknown",
                company_name=input_data.lead.company_name,
                lead_score=0.0,
                priority=PriorityBucket.LOW,
                analysis=f"Error during scoring: {str(e)}",
            )
    
    def _setup_scoring_chain(self):
        """Setup LLM chain for scoring."""
        prompt_template = """You are an expert lead scoring analyst. Score the following lead based on their fit with the Ideal Customer Profile.

IDEAL CUSTOMER PROFILE:
{icp_description}

LEAD INFORMATION:
Company: {company_name}
Industry: {industry}
Location: {location}
Company Size: {company_size}
Contact: {contact_info}
Tech Stack: {tech_stack}
Hiring Signals: {hiring_signals}

Scoring Weights:
- Company Size Match: {company_size_weight}
- Industry Match: {industry_match_weight}
- Tech Stack Match: {tech_stack_match_weight}
- Geography Match: {geography_weight}
- Role Seniority: {role_seniority_weight}
- Hiring Signals: {hiring_signal_weight}

Provide a detailed analysis including:
1. Overall fit score (0-100)
2. Strength in each dimension
3. Key reasons for the score
4. Recommendation (HIGH/MEDIUM/LOW priority)

Format your response as JSON with fields: score, analysis, priority"""
        
        self.scoring_prompt = PromptTemplate(
            template=prompt_template,
            input_variables=[
                "icp_description", "company_name", "industry", "location",
                "company_size", "contact_info", "tech_stack", "hiring_signals",
                "company_size_weight", "industry_match_weight", "tech_stack_match_weight",
                "geography_weight", "role_seniority_weight", "hiring_signal_weight"
            ],
        )
    
    def _build_scoring_context(
        self,
        lead: Lead,
        icp_config: ICPConfig,
        weights: ScoringWeights
    ) -> Dict[str, Any]:
        """Build context for LLM scoring."""
        # Build ICP description
        icp_parts = []
        if icp_config.target_company_sizes:
            icp_parts.append(f"Target company sizes: {', '.join(icp_config.target_company_sizes)}")
        if icp_config.target_industries:
            icp_parts.append(f"Target industries: {', '.join(icp_config.target_industries)}")
        if icp_config.preferred_tech_stack:
            icp_parts.append(f"Preferred tech stack: {', '.join(icp_config.preferred_tech_stack)}")
        if icp_config.target_geographies:
            icp_parts.append(f"Target geographies: {', '.join(icp_config.target_geographies)}")
        if icp_config.target_roles:
            icp_parts.append(f"Target roles: {', '.join(icp_config.target_roles)}")
        
        icp_description = "\n".join(icp_parts) if icp_parts else "No specific ICP defined"
        
        # Extract tech stack
        tech_stack = []
        if lead.company and lead.company.tech_stack:
            tech_stack.extend(lead.company.tech_stack)
        if lead.source_job_posting and lead.source_job_posting.technologies:
            tech_stack.extend(lead.source_job_posting.technologies)
        
        # Extract hiring signals
        hiring_signals = []
        if lead.source_job_posting:
            hiring_signals.append(f"Recent job posting for: {lead.source_job_posting.title}")
            if lead.source_job_posting.seniority_level:
                hiring_signals.append(f"Hiring for {lead.source_job_posting.seniority_level} level")
        
        contact_info = []
        if lead.name:
            contact_info.append(f"Contact: {lead.name}")
        if lead.title:
            contact_info.append(f"Title: {lead.title}")
        if lead.email:
            contact_info.append(f"Email: {lead.email}")
        
        return {
            "icp_description": icp_description,
            "company_name": lead.company_name,
            "industry": lead.industry or "Unknown",
            "location": lead.location or "Unknown",
            "company_size": lead.company.company_size if lead.company else "Unknown",
            "contact_info": ", ".join(contact_info) if contact_info else "No contact info",
            "tech_stack": ", ".join(set(tech_stack)) if tech_stack else "Not specified",
            "hiring_signals": ", ".join(hiring_signals) if hiring_signals else "None detected",
            "company_size_weight": weights.company_size_weight,
            "industry_match_weight": weights.industry_match_weight,
            "tech_stack_match_weight": weights.tech_stack_match_weight,
            "geography_weight": weights.geography_weight,
            "role_seniority_weight": weights.role_seniority_weight,
            "hiring_signal_weight": weights.hiring_signal_weight,
        }
    
    def _analyze_lead(self, context: Dict[str, Any]) -> str:
        """Use LLM to analyze lead."""
        try:
            chain = LLMChain(llm=self.llm, prompt=self.scoring_prompt)
            response = chain.run(**context)
            return response
        except Exception as e:
            logger.error(f"Error in LLM analysis: {e}")
            return f"Analysis failed: {str(e)}"
    
    def _extract_score(self, analysis: str) -> float:
        """Extract numeric score from LLM response."""
        try:
            # Try to parse JSON
            data = json.loads(analysis)
            score = data.get("score")
            if isinstance(score, (int, float)):
                return float(min(100, max(0, score)))
        except (json.JSONDecodeError, KeyError):
            pass
        
        # Try to find a number between 0-100
        import re
        matches = re.findall(r"\b(\d{1,3})\b", analysis)
        for match in matches:
            score = float(match)
            if 0 <= score <= 100:
                return score
        
        # Default to 50 if can't extract
        logger.debug(f"Could not extract score from analysis: {analysis}")
        return 50.0
    
    def _determine_priority(self, score: float) -> PriorityBucket:
        """Determine priority bucket from score."""
        if score >= 70:
            return PriorityBucket.HIGH
        elif score >= 40:
            return PriorityBucket.MEDIUM
        else:
            return PriorityBucket.LOW
