from pydantic import BaseModel, Field
from typing import Optional

class CropBase(BaseModel):
    """📋 Modèle de base pour les cultures"""
    name: str = Field(..., min_length=3, max_length=100, description="Nom de la culture")
    lifecycle_duration: int = Field(..., gt=0, description="Durée du cycle de vie")
    unit: str = Field(..., description="Unité de mesure ('months' ou 'days')")

class CropCreate(CropBase):
    """🆕 Création d'une culture"""
    pass

class CropUpdate(BaseModel):
    """🔄 Mise à jour d'une culture"""
    name: Optional[str] = None
    lifecycle_duration: Optional[int] = None
    unit: Optional[str] = None

class CropResponse(CropBase):
    """📊 Réponse complète d'une culture"""
    id: int
