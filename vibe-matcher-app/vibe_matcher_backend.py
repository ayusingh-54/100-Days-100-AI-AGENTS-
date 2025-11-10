"""
Vibe Matcher Backend
Core logic for fashion product recommendation using embeddings and cosine similarity.
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# Configuration Constants
FALLBACK_THRESHOLD = 0.35
GOOD_HIT_THRESHOLD = 0.7
EMBEDDING_MODEL = "text-embedding-ada-002"
EMBEDDING_DIM = 1536
TOP_K = 3
CACHE_PATH = Path("data/embeddings_cache.json")


@dataclass
class RankedResult:
    """Container for a ranked search result."""
    rank: int
    product_id: int
    name: str
    vibes: List[str]
    similarity_score: float
    description: str = ""


def get_product_catalog() -> pd.DataFrame:
    """Get the mock fashion product catalog.
    
    Returns:
        DataFrame with product information
    """
    products_data = [
        {
            "id": 1,
            "name": "Boho Maxi Dress",
            "desc": "Flowy silhouette in earthy tones with intricate embroidery, perfect for outdoor festivals and weekend markets. Pairs well with sandals and layered jewelry.",
            "vibes": ["boho", "cozy", "earthy", "festival"]
        },
        {
            "id": 2,
            "name": "Urban Streetwear Bomber",
            "desc": "Bold graphic bomber jacket with oversized fit and metallic accents. Makes a statement in the city with edgy attitude and contemporary street style.",
            "vibes": ["urban", "streetwear", "bold", "edgy", "energetic"]
        },
        {
            "id": 3,
            "name": "Minimalist Cashmere Sweater",
            "desc": "Soft cashmere knit in neutral tones with clean lines and timeless design. Ultimate comfort meets understated elegance for everyday wear.",
            "vibes": ["minimal", "cozy", "soft", "elegant", "timeless"]
        },
        {
            "id": 4,
            "name": "Sustainable Linen Set",
            "desc": "Eco-friendly linen co-ord set in natural beige. Breathable fabric perfect for conscious consumers seeking comfort and sustainability without compromising style.",
            "vibes": ["sustainable", "minimal", "earthy", "conscious", "comfortable"]
        },
        {
            "id": 5,
            "name": "Athleisure Jogger Set",
            "desc": "Performance fabric meets loungewear comfort. Sleek joggers and matching hoodie for gym sessions or relaxed weekend vibes with modern athletic aesthetic.",
            "vibes": ["athletic", "comfortable", "modern", "casual", "energetic"]
        },
        {
            "id": 6,
            "name": "Vintage Denim Jacket",
            "desc": "Classic distressed denim with retro wash and brass buttons. Timeless wardrobe staple that adds rugged charm and nostalgic appeal to any outfit.",
            "vibes": ["vintage", "casual", "timeless", "rugged", "classic"]
        },
        {
            "id": 7,
            "name": "Cozy Loungewear Bundle",
            "desc": "Ultra-soft matching sweatpants and oversized pullover in muted pastels. Perfect for self-care Sundays, reading nooks, and Netflix marathons at home.",
            "vibes": ["cozy", "soft", "comfortable", "relaxed", "homey"]
        },
        {
            "id": 8,
            "name": "Chic Blazer Dress",
            "desc": "Sharp tailoring meets feminine silhouette. Structured blazer-style dress in monochrome palette perfect for power meetings or sophisticated evening events.",
            "vibes": ["chic", "elegant", "sophisticated", "modern", "powerful"]
        },
        {
            "id": 9,
            "name": "Festival Fringe Top",
            "desc": "Playful crop top with cascading fringe details and tribal-inspired patterns. Free-spirited design perfect for music festivals and bohemian outdoor adventures.",
            "vibes": ["boho", "festival", "playful", "free-spirited", "tribal"]
        },
        {
            "id": 10,
            "name": "Tech Wear Cargo Pants",
            "desc": "Futuristic utility pants with multiple pockets and technical fabric. Perfect for urban explorers who value function, innovation, and cutting-edge street style.",
            "vibes": ["urban", "streetwear", "futuristic", "functional", "innovative"]
        }
    ]
    
    df = pd.DataFrame(products_data)
    df['desc_normalized'] = df['desc'].apply(normalize_text)
    return df


def normalize_text(text: str) -> str:
    """Normalize text: trim, lowercase, collapse whitespace.
    
    Args:
        text: input string
    
    Returns:
        Cleaned string
    """
    if not text:
        return ""
    s = text.strip().lower()
    s = re.sub(r"[\r\n\t]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s


def load_cache() -> Dict[str, List[float]]:
    """Load embedding cache from disk."""
    if not CACHE_PATH.exists():
        return {}
    try:
        with CACHE_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_cache(cache: Dict[str, List[float]]) -> None:
    """Save embedding cache to disk."""
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CACHE_PATH.open("w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def create_synthetic_embedding(text: str, dim: int = EMBEDDING_DIM) -> np.ndarray:
    """Generate deterministic synthetic embedding for offline testing.
    
    Args:
        text: input text
        dim: embedding dimension
    
    Returns:
        Normalized numpy array of shape (dim,)
    """
    seed = abs(hash(text)) % (2 ** 31)
    rng = np.random.RandomState(seed)
    vec = rng.normal(size=(dim,)).astype(float)
    vec = vec / (np.linalg.norm(vec) + 1e-12)
    return vec


def embed_texts(texts: List[str], use_cache: bool = True) -> Tuple[np.ndarray, str]:
    """Generate embeddings for a list of texts.
    
    Args:
        texts: list of input strings
        use_cache: whether to use cached embeddings
    
    Returns:
        Tuple of (embeddings array, status message)
    """
    cache = load_cache() if use_cache else {}
    to_request = [t for t in texts if t not in cache]
    
    status_msg = ""
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Try OpenAI API
    if to_request and api_key and OPENAI_AVAILABLE:
        try:
            response = openai.Embedding.create(
                model=EMBEDDING_MODEL,
                input=to_request
            )
            for txt, item in zip(to_request, response['data']):
                cache[txt] = item['embedding']
            if use_cache:
                save_cache(cache)
            status_msg = f"✅ Embedded {len(to_request)} texts using OpenAI API"
        except Exception as e:
            status_msg = f"⚠️ OpenAI API error: {str(e)}. Using synthetic embeddings."
            for txt in to_request:
                cache[txt] = create_synthetic_embedding(txt).tolist()
            if use_cache:
                save_cache(cache)
    elif to_request:
        # Use synthetic embeddings
        for txt in to_request:
            cache[txt] = create_synthetic_embedding(txt).tolist()
        if use_cache:
            save_cache(cache)
        status_msg = f"ℹ️ Generated {len(to_request)} synthetic embeddings (no API key set)"
    else:
        status_msg = f"✅ Using {len(texts)} cached embeddings"
    
    # Collect vectors in original order
    vectors = [np.array(cache[t], dtype=float) for t in texts]
    return np.vstack(vectors), status_msg


def rank_by_similarity(
    query_embedding: np.ndarray,
    product_embeddings: np.ndarray,
    products_df: pd.DataFrame,
    topk: int = TOP_K
) -> List[RankedResult]:
    """Rank products by cosine similarity to query.
    
    Args:
        query_embedding: shape (1, dim) or (dim,)
        product_embeddings: shape (n_products, dim)
        products_df: DataFrame with product info
        topk: number of top results to return
    
    Returns:
        List of RankedResult objects, sorted by descending similarity
    """
    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)
    
    similarities = cosine_similarity(query_embedding, product_embeddings).reshape(-1)
    similarities_01 = (similarities + 1.0) / 2.0
    
    top_indices = np.argsort(-similarities_01, kind='mergesort')[:topk]
    
    results = []
    for rank, idx in enumerate(top_indices, start=1):
        product = products_df.iloc[idx]
        results.append(RankedResult(
            rank=rank,
            product_id=int(product['id']),
            name=str(product['name']),
            vibes=list(product['vibes']),
            similarity_score=float(similarities_01[idx]),
            description=str(product['desc'])
        ))
    
    return results


def validate_query(query: str) -> Tuple[bool, str]:
    """Validate user query.
    
    Args:
        query: user's input query
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    query = query.strip()
    if not query:
        return False, "❌ Empty query! Please enter at least 2 descriptive words."
    
    words = query.split()
    if len(words) < 2:
        return False, "❌ Query too short! Please enter at least 2 descriptive words."
    
    return True, ""


def search_vibes(
    query: str,
    products_df: pd.DataFrame,
    product_embeddings: np.ndarray,
    topk: int = TOP_K
) -> Tuple[List[RankedResult], bool, str, str]:
    """Complete search pipeline: validate → embed → rank → check thresholds.
    
    Args:
        query: user's vibe query string
        products_df: product catalog
        product_embeddings: precomputed product embeddings
        topk: number of results to return
    
    Returns:
        Tuple of (results, is_fallback, status_message, warning_message)
    """
    # Validate query
    is_valid, error_msg = validate_query(query)
    if not is_valid:
        return [], True, error_msg, ""
    
    # Normalize and embed query
    normalized_query = normalize_text(query)
    query_embedding, embed_status = embed_texts([normalized_query])
    
    # Rank products
    results = rank_by_similarity(query_embedding, product_embeddings, products_df, topk)
    
    # Check for fallback condition
    max_score = max([r.similarity_score for r in results]) if results else 0.0
    is_fallback = max_score < FALLBACK_THRESHOLD
    
    warning_msg = ""
    if is_fallback:
        warning_msg = (
            f"⚠️ No strong match found (top score: {max_score:.3f}, threshold: {FALLBACK_THRESHOLD})\n\n"
            "💡 Try adding more specific vibe hints:\n"
            "• 'minimal, streetwear, sustainable'\n"
            "• 'boho, earthy, festival vibes'\n"
            "• 'cozy, soft, loungewear comfort'"
        )
    
    return results, is_fallback, embed_status, warning_msg


def initialize_embeddings() -> Tuple[pd.DataFrame, np.ndarray, str]:
    """Initialize product catalog and embeddings.
    
    Returns:
        Tuple of (products_df, product_embeddings, status_message)
    """
    products_df = get_product_catalog()
    product_texts = products_df['desc_normalized'].tolist()
    product_embeddings, status = embed_texts(product_texts)
    return products_df, product_embeddings, status


def get_all_vibes(products_df: pd.DataFrame) -> List[str]:
    """Extract all unique vibe tags from catalog.
    
    Args:
        products_df: product catalog
    
    Returns:
        Sorted list of unique vibe tags
    """
    all_vibes = set()
    for vibes_list in products_df['vibes']:
        all_vibes.update(vibes_list)
    return sorted(list(all_vibes))


def get_metrics_summary(results: List[RankedResult]) -> Dict[str, float]:
    """Calculate summary metrics for search results.
    
    Args:
        results: list of ranked results
    
    Returns:
        Dictionary with metrics
    """
    if not results:
        return {
            "avg_score": 0.0,
            "top_score": 0.0,
            "good_hits": 0,
            "total": 0
        }
    
    scores = [r.similarity_score for r in results]
    good_hits = sum(1 for s in scores if s >= GOOD_HIT_THRESHOLD)
    
    return {
        "avg_score": np.mean(scores),
        "top_score": max(scores),
        "good_hits": good_hits,
        "total": len(results)
    }
