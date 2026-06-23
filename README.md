<!-- ====================== HERO ====================== -->
<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1F3864,50:2E75B6,100:00C2CB&height=200&section=header&text=BIMLO%20RAG%20Copilot&fontSize=52&fontColor=ffffff&fontAlignY=38&desc=Copilot%20T%C3%A9l%C3%A9com%20(RAG)%20%E2%80%94%20R%C3%A9pondre%20%C2%B7%20Produire%20%C2%B7%20V%C3%A9rifier&descSize=18&descAlignY=60" alt="BIMLO RAG Copilot" width="100%"/>

<p>
<em>Assistant IA construit sur la base des projets BIMLO — notes de calcul (trame Word), plans de fabrication, modèles 3D IFC, normes Eurocode.<br/>
Il <b>répond</b> aux questions techniques, aide à <b>produire</b> les notes de calcul et <b>vérifie</b> la cohérence note de calcul ↔ plans.</em>
</p>

<p>
<img src="https://img.shields.io/badge/STATUT-Phase_0_%C3%A0_lancer-F5A623?style=for-the-badge"/>
<img src="https://img.shields.io/badge/D%C3%A9marrage-1_juillet_2026-2E75B6?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Dur%C3%A9e-9_semaines-1F3864?style=for-the-badge"/>
<img src="https://img.shields.io/badge/REPO-PRIV%C3%89-555?style=for-the-badge&logo=github"/>
</p>

<p>
<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/LangGraph_·_LangChain-1C3C3C?style=flat-square&logo=chainlink&logoColor=white"/>
<img src="https://img.shields.io/badge/ChromaDB-FF6F61?style=flat-square"/>
<img src="https://img.shields.io/badge/Neo4j-008CC1?style=flat-square&logo=neo4j&logoColor=white"/>
<img src="https://img.shields.io/badge/Groq_LLM-F55036?style=flat-square"/>
<img src="https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black"/>
<img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white"/>
</p>

🎯 Réutiliser le savoir des projets passés &nbsp;·&nbsp; 👤 Resp. **M. Massoudi — Direction BIMLO** &nbsp;·&nbsp; 🧭 Référent : **Amine**

</div>

<!-- ====================== OBJECTIFS ====================== -->
## 🎯 Les 3 capacités

<div align="center">

| 💬 Répondre | 📝 Produire | ✅ Vérifier |
|:-----------:|:-----------:|:-----------:|
| Retrouver une hypothèse, un précédent, une valeur — **source citée** | Générer un brouillon de note de calcul suivant la **trame Word** officielle | Contrôler la cohérence **NDC ↔ Plan ↔ IFC** et la conformité Eurocode |
| `M2-repondre` | `M3-produire` | `M4-verifier` |

</div>

> ⚖️ **Règle d'or :** l'IA produit un *brouillon* et *signale des écarts* ; la décision et la validation restent à l'ingénieur. Le LLM ne produit **jamais** une valeur de dimensionnement. Toute réponse cite sa source.

---

## 🧰 Stack technique

| Couche | Technologies |
|--------|--------------|
| 🖥️ Frontend | React 18 · TypeScript · Vite · Tailwind |
| ⚡ API | FastAPI (Python) · streaming |
| 🧠 Moteur RAG | LangChain + LangGraph (RAG agentique, routage d'intention) |
| 🔎 Vector store | ChromaDB · embeddings Sentence-Transformers (all-MiniLM-L6-v2) |
| 🤖 LLM | Groq (llama-3.3-70b) · Cloudflare Workers AI (vision) |
| 🗂️ Mémoire / Auth | Neo4j (sessions) — fallback SQLite automatique |
| 💾 Base projets | SQLite `bimlo_projects.db` (documents + chunks + valeurs) |
| 📐 Calcul / Génération | Module déterministe Eurocode (EN 1990/1991/1993) + export Word/PDF |

---

## 📊 Suivi du projet

<div align="center">

### ➡️ **[ Ouvrir le tableau de bord — PROGRESS.md ](./PROGRESS.md)**
*avancement par stagiaire · jalons J0→J4 · % global*

</div>

---

## 🧩 Les 5 contrôles de vérification (NDC ↔ Plan ↔ IFC)

| # | Comparaison | Contrôle |
|:-:|-------------|----------|
| ① | Plan de fabrication → Note de calcul | Hauteurs, sections, charges, normes |
| ② | Note de calcul → Plan de fabrication | Sections, repères, indice de révision |
| ③ | Note de calcul → valeurs structurées | Charges vent/sismique, efforts |
| ④ | Modèle IFC → Note de calcul | Composants, dimensions, matériaux |
| ⑤ | Plan de fabrication ↔ IFC | Cotations DWG vs dimensions IFC |

---

## 📁 Architecture du dépôt

```text
BIMLO-RAG-Copilot/
├── README.md            → cette page
├── PROGRESS.md          → tableau de bord global (avancement, jalons, %)
├── EQUIPE.md            → rôles, permissions, matrice de compétences
├── CONTRIBUTING.md      → workflow Git, branches, conventions
│
├── M1-socle-data/       → ingestion NDC/plans/IFC + base vectorielle   (Bara)
├── M2-repondre/         → moteur RAG, recherche hybride, citations, API (Abid)
├── M3-produire/         → génération trame Word + calcul Eurocode       (Houssem · Amine · Nour)
├── M4-verifier/         → vérification NDC ↔ plans + rapport d'écarts   (Houssem)
└── M5-interface/        → front React (Q&A + formulaire) + exports      (Nour)
```

Chaque dossier `Mx-…/` contient son propre `README.md` (périmètre, tâches, livrables, statut).

---

## 👥 Équipe

| Membre | Module | Rôle |
|--------|:------:|------|
| Mohamed Ali Abid | `M2` | Lead RAG / Backend (*répondre*) |
| Houssem Ben Chaabane | `M3` `M4` | Agents IA & Vérification (*vérifier*) |
| Bara Ben Khedher | `M1` | Data / Ingestion (socle) |
| Nour Rajhi | `M5` `M3` | Génération + Interface (*produire*) |
| Amine *(référent)* | `M3` | Architecture, gabarit NDC, module de calcul |

Détails : [`EQUIPE.md`](./EQUIPE.md) · Contribuer : [`CONTRIBUTING.md`](./CONTRIBUTING.md)

---

## 🚀 Démarrage rapide (local — pas d'hébergement)

> ⚠️ Les secrets (`.env`) et les documents projets ne sont **jamais** commités (voir `.gitignore`).

```bash
# Backend
cd Backend && python -m venv .venv
pip install -r requirements.txt
cp .env.example .env        # remplir les clés (Groq, Cloudflare, Neo4j)
uvicorn main:app --reload

# Frontend
cd Frontend && npm install && npm run dev
```

---

<!-- ====================== CONTACT ====================== -->
<div align="center">

## 📬 Contact

**Mohamed Massoudi** — Direction BIMLO · Responsable du projet

<a href="https://www.linkedin.com/in/mohamed-messaoudi-be/">
<img src="https://img.shields.io/badge/LinkedIn-Mohamed_Massoudi-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white"/>
</a>
<a href="https://www.linkedin.com/company/10759944">
<img src="https://img.shields.io/badge/BIMLO-Page_entreprise-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white"/>
</a>
<a href="mailto:mohamed.massoudi@gmail.com">
<img src="https://img.shields.io/badge/Email-mohamed.massoudi@gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white"/>
</a>
<a href="https://github.com/mohamedmessaoudi-star">
<img src="https://img.shields.io/badge/GitHub-mohamedmessaoudi--star-181717?style=for-the-badge&logo=github&logoColor=white"/>
</a>

<br/><br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:00C2CB,50:2E75B6,100:1F3864&height=120&section=footer"/>

<sub>Projet interne BIMLO — confidentiel. Ne pas diffuser les données projets hors de l'organisation.</sub>

</div>
