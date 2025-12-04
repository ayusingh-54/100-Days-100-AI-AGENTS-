"""
Lead Generation Agent - LangGraph Workflow.
Orchestrates the lead generation, enrichment, and scoring pipeline.
"""

import logging
from typing import TypedDict, Annotated, Optional, List, Dict, Any
from datetime import datetime

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage

from lead_gen_agent.models import Lead, ICPConfig, LeadScoreResult, PriorityBucket, ScoringWeights
from lead_gen_agent.config import Config
from lead_gen_agent.tools.apify_scraper import ApifyScraperTool
from lead_gen_agent.tools.linkedin_jobs import LinkedInJobsTool
from lead_gen_agent.tools.web_search import WebSearchTool
from lead_gen_agent.tools.company_enrichment import CompanyEnrichmentTool
from lead_gen_agent.tools.lead_scoring import LeadScoringTool
from lead_gen_agent.storage import get_storage

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for the lead generation workflow."""
    # Input
    query: str
    sources: List[str]  # "linkedin", "web_search", "apify"
    icp_config: Optional[Dict[str, Any]]
    max_results: int
    
    # Processing
    raw_leads: List[Dict[str, Any]]
    enriched_leads: List[Lead]
    scored_leads: List[Lead]
    
    # Output
    final_leads: List[Lead]
    statistics: Dict[str, Any]
    errors: List[str]
    
    # Metadata
    started_at: Optional[str]
    completed_at: Optional[str]


class LeadGenerationWorkflow:
    """
    LangGraph-based workflow for lead generation.
    
    Pipeline:
    1. Input Processing - Parse and validate input
    2. Source Selection - Determine data sources
    3. Data Collection - Scrape/fetch leads from sources
    4. Enrichment - Enrich lead data
    5. Scoring - Score leads against ICP
    6. Aggregation - Combine and deduplicate results
    """
    
    def __init__(self):
        """Initialize the workflow."""
        self.apify_tool = ApifyScraperTool()
        self.linkedin_tool = LinkedInJobsTool()
        self.web_search_tool = WebSearchTool()
        self.enrichment_tool = CompanyEnrichmentTool()
        self.scoring_tool = LeadScoringTool()
        self.storage = get_storage()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("input_processor", self._process_input)
        workflow.add_node("linkedin_scraper", self._scrape_linkedin)
        workflow.add_node("web_searcher", self._search_web)
        workflow.add_node("enricher", self._enrich_leads)
        workflow.add_node("scorer", self._score_leads)
        workflow.add_node("aggregator", self._aggregate_results)
        
        # Define edges
        workflow.add_edge(START, "input_processor")
        workflow.add_conditional_edges(
            "input_processor",
            self._route_to_sources,
            {
                "linkedin": "linkedin_scraper",
                "web_search": "web_searcher",
                "enricher": "enricher",
            }
        )
        workflow.add_edge("linkedin_scraper", "enricher")
        workflow.add_edge("web_searcher", "enricher")
        workflow.add_edge("enricher", "scorer")
        workflow.add_edge("scorer", "aggregator")
        workflow.add_edge("aggregator", END)
        
        return workflow.compile()
    
    def _route_to_sources(self, state: AgentState) -> str:
        """Route to appropriate data source."""
        sources = state.get("sources", ["web_search"])
        
        if "linkedin" in sources:
            return "linkedin"
        elif "web_search" in sources:
            return "web_search"
        else:
            return "enricher"
    
    def _process_input(self, state: AgentState) -> AgentState:
        """Process and validate input."""
        logger.info("Processing input...")
        
        state["started_at"] = datetime.now().isoformat()
        state["raw_leads"] = []
        state["enriched_leads"] = []
        state["scored_leads"] = []
        state["final_leads"] = []
        state["errors"] = []
        state["statistics"] = {}
        
        # Set defaults
        if not state.get("sources"):
            state["sources"] = ["web_search"]
        if not state.get("max_results"):
            state["max_results"] = 10
        
        return state
    
    def _scrape_linkedin(self, state: AgentState) -> AgentState:
        """Scrape LinkedIn for job postings and leads."""
        logger.info("Scraping LinkedIn jobs...")
        
        try:
            query = state["query"]
            max_results = state.get("max_results", 10)
            
            leads = self.linkedin_tool.search_jobs(
                keywords=query,
                max_results=max_results
            )
            
            for lead in leads:
                state["raw_leads"].append(lead.model_dump())
            
            logger.info(f"Found {len(leads)} leads from LinkedIn")
        
        except Exception as e:
            error_msg = f"LinkedIn scraping error: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
        
        return state
    
    def _search_web(self, state: AgentState) -> AgentState:
        """Search web for businesses/leads."""
        logger.info("Searching web for businesses...")
        
        try:
            query = state["query"]
            max_results = state.get("max_results", 10)
            
            leads = self.web_search_tool.search_businesses(
                query=query,
                max_results=max_results
            )
            
            for lead in leads:
                state["raw_leads"].append(lead.model_dump())
            
            logger.info(f"Found {len(leads)} leads from web search")
        
        except Exception as e:
            error_msg = f"Web search error: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
        
        return state
    
    def _enrich_leads(self, state: AgentState) -> AgentState:
        """Enrich lead data."""
        logger.info("Enriching leads...")
        
        enriched = []
        for raw_lead in state["raw_leads"]:
            try:
                # Convert to Lead if needed
                if isinstance(raw_lead, dict):
                    lead = Lead(**raw_lead)
                else:
                    lead = raw_lead
                
                # Enrich company data
                enriched_lead = self.enrichment_tool.enrich_lead(lead)
                enriched.append(enriched_lead)
            
            except Exception as e:
                logger.warning(f"Error enriching lead: {e}")
                # Keep original if enrichment fails
                if isinstance(raw_lead, dict):
                    try:
                        enriched.append(Lead(**raw_lead))
                    except Exception:
                        pass
        
        state["enriched_leads"] = enriched
        logger.info(f"Enriched {len(enriched)} leads")
        
        return state
    
    def _score_leads(self, state: AgentState) -> AgentState:
        """Score leads against ICP."""
        logger.info("Scoring leads...")
        
        # Build ICP config
        icp_dict = state.get("icp_config", {})
        icp_config = ICPConfig(**icp_dict) if icp_dict else ICPConfig()
        
        scored = []
        for lead in state["enriched_leads"]:
            try:
                result = self.scoring_tool.score_lead(lead, icp_config)
                scored.append(lead)
            except Exception as e:
                logger.warning(f"Error scoring lead: {e}")
                # Assign default score
                lead.lead_score = 50.0
                lead.priority = PriorityBucket.MEDIUM
                scored.append(lead)
        
        # Sort by score
        scored.sort(key=lambda x: x.lead_score or 0, reverse=True)
        state["scored_leads"] = scored
        
        logger.info(f"Scored {len(scored)} leads")
        return state
    
    def _aggregate_results(self, state: AgentState) -> AgentState:
        """Aggregate and deduplicate results."""
        logger.info("Aggregating results...")
        
        # Deduplicate by company name
        seen_companies = set()
        unique_leads = []
        
        for lead in state["scored_leads"]:
            company_key = (lead.company_name or "").lower().strip()
            if company_key and company_key not in seen_companies:
                seen_companies.add(company_key)
                unique_leads.append(lead)
                
                # Save to storage
                self.storage.add_lead(lead)
        
        state["final_leads"] = unique_leads
        state["completed_at"] = datetime.now().isoformat()
        
        # Compute statistics
        state["statistics"] = {
            "total_leads": len(unique_leads),
            "high_priority": sum(1 for l in unique_leads if l.priority == PriorityBucket.HIGH),
            "medium_priority": sum(1 for l in unique_leads if l.priority == PriorityBucket.MEDIUM),
            "low_priority": sum(1 for l in unique_leads if l.priority == PriorityBucket.LOW),
            "avg_score": round(
                sum(l.lead_score or 0 for l in unique_leads) / max(len(unique_leads), 1), 2
            ),
            "sources_used": state.get("sources", []),
            "errors_count": len(state.get("errors", [])),
        }
        
        logger.info(f"Aggregated {len(unique_leads)} unique leads")
        return state
    
    def run(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        icp_config: Optional[Dict[str, Any]] = None,
        max_results: int = 10,
    ) -> Dict[str, Any]:
        """
        Run the lead generation workflow.
        
        Args:
            query: Search query (e.g., "AI startups in California")
            sources: Data sources to use ("linkedin", "web_search")
            icp_config: ICP configuration dict
            max_results: Maximum results per source
        
        Returns:
            Dictionary with leads, statistics, and errors
        """
        initial_state: AgentState = {
            "query": query,
            "sources": sources or ["web_search"],
            "icp_config": icp_config or {},
            "max_results": max_results,
            "raw_leads": [],
            "enriched_leads": [],
            "scored_leads": [],
            "final_leads": [],
            "statistics": {},
            "errors": [],
            "started_at": None,
            "completed_at": None,
        }
        
        try:
            # Run the graph
            result = self.graph.invoke(initial_state)
            
            return {
                "success": True,
                "leads": [lead.model_dump() for lead in result.get("final_leads", [])],
                "statistics": result.get("statistics", {}),
                "errors": result.get("errors", []),
                "started_at": result.get("started_at"),
                "completed_at": result.get("completed_at"),
            }
        
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            return {
                "success": False,
                "leads": [],
                "statistics": {},
                "errors": [str(e)],
                "started_at": initial_state.get("started_at"),
                "completed_at": datetime.now().isoformat(),
            }


# Convenience function
def create_workflow() -> LeadGenerationWorkflow:
    """Create a new workflow instance."""
    return LeadGenerationWorkflow()
