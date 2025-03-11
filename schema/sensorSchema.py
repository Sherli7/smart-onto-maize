from pydantic import BaseModel, Field
from typing import Optional

class SensorBase(BaseModel):
    """📋 Modèle de base pour les capteurs"""
    name: str = Field(..., min_length=3, max_length=100, description="Nom du capteur")
    type: str = Field(..., min_length=3, max_length=100, description="Type de capteur")
    location: str = Field(..., max_length=255, description="Emplacement du capteur")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    installation_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date d'installation (format YYYY-MM-DD)")
    status: str = Field(..., description="Statut du capteur ('active', 'inactive', 'maintenance')")
    field_id: Optional[int] = Field(None, description="ID du champ associé")

class SensorCreate(SensorBase):
    """🆕 Création d'un capteur"""
    pass

class SensorUpdate(BaseModel):
    """🔄 Mise à jour d'un capteur"""
    name: Optional[str] = None
    type: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    installation_date: Optional[str] = None
    status: Optional[str] = None
    field_id: Optional[int] = None

class SensorResponse(SensorBase):
    """📊 Réponse complète d'un capteur"""
    id: int
