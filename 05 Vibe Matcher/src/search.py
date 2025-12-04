"""Search helpers: cosine similarity ranking and pretty printing helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class RankedItem:
    rank: int
    idx: int
    name: str
    vibes: List[str]
    similarity_score: float


def rank_by_similarity(
    query_embedding: np.ndarray,
    product_embeddings: np.ndarray,
    products_df: pd.DataFrame,
    topk: int = 3,
) -> List[RankedItem]:
    """Rank products by cosine similarity to the query.

    Similarity values are transformed to 0-1 via (sim + 1)/2.

    Args:
        query_embedding: shape (dim,) or (1, dim)
        product_embeddings: shape (n_products, dim)
        products_df: DataFrame containing at least 'name' and 'vibes' columns
        topk: number of top items to return

    Returns:
        List[RankedItem] ordered by descending similarity
    """
    if query_embedding.ndim == 1:
        q = query_embedding.reshape(1, -1)
    else:
        q = query_embedding
    sims = cosine_similarity(q, product_embeddings).reshape(-1)
    # transform to 0-1
    sims01 = (sims + 1.0) / 2.0

    # stable argsort descending
    order = np.argsort(-sims01, kind="mergesort")
    top = order[:topk]
    items: List[RankedItem] = []
    for rank, idx in enumerate(top, start=1):
        items.append(
            RankedItem(
                rank=rank,
                idx=int(idx),
                name=str(products_df.iloc[idx]["name"]),
                vibes=list(products_df.iloc[idx]["vibes"]),
                similarity_score=float(sims01[idx]),
            )
        )
    return items


def pretty_topk(items: List[RankedItem]) -> str:
    """Return a small formatted multi-line string for display."""
    lines = [f"Rank | Name | Vibes | Similarity"]
    for it in items:
        lines.append(
            f"{it.rank} | {it.name} | {', '.join(it.vibes)} | {it.similarity_score:.3f}"
        )
    return "\n".join(lines)
