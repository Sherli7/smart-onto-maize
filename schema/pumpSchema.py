from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class PumpBase(BaseModel):
    """📋 Modèle de base pour la pompe"""
    name: str = Field(..., min_length=3, max_length=100)
    field_id: int

class PumpCreate(PumpBase):
    """🆕 Création d'une pompe"""
    pass

class PumpUpdate(BaseModel):
    """🔄 Mise à jour d'une pompe"""
    name: Optional[str] = None
    field_id: Optional[int] = None
    is_on: Optional[bool] = None
    status: Optional[str] = None
    water_flow: Optional[float] = None
    elapsed_time: Optional[float] = None
    # On utilise datetime pour les champs temporels
    last_start_time: Optional[datetime] = None
    last_activated: Optional[datetime] = None
    total_usage_time: Optional[float] = None
    power_consumption: Optional[float] = None
    maintenance_status: Optional[str] = None
    last_maintenance: Optional[datetime] = None

class PumpResponse(PumpBase):
    """📊 Réponse complète de la pompe"""
    id: int
    is_on: bool
    status: str
    water_flow: float
    elapsed_time: float
    last_start_time: Optional[datetime]
    last_activated: Optional[datetime]
    total_usage_time: float
    power_consumption: float
    maintenance_status: str
    last_maintenance: Optional[datetime]
