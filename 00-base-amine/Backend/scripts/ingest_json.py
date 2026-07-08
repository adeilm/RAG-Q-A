import os
import sys
import json
import sqlite3
import glob

# Ensure we can import from Backend.services
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.vector_store import VectorStoreManager
from services.document_processor import DocumentProcessor

JSON_DIR = "/app/data/donnees_json"
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'bimlo_projects.db'))

def run_ingestion():
    print("🚀 Starting JSON ingestion pipeline...")
    
    # 1. Connect to SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 2. Init Vector Store & Chunking
    vs = VectorStoreManager()
    dp = DocumentProcessor(chunk_size=1000, chunk_overlap=200)

    # 3. Process JSON files
    json_files = glob.glob(os.path.join(JSON_DIR, "*.json"))
    
    for filepath in json_files:
        filename = os.path.basename(filepath)
        if filename.startswith('_'): 
            continue # skip _resume.json or hidden
            
        print(f"📄 Processing: {filename}")
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        projet = data.get("projet", {})
        if not projet:
            continue
            
        # -- SQL INSERT PROJECT --
        code_projet = projet.get("code_projet")
        cursor.execute("SELECT id FROM projets WHERE code_projet=?", (code_projet,))
        row = cursor.fetchone()
        if row:
            print(f"   Project {code_projet} already exists. Skipping.")
            continue
            
        cursor.execute('''
            INSERT INTO projets (code_projet, nom, client, localisation, statut, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (code_projet, projet.get("nom"), projet.get("client"), projet.get("localisation"), projet.get("statut"), projet.get("description")))
        projet_id = cursor.lastrowid
        
        # -- SQL INSERT PYLONES --
        pylones = data.get("pylones", [])
        for pyl in pylones:
            cursor.execute('''
                INSERT INTO pylones (projet_id, nom, type_pylone, hauteur_m, charge_admissible_kn, date_installation, etat)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (projet_id, pyl.get("nom"), pyl.get("type_pylone"), pyl.get("hauteur_m"), pyl.get("charge_admissible_kn"), pyl.get("date_installation"), pyl.get("etat")))
            
        # -- SQL & CHROMA INSERT NOTES DE CALCUL --
        ncs = data.get("notes_de_calcul", [])
        for nc in ncs:
            nom_fichier = nc.get("nom_fichier", "NC")
            donnees_extraites = nc.get("donnees_extraites", {})
            texte_complet = nc.get("texte_complet", "")
            
            cursor.execute('''
                INSERT INTO notes_de_calcul (projet_id, nom_fichier, chemin_fichier, version, ingenieur_responsable, contenu_extrait)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (projet_id, nom_fichier, nc.get("chemin_fichier"), nc.get("version"), nc.get("ingenieur_responsable"), json.dumps(donnees_extraites)))
            
            if texte_complet:
                meta = {
                    "project_name": projet.get("nom", ""),
                    "site_id": code_projet,
                    "doc_type": "note_de_calcul",
                    "filename": nom_fichier
                }
                chunks = dp._create_chunks(texte_complet, meta)
                vs.add_document(filename=nom_fichier, chunks=chunks)
                
        # -- SQL & CHROMA INSERT PLANS --
        plans = data.get("plans", [])
        for plan in plans:
            nom_fichier = plan.get("nom_fichier", "PLAN")
            texte_complet = plan.get("texte_complet", "")
            
            cursor.execute('''
                INSERT INTO plans (projet_id, nom_fichier, chemin_fichier, type_plan, echelle, nombre_pages, contenu_extrait)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (projet_id, nom_fichier, plan.get("chemin_fichier"), plan.get("type_plan"), plan.get("echelle"), plan.get("nombre_pages"), "{}"))
            
            if texte_complet:
                meta = {
                    "project_name": projet.get("nom", ""),
                    "site_id": code_projet,
                    "doc_type": "plan",
                    "filename": nom_fichier
                }
                chunks = dp._create_chunks(texte_complet, meta)
                vs.add_document(filename=nom_fichier, chunks=chunks)

    conn.commit()
    conn.close()
    print("✅ Ingestion complete.")

if __name__ == "__main__":
    run_ingestion()
