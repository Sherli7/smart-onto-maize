from datetime import datetime, timedelta
from database.database import get_db_cursor
import psycopg2
import logging

logger = logging.getLogger("irrigation_service")


def check_and_activate_pumps():
    """🚿 Vérifie les plannings et active les pompes si les conditions sont remplies."""
    cursor, conn = get_db_cursor()

    try:
        # 1. Récupérer les plannings qui sont prévus et dont l'heure de début est proche
        cursor.execute("""
            SELECT s.id as schedule_id, s.field_id, s.start_time, s.duration, s.status, s.flow_rate,
                   sp.pump_id, p.is_on, p.status as pump_status, p.maintenance_status, p.last_maintenance
            FROM schedules s
            JOIN schedule_pumps sp ON s.id = sp.schedule_id
            JOIN pumps p ON sp.pump_id = p.id
            WHERE s.status = 'planned'
        """)
        schedules = cursor.fetchall()

        now = datetime.now()

        for schedule in schedules:
            start_time = datetime.combine(now.date(), schedule['start_time'])
            duration_seconds = schedule['duration'].total_seconds()
            end_time = start_time + timedelta(seconds=duration_seconds)

            # Vérifier si le planning doit commencer ou se terminer
            if start_time <= now <= end_time:
                logger.info(
                    f"🚿 Vérification de la pompe {schedule['pump_id']} pour le planning {schedule['schedule_id']}")

                # 2. Vérifier les conditions environnementales avant d'activer la pompe
                if verify_environmental_conditions(schedule['field_id']):
                    # Vérifier que la pompe n'est pas en maintenance
                    if schedule['maintenance_status'] == 'ok':
                        # Activer la pompe si elle est éteinte
                        if not schedule['is_on']:
                            activate_pump(schedule['pump_id'])
                            update_schedule_status(schedule['schedule_id'], 'in_progress')
                            logger.info(f"✅ Pompe {schedule['pump_id']} activée pour le champ {schedule['field_id']}")
                    else:
                        logger.warning(f"⚠️ Pompe {schedule['pump_id']} en maintenance, impossible d'activer.")
                else:
                    logger.info(f"🌿 Conditions non optimales pour activer la pompe {schedule['pump_id']}.")

            # Si le planning est terminé, arrêter la pompe
            elif now > end_time and schedule['is_on']:
                deactivate_pump(schedule['pump_id'])
                update_schedule_status(schedule['schedule_id'], 'completed')
                logger.info(
                    f"⏹️ Pompe {schedule['pump_id']} arrêtée après la fin du planning {schedule['schedule_id']}.")

        conn.commit()
    except psycopg2.Error as e:
        logger.error(f"❌ Erreur lors de l'activation des pompes: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def verify_environmental_conditions(field_id: int) -> bool:
    """🌦️ Vérifie les conditions environnementales pour le champ donné."""
    cursor, conn = get_db_cursor()

    cursor.execute("""
        SELECT * FROM sensor_readings 
        WHERE field_id = %s 
        ORDER BY timestamp DESC LIMIT 1;
    """, (field_id,))
    reading = cursor.fetchone()

    cursor.close()
    conn.close()

    if reading:
        humidity = next((m['valeur'] for m in reading['measurements'] if m['type'] == 'humidity'), None)
        rainfall = next((m['valeur'] for m in reading['measurements'] if m['type'] == 'rainfall'), None)

        # Condition : humidité < 30% et pas de pluie récemment
        if humidity is not None and humidity < 30 and (rainfall is None or rainfall == 0):
            return True  # Conditions favorables
    return False


def activate_pump(pump_id: int):
    """🚿 Active une pompe spécifique."""
    cursor, conn = get_db_cursor()
    cursor.execute("""
        UPDATE pumps SET is_on = TRUE, status = 'active', last_start_time = NOW(), last_activated = NOW()
        WHERE id = %s;
    """, (pump_id,))
    conn.commit()
    cursor.close()
    conn.close()


def deactivate_pump(pump_id: int):
    """⏹️ Désactive une pompe spécifique."""
    cursor, conn = get_db_cursor()
    cursor.execute("""
        UPDATE pumps SET is_on = FALSE, status = 'idle', total_usage_time = total_usage_time + EXTRACT(EPOCH FROM (NOW() - last_start_time))
        WHERE id = %s;
    """, (pump_id,))
    conn.commit()
    cursor.close()
    conn.close()


def update_schedule_status(schedule_id: int, new_status: str):
    """🔄 Met à jour le statut du planning."""
    cursor, conn = get_db_cursor()
    cursor.execute("""
        UPDATE schedules SET status = %s, last_irrigation_time = NOW() 
        WHERE id = %s;
    """, (new_status, schedule_id))
    conn.commit()
    cursor.close()
    conn.close()
