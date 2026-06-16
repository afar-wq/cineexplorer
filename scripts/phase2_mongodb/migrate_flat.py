import sqlite3
import os
from pymongo import MongoClient

def migrate_flat():
    # --- CONFIGURATION DES CHEMINS ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # On remonte de scripts/phase2_mongodb vers la racine, puis dans data/
    root_dir = os.path.dirname(os.path.dirname(script_dir))
    db_path = os.path.join(root_dir, "data", "imdb.db")

    if not os.path.exists(db_path):
        print(f"❌ Erreur : La base SQLite est introuvable à : {db_path}")
        return

    # --- CONNEXIONS ---
    sqlite_conn = sqlite3.connect(db_path)
    sqlite_conn.row_factory = sqlite3.Row # Permet de récupérer les lignes sous forme de dictionnaires
    
    mongo_client = MongoClient("mongodb://127.0.0.1:27017/")
    db = mongo_client["imdb_flat"] # Nom de ta base MongoDB

    # Liste de toutes tes tables SQLite
    tables = [
        "movies", "persons", "ratings", "genres", "directors", 
        "writers", "titles", "principals", "professions", "characters", "known_for"
    ]

    print(f"--- Début de la migration vers MongoDB ---")

    for table in tables:
        print(f"Migration de {table}...")
        try:
            cursor = sqlite_conn.execute(f"SELECT * FROM {table}")
            
            # On récupère toutes les lignes et on les transforme en dictionnaires Python
            rows = [dict(row) for row in cursor.fetchall()]
            
            if rows:
                db[table].drop() # On vide la collection avant d'importer
                db[table].insert_many(rows)
                print(f" ✅ {len(rows)} documents insérés dans la collection '{table}'.")
            else:
                print(f" ⚠️ Table '{table}' vide dans SQLite, rien à migrer.")
        
        except sqlite3.OperationalError as e:
            print(f" ❌ Erreur sur la table {table} : {e}")

    mongo_client.close()
    sqlite_conn.close()
    print(f"\n--- Migration terminée avec succès ! ---")

if __name__ == "__main__":
    migrate_flat()