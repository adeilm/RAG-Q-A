# BIMLO Towermind — Copilot Télécom (RAG)

> Assistant IA (RAG) construit sur la base des projets BIMLO (notes de calcul, plans de
> fabrication, modèles 3D IFC, normes Eurocode). Il **répond**, **vérifie** et aide à
> **produire** les notes de calcul — au service des ingénieurs BIMLO.

**Statut :** dépôt privé · stage été 2026 · référent technique **Amine** (Mohamed Amin Helali)

---

## Les 3 objectifs du produit

| Usage | Ce que ça change pour BIMLO |
|-------|-----------------------------|
| **Répondre** | Retrouver instantanément une hypothèse, un précédent, une valeur — avec la source citée. |
| **Vérifier** | Contrôler automatiquement la cohérence **Note de Calcul ↔ Plan de fabrication ↔ IFC** et la conformité Eurocode. |
| **Produire** | Générer un brouillon de note de calcul suivant la **trame Word officielle BIMLO**. |

**Règle d'or :** l'IA produit un *brouillon* et *signale des écarts* ; la décision et la
validation restent à l'ingénieur. Le LLM ne produit jamais une valeur de dimensionnement.
Toute réponse cite sa source dans la base.

---

## Stack technique

| Couche | Technologies |
|--------|--------------|
| Frontend | React 18 · TypeScript · Vite · Tailwind CSS |
| API | FastAPI (Python) · streaming |
| Moteur RAG | LangChain + LangGraph (RAG agentique, routage d'intention) |
| Vector store | ChromaDB · embeddings Sentence-Transformers (all-MiniLM-L6-v2) |
| LLM | Groq (llama-3.3-70b) · Cloudflare Workers AI (vision) |
| Mémoire / Auth | Neo4j (sessions, conversations) — fallback SQLite |
| Base projets | SQLite `bimlo_projects.db` (documents + chunks + valeurs) |
| Calcul / Génération | Module déterministe Eurocode (EN 1990/1991/1993) + export Word/PDF |

---

## Architecture

```text
Frontend (React/Vite)
        |
        v
   API FastAPI
        |
        +--> Auth + sessions (Neo4j → fallback SQLite)
        +--> Ingestion documents (LangGraph + telecom_doc_processor)
        +--> Recherche vectorielle (ChromaDB) + valeurs structurées (SQLite)
        +--> Agents : RAG / routage / vérification / rapport / vision
        |
        v
   Réponses + sources + rapports d'écarts + brouillons de NDC
```

---

## Structure du dépôt

```text
BIMLO-Towermind/
├─ Backend/            API FastAPI, agents, ingestion, auth, retrieval, vérification, rapports
│  ├─ services/        moteur RAG, compliance_checker, telecom_doc_processor, vision, report_agent...
│  ├─ routers/         endpoints (chat, documents, reports, sessions, health)
│  ├─ core/            dépendances, état de session
│  ├─ evals/           jeux de tests RAG (RAGAS, golden dataset)
│  └─ tests/           tests unitaires (pytest)
├─ Frontend/           application React (pages, UI, client API)
├─ .github/            workflows CI + templates issues/PR
└─ docker-compose.yml  stack locale (API + front + bases)
```

---

## Démarrage rapide (local — pas d'hébergement)

> ⚠️ Les secrets (`.env`) ne sont **jamais** commités. Copier les templates `.env.example`.

```bash
# 1. Backend
cd Backend
python -m venv .venv
# Windows : .venv\Scripts\activate   |   Linux/Mac : source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # puis remplir les clés (Groq, Cloudflare, Neo4j)
uvicorn main:app --reload

# 2. Frontend (nouveau terminal)
cd Frontend
npm install
cp .env.frontend.example .env.local
npm run dev
```

Détails de déploiement et de configuration : voir `DEPLOY.md` et `Backend/README.md`.

---

## L'équipe

Voir [`EQUIPE.md`](./EQUIPE.md) pour les rôles, périmètres et responsabilités.
Pour contribuer : voir [`CONTRIBUTING.md`](./CONTRIBUTING.md).

| Membre | Rôle |
|--------|------|
| Mohamed Ali Abid | Lead RAG / Backend (*répondre*) |
| Houssem Ben Chaabane | Agents IA & Vérification (*vérifier*) |
| Bara Ben Khedher | Data / Ingestion (socle) |
| Nour Rajhi | Génération + Interface (*produire*) |
| Amine (référent) | Architecture, gabarit NDC, module de calcul, encadrement |

---

## Feuille de route

| Jalon | Critère | Échéance |
|-------|---------|----------|
| **J0** | Solution qui tourne en local | Fin S1 |
| **J1** | Copilote Q&A fiable avec citations | Fin S3 |
| **J2** | Premier brouillon de note de calcul auto | Fin S7 |
| **J3** | Vérification NDC ↔ plans automatisée | Fin S9 |
| **J4** | Outil documenté (hébergement = phase ultérieure) | En continu |

---

*Projet interne BIMLO — confidentiel. Ne pas diffuser les données projets hors de l'organisation.*
