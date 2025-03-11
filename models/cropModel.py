from database.database import get_db_cursor
import psycopg2

def create_crop(name: str, lifecycle_duration: int, unit: str):
    """🌱 Ajouter une nouvelle culture"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        try:
            cursor.execute("""
                INSERT INTO crop_types (name, lifecycle_duration, unit)
                VALUES (%s, %s, %s) RETURNING id;
            """, (name, lifecycle_duration, unit))
            crop_id = cursor.fetchone()["id"]
            conn.commit()
            cursor.close()
            conn.close()
            return crop_id
        except psycopg2.Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            raise Exception(f"❌ Erreur lors de la création de la culture : {e}")

def get_crops():
    """📋 Récupérer toutes les cultures"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        cursor.execute("SELECT * FROM crop_types;")
        crops = cursor.fetchall()
        cursor.close()
        conn.close()
        return crops

def get_crop_by_id(crop_id: int):
    """🔍 Récupérer une culture spécifique"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        cursor.execute("SELECT * FROM crop_types WHERE id = %s;", (crop_id,))
        crop = cursor.fetchone()
        cursor.close()
        conn.close()
        return crop

def update_crop(crop_id: int, updates: dict):
    """🛠️ Mettre à jour une culture"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        fields = ", ".join([f"{key} = %s" for key in updates.keys()])
        values = list(updates.values()) + [crop_id]
        query = f"UPDATE crops SET {fields} WHERE id = %s RETURNING *;"
        cursor.execute(query, values)
        updated_crop = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        return updated_crop

def delete_crop(crop_id: int):
    """🗑️ Supprimer une culture"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        cursor.execute("DELETE FROM crop_types WHERE id = %s;", (crop_id,))
        conn.commit()
        cursor.close()
        conn.close()
