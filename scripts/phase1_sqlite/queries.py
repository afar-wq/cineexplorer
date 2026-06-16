import sqlite3

def q1_actor_filmography(conn, actor_name):
    sql = """
    SELECT m.primaryTitle, m.startYear, ch.name, r.averageRating
    FROM movies m
    JOIN principals pr ON m.movie_id = pr.movie_id
    JOIN persons p ON pr.person_id = p.person_id
    LEFT JOIN characters ch
        ON ch.movie_id = m.movie_id AND ch.person_id = p.person_id
    LEFT JOIN ratings r ON r.movie_id = m.movie_id
    WHERE p.primaryName LIKE ?
    ORDER BY m.startYear DESC;
    """
    return conn.execute(sql, (f"%{actor_name}%",)).fetchall()


def q2_top_n_genre(conn, genre, y1, y2, N):
    sql = """
    SELECT m.primaryTitle, m.startYear, r.averageRating
    FROM movies m
    JOIN ratings r ON m.movie_id = r.movie_id
    JOIN genres g ON m.movie_id = g.movie_id
    WHERE g.genre = ?
      AND m.startYear BETWEEN ? AND ?
    ORDER BY r.averageRating DESC
    LIMIT ?;
    """
    return conn.execute(sql, (genre, y1, y2, N)).fetchall()


def q3_multi_roles(conn):
    sql = """
    SELECT p.primaryName, m.primaryTitle, COUNT(*) AS nb_roles
    FROM characters c
    JOIN persons p ON c.person_id = p.person_id
    JOIN movies m ON c.movie_id = m.movie_id
    GROUP BY c.movie_id, c.person_id
    HAVING nb_roles > 1
    ORDER BY nb_roles DESC;
    """
    return conn.execute(sql).fetchall()


def q4_collaborations(conn, actor_name):
    sql = """
    SELECT d.primaryName AS director, COUNT(*) AS films
    FROM principals pr
    JOIN persons a ON pr.person_id = a.person_id
    JOIN directors dr ON pr.movie_id = dr.movie_id
    JOIN persons d ON dr.person_id = d.person_id
    WHERE pr.category IN ('actor','actress')
      AND a.primaryName LIKE ?
    GROUP BY d.person_id
    ORDER BY films DESC;
    """
    return conn.execute(sql, (f"%{actor_name}%",)).fetchall()


def q5_popular_genres(conn):
    sql = """
    SELECT g.genre, AVG(r.averageRating) AS avg_rating, COUNT(*) AS nb_films
    FROM genres g
    JOIN ratings r ON g.movie_id = r.movie_id
    GROUP BY g.genre
    HAVING nb_films > 50 AND avg_rating > 7
    ORDER BY avg_rating DESC;
    """
    return conn.execute(sql).fetchall()


def q6_career_decades(conn, actor):
    sql = """
    WITH films AS (
        SELECT m.startYear AS year, r.averageRating AS rating
        FROM principals pr
        JOIN persons p ON pr.person_id = p.person_id
        JOIN movies m ON pr.movie_id = m.movie_id
        LEFT JOIN ratings r ON r.movie_id = m.movie_id
        WHERE p.primaryName LIKE ?
    )
    SELECT (year/10)*10 AS decade, COUNT(*) AS nb_films, AVG(rating)
    FROM films
    GROUP BY decade
    ORDER BY decade;
    """
    return conn.execute(sql, (f"%{actor}%",)).fetchall()


def q7_rank_genres(conn):
    sql = """
    SELECT genre, primaryTitle, averageRating, rank
    FROM (
        SELECT g.genre,
               m.primaryTitle,
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
    """
    return conn.execute(sql).fetchall()


def q8_breakthrough(conn):
    sql = """
    SELECT p.primaryName
    FROM persons p
    JOIN principals pr ON p.person_id = pr.person_id
    JOIN ratings r ON pr.movie_id = r.movie_id
    GROUP BY p.person_id
    HAVING SUM(r.numVotes < 200000) > 0
       AND SUM(r.numVotes > 200000) > 0;
    """
    return conn.execute(sql).fetchall()


def q9_multiskill(conn):
    sql = """
    SELECT p.primaryName, COUNT(*) AS nb_films
    FROM persons p
    JOIN principals pr ON p.person_id = pr.person_id
    JOIN directors d ON p.person_id = d.person_id
    GROUP BY p.person_id
    HAVING nb_films >= 3
    ORDER BY nb_films DESC;
    """
    return conn.execute(sql).fetchall()