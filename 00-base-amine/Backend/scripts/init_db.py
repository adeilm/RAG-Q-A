import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'bimlo_projects.db')

def init_db():
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    print(f"Initialising database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Table 1: projets
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code_projet TEXT UNIQUE NOT NULL,
        nom TEXT NOT NULL,
        client TEXT,
        localisation TEXT,
        statut TEXT DEFAULT 'en_cours',
        description TEXT,
        date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
        date_maj DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Table 2: pylones
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pylones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        projet_id INTEGER NOT NULL REFERENCES projets(id) ON DELETE CASCADE,
        nom TEXT NOT NULL,
        type_pylone TEXT,
        hauteur_m REAL,
        charge_admissible_kn REAL,
        date_installation DATE,
        etat TEXT DEFAULT 'a_verifier',
        date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Table 3: notes_de_calcul
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notes_de_calcul (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        projet_id INTEGER NOT NULL REFERENCES projets(id) ON DELETE CASCADE,
        pylone_id INTEGER REFERENCES pylones(id) ON DELETE SET NULL,
        nom_fichier TEXT NOT NULL,
        chemin_fichier TEXT,
        version TEXT,
        ingenieur_responsable TEXT,
        contenu_extrait TEXT, -- Stored as JSON string
        date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Table 4: plans
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        projet_id INTEGER NOT NULL REFERENCES projets(id) ON DELETE CASCADE,
        pylone_id INTEGER REFERENCES pylones(id) ON DELETE SET NULL,
        nom_fichier TEXT NOT NULL,
        chemin_fichier TEXT,
        type_plan TEXT,
        echelle TEXT,
        nombre_pages INTEGER,
        contenu_extrait TEXT, -- Stored as JSON string
        date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Table 5: elements_structure
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS elements_structure (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        projet_id INTEGER NOT NULL REFERENCES projets(id) ON DELETE CASCADE,
        pylone_id INTEGER REFERENCES pylones(id) ON DELETE SET NULL,
        reference TEXT NOT NULL,
        profil TEXT,
        longueur_mm REAL,
        masse_kg REAL,
        quantite INTEGER DEFAULT 1,
        materiau TEXT,
        source TEXT,
        date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Table 6: anomalies
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS anomalies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        projet_id INTEGER NOT NULL REFERENCES projets(id) ON DELETE CASCADE,
        pylone_id INTEGER REFERENCES pylones(id) ON DELETE SET NULL,
        type_anomalie TEXT NOT NULL,
        gravite TEXT,
        description TEXT,
        statut TEXT DEFAULT 'ouverte',
        date_detection DATE,
        date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("Database initialised successfully.")

if __name__ == "__main__":
    init_db()
