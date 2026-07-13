# Fiche d'avancement — Ali (Mohamed Ali Abid)

**Module :** 💬 M2 — Répondre (RAG Q&A) · **Rôle :** Lead RAG / Backend
**Phase :** P1 · **Branche :** `feature/m2-agentic-hybrid-search`
**Dernière mise à jour :** 2026-07-13

![M2](https://img.shields.io/badge/M2-~85%25-2E75B6?style=flat-square) ![Statut](https://img.shields.io/badge/Statut-en_cours-yellow?style=flat-square)

---

## 🎯 État des tâches M2

| Tâche | Statut | Détail |
|-------|:------:|--------|
| Recherche hybride (sémantique + valeurs structurées) | ✅ | `vector_store.hybrid_search()` : filtre **PostgreSQL** (projets/pylônes) → scope la recherche ChromaDB aux projets retenus. **Vérifié sur 24 projets réels.** |
| Citations précises (site, document, page) | ✅ | Extraction PDF page-par-page (`page_number`) + `project_name`/`site_id` ; exposés dans les cartes de sources et cités en clair dans la réponse. **Vérifié bout-en-bout.** |
| Filtres par projet / site | ✅ | Champs `project_name` / `site_id` / `type` / `hauteur` propagés jusqu'à la récupération. |
| Recherche de projets similaires | ✅ | `precedent.find_similar_projects()` : **score de proximité** explicable (type + proximité hauteur + Jaccard normes/matériaux). Vérifié : 36 m triangulaire → ESTER/NEVILLE 1.0, treillis 24 m 0.7. ⚠️ Un critère est ignoré quand la donnée manque (hauteur NULL sur 17/24) → à exposer via une route dédiée (étape fine restante). |
| Endpoint de requête + streaming | ✅ | `POST /query` (streaming existant), filtres câblés. |
| Jeu de tests de pertinence (Q&A) | 🟡 | Framework prêt (`tests/test_pertinence.py`, LLM-as-judge + rapport CSV). Dataset Golden encore provisoire (placeholders). |

---

## ✅ Réalisé cette semaine

- **Migration SQLite → PostgreSQL** du store structuré, aligné sur le schéma canonique de Mohamed
  (6 tables, auto-appliqué au boot du conteneur `postgres` ajouté au `docker-compose`).
  → M2 devient compatible avec l'intégration M1/M4 (accès concurrent multi-service).
- **Recherche hybride vérifiée sur les 24 projets réels** (jeu `DATA_TEST_RAG_BIMLO_pour_Ali`) :
  - `projet='ESTER'` → verrouillé sur 1 projet ;
  - `type_pylone='mât braconné'` → 11 projets ;
  - `hauteur_min=30` → ESTER/NEVILLE (36 m) ; combiné `hauteur_max=10 + mât` → mâts courts ;
  - projet/hauteur absents → **0 chunk, aucune fuite**.
- **Citations page/site** surfacées jusqu'à la réponse (vérifié : réponse citant « page 2, site T-1234 »).
- **Enrichissement `pylones.hauteur_m`** depuis `donnees_extraites` à l'ingestion.
- **Image API reconstruite proprement** (psycopg2 intégré) → reproductible sans patch manuel.

---

## ⚠️ Blocages / points à traiter

- **Clés Cloudflare (CF) invalides (401)** dans `.env` — Groq prend le relais mais chaque appel LLM
  perd du temps en tentatives CF. → besoin des bonnes clés, ou basculer Groq en fournisseur unique.
- **Couverture hauteur partielle** : 7/24 pylônes renseignés ; les autres n'ont la valeur nulle part
  dans le JSON source (limite de données, pas de code).
- **À confirmer avec Amine/Mohamed** : PostgreSQL est bien la cible d'intégration commune (M1/M4) ?
- **Dataset Golden réel** attendu (PDF + questions validées) pour rendre la suite de pertinence probante.

---

## 🔜 Prochaines étapes (dans le périmètre M2)

1. Ouvrir la MR de `feature/m2-agentic-hybrid-search` vers `main`.
2. Exposer `find_similar_projects()` via une route/intention dédiée (câblage fin —
   la logique de scoring est faite et vérifiée).

> **Hors périmètre M2** (relève de l'intégration ou de M1) :
> - Validation de pertinence sur le corpus réel complet → **phase d'intégration**.
> - Enrichir `donnees_extraites` (normes, matériaux) en colonnes filtrables → **M1**.
> - Compléter `hauteur_m` manquante (17/24) → dépend des données source (M1).
