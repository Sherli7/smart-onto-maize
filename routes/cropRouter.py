from fastapi import APIRouter, HTTPException
from models.cropModel import create_crop, get_crops, get_crop_by_id, update_crop, delete_crop
from schema.cropSchema import CropCreate, CropUpdate, CropResponse

router = APIRouter(prefix="", tags=["Crops"])

@router.post("", response_model=CropResponse)
def add_crop(crop: CropCreate):
    crop_id = create_crop(crop.name, crop.lifecycle_duration, crop.unit)
    return get_crop_by_id(crop_id)

@router.get("", response_model=list[CropResponse])
def list_crops():
    return get_crops()

@router.get("/{crop_id}", response_model=CropResponse)
def retrieve_crop(crop_id: int):
    crop = get_crop_by_id(crop_id)
    if not crop:
        raise HTTPException(status_code=404, detail="Culture non trouvée")
    return crop

@router.put("/{crop_id}", response_model=CropResponse)
def modify_crop(crop_id: int, updates: CropUpdate):
    updated_crop = update_crop(crop_id, updates.dict(exclude_unset=True))
    if not updated_crop:
        raise HTTPException(status_code=404, detail="Culture non trouvée")
    return updated_crop

@router.delete("/{crop_id}")
def remove_crop(crop_id: int):
    delete_crop(crop_id)
    return {"message": "Culture supprimée avec succès"}
