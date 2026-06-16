import sqlite3
import os

def create_schema():
    # Détection de la racine (identique à import_data.py)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(script_dir))
    db_path = os.path.join(root_dir, "data", "imdb.db")
    print(f"Création des tables dans : {db_path}")
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.executescript("""
    PRAGMA foreign_keys = OFF;

    DROP TABLE IF EXISTS characters;
    DROP TABLE IF EXISTS known_for;
    DROP TABLE IF EXISTS titles;
    DROP TABLE IF EXISTS writers;
    DROP TABLE IF EXISTS directors;
    DROP TABLE IF EXISTS genres;
    DROP TABLE IF EXISTS principals;
    DROP TABLE IF EXISTS professions;
    DROP TABLE IF EXISTS ratings;
    DROP TABLE IF EXISTS persons;
    DROP TABLE IF EXISTS movies;

    PRAGMA foreign_keys = ON;

    CREATE TABLE movies (
        movie_id TEXT PRIMARY KEY,
        titleType TEXT,
        primaryTitle TEXT,
        originalTitle TEXT,
        isAdult INTEGER,
        startYear INTEGER,
        endYear INTEGER,
        runtimeMinutes INTEGER
    );

    CREATE TABLE persons (
        person_id TEXT PRIMARY KEY,
        primaryName TEXT,
        birthYear INTEGER,
        deathYear INTEGER
    );

    CREATE TABLE ratings (
        movie_id TEXT PRIMARY KEY,
        averageRating REAL,
        numVotes INTEGER,
        FOREIGN KEY(movie_id) REFERENCES movies(movie_id)
    );

    CREATE TABLE genres (
        movie_id TEXT,
        genre TEXT,
        PRIMARY KEY (movie_id, genre),
        FOREIGN KEY(movie_id) REFERENCES movies(movie_id)
    );

    CREATE TABLE directors (
        movie_id TEXT,
        person_id TEXT,
        PRIMARY KEY(movie_id, person_id),
        FOREIGN KEY(movie_id) REFERENCES movies(movie_id),
        FOREIGN KEY(person_id) REFERENCES persons(person_id)
    );

    CREATE TABLE writers (
        movie_id TEXT,
        person_id TEXT,
        PRIMARY KEY(movie_id, person_id),
        FOREIGN KEY(movie_id) REFERENCES movies(movie_id),
        FOREIGN KEY(person_id) REFERENCES persons(person_id)
    );

    CREATE TABLE titles (
        movie_id TEXT,
        ordering INTEGER,
        title TEXT,
        region TEXT,
        language TEXT,
        types TEXT,
        attributes TEXT,
        isOriginalTitle INTEGER,
        PRIMARY KEY(movie_id, ordering),
        FOREIGN KEY(movie_id) REFERENCES movies(movie_id)
    );

    CREATE TABLE principals (
        movie_id TEXT,
        ordering INTEGER,
        person_id TEXT,
        category TEXT,
        job TEXT,
        PRIMARY KEY(movie_id, ordering, person_id),
        FOREIGN KEY(movie_id) REFERENCES movies(movie_id),
        FOREIGN KEY(person_id) REFERENCES persons(person_id)
    );

    CREATE TABLE professions (
        person_id TEXT,
        jobName TEXT,
        PRIMARY KEY(person_id, jobName),
        FOREIGN KEY(person_id) REFERENCES persons(person_id)
    );

    CREATE TABLE characters (
        movie_id TEXT,
        person_id TEXT,
        name TEXT,
        FOREIGN KEY(movie_id) REFERENCES movies(movie_id),
        FOREIGN KEY(person_id) REFERENCES persons(person_id)
    );

    CREATE TABLE known_for (
        person_id TEXT,
        movie_id TEXT,
        PRIMARY KEY(person_id, movie_id),
        FOREIGN KEY(person_id) REFERENCES persons(person_id),
        FOREIGN KEY(movie_id) REFERENCES movies(movie_id)
    );
    """)
    
    conn.commit()
    conn.close()
    print("✅ Schéma créé avec succès.")

if __name__ == "__main__":
    create_schema()