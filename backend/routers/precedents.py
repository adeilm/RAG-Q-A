"""
precedents.py — "projet le plus proche" precedent-retrieval endpoint (M2).

Exposes the structured similarity ranking (services/precedent.py) over HTTP so
the app / frontend can retrieve past projects closest to given criteria.

    POST /precedents
    body: { "hauteur_m": 30, "type_pylone": "mât braconné",
            "normes": [...], "materiaux": [...], "top_n": 5 }
    → ranked list with per-component sub-scores (explainable).
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.precedent import find_similar_projects

router = APIRouter(tags=["precedents"])


class PrecedentRequest(BaseModel):
    hauteur_m:   Optional[float] = None
    type_pylone: Optional[str] = None
    normes:      Optional[List[str]] = None
    materiaux:   Optional[List[str]] = None
    top_n:       int = 5


@router.post("/precedents")
async def get_precedents(req: PrecedentRequest):
    """Return past projects ranked by proximity to the given criteria."""
    if not any([req.hauteur_m is not None, req.type_pylone, req.normes, req.materiaux]):
        raise HTTPException(
            status_code=422,
            detail="Provide at least one criterion (hauteur_m, type_pylone, normes, materiaux).",
        )
    try:
        results = find_similar_projects(
            hauteur_m=req.hauteur_m,
            type_pylone=req.type_pylone,
            normes=req.normes,
            materiaux=req.materiaux,
            top_n=req.top_n,
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Precedent search failed: {e}")

    return {"count": len(results), "criteria": req.model_dump(exclude_none=True), "results": results}
