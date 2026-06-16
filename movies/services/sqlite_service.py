import sqlite3
import os

class SQLiteService:
    def __init__(self):
        # Chemin vers ma base SQLite 
        self.db_path = os.path.join('data', 'sqlite', 'imdb.db')

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row # Pour récupérer les résultats sous forme de dictionnaire
        return conn

    def get_stats(self):
        """Exemple : compter le nombre de films dans SQLite"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM titles")
        result = cursor.fetchone()
        conn.close()
        return result['total']