# Guide de contribution — BIMLO Towermind

Bienvenue dans l'équipe. Ce guide définit comment on travaille ensemble sur le dépôt
pour que le code reste propre, traçable et toujours fonctionnel.

## 1. Principes du projet

- **Source unique** : toute réponse de l'outil remonte à un document de la base.
- **Traçabilité** : calculs déterministes + citations. Jamais de valeur de dimensionnement inventée par le LLM.
- **Humain dans la boucle** : toute note générée est validée par un ingénieur.
- **Secrets protégés** : aucun fichier `.env`, clé API, base `.db` ou modèle volumineux n'est commité.

## 2. Workflow Git (branches)

On utilise un modèle simple **branche par fonctionnalité** :

```text
main          ← branche stable, protégée (jamais de push direct)
  └─ dev      ← branche d'intégration (les PR sont fusionnées ici en premier)
       ├─ feat/rag-recherche-hybride      (Abid)
       ├─ feat/verif-ndc-plan             (Houssem)
       ├─ feat/ingestion-ifc              (Bara)
       └─ feat/generation-trame-word      (Nour)
```

**Convention de nommage des branches :**

| Préfixe | Usage | Exemple |
|---------|-------|---------|
| `feat/` | nouvelle fonctionnalité | `feat/endpoint-compliance-check` |
| `fix/` | correction de bug | `fix/citation-page-manquante` |
| `docs/` | documentation | `docs/guide-ingestion` |
| `refactor/` | refonte sans changement de comportement | `refactor/vector-store` |
| `test/` | ajout/correction de tests | `test/compliance-checker` |

## 3. Cycle de travail

1. `git checkout dev && git pull`
2. Créer sa branche : `git checkout -b feat/ma-fonctionnalite`
3. Coder + **tester en local** (`pytest` côté Backend, `npm run build` côté Frontend).
4. Commits clairs (voir convention ci-dessous).
5. `git push -u origin feat/ma-fonctionnalite`
6. Ouvrir une **Pull Request vers `dev`** (jamais directement vers `main`).
7. Au moins **1 review** (le binôme ou Amine) avant fusion.

## 4. Convention de commits

Format : `<type>: <description courte à l'impératif>`

```text
feat: ajoute l'endpoint /compliance-check
fix: corrige l'extraction de hauteur dans telecom_doc_processor
docs: complète le README d'ingestion
test: couvre le scoring de conformité Eurocode
```

Types : `feat`, `fix`, `docs`, `test`, `refactor`, `chore`.

## 5. Pull Requests

- Remplir le template de PR (description, ce qui est testé, captures si UI).
- Une PR = une fonctionnalité cohérente (éviter les PR géantes).
- Ne pas fusionner si : tests cassés, implémentation partielle, secrets exposés.
- Lier la PR à une issue quand c'est possible (`Closes #12`).

## 6. À ne JAMAIS commiter

- `.env`, `.env.local`, `.env.production` et toute clé API
- Bases de données : `*.db`, `*.sqlite3`, dossiers `data/chroma/`
- Environnements : `.venv/`, `node_modules/`, `__pycache__/`
- Logs, sauvegardes, certificats (`*.log`, `*.bak`, `*.pem`, `*.key`)
- Documents projets BIMLO réels (notes de calcul, plans) — **confidentiels**

Le `.gitignore` couvre ces cas ; vérifier `git status` avant chaque commit.

## 7. Qualité

- **Backend** : `pytest` doit passer ; respecter le style du code existant (type hints, docstrings).
- **Frontend** : `npm run lint` et `npm run build` sans erreur.
- La CI (`.github/workflows/ci.yml`) tourne à chaque PR — elle doit être verte avant fusion.

## 8. Questions

En cas de doute sur l'architecture ou un calcul d'ingénierie : demander à **Amine** (référent).
Le LLM ne décide jamais d'une valeur de dimensionnement — c'est l'ingénieur qui valide.
