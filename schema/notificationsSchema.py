from pydantic import BaseModel, Field
from datetime import datetime

class NotificationBase(BaseModel):
    message: str
    # On accepte "type" en entrée JSON, mais on le stocke dans notification_type
    notification_type: str
    timestamp: datetime = Field(default_factory=datetime.now)
    read: bool = False

    class Config:
        allow_population_by_field_name = True


class NotificationCreate(NotificationBase):
    """📩 Schéma pour la création d'une notification"""
    pass  # Utilise les mêmes champs que NotificationBase

class NotificationResponse(NotificationBase):
    """📤 Schéma pour la réponse d'une notification."""
    id: int = Field(..., example=1)

    class Config:
        orm_mode = True
