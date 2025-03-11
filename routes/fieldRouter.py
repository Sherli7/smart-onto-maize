from fastapi import APIRouter, HTTPException
from models.fieldModel import create_field, get_fields, get_field_by_id, update_field, delete_field
from schema.fieldSchema import FieldCreate, FieldUpdate, FieldResponse

router = APIRouter(prefix="", tags=["Fields"])

@router.post("", response_model=FieldResponse)
def add_field(field: FieldCreate):
    print("📥 Requête reçue pour ajouter un champ:", field.dict())  # ✅ Voir les données reçues

    if not field.name or not field.location:
        raise HTTPException(status_code=400, detail="❌ Données invalides : certains champs sont vides.")

    field_id = create_field(
        field.name, field.location,field.latitude,field.longitude,field.size, field.sensor_density,
        field.crop_type_id, field.planting_date
    )

    response = get_field_by_id(field_id)
    print("✅ Champ créé avec succès:", response)  # ✅ Voir le champ inséré

    return response

@router.get("", response_model=list[FieldResponse])
def list_fields():
    return get_fields()

@router.get("/{field_id}", response_model=FieldResponse)
def retrieve_field(field_id: int):
    field = get_field_by_id(field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Champ non trouvé")
    return field

@router.put("/{field_id}", response_model=FieldResponse)
def modify_field(field_id: int, updates: FieldUpdate):
    updated_field = update_field(field_id, updates.dict(exclude_unset=True))
    if not updated_field:
        raise HTTPException(status_code=404, detail="Champ non trouvé")
    return updated_field

@router.delete("/{field_id}")
def remove_field(field_id: int):
    delete_field(field_id)
    return {"message": "Champ supprimé avec succès"}
