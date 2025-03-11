import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# 📌 Charger les variables d'environnement
load_dotenv()

# 📌 Récupérer les valeurs du fichier .env
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# 📌 Construire l'URL de connexion PostgreSQL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 📌 Connexion psycopg2 pour init_db.py
def get_db_connection():
    """🔌 Crée une connexion à la base de données PostgreSQL avec psycopg2."""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        print("✅ Connexion réussie à la base de données.")
        return conn
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return None

# 📌 Fonction de récupération d'un curseur pour exécuter des requêtes
def get_db_cursor():
    """🔄 Récupère un curseur pour exécuter des requêtes SQL."""
    conn = get_db_connection()
    if conn:
        return conn.cursor(), conn
    return None, None
