-- =============================================================================
-- Module M2 — Schéma initial PostgreSQL (Projet TOWERMIND/BIMLO)
-- =============================================================================
-- Canonical schema owned by Mohamed (schema_sql/01_init.sql in the private test
-- dataset). This tracked copy contains the 6 tables ONLY — the demo INSERT rows
-- from the original were removed on purpose so they don't collide (UNIQUE
-- code_projet) with the real project JSON ingested by scripts/ingest_json.py.
--
-- Auto-executed by the postgres container on first boot via the volume mounted
-- on /docker-entrypoint-initdb.d.
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Table 1/6 : projets
CREATE TABLE IF NOT EXISTS projets (
    id              SERIAL PRIMARY KEY,
    code_projet     VARCHAR(50)  UNIQUE NOT NULL,
    nom             VARCHAR(255) NOT NULL,
    client          VARCHAR(255),
    localisation    VARCHAR(255),
    statut          VARCHAR(50) DEFAULT 'en_cours',
    description     TEXT,
    date_creation   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_maj        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2/6 : pylones
CREATE TABLE IF NOT EXISTS pylones (
    id                      SERIAL PRIMARY KEY,
    projet_id               INTEGER NOT NULL REFERENCES projets(id) ON DELETE CASCADE,
    nom                     VARCHAR(255) NOT NULL,
    type_pylone             VARCHAR(50),
    hauteur_m               NUMERIC(6, 2),
    charge_admissible_kn    NUMERIC(10, 2),
    date_installation       DATE,
    etat                    VARCHAR(50) DEFAULT 'a_verifier',
    date_creation           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 3/6 : notes_de_calcul
CREATE TABLE IF NOT EXISTS notes_de_calcul (
    id                      SERIAL PRIMARY KEY,
    projet_id               INTEGER NOT NULL REFERENCES projets(id) ON DELETE CASCADE,
    pylone_id               INTEGER REFERENCES pylones(id) ON DELETE SET NULL,
    nom_fichier             VARCHAR(255) NOT NULL,
    chemin_fichier          TEXT,
    version                 VARCHAR(20),
    ingenieur_responsable   VARCHAR(255),
    contenu_extrait         JSONB,
    date_creation           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 4/6 : plans
CREATE TABLE IF NOT EXISTS plans (
    id              SERIAL PRIMARY KEY,
    projet_id       INTEGER NOT NULL REFERENCES projets(id) ON DELETE CASCADE,
    pylone_id       INTEGER REFERENCES pylones(id) ON DELETE SET NULL,
    nom_fichier     VARCHAR(255) NOT NULL,
    chemin_fichier  TEXT,
    type_plan       VARCHAR(50),
    echelle         VARCHAR(20),
    nombre_pages    INTEGER,
    contenu_extrait JSONB,
    date_creation   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 5/6 : elements_structure
CREATE TABLE IF NOT EXISTS elements_structure (
    id              SERIAL PRIMARY KEY,
    pylone_id       INTEGER NOT NULL REFERENCES pylones(id) ON DELETE CASCADE,
    reference       VARCHAR(100),
    type_element    VARCHAR(50),
    designation     VARCHAR(255),
    profil          VARCHAR(100),
    longueur_mm     NUMERIC(10, 2),
    masse_kg        NUMERIC(10, 3),
    quantite        INTEGER DEFAULT 1,
    materiau        VARCHAR(50),
    position        JSONB,
    source          VARCHAR(50),
    date_creation   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 6/6 : anomalies
CREATE TABLE IF NOT EXISTS anomalies (
    id              SERIAL PRIMARY KEY,
    projet_id       INTEGER NOT NULL REFERENCES projets(id) ON DELETE CASCADE,
    element_id      INTEGER REFERENCES elements_structure(id) ON DELETE SET NULL,
    type_anomalie   VARCHAR(100) NOT NULL,
    severite        VARCHAR(20) DEFAULT 'moyenne',
    description     TEXT NOT NULL,
    detectee_par    VARCHAR(50),
    statut          VARCHAR(50) DEFAULT 'ouverte',
    date_detection  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_resolution TIMESTAMP
);
