"""Embedding helpers: wraps OpenAI embedding calls and simple caching.

Provides:
- embed_texts(texts) -> np.ndarray

If OPENAI_API_KEY is not set, a deterministic synthetic embedding fallback is used
so the notebook can run without hitting the API during exploration.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np

try:
    import openai
except Exception:  # pragma: no cover - openai may not be installed in test env
    openai = None


def _load_cache(path: Path) -> Dict[str, List[float]]:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache(path: Path, cache: Dict[str, List[float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(cache, f)


def embed_texts(
    texts: Iterable[str],
    model: str = "text-embedding-ada-002",
    cache_path: str | Path = "data/embeddings_cache.json",
) -> np.ndarray:
    """Embed a list of texts. Uses OPENAI_API_KEY env var by default.

    Caches results to avoid repeated API calls. If the key is not set or OpenAI
    client isn't available, returns deterministic synthetic vectors.

    Args:
        texts: iterable of input strings
        model: model name for OpenAI embeddings
        cache_path: path to JSON cache (text -> vector)

    Returns:
        numpy array of shape (len(texts), dim)
    """
    texts = list(texts)
    path = Path(cache_path)
    cache = _load_cache(path)

    to_request = [t for t in texts if t not in cache]

    api_key = os.getenv("OPENAI_API_KEY")
    if to_request and api_key and openai is not None:
        openai.api_key = api_key
        # send batch requests in one call where possible
        try:
            resp = openai.Embedding.create(model=model, input=to_request)
            # resp['data'] is list aligned with to_request
            for txt, item in zip(to_request, resp["data"]):
                cache[txt] = item["embedding"]
            _save_cache(path, cache)
        except Exception as e:  # fallback to deterministic synth if API fails
            print("OpenAI embedding failed, falling back to synthetic embeddings:", e)
            # create deterministic synthetic vectors for the remaining
            base = _synthetic_vectors(to_request)
            for txt, vec in zip(to_request, base):
                cache[txt] = vec.tolist()
            _save_cache(path, cache)
    elif to_request:
        # no key or client unavailable: deterministic synthetic
        base = _synthetic_vectors(to_request)
        for txt, vec in zip(to_request, base):
            cache[txt] = vec.tolist()
        _save_cache(path, cache)

    # collect vectors in same order as texts
    vecs = [np.array(cache[t], dtype=float) for t in texts]
    return np.vstack(vecs)


def _synthetic_vectors(texts: Iterable[str], dim: int = 1536) -> List[np.ndarray]:
    """Deterministic synthetic vectors based on hashed text (for offline runs).

    The dimension 1536 is chosen to mimic typical OpenAI embedding sizes for the
    requested model. We use numpy with a fixed seed derived from text for stable output.
    """
    out = []
    for t in texts:
        # create a seed from the text in a stable way
        seed = abs(hash(t)) % (2 ** 31)
        rng = np.random.RandomState(seed)
        vec = rng.normal(size=(dim,)).astype(float)
        # normalize to unit length to mimic real embeddings
        vec = vec / (np.linalg.norm(vec) + 1e-12)
        out.append(vec)
    return out
