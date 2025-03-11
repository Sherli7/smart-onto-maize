import logging
from fastapi import APIRouter, HTTPException
from models.pumpModel import create_pump, get_pump_by_id, get_pumps, update_pump, delete_pump, toggle_pump
from schema.pumpSchema import PumpResponse, PumpCreate, PumpUpdate

# ✅ Configuration du logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Pumps"])


@router.post("", response_model=PumpResponse)
def add_pump(pump: PumpCreate):
    """🆕 Ajouter une nouvelle pompe"""
    logger.info(f"🚀 Ajout d'une pompe : {pump.name} (Field ID: {pump.field_id})")

    pump_id = create_pump(pump.name, pump.field_id)
    if not pump_id:
        logger.error(f"❌ Échec de la création de la pompe : {pump.name}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création de la pompe")

    logger.info(f"✅ Pompe créée avec succès - ID: {pump_id}")
    return get_pump_by_id(pump_id)


@router.get("", response_model=list[PumpResponse])
def list_pumps():
    """📋 Lister toutes les pompes"""
    logger.info("📡 Récupération de la liste des pompes...")

    pumps = get_pumps()
    logger.info(f"✅ {len(pumps)} pompes trouvées.")

    return pumps


@router.get("/{pump_id}", response_model=PumpResponse)
def retrieve_pump(pump_id: int):
    """🔍 Récupérer une pompe spécifique"""
    logger.info(f"🔎 Recherche de la pompe ID: {pump_id}")

    pump = get_pump_by_id(pump_id)
    if not pump:
        logger.warning(f"⚠️ Pompe non trouvée - ID: {pump_id}")
        raise HTTPException(status_code=404, detail="Pompe non trouvée")

    logger.info(f"✅ Pompe trouvée - ID: {pump_id}")
    return pump


@router.put("/{pump_id}", response_model=PumpResponse)
def modify_pump(pump_id: int, updates: PumpUpdate):
    """🛠 Modifier une pompe"""
    logger.info(f"✏️ Modification de la pompe ID: {pump_id} avec les données : {updates.dict(exclude_unset=True)}")

    updated_pump = update_pump(pump_id, updates.dict(exclude_unset=True))
    if not updated_pump:
        logger.warning(f"⚠️ Pompe non trouvée pour modification - ID: {pump_id}")
        raise HTTPException(status_code=404, detail="Pompe non trouvée")

    logger.info(f"✅ Pompe mise à jour avec succès - ID: {pump_id}")
    return updated_pump


@router.delete("/{pump_id}")
def remove_pump(pump_id: int):
    """🗑 Supprimer une pompe"""
    logger.info(f"🗑 Suppression de la pompe ID: {pump_id}")

    success = delete_pump(pump_id)
    if not success:
        logger.warning(f"⚠️ Pompe non trouvée pour suppression - ID: {pump_id}")
        raise HTTPException(status_code=404, detail="Pompe non trouvée")

    logger.info(f"✅ Pompe supprimée avec succès - ID: {pump_id}")
    return {"message": "Pompe supprimée avec succès"}


@router.post("/{pump_id}/toggle", response_model=PumpResponse)
def switch_pump(pump_id: int):
    """🔁 Allumer ou éteindre une pompe"""
    logger.info(f"🔄 Changement d'état de la pompe ID: {pump_id}")

    pump = toggle_pump(pump_id)
    if not pump:
        logger.warning(f"⚠️ Pompe non trouvée - ID: {pump_id}")
        raise HTTPException(status_code=404, detail="Pompe non trouvée")

    # ✅ Correction : Utilisation de pump['is_on'] au lieu de pump.is_on
    logger.info(f"✅ Pompe ID {pump_id} mise à jour - État actuel: {'ON' if pump['is_on'] else 'OFF'}")
    return pump
