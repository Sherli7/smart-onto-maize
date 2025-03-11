from database.database import get_db_cursor
import psycopg2
from datetime import datetime


def create_notification(
        message: str,
        notification_type: str,
        timestamp: str = None,
        read: bool = False,
        active: bool = True
):
    """📩 Créer une nouvelle notification"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        try:
            # Si aucun timestamp n'est fourni, on prend l'heure actuelle en UTC
            if not timestamp:
                timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

            # Insérer dans la colonne notification_type et non 'type'
            cursor.execute("""
                INSERT INTO notifications (message, notification_type, timestamp, read, active)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (message, notification_type, timestamp, read, active))

            notification_id = cursor.fetchone()["id"]
            conn.commit()
            cursor.close()
            conn.close()
            return notification_id

        except psycopg2.Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            raise Exception(f"❌ Erreur lors de la création de la notification : {e}")


def get_notifications():
    """🔍 Récupérer toutes les notifications actives"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        cursor.execute("SELECT * FROM notifications WHERE active = TRUE ORDER BY timestamp DESC;")
        notifications = cursor.fetchall()

        # ✅ Convertir le champ timestamp en format lisible
        for notification in notifications:
            if notification["timestamp"]:
                notification["timestamp"] = notification["timestamp"].strftime('%Y-%m-%d %H:%M:%S')

        cursor.close()
        conn.close()
        return notifications


def get_notification_by_id(notification_id: int):
    """🔍 Récupérer une notification spécifique"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        cursor.execute("SELECT * FROM notifications WHERE id = %s;", (notification_id,))
        notification = cursor.fetchone()

        if notification and notification["timestamp"]:
            notification["timestamp"] = notification["timestamp"].strftime('%Y-%m-%d %H:%M:%S')

        cursor.close()
        conn.close()
        return notification


def mark_notification_as_read(notification_id: int):
    """✅ Marquer une notification comme lue"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        cursor.execute("""
            UPDATE notifications
               SET read = TRUE
             WHERE id = %s
         RETURNING *;
        """, (notification_id,))
        updated_notification = cursor.fetchone()
        conn.commit()

        if updated_notification and updated_notification["timestamp"]:
            updated_notification["timestamp"] = updated_notification["timestamp"].strftime('%Y-%m-%d %H:%M:%S')

        cursor.close()
        conn.close()
        return updated_notification


def deactivate_notification(notification_id: int):
    """🛑 Désactiver une notification au lieu de la supprimer"""
    cursor, conn = get_db_cursor()
    if cursor and conn:
        cursor.execute("""
            UPDATE notifications
               SET active = FALSE
             WHERE id = %s
         RETURNING *;
        """, (notification_id,))
        updated_notification = cursor.fetchone()
        conn.commit()

        cursor.close()
        conn.close()
        return updated_notification
