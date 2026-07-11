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

- [x] Recherche hybride (sémantique + valeurs structurées) — `vector_store.hybrid_search()` : filtre **PostgreSQL** (schéma canonique de Mohamed, tables `projets`/`pylones`) sur les paramètres structurés (hauteur, type_pylône, projet) puis recherche sémantique ChromaDB scopée aux projets retenus. ✅ Verrouillage vérifié sur les 24 projets réels : `projet='ESTER'` → 1 ; `type_pylone='mât braconné'` → 11 ; `hauteur_min=30` → 2 (ESTER/NEVILLE 36 m) ; combiné `hauteur_max=10 + mât` → mâts courts ; projet/hauteur absents → 0 chunk (pas de fuite). ⚠️ Couverture hauteur partielle (7/24 pylônes renseignés — `hauteur_m` enrichie depuis `donnees_extraites` ; les autres n'ont la valeur nulle part dans le JSON).
- [x] Citations précises (site, document, page) — extraction PDF page-par-page (`page_number` par chunk) + `project_name`/`site_id` en métadonnée ; exposés dans les en-têtes `[Source N]` et les cartes de sources renvoyées.
- [x] Filtres par projet / site — champs `project_name` / `site_id` / `filter_doc_type` sur `QueryRequest`, propagés jusqu'au nœud de récupération.
- [x] Recherche de projets similaires — « precedent finder » : `sql_filters` (hauteur, type) extraits par le classifieur d'intention → filtre SQL → projets candidats. ⚠️ Ranking de similarité dédié encore basique (filtre exact, pas de score de proximité).
- [x] Endpoint de requête + streaming — `POST /query` (streaming existant réutilisé), filtres de métadonnées câblés.
- [x] Jeu de tests de pertinence (Q&A) — `tests/test_pertinence.py` : dataset « Golden Q&A » + LLM-as-a-judge + rapport CSV (`pertinence_report.csv`). ⚠️ Dataset actuel provisoire (placeholders) en attente des vrais PDF/questions.

> **Statut MR** : cœur (recherche hybride + verrouillage projet strict) opérationnel. Restent en amélioration : ranking de similarité dédié, et remplacement du dataset Golden provisoire par les cas réels.

## ▶️ Reproduire en local (Docker)

Le store structuré est **PostgreSQL** (conteneur `postgres` dans `docker-compose.yml`).
Le schéma (`db/init/*.sql`) est appliqué automatiquement au premier démarrage.
Les JSON projets réels (dossier `DATA_TEST_RAG_BIMLO_pour_Ali/donnees_json`, gitignored)
sont montés en lecture seule sur `/app/data/donnees_json`.

```bash
cd 00-base-amine/Backend

# 1. Démarrer toute la stack (postgres + neo4j + chroma + api)
docker compose up -d --build           # 1re fois : build (installe psycopg2, etc.)

# 2. Ingérer les 24 projets → PostgreSQL (projets/pylônes/NC) + ChromaDB (embeddings)
docker exec backend-api-1 python scripts/ingest_json.py

# (schéma déjà auto-appliqué ; pour le ré-appliquer manuellement :)
# docker exec backend-api-1 python scripts/init_db.py

# 3a. Vérifier le verrouillage hybride (filtre SQL → scope ChromaDB)
docker exec backend-api-1 python scripts/test_final_m2.py

# 3b. Suite de pertinence + rapport CSV
docker exec backend-api-1 pytest tests/test_pertinence.py -v -s   # → pertinence_report.csv
```

> **Env** : `POSTGRES_HOST/PORT/DB/USER/PASSWORD` (voir `.env.example`). En Docker
> l'API pointe sur le service `postgres` ; en exécution hors conteneur, mettre
> `POSTGRES_HOST=localhost`.

## 📤 Livrables

- Réponses chiffrées fiables avec sources citées → **Jalon J1**
- API de requête documentée
- Rapport de qualité (tests de pertinence)

## 🔗 Dépendances

- **M1** (base ingérée) en entrée
- Sert de socle aux modules **M3** (récupération de précédents) et **M4**

## 🧩 Fichiers du projet d'Amine à réutiliser

`services/rag_engine.py` · `services/graph_rag.py` · `services/reranker.py` · `services/intent_classifier.py` · `routers/chat.py`
