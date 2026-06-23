# M1 — Socle Data / Ingestion

![Responsable](https://img.shields.io/badge/Responsable-Bara_Ben_Khedher-blue) ![Phases](https://img.shields.io/badge/Phases-P0_·_P1_·_P4-lightgrey) ![Statut](https://img.shields.io/badge/Statut-à_lancer-orange)

> Le **carburant du RAG** : sans données bien préparées, pas de bon copilote. Ce module alimente et entretient la base de connaissances.

## 🎯 Objectif

Ingérer les documents projets BIMLO (notes de calcul, plans de fabrication, modèles IFC) vers la base vectorielle et la base de valeurs structurées, de façon fiable et rejouable.

## 📦 Périmètre

- Ingestion des 3 types de documents : notes de calcul (Word/PDF), plans (PDF/DWG), modèles 3D (IFC).
- Double indexation : vectorielle (ChromaDB) + structurée (site, hauteur, charges, sections, normes).
- Extraction IFC (composants, dimensions, matériaux) via `ifcopenshell`.
- Tagging systématique : projet, site, indice de révision.
- Enrichissement continu : chaque projet validé alimente la base.

## ✅ Tâches

- [ ] Pipeline d'ingestion robuste + métadonnées (rejouable)
- [ ] Reconstruire l'index ChromaDB à partir des documents
- [ ] Intégrer l'extraction IFC (`ifcopenshell`)
- [ ] Tagging projet / site / indice
- [ ] Enrichissement automatique à chaque nouveau projet

## 📤 Livrables

- Base vectorielle reconstruite et interrogeable
- Pipeline d'ingestion documenté et rejouable
- Métadonnées normalisées pour tous les documents

## 🔗 Dépendances

- Code d'ingestion d'Amine : `ingestion_graph.py`, `vector_store.py`, `telecom_doc_processor.py`
- En entrée des modules **M2** (répondre) et **M4** (vérifier)

## 🧩 Fichiers du projet d'Amine à réutiliser

`services/ingestion_graph.py` · `services/vector_store.py` · `services/telecom_doc_processor.py` · `ingest_bimlo_docs.py`
