"""
Lead Generation Agent - Streamlit Application.
Advanced UI for lead generation, enrichment, and scoring.

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import plotly.express as px
import plotly.graph_objects as go
import time

from lead_gen_agent.graph import create_workflow
from lead_gen_agent.storage import get_storage
from lead_gen_agent.models import Lead, ICPConfig, ScoringWeights, PriorityBucket
from lead_gen_agent.config import Config

# Page configuration
st.set_page_config(
    page_title="LeadGen AI Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1E88E5, #7C4DFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .sub-header {
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #e7f3ff;
        border: 1px solid #b8daff;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .lead-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1E88E5;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .priority-high { 
        color: white; 
        background-color: #E53935; 
        padding: 2px 8px; 
        border-radius: 12px;
        font-size: 0.8rem;
    }
    .priority-medium { 
        color: white; 
        background-color: #FB8C00; 
        padding: 2px 8px; 
        border-radius: 12px;
        font-size: 0.8rem;
    }
    .priority-low { 
        color: white; 
        background-color: #43A047; 
        padding: 2px 8px; 
        border-radius: 12px;
        font-size: 0.8rem;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #1E88E5, #7C4DFF);
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }
    .search-tip {
        font-size: 0.85rem;
        color: #666;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "leads" not in st.session_state:
        st.session_state.leads = []
    if "search_history" not in st.session_state:
        st.session_state.search_history = []
    if "storage" not in st.session_state:
        st.session_state.storage = get_storage()
    if "last_search_results" not in st.session_state:
        st.session_state.last_search_results = None
    if "workflow" not in st.session_state:
        st.session_state.workflow = None


def get_workflow():
    """Get or create workflow instance."""
    if st.session_state.workflow is None:
        st.session_state.workflow = create_workflow()
    return st.session_state.workflow


def render_sidebar():
    """Render the sidebar with configuration options."""
    with st.sidebar:
        # Logo/Header
        st.markdown("## 🎯 LeadGen AI")
        st.caption("Intelligent B2B Lead Generation")
        st.markdown("---")
        
        # API Status with better visuals
        st.markdown("### 🔑 API Status")
        
        api_statuses = [
            ("OpenAI", Config.OPENAI_API_KEY, "Required for AI scoring"),
            ("Serper", Config.SERPER_API_KEY, "For web search"),
            ("Apify", Config.APIFY_TOKEN, "For LinkedIn scraping"),
        ]
        
        for name, key, desc in api_statuses:
            if key:
                st.markdown(f"✅ **{name}** - Active")
            else:
                st.markdown(f"⚠️ **{name}** - Not configured")
                st.caption(f"  _{desc}_")
        
        st.markdown("---")
        
        # Quick Stats
        st.markdown("### 📊 Session Stats")
        storage = st.session_state.storage
        stats = storage.get_statistics()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Leads", stats["total_leads"])
        with col2:
            st.metric("Avg Score", f"{stats['average_score']:.0f}")
        
        # Priority breakdown
        if stats["total_leads"] > 0:
            st.markdown("**By Priority:**")
            cols = st.columns(3)
            cols[0].markdown(f"🔴 {stats['by_priority']['HIGH']}")
            cols[1].markdown(f"🟡 {stats['by_priority']['MEDIUM']}")
            cols[2].markdown(f"🟢 {stats['by_priority']['LOW']}")
        
        st.markdown("---")
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("🗑️ Clear All Data"):
            storage.clear_all()
            st.session_state.leads = []
            st.session_state.last_search_results = None
            st.success("Data cleared!")
            st.rerun()
        
        st.markdown("---")
        
        # Help Section
        with st.expander("ℹ️ How to Use"):
            st.markdown("""
            **1. Search Tab**
            - Enter keywords like "AI startups" or "SaaS companies"
            - Select data sources
            - Optionally filter by industry/location
            
            **2. Dashboard Tab**
            - View all generated leads
            - Filter by priority and score
            - Analyze lead distribution
            
            **3. ICP Config Tab**
            - Define your ideal customer
            - Set scoring preferences
            
            **4. Export Tab**
            - Download leads as CSV/JSON
            """)
        
        # Version info
        st.markdown("---")
        st.caption("v1.0.0 | Powered by LangChain & LangGraph")


def render_search_tab():
    """Render the search tab with improved UX."""
    st.markdown("## 🔍 Lead Search")
    st.markdown("Find and score B2B leads matching your criteria")
    
    # Search form in a clean card layout
    with st.container():
        # Main search input
        search_query = st.text_input(
            "🔎 Search Query",
            placeholder="e.g., AI startups, SaaS companies in California, FinTech hiring engineers",
            help="Enter keywords to search for businesses and leads",
            key="search_input"
        )
        
        # Search tips
        st.markdown("""
        <p class="search-tip">
        💡 <b>Tips:</b> Try "AI startups", "Healthcare SaaS", "B2B software companies", or "FinTech in New York"
        </p>
        """, unsafe_allow_html=True)
        
        # Options in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sources = st.multiselect(
                "📡 Data Sources",
                options=["web_search", "linkedin"],
                default=["web_search"],
                help="Select where to search for leads"
            )
        
        with col2:
            max_results = st.select_slider(
                "📊 Max Results",
                options=[5, 10, 15, 20, 25, 30, 50],
                value=10,
                help="Number of leads to generate"
            )
        
        with col3:
            search_mode = st.selectbox(
                "🎯 Search Mode",
                options=["Standard", "Deep Search"],
                help="Deep Search takes longer but finds more detailed info"
            )
    
    # Advanced options in expander
    with st.expander("⚙️ Advanced Filters (Optional)"):
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            target_industries = st.text_input(
                "🏭 Target Industries",
                placeholder="Technology, Healthcare, Finance",
                help="Comma-separated list of preferred industries"
            )
        
        with col_b:
            target_locations = st.text_input(
                "📍 Target Locations", 
                placeholder="California, New York, Texas",
                help="Comma-separated list of locations"
            )
        
        with col_c:
            preferred_tech = st.text_input(
                "💻 Preferred Tech Stack",
                placeholder="Python, React, AWS",
                help="Comma-separated list of technologies"
            )
    
    st.markdown("---")
    
    # Search button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        search_clicked = st.button(
            "🚀 Generate Leads", 
            type="primary", 
            disabled=not search_query
        )
    
    # Handle search
    if search_clicked:
        if not search_query:
            st.warning("⚠️ Please enter a search query to continue.")
            return
        
        run_lead_search(
            query=search_query,
            sources=sources,
            max_results=max_results,
            target_industries=target_industries,
            target_locations=target_locations,
            preferred_tech=preferred_tech,
            deep_search=(search_mode == "Deep Search")
        )
    
    # Show last results if available
    if st.session_state.last_search_results:
        render_search_results(st.session_state.last_search_results)


def run_lead_search(query, sources, max_results, target_industries, target_locations, preferred_tech, deep_search=False):
    """Execute lead search with progress tracking."""
    
    # Build ICP config
    icp_config = {}
    if target_industries:
        icp_config["target_industries"] = [i.strip() for i in target_industries.split(",") if i.strip()]
    if target_locations:
        icp_config["target_geographies"] = [l.strip() for l in target_locations.split(",") if l.strip()]
    if preferred_tech:
        icp_config["preferred_tech_stack"] = [t.strip() for t in preferred_tech.split(",") if t.strip()]
    
    # Progress container
    progress_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Initialize
            status_text.markdown("🔄 **Initializing workflow...**")
            progress_bar.progress(10)
            time.sleep(0.3)
            
            workflow = get_workflow()
            
            # Step 2: Searching
            status_text.markdown(f"🌐 **Searching for '{query}'...**")
            progress_bar.progress(30)
            
            # Run the workflow
            result = workflow.run(
                query=query,
                sources=sources,
                icp_config=icp_config,
                max_results=max_results,
            )
            
            # Step 3: Processing
            status_text.markdown("📊 **Processing and scoring leads...**")
            progress_bar.progress(80)
            time.sleep(0.3)
            
            # Step 4: Complete
            progress_bar.progress(100)
            
            if result["success"]:
                leads = result["leads"]
                stats = result["statistics"]
                
                # Store results
                st.session_state.last_search_results = {
                    "leads": leads,
                    "statistics": stats,
                    "query": query,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add to search history
                st.session_state.search_history.append({
                    "query": query,
                    "timestamp": datetime.now().isoformat(),
                    "results_count": len(leads),
                })
                
                # Clear progress
                status_text.empty()
                progress_bar.empty()
                
                # Success message
                st.success(f"✅ **Found {len(leads)} leads!** | High: {stats.get('high_priority', 0)} | Medium: {stats.get('medium_priority', 0)} | Low: {stats.get('low_priority', 0)} | Avg Score: {stats.get('avg_score', 0):.1f}")
                
                st.rerun()
            else:
                status_text.empty()
                progress_bar.empty()
                st.error(f"❌ Search failed: {', '.join(result.get('errors', ['Unknown error']))}")
        
        except Exception as e:
            status_text.empty()
            progress_bar.empty()
            st.error(f"❌ Error: {str(e)}")


def render_search_results(results: Dict):
    """Render search results in a clean format."""
    leads = results["leads"]
    stats = results["statistics"]
    query = results.get("query", "")
    
    if not leads:
        st.info("No leads found. Try a different search query.")
        return
    
    st.markdown(f"### 📋 Results for '{query}' ({len(leads)} leads)")
    
    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", len(leads))
    col2.metric("🔴 High", stats.get("high_priority", 0))
    col3.metric("🟡 Medium", stats.get("medium_priority", 0))
    col4.metric("Avg Score", f"{stats.get('avg_score', 0):.1f}")
    
    st.markdown("---")
    
    # View toggle
    view_mode = st.radio(
        "View Mode",
        ["📊 Table View", "🃏 Card View"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if view_mode == "📊 Table View":
        render_leads_table(leads)
    else:
        render_leads_cards(leads)


def render_leads_table(leads: List[Dict]):
    """Render leads in a table format."""
    df = pd.DataFrame(leads)
    
    if df.empty:
        return
    
    # Prepare display columns
    display_cols = ["company_name", "industry", "location", "lead_score", "priority"]
    available_cols = [c for c in display_cols if c in df.columns]
    
    if not available_cols:
        st.warning("No displayable columns found.")
        return
    
    # Sort by score
    if "lead_score" in df.columns:
        df = df.sort_values("lead_score", ascending=False)
    
    # Clean up priority display
    if "priority" in df.columns:
        df["priority"] = df["priority"].apply(lambda x: x.replace("PriorityBucket.", "") if isinstance(x, str) else x)
    
    # Display with custom styling
    st.dataframe(
        df[available_cols],
        column_config={
            "company_name": st.column_config.TextColumn("🏢 Company", width="large"),
            "industry": st.column_config.TextColumn("🏭 Industry", width="medium"),
            "location": st.column_config.TextColumn("📍 Location", width="medium"),
            "lead_score": st.column_config.ProgressColumn(
                "📈 Score",
                min_value=0,
                max_value=100,
                format="%.0f",
            ),
            "priority": st.column_config.TextColumn("🎯 Priority", width="small"),
        },
        hide_index=True,
    )


def render_leads_cards(leads: List[Dict]):
    """Render leads in a card format."""
    cols = st.columns(2)
    
    for i, lead in enumerate(leads[:20]):  # Show top 20
        with cols[i % 2]:
            priority = lead.get("priority", "MEDIUM")
            if isinstance(priority, str):
                priority = priority.replace("PriorityBucket.", "")
            
            priority_class = {
                "HIGH": "priority-high",
                "MEDIUM": "priority-medium", 
                "LOW": "priority-low"
            }.get(priority, "priority-medium")
            
            score = lead.get("lead_score", 0)
            company = lead.get("company_name", "Unknown")
            industry = lead.get("industry", "N/A")
            location = lead.get("location", "N/A")
            website = lead.get("company_website", "")
            
            st.markdown(f"""
            <div class="lead-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0;">{company}</h4>
                    <span class="{priority_class}">{priority}</span>
                </div>
                <p style="color: #666; margin: 5px 0;">🏭 {industry} | 📍 {location}</p>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="flex: 1; background: #e0e0e0; border-radius: 10px; height: 8px;">
                        <div style="width: {score}%; background: linear-gradient(90deg, #1E88E5, #7C4DFF); height: 100%; border-radius: 10px;"></div>
                    </div>
                    <span style="font-weight: bold; color: #1E88E5;">{score:.0f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_dashboard_tab():
    """Render the dashboard tab."""
    st.markdown("## 📊 Lead Dashboard")
    
    storage = st.session_state.storage
    all_leads = storage.get_all_leads()
    
    if not all_leads:
        st.markdown("""
        <div class="info-box">
            <h4>👋 No leads yet!</h4>
            <p>Go to the <b>Search</b> tab to generate your first leads.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Metrics row with nice styling
    st.markdown("### 📈 Overview")
    
    high_count = len(storage.get_leads_by_priority(PriorityBucket.HIGH))
    medium_count = len(storage.get_leads_by_priority(PriorityBucket.MEDIUM))
    low_count = len(storage.get_leads_by_priority(PriorityBucket.LOW))
    
    scores = [l.lead_score for l in all_leads if l.lead_score]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Leads", len(all_leads))
    with col2:
        st.metric("🔴 High Priority", high_count, help="Score >= 70")
    with col3:
        st.metric("🟡 Medium Priority", medium_count, help="Score 40-69")
    with col4:
        st.metric("📈 Avg Score", f"{avg_score:.1f}")
    
    st.markdown("---")
    
    # Charts row
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("#### Priority Distribution")
        if high_count + medium_count + low_count > 0:
            fig_priority = px.pie(
                values=[high_count, medium_count, low_count],
                names=["High", "Medium", "Low"],
                color_discrete_sequence=["#E53935", "#FB8C00", "#43A047"],
                hole=0.4,
            )
            fig_priority.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2)
            )
            st.plotly_chart(fig_priority)
        else:
            st.info("No priority data available")
    
    with col_right:
        st.markdown("#### Score Distribution")
        if scores:
            fig_scores = px.histogram(
                x=scores,
                nbins=10,
                labels={"x": "Lead Score", "y": "Count"},
                color_discrete_sequence=["#1E88E5"],
            )
            fig_scores.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=False,
            )
            st.plotly_chart(fig_scores)
        else:
            st.info("No score data available")
    
    st.markdown("---")
    
    # Lead table with filters
    st.markdown("### 📋 All Leads")
    
    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        filter_priority = st.selectbox(
            "🎯 Priority",
            options=["All", "HIGH", "MEDIUM", "LOW"],
            key="dash_filter_priority"
        )
    
    with col_f2:
        filter_min_score = st.slider(
            "📈 Min Score", 
            0, 100, 0,
            key="dash_filter_score"
        )
    
    with col_f3:
        filter_search = st.text_input(
            "🔍 Search",
            placeholder="Company or industry",
            key="dash_filter_search"
        )
    
    # Apply filters
    filtered_leads = all_leads
    
    if filter_priority != "All":
        filtered_leads = [l for l in filtered_leads if l.priority and l.priority.value == filter_priority]
    
    if filter_min_score > 0:
        filtered_leads = [l for l in filtered_leads if (l.lead_score or 0) >= filter_min_score]
    
    if filter_search:
        search_lower = filter_search.lower()
        filtered_leads = [
            l for l in filtered_leads
            if search_lower in (l.company_name or "").lower()
            or search_lower in (l.industry or "").lower()
        ]
    
    st.caption(f"Showing {len(filtered_leads)} of {len(all_leads)} leads")
    
    # Display filtered leads
    if filtered_leads:
        df = pd.DataFrame([lead.model_dump() for lead in filtered_leads])
        display_cols = ["company_name", "industry", "location", "lead_score", "priority", "reasons_for_score"]
        available_cols = [c for c in display_cols if c in df.columns]
        
        if available_cols:
            if "lead_score" in df.columns:
                df = df.sort_values("lead_score", ascending=False)
            
            # Clean priority display
            if "priority" in df.columns:
                df["priority"] = df["priority"].apply(lambda x: x.value if hasattr(x, 'value') else str(x).replace("PriorityBucket.", ""))
            
            st.dataframe(
                df[available_cols],
                column_config={
                    "company_name": st.column_config.TextColumn("🏢 Company", width="large"),
                    "industry": st.column_config.TextColumn("🏭 Industry"),
                    "location": st.column_config.TextColumn("📍 Location"),
                    "lead_score": st.column_config.ProgressColumn(
                        "📈 Score",
                        min_value=0,
                        max_value=100,
                        format="%.0f",
                    ),
                    "priority": st.column_config.TextColumn("🎯 Priority"),
                    "reasons_for_score": st.column_config.TextColumn("💡 Scoring Reasons", width="large"),
                },
                hide_index=True,
            )
    else:
        st.info("No leads match the current filters.")


def render_icp_tab():
    """Render the ICP configuration tab."""
    st.markdown("## 🎯 Ideal Customer Profile (ICP)")
    st.markdown("Configure your ideal customer to improve lead scoring accuracy.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Target Criteria")
        
        target_industries = st.text_area(
            "🏭 Target Industries",
            value="Technology\nSoftware\nFinancial Services\nHealthcare",
            height=120,
            help="One industry per line"
        )
        
        target_sizes = st.multiselect(
            "👥 Company Size",
            options=["1-10 (Startup)", "11-50 (Small)", "51-200 (Mid)", "201-500 (Growth)", "501-1000 (Large)", "1000+ (Enterprise)"],
            default=["51-200 (Mid)", "201-500 (Growth)"],
        )
        
        target_locations = st.text_area(
            "📍 Target Locations",
            value="United States\nCanada\nUnited Kingdom",
            height=100,
            help="One location per line"
        )
    
    with col2:
        st.markdown("### 💻 Tech & Signals")
        
        preferred_tech = st.text_area(
            "🛠️ Preferred Tech Stack",
            value="Python\nJavaScript\nReact\nAWS\nKubernetes",
            height=120,
            help="Technologies that indicate a good fit"
        )
        
        st.markdown("### ⚖️ Scoring Weights")
        st.caption("Adjust how much each factor affects the lead score")
        
        weight_industry = st.slider("Industry Match", 0, 100, 30, format="%d%%")
        weight_size = st.slider("Company Size", 0, 100, 20, format="%d%%")
        weight_location = st.slider("Location", 0, 100, 20, format="%d%%")
        weight_tech = st.slider("Tech Stack", 0, 100, 30, format="%d%%")
    
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    
    with col_btn2:
        if st.button("💾 Save ICP Configuration", type="primary"):
            # Build ICP config
            icp_config = {
                "target_industries": [i.strip() for i in target_industries.split("\n") if i.strip()],
                "target_company_sizes": target_sizes,
                "target_geographies": [l.strip() for l in target_locations.split("\n") if l.strip()],
                "preferred_tech_stack": [t.strip() for t in preferred_tech.split("\n") if t.strip()],
                "weights": {
                    "industry": weight_industry / 100,
                    "size": weight_size / 100,
                    "location": weight_location / 100,
                    "tech": weight_tech / 100,
                }
            }
            
            st.session_state.icp_config = icp_config
            st.success("✅ ICP Configuration saved successfully!")
            
            # Show preview
            with st.expander("📄 Configuration Preview"):
                st.json(icp_config)


def render_export_tab():
    """Render the export tab."""
    st.markdown("## 📤 Export Data")
    
    storage = st.session_state.storage
    all_leads = storage.get_all_leads()
    
    if not all_leads:
        st.markdown("""
        <div class="info-box">
            <h4>📭 No leads to export</h4>
            <p>Generate some leads in the <b>Search</b> tab first.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Summary
    st.markdown(f"### 📊 Export Summary")
    st.info(f"**{len(all_leads)} leads** ready for export")
    
    # Export format selection
    st.markdown("### 📁 Choose Format")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📄 CSV Export")
        st.caption("Best for spreadsheets (Excel, Google Sheets)")
        
        df = pd.DataFrame([lead.model_dump() for lead in all_leads])
        
        # Clean up the dataframe for export
        if "priority" in df.columns:
            df["priority"] = df["priority"].apply(lambda x: x.value if hasattr(x, 'value') else str(x).replace("PriorityBucket.", ""))
        
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name=f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
    
    with col2:
        st.markdown("#### 📋 JSON Export")
        st.caption("Best for developers and integrations")
        
        # Clean up for JSON export
        export_data = []
        for lead in all_leads:
            lead_dict = lead.model_dump()
            if "priority" in lead_dict:
                lead_dict["priority"] = lead_dict["priority"].value if hasattr(lead_dict["priority"], 'value') else str(lead_dict["priority"]).replace("PriorityBucket.", "")
            export_data.append(lead_dict)
        
        json_data = json.dumps(export_data, indent=2, default=str)
        
        st.download_button(
            label="⬇️ Download JSON",
            data=json_data,
            file_name=f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )
    
    st.markdown("---")
    
    # Data Preview
    st.markdown("### 👀 Data Preview")
    
    preview_df = pd.DataFrame([lead.model_dump() for lead in all_leads[:10]])
    
    # Select columns for preview
    preview_cols = ["company_name", "industry", "location", "lead_score", "priority", "company_website"]
    available_preview_cols = [c for c in preview_cols if c in preview_df.columns]
    
    if available_preview_cols:
        if "priority" in preview_df.columns:
            preview_df["priority"] = preview_df["priority"].apply(lambda x: x.value if hasattr(x, 'value') else str(x).replace("PriorityBucket.", ""))
        
        st.dataframe(
            preview_df[available_preview_cols],
            hide_index=True,
        )
    
    if len(all_leads) > 10:
        st.caption(f"Showing 10 of {len(all_leads)} leads")


def main():
    """Main application entry point."""
    init_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🎯 Lead Generation Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-powered B2B lead discovery, enrichment, and scoring</p>', unsafe_allow_html=True)
    
    # Sidebar
    render_sidebar()
    
    # Main content with tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Search",
        "📊 Dashboard", 
        "🎯 ICP Config",
        "📤 Export"
    ])
    
    with tab1:
        render_search_tab()
    
    with tab2:
        render_dashboard_tab()
    
    with tab3:
        render_icp_tab()
    
    with tab4:
        render_export_tab()


if __name__ == "__main__":
    main()
