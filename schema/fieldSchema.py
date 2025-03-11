from pydantic import BaseModel, Field
from typing import Optional

from datetime import date

class FieldBase(BaseModel):
    """📋 Modèle de base pour les champs"""
    name: str = Field(..., min_length=3, max_length=100, description="Nom du champ")
    location: str = Field(..., max_length=255, description="Localisation du champ")
    latitude: float = Field(..., description="Latitude du champ")
    longitude: float = Field(..., description="Longitude du champ")
    size: float = Field(..., gt=0, description="Superficie du champ (en hectares)")
    sensor_density: float = Field(..., gt=0, description="Densité des capteurs par m²")
    crop_type_id: Optional[int] = Field(None, description="ID du type de culture")
    planting_date: Optional[date] = Field(None, description="Date de plantation (format YYYY-MM-DD)")

class FieldCreate(FieldBase):
    """🆕 Création d'un champ"""
    pass

class FieldUpdate(BaseModel):
    """🔄 Mise à jour d'un champ"""
    name: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    size: Optional[float] = None
    sensor_density: Optional[float] = None
    crop_type_id: Optional[int] = None
    planting_date: Optional[str] = None

class FieldResponse(FieldBase):
    """📊 Réponse complète d'un champ"""
    id: int
