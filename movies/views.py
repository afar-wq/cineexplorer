from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.http import HttpResponse
from movies.services.mongo_service import MongoService
import random
from django.core.paginator import Paginator


service = MongoService()

def home(request):
    db = settings.MONGO_DB
    
    #  Statistiques précises
    stats = {
        'total_movies': db['movies'].count_documents({'titleType': 'movie'}),
        'total_persons': db['persons'].count_documents({}),
        # On compte les entrées uniques dans la collection 'directors'
        'total_directors': len(db['directors'].distinct('person_id')),
    }

    #  Top 10 des films les mieux notés
    # On part de 'ratings' pour filtrer sur le nombre de votes, puis on cherche le titre
    top_10_raw = list(db['ratings'].find(
        {'numVotes': {'$gte': 5000}},
        {'_id': 0}
    ).sort('averageRating', -1).limit(10))

    top_10 = []
    for r in top_10_raw:
        movie = db['movies'].find_one({'movie_id': r['movie_id']}, {'_id': 0, 'primaryTitle': 1, 'startYear': 1})
        if movie:
            top_10.append({
                'movie_id': r['movie_id'],
                'primaryTitle': movie['primaryTitle'],
                'startYear': movie['startYear'],
                'averageRating': r['averageRating']
            })

    #  4 Films aléatoires avec une note > 7
    # On utilise un échantillon sur 'movies' et on récupère la note après
    random_movies_list = list(db['movies'].aggregate([
        {'$match': {'titleType': 'movie'}},
        {'$sample': {'size': 4}}
    ]))
    
    random_suggestions = []
    for m in random_movies_list:
        rating_info = db['ratings'].find_one({'movie_id': m['movie_id']}, {'_id': 0, 'averageRating': 1})
        random_suggestions.append({
            'movie_id': m['movie_id'],
            'primaryTitle': m['primaryTitle'],
            'startYear': m['startYear'],
            'rating': rating_info['averageRating'] if rating_info else "N/A"
        })

    context = {
        'stats': stats,
        'top_10': top_10,
        'random_suggestions': random_suggestions,
    }
    return render(request, 'home.html', context)


def movie_list(request):
    db = settings.MONGO_DB
    
    # Récupération des paramètres de filtrage 
    genre = request.GET.get('genre')
    year_min = request.GET.get('year_min')
    year_max = request.GET.get('year_max')
    rating_min = request.GET.get('rating_min')
    sort_by = request.GET.get('sort', 'primaryTitle')  # Tri par défaut
    order = request.GET.get('order', 'asc')
    
    # Construction de la requête MongoDB 
    query = {'titleType': 'movie'}
    
    if genre:
        # On cherche les IDs dans la collection genres
        movie_ids_in_genre = db['genres'].distinct('movie_id', {'genre': genre})
        query['movie_id'] = {'$in': movie_ids_in_genre}
    
    if year_min or year_max:
        query['startYear'] = {}
        if year_min: query['startYear']['$gte'] = int(year_min)
        if year_max: query['startYear']['$lte'] = int(year_max)

    # Gestion du Tri 
    direction = 1 if order == 'asc' else -1
    
    # Exécution et Pagination 
    movies_cursor = db['movies'].find(query).sort(sort_by, direction)
    
    # Note: La pagination sur un curseur MongoDB est plus efficace avec limit/skip
    # mais pour simplifier avec Django Paginator :
    page_number = request.GET.get('page', 1)
    paginator = Paginator(list(movies_cursor.limit(500)), 20) # On limite à 500 pour la rapidité
    page_obj = paginator.get_page(page_number)

    # Enrichir avec les notes
    for movie in page_obj:
        r = db['ratings'].find_one({'movie_id': movie['movie_id']})
        movie['rating'] = r['averageRating'] if r else "N/A"

    # Récupérer la liste des genres pour le filtre
    all_genres = db['genres'].distinct('genre')

    context = {
        'page_obj': page_obj,
        'all_genres': all_genres,
        'current_genre': genre,
        'sort_by': sort_by,
        'order': order,
    }
    return render(request, 'list.html', context)

def movie_detail(request, tconst):
    db = settings.MONGO_DB
    
    # Infos de base du film
    movie = db['movies'].find_one({'movie_id': tconst})
    if not movie:
        return render(request, '404.html') # Gérer le cas où le film n'existe pas

    # Note et Votes
    rating_doc = db['ratings'].find_one({'movie_id': tconst})
    movie['rating'] = rating_doc['averageRating'] if rating_doc else "N/A"
    movie['votes'] = rating_doc['numVotes'] if rating_doc else 0

    # Casting (Jointure movies -> characters -> persons)
    # On récupère les personnages joués par des acteurs
    casting = []
    char_cursor = db['characters'].find({'movie_id': tconst})
    for char in char_cursor:
        person = db['persons'].find_one({'person_id': char['person_id']}, {'primaryName': 1})
        if person:
            casting.append({
                'name': person['primaryName'],
                'role': char['name']
            })

    # Réalisateurs et Scénaristes
    director_ids = db['directors'].distinct('person_id', {'movie_id': tconst})
    directors = list(db['persons'].find({'person_id': {'$in': director_ids}}, {'primaryName': 1}))

    writer_ids = db['writers'].distinct('person_id', {'movie_id': tconst})
    writers = list(db['persons'].find({'person_id': {'$in': writer_ids}}, {'primaryName': 1}))

    # Titres alternatifs (Collection 'titles')
    alt_titles = list(db['titles'].find({'movie_id': tconst, 'region': {'$ne': None}}))

    # Films similaires
    # On récupère d'abord les genres du film actuel
    movie_genres = db['genres'].distinct('genre', {'movie_id': tconst})
    similar_ids = db['genres'].distinct('movie_id', {'genre': {'$in': movie_genres}})
    
    similar_movies = list(db['movies'].find(
        {'movie_id': {'$in': similar_ids[:20], '$ne': tconst}}, 
        {'primaryTitle': 1, 'movie_id': 1, 'startYear': 1}
    ).limit(5))

    context = {
        'movie': movie,
        'casting': casting,
        'directors': directors,
        'writers': writers,
        'alt_titles': alt_titles,
        'similar_movies': similar_movies,
    }
    return render(request, 'detail.html', context)

def search(request):
    db = settings.MONGO_DB
    query_text = request.GET.get('q', '').strip()
    
    movie_results = []
    person_results = []

    if query_text:
        # Recherche dans la collection movies (par titre)
        # 'i' signifie insensible à la casse
        movie_cursor = db['movies'].find(
            {'primaryTitle': {'$regex': query_text, '$options': 'i'}},
            {'_id': 0, 'movie_id': 1, 'primaryTitle': 1, 'startYear': 1}
        ).limit(20)
        movie_results = list(movie_cursor)

        # Recherche dans la collection persons (par nom)
        person_cursor = db['persons'].find(
            {'primaryName': {'$regex': query_text, '$options': 'i'}},
            {'_id': 0, 'person_id': 1, 'primaryName': 1, 'birthYear': 1}
        ).limit(20)
        person_results = list(person_cursor)

    context = {
        'query': query_text,
        'movies': movie_results,
        'persons': person_results,
        'total_found': len(movie_results) + len(person_results)
    }
    return render(request, 'search.html', context)

def stats(request):
    db = settings.MONGO_DB
    
    # Films par genre (Bar Chart)
    genre_stats = list(db['genres'].aggregate([
        {'$group': {'_id': '$genre', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}, {'$limit': 10}
    ]))

    # Films par décennie (Line Chart)
    decade_stats = list(db['movies'].aggregate([
        {'$match': {'startYear': {'$ne': None}}},
        {'$group': {
            '_id': {'$subtract': ['$startYear', {'$mod': ['$startYear', 10]}]},
            'count': {'$sum': 1}
        }},
        {'$sort': {'_id': 1}}
    ]))

    # Distribution des notes (Histogramme)
    rating_dist = list(db['ratings'].aggregate([
        {'$group': {
            '_id': {'$floor': '$averageRating'}, 
            'count': {'$sum': 1}
        }},
        {'$sort': {'_id': 1}}
    ]))



    #  Top 10 acteurs prolifiques (Essai avec la collection principals) 
    top_actors_raw = list(db['principals'].aggregate([
        # On filtre uniquement sur les catégories liées au jeu d'acteur
        {'$match': {'category': {'$in': ['actor', 'actress']}}},
        {'$group': {'_id': '$person_id', 'movie_count': {'$sum': 1}}},
        {'$sort': {'movie_count': -1}},
        {'$limit': 10}
    ]))

    top_actors = []
    for actor in top_actors_raw:
        p = db['persons'].find_one({'person_id': actor['_id']}, {'primaryName': 1})
        if p:
            top_actors.append({
                'name': p['primaryName'],
                'count': actor['movie_count']
            })

    context = {
        'genre_labels': [g['_id'] for g in genre_stats],
        'genre_counts': [g['count'] for g in genre_stats],
        'decade_labels': [d['_id'] for d in decade_stats],
        'decade_counts': [d['count'] for d in decade_stats],
        'rating_labels': [r['_id'] for r in rating_dist],
        'rating_counts': [r['count'] for r in rating_dist],
        'actor_labels': [a['name'] for a in top_actors],
        'actor_counts': [a['count'] for a in top_actors],
        'actor_labels': [a['name'] for a in top_actors],
        'actor_counts': [a['count'] for a in top_actors],
    }
    return render(request, 'stats.html', context)


def test_mongo(request):
    try:
        count = service.collection.count_documents({})
        status = "Connecté au Replica Set "
    except Exception as e:
        status = f"Erreur : {e}"
        count = 0
    return render(request, 'test.html', {'status': status, 'count': count})