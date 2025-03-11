from fastapi.encoders import jsonable_encoder
import json  # ✅ Utilisation du module standard JSON
import psycopg2.extras
from database.database import get_db_connection
from schema.sensorReadingsSchema import SensorReading

class SensorReadingsModel:
    @staticmethod
    def save_sensor_data(sensor_data: SensorReading):
        """ Ajoute ou met à jour les mesures d'un capteur dans `raw_data`. """
        conn = get_db_connection()
        if not conn:
            print("❌ Impossible de se connecter à la BD pour enregistrer les mesures.")
            return

        try:
            cursor = conn.cursor()

            # ✅ Convertir la nouvelle donnée en JSONB
            new_measurement = jsonable_encoder(sensor_data.raw_data)

            # ✅ Vérifier si le capteur a déjà un enregistrement
            cursor.execute("""
                SELECT raw_data FROM sensorreadings WHERE sensor_id = %s
            """, (sensor_data.sensor_id,))
            existing_record = cursor.fetchone()

            if existing_record:
                # ✅ Ajouter la nouvelle mesure dans `raw_data` existant
                cursor.execute("""
                    UPDATE sensorreadings
                    SET raw_data = raw_data || %s::jsonb
                    WHERE sensor_id = %s
                """, (json.dumps(new_measurement), sensor_data.sensor_id))

                print(f"🔄 Mise à jour des mesures pour le capteur {sensor_data.sensor_id}.")
            else:
                # ✅ Créer un nouvel enregistrement s'il n'existe pas encore
                cursor.execute("""
                    INSERT INTO sensorreadings (sensor_id, field_id, raw_data)
                    VALUES (%s, %s, %s)
                """, (
                    sensor_data.sensor_id,
                    sensor_data.field_id,
                    json.dumps(new_measurement)  # ✅ Utilisation correcte de JSONB
                ))

                print(f"✅ Nouveau capteur enregistré {sensor_data.sensor_id} avec ses premières mesures.")

            conn.commit()

        except Exception as e:
            print(f"❌ Erreur lors de l'enregistrement des données : {e}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_all_sensor_readings_with_names():
        """ Récupère toutes les mesures avec les noms des capteurs et des champs, même s'ils n'ont pas encore de mesures. """
        conn = get_db_connection()
        if not conn:
            print("❌ Impossible de se connecter à la BD.")
            return []

        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT s.id as sensor_id, s.name as sensor_name, f.id as field_id, f.name as field_name, 
                       COALESCE(sr.raw_data, '[]') as raw_data
                FROM sensors s
                JOIN fields f ON s.field_id = f.id
                LEFT JOIN sensorreadings sr ON s.id = sr.sensor_id
                ORDER BY s.id DESC
            """)
            readings = cursor.fetchall()

            return [
                {
                    "sensor_id": row["sensor_id"],
                    "sensor_name": row["sensor_name"],
                    "field_id": row["field_id"],
                    "field_name": row["field_name"],
                    "raw_data": json.loads(row["raw_data"]) if isinstance(row["raw_data"], str) else row["raw_data"]
                }
                for row in readings
            ]
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des mesures : {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_sensor_data(sensor_id: int):
        """ Récupère la dernière mesure d'un capteur donné sous `raw_data`. """
        conn = get_db_connection()
        if not conn:
            print("❌ Impossible de se connecter à la BD pour la lecture.")
            return {}

        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT sensor_id, field_id, raw_data
                FROM sensorreadings
                WHERE sensor_id = %s
                ORDER BY id DESC
                LIMIT 1
            """, (sensor_id,))
            data = cursor.fetchone()

            return {
                "sensor_id": data["sensor_id"],
                "field_id": data["field_id"],
                "raw_data": json.loads(data["raw_data"]) if data else []
            } if data else {}  # ✅ Retourne un objet vide s'il n'y a aucun enregistrement.

        except Exception as e:
            print(f"❌ Erreur lors de la lecture des données : {e}")
            return {}

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_field_id_by_sensor(sensor_id: int):
        """ Récupère l'ID du champ auquel un capteur est associé. """
        conn = get_db_connection()
        if not conn:
            print("❌ Impossible de se connecter à la BD pour récupérer l'ID du champ.")
            return None

        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT field_id FROM sensors WHERE id = %s
            """, (sensor_id,))
            result = cursor.fetchone()
            return result["field_id"] if result else None
        except Exception as e:
            print(f"❌ Erreur lors de la récupération de l'ID du champ du capteur {sensor_id} : {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_all_sensor_readings():
        """ Récupère toutes les mesures des capteurs sous forme de `raw_data` JSONB. """
        conn = get_db_connection()
        if not conn:
            print("❌ Impossible de se connecter à la BD pour récupérer les mesures.")
            return {}

        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT sensor_id, field_id, raw_data
                FROM sensorreadings
                ORDER BY sensor_id DESC
            """)
            readings = cursor.fetchall()

            return [
                {
                    "sensor_id": row["sensor_id"],
                    "field_id": row["field_id"],
                    "raw_data": row["raw_data"] if isinstance(row["raw_data"], list) else json.loads(row["raw_data"])
                }
                for row in readings
            ] if readings else {}  # ✅ Retourne un objet vide s'il n'y a aucun enregistrement.

        except Exception as e:
            print(f"❌ Erreur lors de la récupération des mesures : {e}")
            return {}

        finally:
            cursor.close()
            conn.close()


    @staticmethod
    def get_all_sensor_readings():
        """ Récupère toutes les mesures des capteurs sous forme de `raw_data` JSONB. Renvoie `{}` si aucun enregistrement. """
        conn = get_db_connection()
        if not conn:
            print("❌ Impossible de se connecter à la base de données pour la récupération des mesures.")
            return {}

        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT sensor_id, field_id, raw_data
                FROM sensorreadings
                ORDER BY sensor_id DESC
            """)
            readings = cursor.fetchall()

            if not readings:
                return {}

            return [
                {
                    "sensor_id": row["sensor_id"],
                    "field_id": row["field_id"],
                    "raw_data": row["raw_data"] if isinstance(row["raw_data"], list) else json.loads(row["raw_data"])
                }
                for row in readings
            ]
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des mesures : {e}")
            return {}
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_sensor_data(sensor_id: int):
        """ Récupère la dernière mesure d'un capteur donné sous `raw_data`. """
        conn = get_db_connection()
        if not conn:
            print("❌ Impossible de se connecter à la base de données pour la lecture.")
            return None
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT sensor_id, field_id, raw_data
                FROM sensorreadings
                WHERE sensor_id = %s
                ORDER BY id DESC
                LIMIT 1
            """, (sensor_id,))
            data = cursor.fetchone()
            if data:
                print(f"✅ Données récupérées pour le capteur {sensor_id}.")
                return {
                    "sensor_id": data["sensor_id"],
                    "field_id": data["field_id"],
                    "raw_data": json.loads(data["raw_data"])  # ✅ JSONB converti en dict
                }
            else:
                print(f"❌ Aucune donnée trouvée pour le capteur {sensor_id}.")
                return None
        except Exception as e:
            print(f"❌ Erreur lors de la lecture des données : {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def is_sensor_active(sensor_id: int):
        """ Vérifie si un capteur est actif. """
        conn = get_db_connection()
        if not conn:
            print("❌ Impossible de se connecter à la base de données pour vérifier le capteur.")
            return False
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT status
                FROM sensors
                WHERE id = %s
            """, (sensor_id,))
            result = cursor.fetchone()
            return result and result["status"] == "active"
        except Exception as e:
            print(f"❌ Erreur lors de la vérification du capteur : {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_sensor_type(sensor_id: int):
        """ Récupère le type d'un capteur (humidity, temperature, npk, etc.) """
        conn = get_db_connection()
        if not conn:
            print("❌ Impossible de se connecter à la BD pour récupérer le type du capteur.")
            return "unknown"

        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT type
                FROM sensors
                WHERE id = %s
            """, (sensor_id,))
            result = cursor.fetchone()
            return result["type"] if result else "unknown"
        except Exception as e:
            print(f"❌ Erreur lors de la récupération du type du capteur : {e}")
            return "unknown"
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_all_sensors_status():
        """ Récupère le statut de tous les capteurs. """
        conn = get_db_connection()
        if not conn:
            print("❌ Impossible de se connecter à la base de données pour récupérer les capteurs.")
            return []
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT id, name, type, status
                FROM sensors
            """)
            sensors = cursor.fetchall()
            return [dict(sensor) for sensor in sensors]
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des capteurs : {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_active_sensors():
        """ Récupère uniquement les capteurs actifs. """
        conn = get_db_connection()
        if not conn:
            print("❌ Impossible de se connecter à la base de données pour récupérer les capteurs actifs.")
            return []
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT id
                FROM sensors
                WHERE status = 'active'
            """)
            active_sensors = cursor.fetchall()
            return [sensor["id"] for sensor in active_sensors]
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des capteurs actifs : {e}")
            return []
        finally:
            cursor.close()
            conn.close()
