#  CineExplorer - IMDb MongoDB Analytics

CineExplorer est une plateforme d'analyse et d'exploration cinématographique basée sur un dataset IMDb de plus de 36 000 titres. Ce projet a été réalisé dans le cadre du module NoSQL pour démontrer la mise en œuvre d'une architecture haute disponibilité avec MongoDB et une interface web moderne avec Django.

---

##  Architecture Technique

Ce projet repose sur une pile technologique robuste :

- **Backend :** Django 5.0 (Python 3.11)
- **Base de données :** MongoDB avec **Replica Set (rs0)** composé de 3 instances (1 Primary, 2 Secondaries).
- **Frontend :** Bootstrap 5 pour le design responsive et **Chart.js** pour la visualisation de données.
- **Communication DB :** PyMongo pour la gestion des agrégations complexes.

##  Fonctionnalités Clés

1. **Dashboard (Accueil) :** Vue d'ensemble avec KPIs, Top 10 des films les mieux notés et suggestions aléatoires.
2. **Exploration Filtrée :** Système de filtrage dynamique par genre, année et tri (croissant/décroissant) avec pagination.
3. **Recherche Intelligente :** Barre de recherche globale permettant de trouver des films et des membres de l'équipe technique.
4. **Analyses Statistiques :** - Répartition des films par genre.
   - Évolution de la production par décennie.
   - Top 10 des acteurs les plus prolifiques.
   - Comparaison des durées moyennes des films.
5. **Fiche Détail :** Informations complètes sur chaque film, incluant la note, la durée et les genres associés.

##  Installation et Configuration

### 1. Prérequis
- Python 3.11+
- Un Replica Set MongoDB actif (`rs0`) sur les ports `27017`, `27018`, `27019`.

### 2. Etapes
```bash

#Télecharger le dossier puis se déplacer dedans
cd cineexplorer/cineexplorer/

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les packages nécessaires
pip install -r requirements.txt

#Lancer les ports et charger les données
cd scripts/phase3_replica/
Start-Process "setup_replica.bat"

#Lancer les serveurs
python manage.py runserver

#Se connecter à l'addresse suivante:
http://127.0.0.1:8000/
