from pymongo import MongoClient

def migrate_structured():
    client = MongoClient("mongodb://127.0.0.1:27017/")
    db = client["imdb_flat"]
    db.movies_complete.drop()

    pipeline = [
        {
            "$lookup": {
                "from": "ratings",
                "localField": "movie_id",
                "foreignField": "movie_id",
                "as": "rating_info"
            }
        },
        {
            "$lookup": {
                "from": "genres",
                "localField": "movie_id",
                "foreignField": "movie_id",
                "as": "genre_docs"
            }
        },
        {
            "$project": {
                "_id": 0,
                "movie_id": 1,
                "title": "$primaryTitle",      # Renomme primaryTitle en title
                "year": "$startYear",         # Renomme startYear en year
                "runtime": "$runtimeMinutes",  # Renomme runtimeMinutes en runtime
                "rating": {"$arrayElemAt": ["$rating_info.averageRating", 0]},
                "genres": "$genre_docs.genre"
            }
        },
        {"$out": "movies_complete"}
    ]

    db.movies.aggregate(pipeline)
    print(f"✅ Collection movies_complete créée avec {db.movies_complete.count_documents({})} documents.")
    client.close()

if __name__ == "__main__":
    migrate_structured()




    