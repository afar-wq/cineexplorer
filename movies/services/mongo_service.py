from pymongo import MongoClient
from django.conf import settings

MONGO_URI = "mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0"

class MongoService:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client['imdb_flat']  
        self.collection = self.db['movies'] 

    def get_all_movies(self, limit=20):
        """Récupère une liste de films simplifiée"""
        return list(self.collection.find({}, {"_id": 0, "title": 1, "year": 1, "rating": 1}).limit(limit))

    def get_movie_details(self, tconst):
        """Récupère les détails complets d'un film par son ID (tconst)"""
        return self.collection.find_one({"tconst": tconst}, {"_id": 0})

    def search_movies(self, query):
        # Recherche insensible à la casse
        return list(self.collection.find(
            {"title": {"$regex": query, "$options": "i"}}, 
            {"_id": 0}
        ).limit(20))
    
    def get_db_stats(self):
        return {
            "total_movies": self.collection.count_documents({}),
            "avg_rating": list(self.collection.aggregate([
                {"$group": {"_id": None, "avg": {"$avg": "$rating"}}}
            ]))[0]['avg']
        }



    