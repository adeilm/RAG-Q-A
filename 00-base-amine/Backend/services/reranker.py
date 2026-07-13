"""
reranker.py — ColBERT / Cross-Encoder Re-ranking for BIMLO Copilot

Pipeline:
  1. Vector store returns top-N candidates (fetch_k, default 20)
  2. Cross-encoder scores every (query, chunk) pair for EXACT relevance
  3. Return top-K re-ranked chunks (what the LLM actually sees)

Model: BAAI/bge-reranker-v2-m3
  - Best-in-class multilingual reranker (handles French, Arabic, English)
  - ~560 MB download on first use (cached via HF_HOME volume in Docker)
  - Runs on CPU fine for batches of 20 chunks
  - Outputs raw logits (unbounded floats) — we sigmoid-normalize to 0–1
    so scores are human-readable AND compatible with _is_good_retrieval()

Env vars:
  RERANKER_MODEL   — HuggingFace model ID   (default: BAAI/bge-reranker-v2-m3)
  RERANKER_ENABLED — set "0" to disable     (default: enabled if model loads)
  RERANKER_FETCH_K — candidates to fetch    (default: 20)

Docker performance note:
  Mount a named volume at $HF_HOME (/root/.cache/huggingface) so the model
  survives restarts without a 500s re-download.  See docker-compose.yml.
"""

from __future__ import annotations

import os
import math
import time
import threading
from typing import List, Dict

_RERANKER_MODEL   = os.getenv("RERANKER_MODEL",   "BAAI/bge-reranker-v2-m3")
_RERANKER_ENABLED = os.getenv("RERANKER_ENABLED", "1").strip() != "0"
_FETCH_K          = int(os.getenv("RERANKER_FETCH_K", "20"))

# ── Hosted GPU rerank provider (prototype) ───────────────────────────────────
# When RERANK_PROVIDER is "jina" or "cohere" and a key is set, rerank via the
# hosted API (GPU, ~sub-second) instead of the local CPU cross-encoder.
# ⚠️  This sends chunk text to a 3rd party — acceptable for the prototype only;
#     confirm data-governance before using on production/confidential corpora.
_RERANK_PROVIDER  = os.getenv("RERANK_PROVIDER", "").strip().lower()   # "jina" | "cohere" | ""
_RERANK_MAX_DOCS  = int(os.getenv("RERANK_MAX_DOCS", "100"))           # cap docs sent per call

_HOSTED_RERANK = {
    "jina": {
        "url":     "https://api.jina.ai/v1/rerank",
        "key_env": "JINA_API_KEY",
        "model":   os.getenv("RERANK_MODEL", "jina-reranker-v2-base-multilingual"),
    },
    "cohere": {
        "url":     "https://api.cohere.com/v2/rerank",
        "key_env": "COHERE_API_KEY",
        "model":   os.getenv("RERANK_MODEL", "rerank-v3.5"),
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Model state
# ─────────────────────────────────────────────────────────────────────────────

_cross_encoder = None
_load_attempted = False
_load_lock      = threading.Lock()   # prevents double-load if two requests race


def _load_model() -> None:
    """
    Load the cross-encoder into the global _cross_encoder slot.
    Safe to call from any thread; uses _load_lock to prevent races.
    """
    global _cross_encoder, _load_attempted

    with _load_lock:
        if _load_attempted:
            return
        _load_attempted = True

        if not _RERANKER_ENABLED:
            print("ℹ️  reranker: disabled via RERANKER_ENABLED=0")
            return

        try:
            from sentence_transformers import CrossEncoder
            cache_dir = os.getenv("HF_HOME", None)  # respects Docker volume env var
            print(f"⏳ reranker: loading {_RERANKER_MODEL}"
                  f"{' (cached at ' + cache_dir + ')' if cache_dir else ' (first run downloads ~560 MB)'}…")
            t0 = time.time()

            # CrossEncoder does NOT accept cache_folder — set HF_HOME env var instead,
            # which HuggingFace hub respects natively. Passing cache_folder here raises
            # TypeError on newer sentence-transformers versions, leaving _cross_encoder=None.
            if cache_dir:
                os.environ.setdefault("HF_HOME", cache_dir)
                os.environ.setdefault("TRANSFORMERS_CACHE", cache_dir)

            _cross_encoder = CrossEncoder(
                _RERANKER_MODEL,
                max_length=512,
            )
            print(f"✅ reranker: {_RERANKER_MODEL} ready ({time.time() - t0:.1f}s)")
        except ImportError:
            print("⚠️  reranker: sentence-transformers not installed — run: pip install sentence-transformers")
        except Exception as e:
            print(f"⚠️  reranker: failed to load model ({e}) — falling back to vector-only retrieval")


def _get_cross_encoder():
    """Return the loaded model, triggering a synchronous load if not ready yet.
    Reads _load_attempted under the lock to avoid racing the prewarm thread."""
    with _load_lock:
        already = _load_attempted
    if not already:
        _load_model()
    return _cross_encoder


# ─────────────────────────────────────────────────────────────────────────────
# Eager pre-warm on import — model loads in a background thread at startup
# so the FIRST real query never has to wait for the 560 MB download.
# ─────────────────────────────────────────────────────────────────────────────

def _prewarm() -> None:
    """Called once at module import time from a daemon thread."""
    _load_model()

if _RERANKER_ENABLED:
    _prewarm_thread = threading.Thread(target=_prewarm, daemon=True, name="reranker-prewarm")
    _prewarm_thread.start()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _sigmoid(x: float) -> float:
    """Normalize a raw logit to 0–1 probability."""
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def _rerank_hosted(query: str, chunks: List[Dict], top_k: int) -> List[Dict]:
    """
    Rerank via a hosted GPU API (Jina or Cohere). Both expose the same shape:
      POST {model, query, documents[], top_n} → {results: [{index, relevance_score}]}
    Raises on any failure so the caller can fall back to the local model.
    """
    import requests

    cfg = _HOSTED_RERANK[_RERANK_PROVIDER]
    key = os.getenv(cfg["key_env"], "").strip()
    if not key:
        raise RuntimeError(f"{_RERANK_PROVIDER} rerank selected but {cfg['key_env']} is empty")

    # Cap docs sent (cost/payload): keep the best candidates by vector distance
    candidates = sorted(chunks, key=lambda c: c.get("distance", 1.0))[:_RERANK_MAX_DOCS]
    documents = [c["text"][:2000] for c in candidates]

    t0 = time.time()
    resp = requests.post(
        cfg["url"],
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"model": cfg["model"], "query": query, "documents": documents, "top_n": top_k},
        timeout=20,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        raise RuntimeError("hosted reranker returned no results")

    ranked: List[Dict] = []
    for r in results:
        c = candidates[r["index"]]
        score = float(r.get("relevance_score", 0.0))
        c["rerank_score"] = score
        c["distance"]     = 1.0 - score
        ranked.append(c)

    print(
        f"🏆 reranker[{_RERANK_PROVIDER}]: {len(documents)} → {len(ranked)} chunks "
        f"(top: {ranked[0]['rerank_score']:.3f}, {time.time() - t0:.2f}s)"
    )
    return ranked[:top_k]


def rerank(query: str, chunks: List[Dict], top_k: int = 5) -> List[Dict]:
    """
    Re-rank `chunks` by exact relevance to `query`.

    Uses a hosted GPU rerank API when RERANK_PROVIDER is configured (fast),
    otherwise the local CPU cross-encoder. Falls back to local (then to the
    original order) on any hosted-API failure.

    Args:
        query:  The user's question.
        chunks: Raw candidate chunks from the vector store (up to FETCH_K).
        top_k:  How many to return after re-ranking.

    Returns:
        The top_k most relevant chunks, each with:
          - rerank_score : relevance score (0–1)
          - distance     : overwritten with (1 - rerank_score) so that
                           _is_good_retrieval() in rag_engine works correctly
    """
    if not chunks:
        return chunks

    # ── Hosted GPU rerank (prototype) ─────────────────────────────────────────
    if _RERANK_PROVIDER in _HOSTED_RERANK:
        try:
            return _rerank_hosted(query, chunks, top_k)
        except Exception as e:
            print(f"⚠️  hosted rerank ({_RERANK_PROVIDER}) failed ({e}) — falling back to local model")

    model = _get_cross_encoder()

    if model is None:
        # Graceful degradation — return as-is, trimmed to top_k
        return chunks[:top_k]

    t0 = time.time()

    # Build (query, passage) pairs for the cross-encoder
    pairs = [(query, c["text"][:512]) for c in chunks]

    try:
        raw_scores = model.predict(pairs, show_progress_bar=False)
    except Exception as e:
        print(f"⚠️  reranker.predict failed ({e}) — using original order")
        return chunks[:top_k]

    # Normalize logits → 0–1 via sigmoid, then write back onto each chunk.
    # Also update `distance` (= 1 - score) so _is_good_retrieval() in
    # rag_engine.py can correctly judge quality from reranked results.
    for chunk, raw in zip(chunks, raw_scores):
        score = _sigmoid(float(raw))
        chunk["rerank_score"] = score
        chunk["distance"]     = 1.0 - score   # ← keeps _is_good_retrieval() honest

    ranked = sorted(chunks, key=lambda c: c["rerank_score"], reverse=True)
    result = ranked[:top_k]

    print(
        f"🏆 reranker: {len(chunks)} → {len(result)} chunks "
        f"(top score: {result[0]['rerank_score']:.3f}, "
        f"bottom: {result[-1]['rerank_score']:.3f}, "
        f"{time.time() - t0:.2f}s)"
    )

    return result


def get_fetch_k(top_k: int) -> int:
    """
    How many candidates to fetch from the vector store before re-ranking.
    Always at least 3× top_k, capped at FETCH_K.
    """
    return max(_FETCH_K, top_k * 3)