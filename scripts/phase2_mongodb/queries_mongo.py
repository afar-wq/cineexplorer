from pymongo import MongoClient
import re

# Q1 : Filmographie d'un acteur (Trié par année décroissante)
def q1_actor_filmography(db, actor_name):
    pipeline = [
        {"$match": {"primaryName": {"$regex": actor_name, "$options": "i"}}},
        {"$lookup": {
            "from": "principals",
            "localField": "person_id",
            "foreignField": "person_id",
            "as": "roles"
        }},
        {"$unwind": "$roles"},
        {"$lookup": {
            "from": "movies_complete", 
            "localField": "roles.movie_id",
            "foreignField": "movie_id",
            "as": "m"
        }},
        {"$unwind": "$m"},
        {"$sort": {"m.year": -1}},
        {"$project": {
            "_id": 0,
            "title": "$m.title",
            "year": "$m.year",
            "rating": "$m.rating"
        }}
    ]
    return list(db.persons.aggregate(pipeline))

# Q2 : Top N films d'un genre sur une période donnée
def q2_top_n_genre(db, genre_name, y1, y2, N):
    pipeline = [
        {
            "$match": {
                "genres": genre_name,
                "year": {"$gte": y1, "$lte": y2}
            }
        },
        {"$sort": {"rating": -1}},
        {"$limit": N},
        {"$project": {"_id": 0, "title": 1, "year": 1, "rating": 1}}
    ]
    return list(db.movies_complete.aggregate(pipeline))

# Q3 : Acteurs ayant plusieurs rôles dans le même film
def q3_multi_roles(db):
    pipeline = [
        {"$group": {
            "_id": {"movie_id": "$movie_id", "person_id": "$person_id"},
            "nb_roles": {"$sum": 1}
        }},
        {"$match": {"nb_roles": {"$gt": 1}}},
        {"$lookup": {
            "from": "persons",
            "localField": "_id.person_id",
            "foreignField": "person_id",
            "as": "person"
        }},
        {"$lookup": {
            "from": "movies_complete",
            "localField": "_id.movie_id",
            "foreignField": "movie_id",
            "as": "movie"
        }},
        {"$unwind": "$person"}, 
        {"$unwind": "$movie"},
        {"$sort": {"nb_roles": -1}},
        {"$project": {
            "_id": 0,
            "name": "$person.primaryName", 
            "title": "$movie.title", 
            "nb_roles": 1
        }}
    ]
    return list(db.characters.aggregate(pipeline))

# Q4 : Collaborations Acteur/Réalisateur
def q4_collaborations(db, actor_name):
    pipeline = [
        {"$match": {"primaryName": {"$regex": actor_name, "$options": "i"}}},
        {"$lookup": {
            "from": "principals",
            "localField": "person_id",
            "foreignField": "person_id",
            "as": "acting_jobs"
        }},
        {"$unwind": "$acting_jobs"},
        {"$match": {"acting_jobs.category": {"$in": ["actor", "actress"]}}},
        {"$lookup": {
            "from": "directors",
            "localField": "acting_jobs.movie_id",
            "foreignField": "movie_id",
            "as": "movie_directors"
        }},
        {"$unwind": "$movie_directors"},
        {"$group": {"_id": "$movie_directors.person_id", "films": {"$sum": 1}}},
        {"$lookup": {
            "from": "persons",
            "localField": "_id",
            "foreignField": "person_id",
            "as": "director"
        }},
        {"$unwind": "$director"},
        {"$sort": {"films": -1}},
        {"$project": {"_id": 0, "director": "$director.primaryName", "films": 1}}
    ]
    return list(db.persons.aggregate(pipeline))

# Q5 : Genres populaires (Moyenne > 7 et Count > 50)
def q5_popular_genres(db):
    pipeline = [
        {"$unwind": "$genres"},
        {"$group": {
            "_id": "$genres",
            "avg_rating": {"$avg": "$rating"},
            "nb_films": {"$sum": 1}
        }},
        {"$match": {"nb_films": {"$gt": 50}, "avg_rating": {"$gt": 7}}},
        {"$sort": {"avg_rating": -1}}
    ]
    return list(db.movies_complete.aggregate(pipeline))

# Q6 : Évolution de carrière par décennie
def q6_career_decades(db, actor):
    pipeline = [
        {"$match": {"primaryName": {"$regex": actor, "$options": "i"}}},
        {"$lookup": {
            "from": "principals",
            "localField": "person_id",
            "foreignField": "person_id",
            "as": "p"
        }},
        {"$unwind": "$p"},
        {"$lookup": {
            "from": "movies_complete",
            "localField": "p.movie_id",
            "foreignField": "movie_id",
            "as": "m"
        }},
        {"$unwind": "$m"},
        {"$project": {
            "decade": {"$multiply": [{"$floor": {"$divide": ["$m.year", 10]}}, 10]},
            "rating": "$m.rating"
        }},
        {"$group": {
            "_id": "$decade",
            "nb_films": {"$sum": 1},
            "avg_rating": {"$avg": "$rating"}
        }},
        {"$sort": {"_id": 1}}
    ]
    return list(db.persons.aggregate(pipeline))

# Q7 : Top 3 des films par genre (Window Function / denseRank)
def q7_rank_genres(db):
    pipeline = [
        {"$unwind": "$genres"},
        {"$setWindowFields": {
            "partitionBy": "$genres",
            "sortBy": {"rating": -1},
            "output": {"rank": {"$denseRank": {}}}
        }},
        {"$match": {"rank": {"$lte": 3}}},
        {"$project": {"_id": 0, "genre": "$genres", "title": 1, "rating": 1, "rank": 1}}
    ]
    return list(db.movies_complete.aggregate(pipeline))

# Q8 : Acteurs "Breakthrough"
def q8_breakthrough(db):
    pipeline = [
        {"$lookup": {
            "from": "ratings",
            "localField": "movie_id",
            "foreignField": "movie_id",
            "as": "r"
        }},
        {"$unwind": "$r"},
        {"$group": {
            "_id": "$person_id",
            "small_films": {"$sum": {"$cond": [{"$lt": ["$r.numVotes", 200000]}, 1, 0]}},
            "big_films": {"$sum": {"$cond": [{"$gt": ["$r.numVotes", 200000]}, 1, 0]}}
        }},
        {"$match": {"small_films": {"$gt": 0}, "big_films": {"$gt": 0}}},
        {"$lookup": {
            "from": "persons",
            "localField": "_id",
            "foreignField": "person_id",
            "as": "p"
        }},
        {"$unwind": "$p"},
        {"$project": {"_id": 0, "name": "$p.primaryName"}}
    ]
    return list(db.principals.aggregate(pipeline))

# Q9 : Multi-talents
def q9_multiskill(db):
    pipeline = [
        {"$lookup": {
            "from": "directors",
            "localField": "person_id",
            "foreignField": "person_id",
            "as": "dir_info"
        }},
        {"$project": {
            "person_id": 1,
            "is_director": {"$gt": [{"$size": "$dir_info"}, 0]}
        }},
        {"$match": {"is_director": True}},
        {"$group": {"_id": "$person_id", "nb_films": {"$sum": 1}}},
        {"$match": {"nb_films": {"$gte": 3}}},
        {"$lookup": {
            "from": "persons",
            "localField": "_id",
            "foreignField": "person_id",
            "as": "p"
        }},
        {"$unwind": "$p"},
        {"$sort": {"nb_films": -1}},
        {"$project": {"_id": 0, "name": "$p.primaryName", "nb_films": 1}}
    ]
    return list(db.principals.aggregate(pipeline))