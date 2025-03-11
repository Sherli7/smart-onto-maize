import os
from database.database import get_db_connection

# 📌 Obtenir le chemin absolu du fichier `schema.sql`
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema.sql")

def init_database():
    """ Exécute le script SQL `schema.sql` pour créer les tables si elles n'existent pas déjà """
    conn = get_db_connection()
    if conn is None:
        print("❌ Impossible de se connecter à la base de données.")
        return

    cur = conn.cursor()
    try:
        # 📌 Lire et exécuter le contenu de schema.sql
        with open(SCHEMA_FILE, "r", encoding="utf-8") as schema_file:
            schema_sql = schema_file.read()
            cur.execute(schema_sql)
            conn.commit()
            print("✅ Base de données initialisée avec succès.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    init_database()
