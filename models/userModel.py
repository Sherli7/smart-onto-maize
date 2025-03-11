import psycopg2
from database.database import get_db_connection
from utils.security import get_password_hash


def get_user_by_email(email: str):
    """🔍 Recherche un utilisateur par email."""
    conn = get_db_connection()
    if not conn:
        return None  # Gestion d'erreur en cas d'échec de connexion

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s;", (email,))
            user = cursor.fetchone()
            if user:
                print(f"✅ Utilisateur trouvé : {user}")  # Ajout du log
            else:
                print(f"⚠️ Aucun utilisateur trouvé pour l'email {email}")
            return user
    except psycopg2.Error as e:
        print(f"❌ Erreur lors de la récupération de l'utilisateur : {e}")
        return None
    finally:
        conn.close()

def register_user(username: str, email: str, password: str, role: str):
    """🆕 Insère un nouvel utilisateur."""
    conn = get_db_connection()
    if not conn:
        raise Exception("❌ Erreur : impossible de se connecter à la base de données.")

    try:
        with conn.cursor() as cursor:
            hashed_password = get_password_hash(password)
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role)
                VALUES (%s, %s, %s, %s) RETURNING id;
            """, (username, email, hashed_password, role))

            # Récupérer le résultat de l'insertion
            user_id = cursor.fetchone()
            if not user_id or "id" not in user_id:
                conn.rollback()
                raise Exception("❌ Erreur : Aucun ID retourné après insertion. Vérifiez la structure de la table.")

            conn.commit()
            return user_id["id"]  # Retourner l'ID de l'utilisateur

    except psycopg2.Error as e:
        conn.rollback()
        raise Exception(f"❌ Erreur lors de l'inscription: {e}")
    finally:
        conn.close()