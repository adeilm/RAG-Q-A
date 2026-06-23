# M3 — Produire (génération de la note de calcul)

![Responsable](https://img.shields.io/badge/Responsable-Houssem_·_Amine_·_Nour-blue) ![Phase](https://img.shields.io/badge/Phase-P2-lightgrey) ![Statut](https://img.shields.io/badge/Statut-à_lancer-orange)

> Faire de la trame Word officielle BIMLO un standard exploitable, puis la remplir automatiquement — brouillon validé par un ingénieur.

## 🎯 Objectif

Générer un brouillon de note de calcul suivant la trame Word officielle, à partir des paramètres d'un nouveau site.

## 📦 Périmètre

- Formaliser la trame Word (sections : objet, hypothèses, équipements, descentes de charges, vérifications, conclusion).
- Cartographier « section ↔ donnée » (quelle info va dans quelle section).
- Module de calcul **déterministe** Eurocode (valeurs sûres — jamais le LLM).
- Agent de génération section par section (LangGraph) + récupération de précédents (RAG via M2).
- Export Word / PDF conforme au gabarit.

## ✅ Tâches

- [ ] Gabarit-type NDC + cartographie section ↔ donnée *(Houssem · Amine)*
- [ ] Module de calcul déterministe Eurocode *(Amine · Abid)*
- [ ] Agent de génération section par section (LangGraph) *(Houssem)*
- [ ] Récupération de précédents par section (RAG) *(Abid)*
- [ ] Export Word / PDF conforme au gabarit *(Nour)*

## 📤 Livrables

- Trame Word remplie automatiquement → **Jalon J2**
- Brouillon de NDC exportable (Word/PDF)
- Module de calcul traçable (validé par un ingénieur structure)

## ⚠️ Garde-fou

Le LLM **ne produit jamais** une valeur de dimensionnement. Il met en forme et rédige ; les valeurs viennent du module Eurocode et sont validées par un ingénieur.

## 🔗 Dépendances

- **M2** (récupération de précédents) et **M5** (formulaire de saisie + export)

## 🧩 Fichiers du projet d'Amine à réutiliser

`services/report_agent.py` · `services/llm_client.py` · `services/compliance_checker.py` (normes)
