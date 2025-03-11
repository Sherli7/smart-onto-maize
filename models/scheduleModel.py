from database.database import get_db_cursor
import psycopg2
import logging

# Configuration du logger
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def create_schedule(field_id: int, start_date: str, start_time: str, duration: str, status: str, flow_rate: float, pump_ids: list):
    cursor, conn = get_db_cursor()
    if cursor and conn:
        try:
            cursor.execute("""
                INSERT INTO schedules (field_id, start_date, start_time, duration, status, flow_rate)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
            """, (field_id, start_date, start_time, duration, status, flow_rate))

            schedule_id = cursor.fetchone()["id"]

            # Enregistrement des pompes liées
            for pump_id in pump_ids:
                cursor.execute("""
                    INSERT INTO schedule_pumps (pump_id,schedule_id)
                    VALUES (%s, %s);
                """, (pump_id,schedule_id))

            conn.commit()
            return schedule_id
        except psycopg2.Error as e:
            conn.rollback()
            raise Exception(f"Erreur PostgreSQL: {e}")
        finally:
            cursor.close()
            conn.close()

def update_schedule(schedule_id: int, updates: dict):
    """🛠️ Mettre à jour un planning (champs multiples)"""
    cursor, conn = get_db_cursor()
    updated_schedule = None
    if cursor and conn:
        try:
            logger.info(f"📥 Mise à jour du planning ID {schedule_id} avec les données: {updates}")

            # Vérification de l'existence du planning avant la mise à jour
            cursor.execute("SELECT * FROM schedules WHERE id = %s;", (schedule_id,))
            existing_schedule = cursor.fetchone()
            if not existing_schedule:
                raise Exception(f"❌ Le planning avec ID {schedule_id} n'existe pas.")

            # Prépare une liste des champs autorisés à mettre à jour
            valid_fields = ["field_id", "start_date", "start_time", "duration", "status", "flow_rate"]

            # Construit des fragments de requête pour chaque champ présent dans `updates`
            set_clauses = []
            values = []

            for field in valid_fields:
                if field in updates:
                    set_clauses.append(f"{field} = %s")
                    values.append(updates[field])

            # S'il n'y a aucun champ valide à mettre à jour, on arrête
            if not set_clauses:
                raise Exception("❌ Aucune donnée valide à mettre à jour.")

            # Construire la requête UPDATE dynamiquement
            set_clause = ", ".join(set_clauses)
            query = f"UPDATE schedules SET {set_clause} WHERE id = %s RETURNING *;"
            values.append(schedule_id)  # Ajout de l'id à la fin

            cursor.execute(query, tuple(values))
            updated_schedule = cursor.fetchone()

            # MàJ des pump_ids si nécessaire
            if "pump_ids" in updates and isinstance(updates["pump_ids"], list):
                # On supprime d'abord toutes les associations existantes
                cursor.execute("DELETE FROM schedule_pumps WHERE schedule_id = %s;", (schedule_id,))
                # Puis on insère les nouvelles associations
                for pump_id in updates["pump_ids"]:
                    cursor.execute(
                        "INSERT INTO schedule_pumps (pump_id, schedule_id) VALUES (%s, %s);",
                        (pump_id, schedule_id)
                    )

            conn.commit()
            return updated_schedule

        except psycopg2.Error as e:
            conn.rollback()
            logger.error("❌ Erreur lors de la mise à jour du planning ID %s: %s", schedule_id, e)
            raise Exception(f"Erreur PostgreSQL: {e}")
        finally:
            cursor.close()
            conn.close()

def get_schedules():
    """📋 Récupérer tous les plannings avec les pompes associées"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        try:
            cursor.execute("""
                SELECT s.id,
                       s.field_id,
                       s.start_date,
                       s.start_time,
                       s.duration,
                       s.status,
                       s.flow_rate,
                       s.last_irrigation_time,
                       COALESCE(ARRAY_AGG(sp.pump_id) FILTER (WHERE sp.pump_id IS NOT NULL), '{}') AS pump_ids
                FROM schedules s
                LEFT JOIN schedule_pumps sp ON s.id = sp.schedule_id
                GROUP BY s.id, s.field_id, s.start_date, s.start_time, s.duration, s.status, s.flow_rate, s.last_irrigation_time
                ORDER BY s.start_time;
            """)
            schedules = cursor.fetchall()
            return schedules
        except psycopg2.Error as e:
            logger.error("❌ Erreur lors de la récupération des plannings: %s", e)
            raise Exception(f"Erreur PostgreSQL: {e}")
        finally:
            cursor.close()
            conn.close()

def get_schedule_by_id(schedule_id: int):
    cursor, conn = get_db_cursor()
    if cursor and conn:
        try:
            cursor.execute("""
                SELECT s.*, ARRAY_AGG(sp.pump_id) AS pump_ids
                FROM schedules s
                LEFT JOIN schedule_pumps sp ON s.id = sp.schedule_id
                WHERE s.id = %s
                GROUP BY s.id;
            """, (schedule_id,))
            schedule = cursor.fetchone()
            return schedule
        except psycopg2.Error as e:
            raise Exception(f"Erreur PostgreSQL: {e}")
        finally:
            cursor.close()
            conn.close()

def delete_schedule(schedule_id: int):
    """🗑️ Supprimer un planning"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        try:
            cursor.execute("DELETE FROM schedules WHERE id = %s RETURNING id;", (schedule_id,))
            deleted_id = cursor.fetchone()
            conn.commit()
            return deleted_id
        except psycopg2.Error as e:
            conn.rollback()
            logger.error("❌ Erreur lors de la suppression du planning ID %s: %s", schedule_id, e)
            raise Exception(f"Erreur PostgreSQL: {e}")
        finally:
            cursor.close()
            conn.close()

def start_irrigation(schedule_id: int):
    """🚀 Démarrer l'irrigation"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        try:
            cursor.execute("""
                UPDATE schedules SET status = 'in_progress', last_irrigation_time = NOW()
                WHERE id = %s RETURNING *;
            """, (schedule_id,))
            updated_schedule = cursor.fetchone()
            conn.commit()
            return updated_schedule
        except psycopg2.Error as e:
            conn.rollback()
            logger.error("❌ Erreur lors du démarrage de l'irrigation ID %s: %s", schedule_id, e)
            raise Exception(f"Erreur PostgreSQL: {e}")
        finally:
            cursor.close()
            conn.close()
