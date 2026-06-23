# M2 — Répondre (RAG Q&A)

![Responsable](https://img.shields.io/badge/Responsable-Mohamed_Ali_Abid-blue) ![Phase](https://img.shields.io/badge/Phase-P1-lightgrey) ![Statut](https://img.shields.io/badge/Statut-à_lancer-orange)

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

- [ ] Recherche hybride (sémantique + valeurs structurées)
- [ ] Citations précises (site, document, page)
- [ ] Filtres par projet / site
- [ ] Recherche de projets similaires
- [ ] Endpoint de requête + streaming
- [ ] Jeu de tests de pertinence (Q&A)

## 📤 Livrables

- Réponses chiffrées fiables avec sources citées → **Jalon J1**
- API de requête documentée
- Rapport de qualité (tests de pertinence)

## 🔗 Dépendances

- **M1** (base ingérée) en entrée
- Sert de socle aux modules **M3** (récupération de précédents) et **M4**

## 🧩 Fichiers du projet d'Amine à réutiliser

`services/rag_engine.py` · `services/graph_rag.py` · `services/reranker.py` · `services/intent_classifier.py` · `routers/chat.py`
