from fastapi import APIRouter, HTTPException
from typing import List

from models.notificationModel import (
    get_notifications,
    get_notification_by_id,
    create_notification,
    mark_notification_as_read,
    deactivate_notification
)
from schema.notificationsSchema import NotificationResponse, NotificationCreate

router = APIRouter(prefix="", tags=["Notifications"])

@router.get("", response_model=List[NotificationResponse])
def fetch_notifications():
    """🔍 Récupérer toutes les notifications actives"""
    return get_notifications()

@router.get("/{notification_id}", response_model=NotificationResponse)
def fetch_notification_by_id(notification_id: int):
    """🔍 Récupérer une notification spécifique par ID"""
    notification = get_notification_by_id(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    return notification

@router.post("", response_model=NotificationResponse)
def create_new_notification(notification: NotificationCreate):
    """📩 Créer une nouvelle notification"""
    notification_id = create_notification(
        message=notification.message,
        notification_type=notification.notification_type,  # <-- Renommé ici
        timestamp=notification.timestamp
    )
    # Retourne l'objet créé avec son ID
    return {
        **notification.dict(),
        "id": notification_id
    }

@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_as_read(notification_id: int):
    """✅ Marquer une notification comme lue"""
    updated_notification = mark_notification_as_read(notification_id)
    if not updated_notification:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    return updated_notification

@router.put("/{notification_id}/deactivate", response_model=NotificationResponse)
def disable_notification(notification_id: int):
    """🛑 Désactiver une notification sans la supprimer"""
    updated_notification = deactivate_notification(notification_id)
    if not updated_notification:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    return updated_notification
