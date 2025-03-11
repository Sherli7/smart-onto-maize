from fastapi import APIRouter, HTTPException
from models.sensorModel import create_sensor, get_sensors, get_sensor_by_id, update_sensor, delete_sensor
from schema.sensorSchema import SensorCreate, SensorUpdate, SensorResponse

router = APIRouter(prefix="", tags=["Sensors"])

@router.post("", response_model=SensorResponse)
def add_sensor(sensor: SensorCreate):
    sensor_id = create_sensor(sensor.name, sensor.type, sensor.location, sensor.latitude, sensor.longitude, sensor.installation_date, sensor.status, sensor.field_id)
    return get_sensor_by_id(sensor_id)

@router.get("", response_model=list[SensorResponse])
def list_sensors():
    return get_sensors()

@router.get("/{sensor_id}", response_model=SensorResponse)
def retrieve_sensor(sensor_id: int):
    sensor = get_sensor_by_id(sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Capteur non trouvé")
    return sensor

@router.put("/{sensor_id}", response_model=SensorResponse)
def modify_sensor(sensor_id: int, updates: SensorUpdate):
    updated_sensor = update_sensor(sensor_id, updates.dict(exclude_unset=True))
    if not updated_sensor:
        raise HTTPException(status_code=404, detail="Capteur non trouvé")
    return updated_sensor

@router.delete("/{sensor_id}")
def remove_sensor(sensor_id: int):
    delete_sensor(sensor_id)
    return {"message": "Capteur supprimé avec succès"}
