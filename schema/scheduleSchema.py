from datetime import date, time, timedelta
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, conlist


class StatusEnum(str, Enum):
    planned = 'planned'
    in_progress = 'in_progress'
    completed = 'completed'
    cancelled = 'cancelled'

class ScheduleBase(BaseModel):
    """📋 Modèle de base pour les plannings"""
    field_id: int
    start_date: str = Field(
        ..., pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Date de début (format: 'YYYY-MM-DD')"
    )
    start_time: str = Field(
        ..., pattern=r"^\d{2}:\d{2}(:\d{2})?$",
        description="Heure de début (format: 'HH:MM:SS')"
    )
    duration: str = Field(..., description="Durée en INTERVAL PostgreSQL (ex: '30 minutes')")
    status: StatusEnum = Field(..., description="État du planning ('planned', 'in_progress', 'completed', 'cancelled')")
    flow_rate: float = Field(..., description="Débit d'irrigation en L/min")
    pump_ids: conlist(int) | None  # ✅ Assurer que la liste contient uniquement des entiers

class ScheduleCreate(ScheduleBase):
    """🆕 Création d'un planning"""
    pass

class ScheduleUpdate(BaseModel):
    """🔄 Mise à jour d'un planning"""
    field_id: Optional[int] = None
    start_date: Optional[str] = Field(
        None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date de début (format: 'YYYY-MM-DD')"
    )
    start_time: Optional[str] = Field(
        None, pattern=r"^\d{2}:\d{2}(:\d{2})?$", description="Heure de début (format: 'HH:MM:SS')"
    )
    duration: Optional[str] = None
    status: Optional[StatusEnum] = None  # ✅ Utilisation de l'Enum pour validation stricte
    last_irrigation_time: Optional[str] = None
    flow_rate: Optional[float] = None
    pump_ids: Optional[conlist(int)] = None  # ✅ Vérification que la liste ne contient que des entiers

class ScheduleResponse(ScheduleBase):
    """📊 Réponse complète d'un planning"""
    id: int
    last_irrigation_time: Optional[str] = None

    @classmethod
    def from_db(cls, schedule: dict):
        """Transforme un objet récupéré de la base en une réponse valide"""
        return cls(
            id=schedule["id"],
            field_id=schedule["field_id"],
            start_date=schedule["start_date"].strftime("%Y-%m-%d") if isinstance(schedule["start_date"], date) else schedule["start_date"],
            start_time=schedule["start_time"].strftime("%H:%M:%S") if isinstance(schedule["start_time"], time) else schedule["start_time"],
            duration=str(schedule["duration"]) if isinstance(schedule["duration"], timedelta) else schedule["duration"],
            status=schedule["status"],
            flow_rate=schedule["flow_rate"],
            last_irrigation_time=schedule["last_irrigation_time"].strftime("%Y-%m-%d %H:%M:%S") if schedule.get("last_irrigation_time") and isinstance(schedule["last_irrigation_time"], (date, time)) else schedule["last_irrigation_time"],
            pump_ids=schedule.get("pump_ids", [])
        )
