import logging

from pydantic import BaseModel

from database.database import get_db_cursor
import psycopg2
from datetime import datetime, date
from typing import Optional

# ✅ Configuration du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def create_field(
        name: str,
        location: str,
        latitude: float,
        longitude: float,
        size: float,
        sensor_density: float,
        crop_type_id: Optional[int] = None,
        planting_date: Optional[date] = None
):
    """🌾 Ajouter un nouveau champ avec gestion stricte des types"""
    cursor, conn = get_db_cursor()

    # ✅ Log des données reçues pour debug
    logger.info("📩 Données reçues pour création de champ :")
    logger.info(" - name: %s (type: %s)", name, type(name))
    logger.info(" - location: %s (type: %s)", location, type(location))
    logger.info(" - latitude: %s (type: %s)", latitude, type(latitude))
    logger.info(" - longitude: %s (type: %s)", longitude, type(longitude))
    logger.info(" - size: %s (type: %s)", size, type(size))
    logger.info(" - sensor_density: %s (type: %s)", sensor_density, type(sensor_density))
    logger.info(" - crop_type_id: %s (type: %s)", crop_type_id, type(crop_type_id))
    logger.info(" - planting_date: %s (type: %s)", planting_date, type(planting_date))

    if cursor and conn:
        try:
            # ✅ Vérification des types
            if not isinstance(sensor_density, (int, float)):
                raise ValueError(f"❌ Erreur : sensor_density attendu en float, reçu {type(sensor_density)}")

            # ✅ Correction du type de `planting_date`
            if planting_date:
                if isinstance(planting_date, date):  # Si c'est déjà une date, convertir en string
                    planting_date = planting_date.strftime("%Y-%m-%d")
                elif isinstance(planting_date, str):  # Vérifier que c'est bien au format YYYY-MM-DD
                    try:
                        planting_date = datetime.strptime(planting_date, "%Y-%m-%d").date().strftime("%Y-%m-%d")
                    except ValueError:
                        raise ValueError(
                            f"❌ Erreur : planting_date doit être au format YYYY-MM-DD, reçu {planting_date}")
                else:
                    raise ValueError(
                        f"❌ Erreur : planting_date attendu en str (YYYY-MM-DD), reçu {type(planting_date)}")

            # ✅ Insertion dans la base de données avec un bon ordre des champs
            cursor.execute("""
                INSERT INTO fields (name, location, latitude, longitude, size, sensor_density, crop_type_id, planting_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
            """, (name, location, latitude, longitude, size, sensor_density, crop_type_id, planting_date))

            field_id = cursor.fetchone()["id"]
            conn.commit()
            logger.info("✅ Champ ajouté avec succès : ID %d", field_id)
            return field_id

        except (psycopg2.Error, ValueError) as e:
            conn.rollback()
            logger.error("❌ Erreur SQL ou Type lors de la création du champ : %s", e)
            raise Exception(f"❌ Erreur lors de la création du champ : {e}")

        finally:
            cursor.close()
            conn.close()
def get_fields():
    """📋 Récupérer tous les champs"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        cursor.execute("SELECT * FROM fields;")
        fields = cursor.fetchall()
        cursor.close()
        conn.close()
        return fields

def get_field_by_id(field_id: int):
    """🔍 Récupérer un champ spécifique"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        cursor.execute("SELECT * FROM fields WHERE id = %s;", (field_id,))
        field = cursor.fetchone()
        cursor.close()
        conn.close()
        return field

def update_field(field_id: int, updates: dict):
    """🛠️ Mettre à jour un champ"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        try:
            if "planting_date" in updates:
                planting_date = updates["planting_date"]
                if isinstance(planting_date, str):
                    updates["planting_date"] = datetime.strptime(planting_date, "%Y-%m-%d").date()

            if "sensor_density" in updates:
                try:
                    updates["sensor_density"] = float(updates["sensor_density"])
                except ValueError:
                    raise ValueError("❌ Erreur : sensor_density doit être un nombre valide.")

            fields = ", ".join([f"{key} = %s" for key in updates.keys()])
            values = list(updates.values()) + [field_id]
            query = f"UPDATE fields SET {fields} WHERE id = %s RETURNING *;"
            cursor.execute(query, values)
            updated_field = cursor.fetchone()
            conn.commit()
            return updated_field
        except (psycopg2.Error, ValueError) as e:
            conn.rollback()
            raise Exception(f"❌ Erreur lors de la mise à jour du champ : {e}")
        finally:
            cursor.close()
            conn.close()

def delete_field(field_id: int):
    """🗑️ Supprimer un champ"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        cursor.execute("DELETE FROM fields WHERE id = %s;", (field_id,))
        conn.commit()
        cursor.close()
        conn.close()

# ✅ Modèle Pydantic mis à jour pour les mises à jour de champs
class FieldUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    size: Optional[float] = None
    sensor_density: Optional[float] = None
    crop_type_id: Optional[int] = None
    planting_date: Optional[date] = None  # ✅ Correction du type
