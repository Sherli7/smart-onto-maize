from fastapi import APIRouter, HTTPException
from models.scheduleModel import create_schedule, get_schedules, get_schedule_by_id, update_schedule, delete_schedule, start_irrigation
from schema.scheduleSchema import ScheduleCreate, ScheduleUpdate, ScheduleResponse
import logging

# Configuration du logger en mode DEBUG
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Schedules"])


@router.post("", response_model=ScheduleResponse)
def add_schedule(schedule: ScheduleCreate):
    logger.debug("📩 Requête reçue pour ajouter un planning: %s", schedule.dict())

    # 🔥 Log détaillé pour les paramètres
    logger.debug(
        "🛠️ Paramètres envoyés: field_id=%s, start_date=%s, start_time=%s, duration=%s, status=%s, flow_rate=%s, pump_ids=%s",
        schedule.field_id, schedule.start_date, schedule.start_time, schedule.duration, schedule.status,
        schedule.flow_rate, schedule.pump_ids)

    try:
        schedule_id = create_schedule(
            schedule.field_id,
            schedule.start_date,
            schedule.start_time,
            schedule.duration,
            schedule.status,
            schedule.flow_rate,
            schedule.pump_ids  # Assure-toi que c'est bien un tableau ici
        )
        logger.debug("✅ ID du planning créé: %s", schedule_id)

        new_schedule = get_schedule_by_id(schedule_id)
        if not new_schedule:
            logger.error("⚠️ Erreur: le planning créé (ID %s) n'a pas été retrouvé en base", schedule_id)
            raise HTTPException(status_code=500, detail="Erreur lors de la récupération du planning après création")

        logger.debug("✅ Planning ajouté avec succès: %s", new_schedule)
        return ScheduleResponse.from_db(new_schedule)
    except Exception as e:
        logger.error("❌ Erreur lors de l'ajout du planning: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=list[ScheduleResponse])
def list_schedules():
    logger.debug("📥 Requête reçue pour récupérer tous les plannings")
    schedules = get_schedules()
    logger.debug("📄 %d plannings récupérés", len(schedules))
    return [ScheduleResponse.from_db(s) for s in schedules]

@router.get("/{schedule_id}", response_model=ScheduleResponse)
def retrieve_schedule(schedule_id: int):
    logger.debug("🔍 Requête reçue pour récupérer le planning ID: %s", schedule_id)
    schedule = get_schedule_by_id(schedule_id)
    if not schedule:
        logger.warning("⚠️ Planning introuvable: ID %s", schedule_id)
        raise HTTPException(status_code=404, detail="Planning non trouvé")

    logger.debug("✅ Planning trouvé: %s", schedule)
    return ScheduleResponse.from_db(schedule)

@router.put("/{schedule_id}", response_model=ScheduleResponse)
def modify_schedule(schedule_id: int, updates: ScheduleUpdate):
    logger.debug("🛠️ Requête reçue pour modifier le planning ID: %s avec: %s", schedule_id, updates.dict())
    updated_schedule = update_schedule(schedule_id, updates.dict(exclude_unset=True))

    if not updated_schedule:
        logger.warning("⚠️ Aucun planning mis à jour: ID %s", schedule_id)
        raise HTTPException(status_code=404, detail="Planning non trouvé")

    logger.debug("✅ Planning mis à jour avec succès: %s", updated_schedule)
    return ScheduleResponse.from_db(updated_schedule)

@router.delete("/{schedule_id}")
def remove_schedule(schedule_id: int):
    logger.debug("🗑️ Requête reçue pour supprimer le planning ID: %s", schedule_id)
    try:
        deleted_id = delete_schedule(schedule_id)
        if not deleted_id:
            logger.warning("⚠️ Suppression échouée, planning ID %s introuvable", schedule_id)
            raise HTTPException(status_code=404, detail="Planning non trouvé")

        logger.debug("✅ Planning supprimé avec succès: ID %s", schedule_id)
        return {"message": "Planning supprimé avec succès"}
    except Exception as e:
        logger.error("❌ Erreur lors de la suppression du planning ID %s: %s", schedule_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur lors de la suppression du planning")

@router.post("/{schedule_id}/start", response_model=ScheduleResponse)
def start_schedule(schedule_id: int):
    logger.debug("🚀 Requête reçue pour démarrer l'irrigation du planning ID: %s", schedule_id)
    try:
        schedule = start_irrigation(schedule_id)
        if not schedule:
            logger.warning("⚠️ Impossible de démarrer l'irrigation: le planning ID %s est inexistant ou déjà en cours", schedule_id)
            raise HTTPException(status_code=400, detail="Impossible de démarrer l'irrigation: planning inexistant ou déjà en cours")

        logger.debug("✅ Irrigation démarrée avec succès: %s", schedule)
        return ScheduleResponse.from_db(schedule)
    except Exception as e:
        logger.error("❌ Erreur lors du démarrage de l'irrigation ID %s: %s", schedule_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
