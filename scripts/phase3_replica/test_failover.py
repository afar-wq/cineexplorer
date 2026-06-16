import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, AutoReconnect, NotPrimaryError

# On se connecte au cluster
uri = "mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0&retryWrites=false&serverSelectionTimeoutMS=500"
client = MongoClient(uri, serverSelectionTimeoutMS=2000)
db = client["test_db"]

print("1. Vérifie que le port 27017 est PRIMARY (rs.status() dans mongosh)")
print("2. Prépare-toi à couper le terminal 27017...")
input("Appuie sur Entrée pour commencer le bombardement d'écritures...")

start_time = None
recovered = False

print("C'est parti ! COUPE LE PORT 27017 MAINTENANT !")

while not recovered:
    try:
        # On tente une ECRITURE 
        db.failover_collection.insert_one({"test": "data", "at": time.time()})
        
        if start_time is not None:
            end_time = time.time()
            duration = end_time - start_time
            print(f"\n✅ Élection terminée !")
            print(f"⏱ Temps de failover réel (arrêt du service d'écriture) : {duration:.2f} secondes")
            recovered = True
        else:
            # Tant que ça marche, c'est que le 27017 n'est pas encore mort
            print("S", end="", flush=True) 
            
    except (ConnectionFailure, AutoReconnect, NotPrimaryError):
        if start_time is None:
            start_time = time.time() # On commence à compter au moment de la première erreur
        print(".", end="", flush=True)
        time.sleep(0.2)

client.close()