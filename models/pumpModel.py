import psycopg2
from database.database import get_db_connection

def create_pump(name: str, field_id: int):
    """🆕 Créer une nouvelle pompe"""
    conn = get_db_connection()
    if not conn:
        raise Exception("❌ Impossible de se connecter à la base de données.")

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("""
                INSERT INTO pumps (name, field_id, is_on, status, water_flow, elapsed_time, last_start_time, 
                                   last_activated, total_usage_time, power_consumption, maintenance_status, last_maintenance)
                VALUES (%s, %s, FALSE, 'idle', 0.0, 0.0, NULL, NULL, 0.0, 0.0, 'ok', NULL)
                RETURNING id;
            """, (name, field_id))

            pump_id = cursor.fetchone()["id"]
            conn.commit()
            return pump_id

    except psycopg2.Error as e:
        conn.rollback()
        raise Exception(f"❌ Erreur lors de la création de la pompe: {e}")

    finally:
        conn.close()


def get_pump_by_id(pump_id: int):
    """🔍 Récupérer une pompe par son ID"""
    conn = get_db_connection()
    if not conn:
        raise Exception("❌ Impossible de se connecter à la base de données.")

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM pumps WHERE id = %s;", (pump_id,))
            pump = cursor.fetchone()

            if pump and pump["last_activated"]:
                pump["last_activated"] = pump["last_activated"].isoformat()  # ✅ Convertir `datetime` en string

            return pump

    except psycopg2.Error as e:
        raise Exception(f"❌ Erreur lors de la récupération de la pompe: {e}")

    finally:
        conn.close()


def get_pumps():
    """📋 Récupérer la liste de toutes les pompes"""
    conn = get_db_connection()
    if not conn:
        raise Exception("❌ Impossible de se connecter à la base de données.")

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM pumps;")
            pumps = cursor.fetchall()

            # ✅ Convertir `datetime` en string pour toutes les pompes
            for pump in pumps:
                if pump["last_activated"]:
                    pump["last_activated"] = pump["last_activated"].isoformat()

            return pumps

    except psycopg2.Error as e:
        raise Exception(f"❌ Erreur lors de la récupération des pompes: {e}")

    finally:
        conn.close()


def update_pump(pump_id: int, updates: dict):
    """🛠 Mettre à jour une pompe"""
    conn = get_db_connection()
    if not conn:
        raise Exception("❌ Impossible de se connecter à la base de données.")

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
            values = list(updates.values()) + [pump_id]

            query = f"UPDATE pumps SET {set_clause} WHERE id = %s RETURNING *;"
            cursor.execute(query, tuple(values))

            updated_pump = cursor.fetchone()
            conn.commit()

            if updated_pump and updated_pump["last_activated"]:
                updated_pump["last_activated"] = updated_pump["last_activated"].isoformat()

            return updated_pump

    except psycopg2.Error as e:
        conn.rollback()
        raise Exception(f"❌ Erreur lors de la mise à jour de la pompe: {e}")

    finally:
        conn.close()


def delete_pump(pump_id: int):
    """🗑 Supprimer une pompe"""
    conn = get_db_connection()
    if not conn:
        raise Exception("❌ Impossible de se connecter à la base de données.")

    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM pumps WHERE id = %s RETURNING id;", (pump_id,))
            deleted_pump = cursor.fetchone()

            if deleted_pump:
                conn.commit()
                return True
            return False

    except psycopg2.Error as e:
        conn.rollback()
        raise Exception(f"❌ Erreur lors de la suppression de la pompe: {e}")

    finally:
        conn.close()


def toggle_pump(pump_id: int):
    """🔄 Activer/Désactiver une pompe"""
    conn = get_db_connection()
    if not conn:
        raise Exception("❌ Impossible de se connecter à la base de données.")

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            # 🔄 Récupérer l'état actuel de la pompe
            cursor.execute("SELECT is_on FROM pumps WHERE id = %s;", (pump_id,))
            pump = cursor.fetchone()

            if not pump:
                return None  # Pompe inexistante

            new_status = not pump["is_on"]

            # 🔄 Mettre à jour l'état de la pompe
            cursor.execute("""
                UPDATE pumps 
                SET is_on = %s, last_activated = NOW() 
                WHERE id = %s 
                RETURNING *;
            """, (new_status, pump_id))

            updated_pump = cursor.fetchone()
            conn.commit()

            # ✅ Convertir `datetime` en string
            if updated_pump and updated_pump["last_activated"]:
                updated_pump["last_activated"] = updated_pump["last_activated"].isoformat()

            return updated_pump

    except psycopg2.Error as e:
        conn.rollback()
        raise Exception(f"❌ Erreur lors du changement d'état de la pompe: {e}")

    finally:
        conn.close()
