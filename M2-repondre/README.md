# M2 — Répondre (RAG Q&A)

![Responsable](https://img.shields.io/badge/Responsable-Mohamed_Ali_Abid-blue) ![Phase](https://img.shields.io/badge/Phase-P1-lightgrey) ![Statut](https://img.shields.io/badge/Statut-en_cours-yellow)

> Capitaliser sur les projets passés : le savoir des anciens dossiers devient immédiatement accessible à toute l'équipe.

## 🎯 Objectif

Répondre aux questions techniques avec citation de la source, et retrouver des projets/précédents similaires.

## 📦 Périmètre

- Recherche hybride : sémantique (vecteurs) + valeurs structurées (chiffres fiables).
- Citations précises : site, document, page.
- Filtres par projet / site.
- Recherche de précédents (projet le plus proche).
- API FastAPI de requête (streaming).

## ✅ Tâches

- [x] Recherche hybride (sémantique + valeurs structurées) — `vector_store.hybrid_search()` : filtre SQLite (`bimlo_projects.db`) sur les paramètres structurés (hauteur, type_pylône, projet) puis recherche sémantique ChromaDB scopée aux projets retenus.
- [x] Citations précises (site, document, page) — extraction PDF page-par-page (`page_number` par chunk) + `project_name`/`site_id` en métadonnée ; exposés dans les en-têtes `[Source N]` et les cartes de sources renvoyées.
- [x] Filtres par projet / site — champs `project_name` / `site_id` / `filter_doc_type` sur `QueryRequest`, propagés jusqu'au nœud de récupération.
- [x] Recherche de projets similaires — « precedent finder » : `sql_filters` (hauteur, type) extraits par le classifieur d'intention → filtre SQL → projets candidats. ⚠️ Ranking de similarité dédié encore basique (filtre exact, pas de score de proximité).
- [x] Endpoint de requête + streaming — `POST /query` (streaming existant réutilisé), filtres de métadonnées câblés.
- [x] Jeu de tests de pertinence (Q&A) — `tests/test_pertinence.py` : dataset « Golden Q&A » + LLM-as-a-judge + rapport CSV (`pertinence_report.csv`). ⚠️ Dataset actuel provisoire (placeholders) en attente des vrais PDF/questions.

> **Statut MR** : cœur (recherche hybride + verrouillage projet strict) opérationnel. Restent en amélioration : ranking de similarité dédié, et remplacement du dataset Golden provisoire par les cas réels.

## ▶️ Reproduire en local

```bash
cd 00-base-amine/Backend

# 1. Créer le schéma SQLite structuré (projets, pylônes, notes de calcul…)
python scripts/init_db.py               # → data/bimlo_projects.db

# 2. Ingérer les JSON projets (SQLite + ChromaDB global)
#    JSON attendus dans le dossier data/donnees_json/ (voir JSON_DIR dans le script)
python scripts/ingest_json.py

# 3. Lancer l'API
uvicorn main:app --reload               # http://localhost:8000

# 4a. Tests fumée hybride (nécessite l'API démarrée)
python scripts/test_final_m2.py

# 4b. Suite de pertinence + rapport CSV
pytest tests/test_pertinence.py -v -s   # → pertinence_report.csv
```

## 📤 Livrables

- Réponses chiffrées fiables avec sources citées → **Jalon J1**
- API de requête documentée
- Rapport de qualité (tests de pertinence)

## 🔗 Dépendances

- **M1** (base ingérée) en entrée
- Sert de socle aux modules **M3** (récupération de précédents) et **M4**

## 🧩 Fichiers du projet d'Amine à réutiliser

`services/rag_engine.py` · `services/graph_rag.py` · `services/reranker.py` · `services/intent_classifier.py` · `routers/chat.py`
