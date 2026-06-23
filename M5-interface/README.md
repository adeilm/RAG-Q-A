# M5 — Interface (web utilisable)

![Responsable](https://img.shields.io/badge/Responsable-Nour_Rajhi-blue) ![Phases](https://img.shields.io/badge/Phases-P1_·_P2-lightgrey) ![Statut](https://img.shields.io/badge/Statut-à_lancer-orange)

> Relier l'IA à une interface claire : poser une question, lancer une vérification, générer une note, télécharger le résultat.

## 🎯 Objectif

Fournir une interface web simple et utilisable pour les trois usages (répondre, produire, vérifier).

## 📦 Périmètre

- Interface de questions-réponses (Q&A) avec affichage des sources citées.
- Formulaire de génération : saisie des paramètres du site (type pylône, hauteur, charges, zone).
- Affichage et téléchargement des notes générées et des rapports d'écarts.
- Exports Word / PDF.

## ✅ Tâches

- [ ] Interface Q&A fonctionnelle (réponses + citations)
- [ ] Filtres par projet / site dans l'UI
- [ ] Formulaire de génération (paramètres site)
- [ ] Affichage + téléchargement des brouillons de NDC
- [ ] Affichage + export des rapports de vérification

## 📤 Livrables

- UI Q&A fonctionnelle (Phase 1)
- Formulaire de génération + exports (Phase 2)

## 🔗 Dépendances

- **M2** (réponses), **M3** (génération), **M4** (rapports de vérification)

## 🧩 Fichiers du projet d'Amine à réutiliser

`Frontend/src/pages/Chat.tsx` · `Frontend/src/components/chat/` · `Frontend/src/services/api.ts` · `Frontend/src/hooks/useReports.ts`
