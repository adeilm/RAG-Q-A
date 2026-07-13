"""
precedent.py — "projet le plus proche" similarity ranking (M2).

The hybrid search does *exact* structured filtering (height >= X, type LIKE …).
The M2 périmètre also asks for precedent retrieval — the CLOSEST past project,
not just exact matches. This module scores every project against target criteria
on its structured attributes and returns them ranked by proximity.

Scoring is transparent and explainable (important for engineers reviewing a
precedent): each component contributes a 0..1 sub-score, combined as a weighted
average over whichever criteria were actually provided.

  • type      — categorical: 1.0 if the target type appears in the project's
                type_pylone / type_structure, else 0.0
  • height    — numeric proximity: 1 - min(|h - target| / HEIGHT_SCALE, 1)
  • normes    — Jaccard overlap of Eurocode lists
  • materiaux — Jaccard overlap of material lists

Data source: PostgreSQL (projets + pylones + notes_de_calcul.contenu_extrait JSONB).
"""

from typing import Dict, List, Optional, Set

from services.db import get_pg_conn

# A 20 m difference drives the height sub-score to 0. Tuned for telecom pylons
# (dataset spans ~5–36 m); adjust if the corpus range changes.
HEIGHT_SCALE = 20.0


def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _norm_set(values) -> Set[str]:
    """Normalise a JSON list (or None) into a lowercased set of tokens."""
    if not values:
        return set()
    if isinstance(values, str):
        values = [values]
    return {str(v).strip().lower() for v in values if str(v).strip()}


def _fetch_projects() -> List[Dict]:
    """
    One row per project with its structured attributes. A project may have
    several pylons / NCs; we keep the first non-null values (aggregation).
    """
    conn = get_pg_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.code_projet,
               p.nom,
               MAX(py.hauteur_m)                                    AS hauteur_m,
               COALESCE(MAX(py.type_pylone),
                        MAX(nc.contenu_extrait->>'type_structure')) AS type_pylone,
               (ARRAY_AGG(nc.contenu_extrait->'normes')
                        FILTER (WHERE nc.contenu_extrait ? 'normes'))[1]    AS normes,
               (ARRAY_AGG(nc.contenu_extrait->'materiaux')
                        FILTER (WHERE nc.contenu_extrait ? 'materiaux'))[1] AS materiaux
        FROM projets p
        LEFT JOIN pylones py         ON py.projet_id = p.id
        LEFT JOIN notes_de_calcul nc ON nc.projet_id = p.id
        GROUP BY p.code_projet, p.nom
        """
    )
    cols = [c[0] for c in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    conn.close()
    return rows


def find_similar_projects(
    hauteur_m: Optional[float] = None,
    type_pylone: Optional[str] = None,
    normes: Optional[List[str]] = None,
    materiaux: Optional[List[str]] = None,
    top_n: int = 5,
) -> List[Dict]:
    """
    Rank projects by similarity to the given criteria.

    Returns up to `top_n` dicts sorted by descending score, each with:
        code_projet, nom, hauteur_m, type_pylone, score (0..1), components{...}
    `components` holds the per-criterion sub-scores for explainability.
    Only the criteria you pass are scored (weights normalise over them).
    """
    target_type = (type_pylone or "").strip().lower()
    target_normes = _norm_set(normes)
    target_materiaux = _norm_set(materiaux)

    ranked: List[Dict] = []
    for proj in _fetch_projects():
        components: Dict[str, float] = {}

        if type_pylone:
            proj_type = (proj.get("type_pylone") or "").lower()
            components["type"] = 1.0 if target_type and target_type in proj_type else 0.0

        if hauteur_m is not None and proj.get("hauteur_m") is not None:
            diff = abs(float(proj["hauteur_m"]) - float(hauteur_m))
            components["height"] = max(0.0, 1.0 - min(diff / HEIGHT_SCALE, 1.0))

        if target_normes:
            components["normes"] = _jaccard(target_normes, _norm_set(proj.get("normes")))

        if target_materiaux:
            components["materiaux"] = _jaccard(target_materiaux, _norm_set(proj.get("materiaux")))

        if not components:
            continue  # nothing to score this project on

        score = sum(components.values()) / len(components)
        ranked.append({
            "code_projet": proj["code_projet"],
            "nom":         proj["nom"],
            "hauteur_m":   float(proj["hauteur_m"]) if proj.get("hauteur_m") is not None else None,
            "type_pylone": proj.get("type_pylone"),
            "score":       round(score, 3),
            "components":  {k: round(v, 3) for k, v in components.items()},
        })

    ranked.sort(key=lambda r: r["score"], reverse=True)
    return ranked[:top_n]
