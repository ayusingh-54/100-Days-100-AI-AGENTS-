"""
Main LangGraph workflow definition.

The workflow is structured as follows:
1. input_node: Validate and prepare input parameters
2. source_selection_node: Determine which data sources to use
3. scraping_node: Execute scraping tasks (LinkedIn, Google Maps, CSV, etc.)
4. aggregation_node: Combine results from multiple sources
5. enrichment_node: Enrich leads with company data
6. scoring_node: Score leads against ICP
7. filtering_node: Filter and prioritize results
8. output_node: Format and return results
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from ..models import Lead, ICPConfig, ScoringWeights
from ..tools import (
    LinkedInJobsTool,
    GoogleMapsBusinessSearchTool,
    CompanyEnrichmentTool,
    LeadScoringTool,
)
from ..config import Config
from ..utils import deduplicate_leads, setup_logging

logger = logging.getLogger(__name__)


class WorkflowState(BaseModel):
    """State passed through the workflow graph."""
    
    # Input parameters
    search_keywords: Optional[str] = None
    search_location: Optional[str] = None
    search_source: List[str] = Field(default_factory=list)  # linkedin, google_maps, csv
    csv_data: Optional[List[Dict[str, Any]]] = None
    max_leads: int = 50
    
    # ICP and scoring config
    icp_config: Optional[ICPConfig] = None
    scoring_weights: Optional[ScoringWeights] = None
    
    # Process state
    current_step: str = "input"
    errors: List[str] = Field(default_factory=list)
    
    # Results
    raw_leads: List[Lead] = Field(default_factory=list)
    enriched_leads: List[Lead] = Field(default_factory=list)
    scored_leads: List[Lead] = Field(default_factory=list)
    
    # Metadata
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    run_duration: Optional[float] = None
    
    class Config:
        arbitrary_types_allowed = True


def input_node(state: WorkflowState) -> WorkflowState:
    """Validate and prepare input parameters."""
    logger.info("=== INPUT NODE ===")
    
    state.current_step = "input"
    state.started_at = datetime.now()
    
    # Validate required fields
    if not state.search_keywords and not state.csv_data:
        state.errors.append("Either search_keywords or csv_data must be provided")
        return state
    
    if not state.search_source or len(state.search_source) == 0:
        state.errors.append("At least one search_source must be specified")
        return state
    
    # Set defaults
    if not state.icp_config:
        state.icp_config = ICPConfig()
    
    if not state.scoring_weights:
        state.scoring_weights = ScoringWeights()
    
    if not state.max_leads:
        state.max_leads = Config.MAX_LEADS_PER_RUN
    
    logger.info(f"Input validated. Keywords: {state.search_keywords}, Location: {state.search_location}")
    logger.info(f"Sources: {state.search_source}, Max leads: {state.max_leads}")
    
    return state


def source_selection_node(state: WorkflowState) -> WorkflowState:
    """Determine which data sources to use."""
    logger.info("=== SOURCE SELECTION NODE ===")
    
    state.current_step = "source_selection"
    
    if state.errors:
        logger.warning("Skipping source selection due to previous errors")
        return state
    
    sources_available = []
    
    # Check LinkedIn
    if "linkedin" in state.search_source:
        if not Config.APIFY_TOKEN:
            logger.warning("APIFY_TOKEN not configured, skipping LinkedIn")
        else:
            sources_available.append("linkedin")
    
    # Check Google Maps
    if "google_maps" in state.search_source:
        if not Config.APIFY_TOKEN and not Config.GOOGLE_MAPS_API_KEY:
            logger.warning("No API credentials for Google Maps, skipping")
        else:
            sources_available.append("google_maps")
    
    # Check CSV
    if "csv" in state.search_source:
        if state.csv_data:
            sources_available.append("csv")
        else:
            logger.warning("CSV source selected but no csv_data provided")
    
    logger.info(f"Selected sources: {sources_available}")
    
    return state


def scraping_node(state: WorkflowState) -> WorkflowState:
    """Execute scraping tasks from selected sources."""
    logger.info("=== SCRAPING NODE ===")
    
    state.current_step = "scraping"
    
    if state.errors:
        logger.warning("Skipping scraping due to previous errors")
        return state
    
    leads = []
    
    try:
        # LinkedIn Jobs Scraping
        if "linkedin" in state.search_source:
            logger.info("Scraping LinkedIn jobs...")
            linkedin_tool = LinkedInJobsTool(token=Config.APIFY_TOKEN)
            from ..tools.linkedin_jobs import LinkedInJobsInput
            
            search_input = LinkedInJobsInput(
                keywords=state.search_keywords or "Software Engineer",
                location=state.search_location or "United States",
                max_results=state.max_leads,
            )
            
            job_postings = linkedin_tool.search_jobs(search_input)
            linkedin_leads = linkedin_tool.create_leads_from_jobs(job_postings)
            leads.extend(linkedin_leads)
            logger.info(f"Found {len(linkedin_leads)} leads from LinkedIn")
        
        # Google Maps Scraping
        if "google_maps" in state.search_source:
            logger.info("Searching Google Maps...")
            google_maps_tool = GoogleMapsBusinessSearchTool(
                token=Config.APIFY_TOKEN,
                api_key=Config.GOOGLE_MAPS_API_KEY
            )
            from ..tools.google_maps import GoogleMapsSearchInput
            
            search_input = GoogleMapsSearchInput(
                query=state.search_keywords or "Software companies",
                location=state.search_location or "United States",
                max_results=state.max_leads,
            )
            
            maps_leads = google_maps_tool.search_businesses(search_input)
            leads.extend(maps_leads)
            logger.info(f"Found {len(maps_leads)} leads from Google Maps")
        
        # CSV Data
        if "csv" in state.search_source and state.csv_data:
            logger.info("Processing CSV data...")
            for row in state.csv_data[:state.max_leads]:
                try:
                    lead = Lead(
                        company_name=row.get("company_name", "Unknown"),
                        name=row.get("name"),
                        title=row.get("title"),
                        email=row.get("email"),
                        company_website=row.get("company_website"),
                        location=row.get("location"),
                        industry=row.get("industry"),
                        enrichment_sources=["csv_import"],
                    )
                    leads.append(lead)
                except Exception as e:
                    logger.debug(f"Error parsing CSV row: {e}")
        
        # Deduplicate
        leads_dict = [lead.to_dict() for lead in leads]
        deduplicated_dict = deduplicate_leads(leads_dict)
        leads = [Lead.from_dict(d) for d in deduplicated_dict]
        
        state.raw_leads = leads[:state.max_leads]
        logger.info(f"Total leads after deduplication: {len(state.raw_leads)}")
    
    except Exception as e:
        error_msg = f"Error during scraping: {str(e)}"
        logger.error(error_msg)
        state.errors.append(error_msg)
    
    return state


def enrichment_node(state: WorkflowState) -> WorkflowState:
    """Enrich leads with company information."""
    logger.info("=== ENRICHMENT NODE ===")
    
    state.current_step = "enrichment"
    
    if not state.raw_leads:
        logger.warning("No leads to enrich")
        return state
    
    try:
        enrichment_tool = CompanyEnrichmentTool()
        enriched = []
        
        for i, lead in enumerate(state.raw_leads):
            try:
                enriched_lead = enrichment_tool.enrich_lead(lead)
                enriched.append(enriched_lead)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Enriched {i + 1}/{len(state.raw_leads)} leads")
            
            except Exception as e:
                logger.debug(f"Error enriching lead {lead.company_name}: {e}")
                enriched.append(lead)
        
        enrichment_tool.close()
        state.enriched_leads = enriched
        logger.info(f"Enrichment complete. Enriched {len(state.enriched_leads)} leads")
    
    except Exception as e:
        error_msg = f"Error during enrichment: {str(e)}"
        logger.error(error_msg)
        state.errors.append(error_msg)
        state.enriched_leads = state.raw_leads
    
    return state


def scoring_node(state: WorkflowState) -> WorkflowState:
    """Score leads against ICP."""
    logger.info("=== SCORING NODE ===")
    
    state.current_step = "scoring"
    
    if not state.enriched_leads:
        logger.warning("No leads to score")
        return state
    
    try:
        scoring_tool = LeadScoringTool()
        scored = []
        
        for i, lead in enumerate(state.enriched_leads):
            try:
                from ..tools.lead_scoring import LeadScoringInput
                
                scoring_input = LeadScoringInput(
                    lead=lead,
                    icp_config=state.icp_config or ICPConfig(),
                    scoring_weights=state.scoring_weights or ScoringWeights(),
                )
                
                score_result = scoring_tool.score_lead(scoring_input)
                scored.append(lead)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Scored {i + 1}/{len(state.enriched_leads)} leads")
            
            except Exception as e:
                logger.debug(f"Error scoring lead {lead.company_name}: {e}")
                scored.append(lead)
        
        state.scored_leads = scored
        logger.info(f"Scoring complete. Scored {len(state.scored_leads)} leads")
    
    except Exception as e:
        error_msg = f"Error during scoring: {str(e)}"
        logger.error(error_msg)
        state.errors.append(error_msg)
        state.scored_leads = state.enriched_leads
    
    return state


def filtering_node(state: WorkflowState) -> WorkflowState:
    """Filter and sort results."""
    logger.info("=== FILTERING NODE ===")
    
    state.current_step = "filtering"
    
    # Sort by score descending
    state.scored_leads = sorted(
        state.scored_leads,
        key=lambda x: x.lead_score,
        reverse=True
    )
    
    logger.info(f"Sorted {len(state.scored_leads)} leads by score")
    
    return state


def output_node(state: WorkflowState) -> WorkflowState:
    """Format and return results."""
    logger.info("=== OUTPUT NODE ===")
    
    state.current_step = "output"
    state.completed_at = datetime.now()
    state.run_duration = (state.completed_at - state.started_at).total_seconds()
    
    logger.info(f"Workflow complete. Duration: {state.run_duration:.2f}s")
    logger.info(f"Total leads generated: {len(state.scored_leads)}")
    
    if state.errors:
        logger.warning(f"Completed with {len(state.errors)} errors:")
        for error in state.errors:
            logger.warning(f"  - {error}")
    
    return state


def build_lead_gen_graph() -> StateGraph:
    """Build the LangGraph workflow graph."""
    
    # Create graph
    graph = StateGraph(WorkflowState)
    
    # Add nodes
    graph.add_node("input", input_node)
    graph.add_node("source_selection", source_selection_node)
    graph.add_node("scraping", scraping_node)
    graph.add_node("enrichment", enrichment_node)
    graph.add_node("scoring", scoring_node)
    graph.add_node("filtering", filtering_node)
    graph.add_node("output", output_node)
    
    # Add edges
    graph.set_entry_point("input")
    graph.add_edge("input", "source_selection")
    graph.add_edge("source_selection", "scraping")
    graph.add_edge("scraping", "enrichment")
    graph.add_edge("enrichment", "scoring")
    graph.add_edge("scoring", "filtering")
    graph.add_edge("filtering", "output")
    graph.add_edge("output", END)
    
    return graph.compile()


def run_lead_gen_workflow(
    search_keywords: Optional[str] = None,
    search_location: Optional[str] = None,
    search_source: Optional[List[str]] = None,
    csv_data: Optional[List[Dict[str, Any]]] = None,
    max_leads: int = 50,
    icp_config: Optional[ICPConfig] = None,
    scoring_weights: Optional[ScoringWeights] = None,
) -> WorkflowState:
    """
    Run the lead generation workflow.
    
    Args:
        search_keywords: Search keywords/job titles
        search_location: Geographic location
        search_source: List of sources to use (linkedin, google_maps, csv)
        csv_data: CSV data if using csv source
        max_leads: Maximum number of leads to generate
        icp_config: ICP configuration
        scoring_weights: Scoring weights configuration
    
    Returns:
        WorkflowState with results
    """
    
    setup_logging("INFO" if not Config.DEBUG else "DEBUG")
    
    # Create initial state
    initial_state = WorkflowState(
        search_keywords=search_keywords,
        search_location=search_location,
        search_source=search_source or ["linkedin"],
        csv_data=csv_data,
        max_leads=max_leads,
        icp_config=icp_config or ICPConfig(),
        scoring_weights=scoring_weights or ScoringWeights(),
    )
    
    # Build and run graph
    graph = build_lead_gen_graph()
    final_state = graph.invoke(initial_state)
    
    return final_state
