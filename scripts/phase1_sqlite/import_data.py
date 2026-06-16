import os
import csv
import sqlite3

# Trouve la racine du projet "cineexplorer" peu importe d'où on lance le script
# scripts/phaseX/script.py -> remonte de 2 niveaux pour arriver à la racine
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(script_dir))
db_path = os.path.join(root_dir, "imdb.db") # On le met à la racine pour simplifier

def import_csv(conn, table, path, columns):
    cur = conn.cursor()
    if not os.path.exists(path):
        print(f"❌ Fichier introuvable : {path}")
        return

    with open(path, encoding="utf-8") as f:
        # On lit la 1ère ligne pour nettoyer les headers CSV bizarres
        reader = csv.reader(f)
        raw_headers = next(reader)
        clean_headers = [h.replace("(", "").replace(")", "").replace("'", "").replace(",", "").strip() for h in raw_headers]
        
        # Correspondance entre vos noms SQL et les noms CSV (si différent)
        mapping = {"movie_id": "mid", "person_id": "pid"}
        
        # On trouve l'index de chaque colonne demandée
        indices = []
        for col in columns:
            target = mapping.get(col, col)
            if target in clean_headers:
                indices.append(clean_headers.index(target))
            else:
                print(f"⚠️ Colonne {target} absente de {path}")
                return

        rows = []
        for row in reader:
            # On extrait les données par index
            values = [row[i] if row[i] not in ("", "\\N") else None for i in indices]
            rows.append(values)

        placeholder = ",".join(["?"] * len(columns))
        sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholder})"
        cur.executemany(sql, rows)
        conn.commit()
        print(f"✅ {table}: {len(rows)} lignes insérées")

def import_all():
    # --- LOGIQUE DE CHEMIN AUTOMATIQUE ---
    # On trouve le dossier racine du projet (3 niveaux au-dessus de ce script)
    # scripts/phase1_sqlite/import_data.py -> cineexplorer/
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    db_path = os.path.join(base_dir, "data\imdb.db")
    csv_dir = os.path.join(base_dir, "data", "csv")

    print(f"Base de données : {db_path}")
    print(f"Dossier CSV : {csv_dir}\n")

    conn = sqlite3.connect(db_path)

    # Liste des imports (Ordre important pour les clés étrangères)
    import_csv(conn, "movies", os.path.join(csv_dir, "movies.csv"),
           ["movie_id", "titleType", "primaryTitle", "originalTitle", "isAdult", "startYear", "endYear", "runtimeMinutes"])

    import_csv(conn, "persons", os.path.join(csv_dir, "persons.csv"),
               ["person_id","primaryName","birthYear","deathYear"])

    import_csv(conn, "ratings", os.path.join(csv_dir, "ratings.csv"),
               ["movie_id","averageRating","numVotes"])

    import_csv(conn, "genres", os.path.join(csv_dir, "genres.csv"),
               ["movie_id","genre"])

    import_csv(conn, "directors", os.path.join(csv_dir, "directors.csv"),
               ["movie_id","person_id"])

    import_csv(conn, "writers", os.path.join(csv_dir, "writers.csv"),
               ["movie_id","person_id"])

    import_csv(conn, "titles", os.path.join(csv_dir, "titles.csv"),
               ["movie_id","ordering","title","region","language",
                "types","attributes","isOriginalTitle"])

    import_csv(conn, "principals", os.path.join(csv_dir, "principals.csv"),
               ["movie_id","ordering","person_id","category","job"])

    import_csv(conn, "professions", os.path.join(csv_dir, "professions.csv"),
               ["person_id","jobName"])

    import_csv(conn, "characters", os.path.join(csv_dir, "characters.csv"),
           ["movie_id", "person_id", "name"])

    # Attention au nom du fichier ici, parfois c'est "knownformovies.csv"
    import_csv(conn, "known_for", os.path.join(csv_dir, "knownformovies.csv"),
               ["person_id","movie_id"])

    conn.close()
    print("\nImportation terminée.")

if __name__ == "__main__":
    import_all()