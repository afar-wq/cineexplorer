import sqlite3
import time
import os
import sys
from pymongo import MongoClient

# --- CONFIGURATION DES CHEMINS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
phase1_dir = os.path.join(os.path.dirname(current_dir), "phase1_sqlite")

sys.path.append(current_dir)
sys.path.append(phase1_dir)

try:
    import queries        # SQL Phase 1
    import queries_mongo  # MongoDB Phase 2
    print("✅ Modules de requêtes chargés.")
except ImportError as e:
    print(f"❌ Erreur d'import : {e}")
    sys.exit(1)

def benchmark():
    # Connexion SQLite
    root_dir = os.path.dirname(os.path.dirname(current_dir))
    db_path = os.path.join(root_dir, "data", "imdb.db")
    conn_sql = sqlite3.connect(db_path)
    
    # Connexion MongoDB
    client_mongo = MongoClient("mongodb://127.0.0.1:27017/")
    db_mongo = client_mongo["imdb_flat"]

    # --- LISTE COMPLÈTE DES 9 TESTS ---
    # Format : (Nom, Fonction_SQL, Fonction_Mongo, Arguments)
    tests = [
        ("Q1 Filmographie", queries.q1_actor_filmography, queries_mongo.q1_actor_filmography, ("Tom Hanks",)),
        ("Q2 Top N Genre", queries.q2_top_n_genre, queries_mongo.q2_top_n_genre, ("Drama", 1990, 2020, 10)),
        ("Q3 Multi-roles", queries.q3_multi_roles, queries_mongo.q3_multi_roles, ()),
        ("Q4 Collaborations", queries.q4_collaborations, queries_mongo.q4_collaborations, ("Tom Hanks",)),
        ("Q5 Popular Genres", queries.q5_popular_genres, queries_mongo.q5_popular_genres, ()),
        ("Q6 Career Decades", queries.q6_career_decades, queries_mongo.q6_career_decades, ("Tom Hanks",)),
        ("Q7 Rank Genres", queries.q7_rank_genres, queries_mongo.q7_rank_genres, ()),
        ("Q8 Breakthrough", queries.q8_breakthrough, queries_mongo.q8_breakthrough, ()),
        ("Q9 Multiskill", queries.q9_multiskill, queries_mongo.q9_multiskill, ()),
    ]

    print(f"\n{'Requête':<20} | {'SQLite (ms)':<15} | {'MongoDB (ms)':<15} | {'Ratio'}")
    print("-" * 70)

    for name, fn_sql, fn_mongo, args in tests:
        try:
            # Benchmark SQLite
            start_sql = time.perf_counter()
            fn_sql(conn_sql, *args)
            t_sql = (time.perf_counter() - start_sql) * 1000

            # Benchmark MongoDB
            start_mongo = time.perf_counter()
            fn_mongo(db_mongo, *args)
            t_mongo = (time.perf_counter() - start_mongo) * 1000

            ratio = t_mongo / t_sql if t_sql > 0 else 0
            print(f"{name:<20} | {t_sql:>13.2f} | {t_mongo:>13.2f} | x{ratio:.1f}")
        
        except Exception as e:
            print(f"{name:<20} | ERREUR : {e}")

    conn_sql.close()
    client_mongo.close()

if __name__ == "__main__":
    print("Démarrage du benchmark comparatif SQL vs MongoDB...")
    benchmark()