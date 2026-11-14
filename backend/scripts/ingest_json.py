"""
ingest_json.py — load the BIMLO project JSON dataset into PostgreSQL + ChromaDB.

For each project JSON:
  • PostgreSQL (structured half of hybrid search):
      projets, pylones, notes_de_calcul (with donnees_extraites → JSONB), plans
  • ChromaDB (semantic half):
      embed notes_de_calcul[].texte_complet and plans[].texte_complet,
      tagged with project_name / site_id / doc_type for filtering + citations.

Run inside the api container:
    docker compose exec api python scripts/ingest_json.py

Env:
    JSON_DIR  directory of *.json project files (default /app/data/donnees_json)
    POSTGRES_* connection (see services/db.py)
"""

import os
import sys
import json
import glob

# Ensure we can import from Backend.services
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import psycopg2.extras
from services.db import get_pg_conn
from services.vector_store import VectorStoreManager
from services.document_processor import DocumentProcessor

JSON_DIR = os.getenv("JSON_DIR", "/app/data/donnees_json")


def _load_json(filepath: str) -> dict:
    """Read a project JSON, tolerating non-UTF-8 (dataset is partly cp1252)."""
    with open(filepath, "rb") as f:
        raw = f.read()
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return json.loads(raw.decode(enc))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    # Last resort: utf-8 with replacement so we don't crash the whole run
    return json.loads(raw.decode("utf-8", errors="replace"))


def run_ingestion():
    print(f"🚀 Starting JSON ingestion pipeline (JSON_DIR={JSON_DIR})...")

    conn = get_pg_conn()
    conn.autocommit = False
    cursor = conn.cursor()

    vs = VectorStoreManager()
    dp = DocumentProcessor(chunk_size=1000, chunk_overlap=200)

    json_files = sorted(glob.glob(os.path.join(JSON_DIR, "*.json")))
    if not json_files:
        print(f"⚠️  No JSON files found in {JSON_DIR}")
        return

    n_projects = n_chunks = 0

    for filepath in json_files:
        filename = os.path.basename(filepath)
        if filename.startswith("_"):
            continue  # skip _resume.json / hidden

        print(f"📄 Processing: {filename}")
        data = _load_json(filepath)

        projet = data.get("projet", {})
        code_projet = projet.get("code_projet")
        if not projet or not code_projet:
            print("   ⚠️  no projet/code_projet — skipping")
            continue

        # -- SQL INSERT PROJECT (skip if already present) --
        cursor.execute("SELECT id FROM projets WHERE code_projet = %s", (code_projet,))
        row = cursor.fetchone()
        if row:
            print(f"   Project {code_projet} already exists. Skipping.")
            continue

        cursor.execute(
            """
            INSERT INTO projets (code_projet, nom, client, localisation, statut, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (code_projet, projet.get("nom"), projet.get("client"),
             projet.get("localisation"), projet.get("statut"), projet.get("description")),
        )
        projet_id = cursor.fetchone()[0]
        n_projects += 1

        # Structured values (hauteur_m, type_structure) often live in the NC's
        # donnees_extraites rather than in pylones[]. Build a project-level
        # fallback so the hybrid-search height/type filters actually have data.
        ncs = data.get("notes_de_calcul", [])
        dext_hauteur = next(
            (nc.get("donnees_extraites", {}).get("hauteur_m")
             for nc in ncs if nc.get("donnees_extraites", {}).get("hauteur_m") is not None),
            None,
        )
        dext_type = next(
            (nc.get("donnees_extraites", {}).get("type_structure")
             for nc in ncs if nc.get("donnees_extraites", {}).get("type_structure")),
            None,
        )

        # -- SQL INSERT PYLONES (enriched from donnees_extraites when missing) --
        for pyl in data.get("pylones", []):
            hauteur = pyl.get("hauteur_m")
            if hauteur is None:
                hauteur = dext_hauteur
            type_pyl = pyl.get("type_pylone") or dext_type
            cursor.execute(
                """
                INSERT INTO pylones (projet_id, nom, type_pylone, hauteur_m,
                                     charge_admissible_kn, date_installation, etat)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (projet_id, pyl.get("nom"), type_pyl, hauteur,
                 pyl.get("charge_admissible_kn"), pyl.get("date_installation"), pyl.get("etat")),
            )

        # -- SQL + CHROMA: notes de calcul --
        for nc in data.get("notes_de_calcul", []):
            nom_fichier = nc.get("nom_fichier", "NC")
            donnees_extraites = nc.get("donnees_extraites", {})
            texte_complet = nc.get("texte_complet", "")

            cursor.execute(
                """
                INSERT INTO notes_de_calcul
                    (projet_id, nom_fichier, chemin_fichier, version,
                     ingenieur_responsable, contenu_extrait)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (projet_id, nom_fichier, nc.get("chemin_fichier"), nc.get("version"),
                 nc.get("ingenieur_responsable"), psycopg2.extras.Json(donnees_extraites)),
            )

            if texte_complet:
                meta = {
                    "project_name": projet.get("nom", ""),
                    "site_id": code_projet,
                    "doc_type": "note_de_calcul",
                    "filename": nom_fichier,
                }
                chunks = dp._create_chunks(texte_complet, meta)
                vs.add_document(filename=nom_fichier, chunks=chunks, session_id="global")
                n_chunks += len(chunks)

        # -- SQL + CHROMA: plans --
        for plan in data.get("plans", []):
            nom_fichier = plan.get("nom_fichier", "PLAN")
            texte_complet = plan.get("texte_complet", "")

            cursor.execute(
                """
                INSERT INTO plans
                    (projet_id, nom_fichier, chemin_fichier, type_plan,
                     echelle, nombre_pages, contenu_extrait)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (projet_id, nom_fichier, plan.get("chemin_fichier"), plan.get("type_plan"),
                 plan.get("echelle"), plan.get("nombre_pages"), psycopg2.extras.Json({})),
            )

            if texte_complet:
                meta = {
                    "project_name": projet.get("nom", ""),
                    "site_id": code_projet,
                    "doc_type": "plan",
                    "filename": nom_fichier,
                }
                chunks = dp._create_chunks(texte_complet, meta)
                vs.add_document(filename=nom_fichier, chunks=chunks, session_id="global")
                n_chunks += len(chunks)

        conn.commit()  # commit per project so a later failure keeps earlier work

    conn.close()
    print(f"✅ Ingestion complete. {n_projects} new projects, {n_chunks} chunks embedded.")


if __name__ == "__main__":
    run_ingestion()
