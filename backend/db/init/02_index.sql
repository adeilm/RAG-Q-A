-- =============================================================================
-- Module M2 — Index pour des requêtes rapides
-- =============================================================================
-- Auto-executed after 01_init.sql by the postgres container (both live in
-- /docker-entrypoint-initdb.d and run in filename order).
-- =============================================================================

-- Trigram extension for fast substring search (nom ILIKE '%MARSEILLE%')
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- projets
CREATE INDEX IF NOT EXISTS idx_projets_statut     ON projets(statut);
CREATE INDEX IF NOT EXISTS idx_projets_nom_trgm   ON projets USING gin (nom gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_projets_client     ON projets(client);

-- pylones (height/type are the hybrid-search filter columns)
CREATE INDEX IF NOT EXISTS idx_pylones_projet_id  ON pylones(projet_id);
CREATE INDEX IF NOT EXISTS idx_pylones_etat       ON pylones(etat);
CREATE INDEX IF NOT EXISTS idx_pylones_hauteur    ON pylones(hauteur_m);
CREATE INDEX IF NOT EXISTS idx_pylones_type_trgm  ON pylones USING gin (type_pylone gin_trgm_ops);

-- notes_de_calcul (+ GIN on JSONB donnees_extraites for structured filtering)
CREATE INDEX IF NOT EXISTS idx_ndc_projet_id      ON notes_de_calcul(projet_id);
CREATE INDEX IF NOT EXISTS idx_ndc_pylone_id      ON notes_de_calcul(pylone_id);
CREATE INDEX IF NOT EXISTS idx_ndc_contenu_gin    ON notes_de_calcul USING gin (contenu_extrait);

-- plans
CREATE INDEX IF NOT EXISTS idx_plans_projet_id    ON plans(projet_id);
CREATE INDEX IF NOT EXISTS idx_plans_pylone_id    ON plans(pylone_id);
CREATE INDEX IF NOT EXISTS idx_plans_type_plan    ON plans(type_plan);

-- elements_structure
CREATE INDEX IF NOT EXISTS idx_elements_pylone_id ON elements_structure(pylone_id);
CREATE INDEX IF NOT EXISTS idx_elements_type      ON elements_structure(type_element);
CREATE INDEX IF NOT EXISTS idx_elements_profil    ON elements_structure(profil);
CREATE INDEX IF NOT EXISTS idx_elements_pyl_type  ON elements_structure(pylone_id, type_element);

-- anomalies
CREATE INDEX IF NOT EXISTS idx_anomalies_projet_id ON anomalies(projet_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_severite  ON anomalies(severite);
CREATE INDEX IF NOT EXISTS idx_anomalies_statut    ON anomalies(statut);
CREATE INDEX IF NOT EXISTS idx_anomalies_ouvertes  ON anomalies(projet_id, severite) WHERE statut = 'ouverte';
