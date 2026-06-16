import sqlite3
import time
import os
import queries

DB_PATH = "imdb.db"

def timer(fn):
    t1 = time.perf_counter()
    fn()
    t2 = time.perf_counter()
    return (t2 - t1) * 1000


def explain_query(conn, sql, params=()):
    """
    Retourne les lignes EXPLAIN QUERY PLAN pour une requête donnée.
    """
    explain_sql = "EXPLAIN QUERY PLAN " + sql
    cur = conn.execute(explain_sql, params)
    return cur.fetchall()


def sizeof_db(path):
    if os.path.exists(path):
        return os.path.getsize(path)
    return 0


def run_benchmark():

    conn = sqlite3.connect(DB_PATH)

    # Liste des requêtes avec appel Python et SQL brut pour EXPLAIN
    QUERIES = [
        ("Q1 Filmography",
         lambda: queries.q1_actor_filmography(conn, "Tom Hanks"),
         """
         SELECT m.title, m.year, ch.character_name, r.averageRating
         FROM movies m
         JOIN principals pr ON m.movie_id = pr.movie_id
         JOIN persons p ON pr.person_id = p.person_id
         LEFT JOIN characters ch
             ON ch.movie_id = m.movie_id AND ch.person_id = p.person_id
         LEFT JOIN ratings r ON r.movie_id = m.movie_id
         WHERE p.primaryName LIKE '%Tom Hanks%'
         ORDER BY m.year DESC;
         """),

        ("Q2 Top N genre",
         lambda: queries.q2_top_n_genre(conn, "Drama", 1990, 2020, 10),
         """
         SELECT m.title, m.year, r.averageRating
         FROM movies m
         JOIN ratings r ON m.movie_id = r.movie_id
         JOIN genres g ON m.movie_id = g.movie_id
         WHERE g.genre = 'Drama'
           AND m.year BETWEEN 1990 AND 2020
         ORDER BY r.averageRating DESC
         LIMIT 10;
         """),

        ("Q3 Multi-roles",
         lambda: queries.q3_multi_roles(conn),
         """
         SELECT p.primaryName, m.title, COUNT(*) AS nb_roles
         FROM characters c
         JOIN persons p ON c.person_id = p.person_id
         JOIN movies m ON c.movie_id = m.movie_id
         GROUP BY c.movie_id, c.person_id
         HAVING nb_roles > 1
         ORDER BY nb_roles DESC;
         """),

        ("Q4 Collaborations",
         lambda: queries.q4_collaborations(conn, "Tom Hanks"),
         """
         SELECT d.primaryName AS director, COUNT(*) AS films
         FROM principals pr
         JOIN persons a ON pr.person_id = a.person_id
         JOIN directors dr ON pr.movie_id = dr.movie_id
         JOIN persons d ON dr.person_id = d.person_id
         WHERE pr.category IN ('actor', 'actress')
           AND a.primaryName LIKE '%Tom Hanks%'
         GROUP BY d.person_id
         ORDER BY films DESC;
         """),

        ("Q5 Popular Genres",
         lambda: queries.q5_popular_genres(conn),
         """
         SELECT g.genre, AVG(r.averageRating) AS avg_rating, COUNT(*) AS nb_films
         FROM genres g
         JOIN ratings r ON g.movie_id = r.movie_id
         GROUP BY g.genre
         HAVING nb_films > 50 AND avg_rating > 7
         ORDER BY avg_rating DESC;
         """),

        ("Q6 Career Decades",
         lambda: queries.q6_career_decades(conn, "Tom Hanks"),
         """
         WITH films AS (
             SELECT m.year AS year, r.averageRating AS rating
             FROM principals pr
             JOIN persons p ON pr.person_id = p.person_id
             JOIN movies m ON pr.movie_id = m.movie_id
             LEFT JOIN ratings r ON r.movie_id = m.movie_id
             WHERE p.primaryName LIKE '%Tom Hanks%'
         )
         SELECT (year/10)*10 AS decade, COUNT(*) AS nb_films, AVG(rating)
         FROM films
         GROUP BY decade
         ORDER BY decade;
         """),

        ("Q7 Rank Genres",
         lambda: queries.q7_rank_genres(conn),
         """
         SELECT genre, title, averageRating, rank
         FROM (
             SELECT g.genre,
                    m.title,
                    r.averageRating,
                    ROW_NUMBER() OVER (
                        PARTITION BY g.genre
                        ORDER BY r.averageRating DESC
                    ) AS rank
             FROM genres g
             JOIN movies m ON g.movie_id = m.movie_id
             JOIN ratings r ON g.movie_id = r.movie_id
         )
         WHERE rank <= 3;
         """),

        ("Q8 Breakthrough",
         lambda: queries.q8_breakthrough(conn),
         """
         SELECT p.primaryName
         FROM persons p
         JOIN principals pr ON p.person_id = pr.person_id
         JOIN ratings r ON pr.movie_id = r.movie_id
         GROUP BY p.person_id
         HAVING SUM(r.numVotes < 200000) > 0
            AND SUM(r.numVotes > 200000) > 0;
         """),

        ("Q9 Multiskill",
         lambda: queries.q9_multiskill(conn),
         """
         SELECT p.primaryName, COUNT(*) AS nb_films
         FROM persons p
         JOIN principals pr ON p.person_id = pr.person_id
         JOIN directors d ON p.person_id = d.person_id
         GROUP BY p.person_id
         HAVING nb_films >= 3
         ORDER BY nb_films DESC;
         """)
    ]

    # Taille initiale du fichier
    size_before = sizeof_db(DB_PATH)

    # --- 1 Exécution sans index ---
    print("=== Benchmark sans index ===")
    times_no_index = []
    explains_no_index = []

    for name, fn, sql in QUERIES:
        ms = timer(fn)
        times_no_index.append(ms)

        # Collecte EXPLAIN
        expl = explain_query(conn, sql)
        explains_no_index.append(expl)

        print(f"{name}: {ms:.2f} ms")


    # --- 3 Ajout des index ---
    conn.executescript("""
        CREATE INDEX IF NOT EXISTS idx_principals_movie ON principals(movie_id);
        CREATE INDEX IF NOT EXISTS idx_principals_person ON principals(person_id);
        CREATE INDEX IF NOT EXISTS idx_genres_movie ON genres(movie_id);
        CREATE INDEX IF NOT EXISTS idx_titles_movie ON titles(movie_id);
        CREATE INDEX IF NOT EXISTS idx_ratings_rating ON ratings(averageRating);
        CREATE INDEX IF NOT EXISTS idx_movies_year ON movies(year);
        CREATE INDEX IF NOT EXISTS idx_persons_name ON persons(primaryName);
        CREATE INDEX IF NOT EXISTS idx_characters_movie ON characters(movie_id);
        CREATE INDEX IF NOT EXISTS idx_characters_person ON characters(person_id);
        CREATE INDEX IF NOT EXISTS idx_knownfor_person ON known_for(person_id);
    """)

    # --- Taille après index ---
    size_after = sizeof_db(DB_PATH)

    # --- 4 Exécution avec index ---
    print("\n=== Benchmark avec index ===")
    times_with_index = []
    explains_with_index = []

    for name, fn, sql in QUERIES:
        ms = timer(fn)
        times_with_index.append(ms)

        expl = explain_query(conn, sql)
        explains_with_index.append(expl)

        print(f"{name}: {ms:.2f} ms")


    # --- 5 Comparaison finale ---
    print("\n=== Tableau comparatif ===")
    for (name, _, _), t1, t2 in zip(QUERIES, times_no_index, times_with_index):
        gain = (1 - t2/t1) * 100
        print(f"{name}: {t1:.2f} ms → {t2:.2f} ms (gain = {gain:.1f}%)")


    print("\n=== Taille de la base ===")
    print(f"Avant index : {size_before/1024:.2f} KB")
    print(f"Après index : {size_after/1024:.2f} KB")
    print(f"Augmentation : {(size_after - size_before)/1024:.2f} KB")

    conn.close()


if __name__ == "__main__":
    run_benchmark()
