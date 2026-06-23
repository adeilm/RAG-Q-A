# M4 — Vérifier (NDC ↔ Plan ↔ IFC)

![Responsable](https://img.shields.io/badge/Responsable-Houssem_Ben_Chaabane-blue) ![Phase](https://img.shields.io/badge/Phase-P3-lightgrey) ![Statut](https://img.shields.io/badge/Statut-à_lancer-orange)

> Une vérification qui prend aujourd'hui des heures se ramène à quelques minutes, avec moins d'erreurs.

## 🎯 Objectif

Contrôler automatiquement la cohérence Note de Calcul ↔ Plan de fabrication ↔ IFC et la conformité normative, puis produire un rapport d'écarts.

## 📦 Périmètre (les 5 contrôles)

| # | Comparaison | Contrôle |
|---|-------------|----------|
| ① | Plan → NDC | Hauteurs, sections, charges, normes |
| ② | NDC → Plan | Sections, repères, indice de révision |
| ③ | NDC → valeurs structurées | Charges vent/sismique, efforts |
| ④ | IFC → NDC | Composants, dimensions, matériaux |
| ⑤ | Plan ↔ IFC | Cotations DWG vs dimensions IFC |

## ✅ Tâches

- [ ] Service de vérification NDC ↔ plans (`ndc_plan_verifier.py`)
- [ ] Contrôle de conformité normative (Eurocode + télécom) avec score
- [ ] Brancher la vérification sur la base réelle (via M1)
- [ ] Endpoint `/compliance-check`
- [ ] Rapport d'écarts horodaté exportable (Word/PDF)

## 📤 Livrables

- Détection d'incohérences fiable → **Jalon J3**
- Endpoint `/compliance-check`
- Rapport d'écarts horodaté et archivable

## 🔗 Dépendances

- **M1** (données réelles), **M5** (export du rapport)

## 🧩 Fichiers du projet d'Amine à réutiliser

`services/compliance_checker.py` · `services/vision_service.py` (analyse de plans) · `services/telecom_doc_processor.py` · `services/report_agent.py`
