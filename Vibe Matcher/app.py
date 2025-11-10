"""
Vibe Matcher - Interactive Streamlit App
Fashion product recommender using AI-powered vibe matching
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

from vibe_matcher_backend import (
    initialize_embeddings,
    search_vibes,
    get_all_vibes,
    get_metrics_summary,
    FALLBACK_THRESHOLD,
    GOOD_HIT_THRESHOLD,
    TOP_K
)


# Page Configuration
st.set_page_config(
    page_title="Vibe Matcher - Fashion Recommender",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .product-card {
        border: 2px solid #f0f0f0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .vibe-tag {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .score-badge {
        font-size: 1.5rem;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        display: inline-block;
    }
    .score-high {
        background: #d4edda;
        color: #155724;
    }
    .score-medium {
        background: #fff3cd;
        color: #856404;
    }
    .score-low {
        background: #f8d7da;
        color: #721c24;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 10px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)


# Session State Initialization
if 'products_df' not in st.session_state:
    with st.spinner('🔄 Loading product catalog and embeddings...'):
        products_df, product_embeddings, status = initialize_embeddings()
        st.session_state.products_df = products_df
        st.session_state.product_embeddings = product_embeddings
        st.session_state.init_status = status

if 'search_history' not in st.session_state:
    st.session_state.search_history = []

if 'total_searches' not in st.session_state:
    st.session_state.total_searches = 0


# Header
st.markdown('<div class="main-header">👗 Vibe Matcher</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Fashion Recommender • Find Your Perfect Style Match</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/clothes.png", width=80)
    st.title("⚙️ Settings & Info")
    
    st.markdown("---")
    
    # Configuration
    st.subheader("🎛️ Configuration")
    show_scores = st.checkbox("Show Similarity Scores", value=True)
    show_descriptions = st.checkbox("Show Full Descriptions", value=True)
    num_results = st.slider("Number of Results", 1, 10, TOP_K)
    
    st.markdown("---")
    
    # Statistics
    st.subheader("📊 Statistics")
    st.metric("Total Products", len(st.session_state.products_df))
    st.metric("Total Searches", st.session_state.total_searches)
    st.metric("Catalog Vibes", len(get_all_vibes(st.session_state.products_df)))
    
    st.markdown("---")
    
    # Thresholds Info
    st.subheader("🎯 Thresholds")
    st.info(f"**Good Hit**: ≥ {GOOD_HIT_THRESHOLD:.2f}\n\n**Fallback**: < {FALLBACK_THRESHOLD:.2f}")
    
    st.markdown("---")
    
    # About
    with st.expander("ℹ️ About"):
        st.write("""
        **Vibe Matcher** uses OpenAI embeddings and cosine similarity to match 
        your vibe query with fashion products.
        
        **How it works:**
        1. Enter your style vibe
        2. AI embeds your query
        3. Matches with products
        4. Returns top recommendations
        
        Built with ❤️ using Streamlit & OpenAI
        """)
    
    # API Status
    st.markdown("---")
    st.caption(f"🔧 Status: {st.session_state.init_status}")


# Main Content Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Search", 
    "📚 Catalog Browser", 
    "📊 Analytics", 
    "📜 History"
])


# TAB 1: SEARCH
with tab1:
    st.header("🔍 Search by Vibe")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Enter your vibe (e.g., 'energetic urban chic', 'cozy minimal loungewear')",
            placeholder="Try: boho festival earthy, soft cozy comfort, bold streetwear...",
            key="search_query"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        search_button = st.button("🔎 Search", use_container_width=True)
    
    # Quick Suggestions
    st.caption("💡 Quick suggestions:")
    suggestion_cols = st.columns(4)
    suggestions = [
        "energetic urban chic",
        "soft cozy loungewear",
        "boho festival earthy",
        "minimal sustainable"
    ]
    
    for idx, (col, suggestion) in enumerate(zip(suggestion_cols, suggestions)):
        with col:
            if st.button(f"✨ {suggestion}", key=f"suggest_{idx}", use_container_width=True):
                query = suggestion
                search_button = True
    
    if search_button and query:
        st.session_state.total_searches += 1
        
        with st.spinner('🤔 Finding your perfect match...'):
            start_time = time.time()
            results, is_fallback, embed_status, warning_msg = search_vibes(
                query,
                st.session_state.products_df,
                st.session_state.product_embeddings,
                topk=num_results
            )
            latency = (time.time() - start_time) * 1000
        
        # Save to history
        st.session_state.search_history.insert(0, {
            'timestamp': datetime.now(),
            'query': query,
            'results_count': len(results),
            'top_score': results[0].similarity_score if results else 0,
            'latency_ms': latency,
            'is_fallback': is_fallback
        })
        
        # Keep only last 20 searches
        st.session_state.search_history = st.session_state.search_history[:20]
        
        st.markdown("---")
        
        # Display warnings
        if warning_msg:
            st.warning(warning_msg)
        
        if results:
            # Metrics Summary
            st.subheader(f"📊 Found {len(results)} Matches")
            
            metrics = get_metrics_summary(results)
            metric_cols = st.columns(4)
            
            with metric_cols[0]:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 2rem;">🎯</div>
                    <div style="font-size: 1.5rem; font-weight: bold;">{metrics['top_score']:.3f}</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">Top Score</div>
                </div>
                """, unsafe_allow_html=True)
            
            with metric_cols[1]:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 2rem;">✅</div>
                    <div style="font-size: 1.5rem; font-weight: bold;">{metrics['good_hits']}/{metrics['total']}</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">Good Hits</div>
                </div>
                """, unsafe_allow_html=True)
            
            with metric_cols[2]:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 2rem;">⏱️</div>
                    <div style="font-size: 1.5rem; font-weight: bold;">{latency:.1f}ms</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">Latency</div>
                </div>
                """, unsafe_allow_html=True)
            
            with metric_cols[3]:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 2rem;">📈</div>
                    <div style="font-size: 1.5rem; font-weight: bold;">{metrics['avg_score']:.3f}</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">Avg Score</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Display Results
            st.subheader("🎨 Your Perfect Matches")
            
            for result in results:
                # Determine score class
                if result.similarity_score >= GOOD_HIT_THRESHOLD:
                    score_class = "score-high"
                    emoji = "🔥"
                elif result.similarity_score >= FALLBACK_THRESHOLD:
                    score_class = "score-medium"
                    emoji = "✨"
                else:
                    score_class = "score-low"
                    emoji = "💫"
                
                with st.container():
                    col1, col2 = st.columns([1, 4])
                    
                    with col1:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 1rem;">
                            <div style="font-size: 3rem;">{emoji}</div>
                            <div style="font-size: 2rem; font-weight: bold; color: #667eea;">#{result.rank}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"### {result.name}")
                        
                        if show_scores:
                            st.markdown(f"""
                            <span class="score-badge {score_class}">
                                {result.similarity_score:.3f}
                            </span>
                            """, unsafe_allow_html=True)
                        
                        # Vibes
                        vibes_html = "".join([f'<span class="vibe-tag">{vibe}</span>' for vibe in result.vibes])
                        st.markdown(vibes_html, unsafe_allow_html=True)
                        
                        if show_descriptions:
                            st.write(result.description)
                    
                    st.markdown("---")
            
            # Visualization
            st.subheader("📊 Score Distribution")
            fig = go.Figure(data=[
                go.Bar(
                    x=[f"#{r.rank}" for r in results],
                    y=[r.similarity_score for r in results],
                    text=[f"{r.similarity_score:.3f}" for r in results],
                    textposition='auto',
                    marker=dict(
                        color=[r.similarity_score for r in results],
                        colorscale='Viridis',
                        showscale=True,
                        colorbar=dict(title="Score")
                    )
                )
            ])
            
            fig.add_hline(y=GOOD_HIT_THRESHOLD, line_dash="dash", line_color="green",
                         annotation_text="Good Hit Threshold")
            fig.add_hline(y=FALLBACK_THRESHOLD, line_dash="dash", line_color="red",
                         annotation_text="Fallback Threshold")
            
            fig.update_layout(
                title="Similarity Scores by Rank",
                xaxis_title="Rank",
                yaxis_title="Similarity Score",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("❌ No results found. Please check your query.")


# TAB 2: CATALOG BROWSER
with tab2:
    st.header("📚 Product Catalog Browser")
    
    # Filters
    col1, col2 = st.columns([1, 3])
    
    with col1:
        all_vibes = get_all_vibes(st.session_state.products_df)
        selected_vibes = st.multiselect(
            "Filter by Vibes",
            options=all_vibes,
            default=[]
        )
    
    with col2:
        search_name = st.text_input("Search by Name", placeholder="Enter product name...")
    
    # Filter products
    filtered_df = st.session_state.products_df.copy()
    
    if selected_vibes:
        filtered_df = filtered_df[
            filtered_df['vibes'].apply(
                lambda vibes: any(v in vibes for v in selected_vibes)
            )
        ]
    
    if search_name:
        filtered_df = filtered_df[
            filtered_df['name'].str.contains(search_name, case=False, na=False)
        ]
    
    st.write(f"**Showing {len(filtered_df)} of {len(st.session_state.products_df)} products**")
    
    # Display catalog
    for idx, row in filtered_df.iterrows():
        with st.expander(f"**{row['name']}** • ID: {row['id']}"):
            vibes_html = "".join([f'<span class="vibe-tag">{vibe}</span>' for vibe in row['vibes']])
            st.markdown(vibes_html, unsafe_allow_html=True)
            st.write(row['desc'])


# TAB 3: ANALYTICS
with tab3:
    st.header("📊 Analytics Dashboard")
    
    if st.session_state.search_history:
        # Convert to DataFrame
        history_df = pd.DataFrame(st.session_state.search_history)
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Searches", len(history_df))
        
        with col2:
            avg_score = history_df['top_score'].mean()
            st.metric("Avg Top Score", f"{avg_score:.3f}")
        
        with col3:
            avg_latency = history_df['latency_ms'].mean()
            st.metric("Avg Latency", f"{avg_latency:.1f}ms")
        
        with col4:
            fallback_rate = (history_df['is_fallback'].sum() / len(history_df)) * 100
            st.metric("Fallback Rate", f"{fallback_rate:.1f}%")
        
        st.markdown("---")
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Score Distribution
            fig = px.histogram(
                history_df,
                x='top_score',
                nbins=20,
                title="Top Score Distribution",
                labels={'top_score': 'Similarity Score'}
            )
            fig.add_vline(x=GOOD_HIT_THRESHOLD, line_dash="dash", line_color="green")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Latency Over Time
            fig = px.line(
                history_df,
                y='latency_ms',
                title="Latency Over Time",
                labels={'latency_ms': 'Latency (ms)', 'index': 'Search #'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent Searches Table
        st.subheader("📋 Recent Performance")
        display_df = history_df[['timestamp', 'query', 'top_score', 'latency_ms', 'results_count']].head(10)
        display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(display_df, use_container_width=True)
        
    else:
        st.info("📊 No search data yet. Try searching for some vibes!")


# TAB 4: HISTORY
with tab4:
    st.header("📜 Search History")
    
    if st.session_state.search_history:
        col1, col2 = st.columns([3, 1])
        
        with col2:
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.search_history = []
                st.rerun()
        
        for idx, search in enumerate(st.session_state.search_history):
            with st.expander(
                f"**{search['query']}** • {search['timestamp'].strftime('%H:%M:%S')} • Score: {search['top_score']:.3f}",
                expanded=(idx == 0)
            ):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Top Score", f"{search['top_score']:.3f}")
                
                with col2:
                    st.metric("Results", search['results_count'])
                
                with col3:
                    st.metric("Latency", f"{search['latency_ms']:.1f}ms")
                
                with col4:
                    fallback_emoji = "⚠️" if search['is_fallback'] else "✅"
                    st.metric("Status", f"{fallback_emoji}")
                
                if st.button(f"🔄 Repeat Search", key=f"repeat_{idx}", use_container_width=True):
                    st.session_state.search_query = search['query']
                    st.rerun()
    else:
        st.info("📜 No search history yet. Start searching to build your history!")


# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("🚀 **Vibe Matcher v1.0**")

with col2:
    st.caption("🤖 Powered by OpenAI Embeddings")

with col3:
    st.caption("💜 Built with Streamlit")
