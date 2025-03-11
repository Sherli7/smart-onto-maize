from database.database import get_db_cursor
import psycopg2

def create_sensor(name: str, type: str, location: str, latitude: float, longitude: float, installation_date: str, status: str, field_id: int = None):
    """📡 Ajouter un nouveau capteur"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        try:
            cursor.execute("""
                INSERT INTO sensors (name, type, location, latitude, longitude, installation_date, status, field_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
            """, (name, type, location, latitude, longitude, installation_date, status, field_id))
            sensor_id = cursor.fetchone()["id"]
            conn.commit()
            cursor.close()
            conn.close()
            return sensor_id
        except psycopg2.Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            raise Exception(f"❌ Erreur lors de la création du capteur : {e}")

def get_sensors():
    """🔍 Récupérer tous les capteurs avec conversion `installation_date`"""
    cursor, conn = get_db_cursor()
    cursor.execute("SELECT * FROM sensors")
    sensors = cursor.fetchall()

    print("🔍 Capteurs récupérés depuis la BD:", sensors)  # ✅ Ajoute ceci pour debug

    # ✅ Convertir installation_date en format string
    for sensor in sensors:
        if sensor["installation_date"]:
            sensor["installation_date"] = sensor["installation_date"].strftime('%Y-%m-%d')

    cursor.close()
    conn.close()
    return sensors

def get_sensor_by_id(sensor_id: int):
    """🔍 Récupérer un capteur spécifique"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        cursor.execute("SELECT * FROM sensors WHERE id = %s;", (sensor_id,))
        sensor = cursor.fetchone()
        cursor.close()
        conn.close()
        return sensor

def update_sensor(sensor_id: int, updates: dict):
    """🛠️ Mettre à jour un capteur"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        fields = ", ".join([f"{key} = %s" for key in updates.keys()])
        values = list(updates.values()) + [sensor_id]
        query = f"UPDATE sensors SET {fields} WHERE id = %s RETURNING *;"
        cursor.execute(query, values)
        updated_sensor = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        return updated_sensor

def delete_sensor(sensor_id: int):
    """🗑️ Supprimer un capteur"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        cursor.execute("DELETE FROM sensors WHERE id = %s;", (sensor_id,))
        conn.commit()
        cursor.close()
        conn.close()

def get_sensor_by_id(sensor_id: int):
    """🔍 Récupérer un capteur par son ID avec conversion `installation_date`"""
    cursor, conn = get_db_cursor()
    cursor.execute("SELECT * FROM sensors WHERE id = %s", (sensor_id,))
    sensor = cursor.fetchone()

    if sensor and sensor["installation_date"]:
        sensor["installation_date"] = sensor["installation_date"].strftime('%Y-%m-%d')

    cursor.close()
    conn.close()
    return sensor
