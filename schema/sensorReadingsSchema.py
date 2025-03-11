from pydantic import BaseModel
from typing import List, Union

class Measurement(BaseModel):
    type: str
    valeur: Union[float, dict]  # ✅ Supporte NPK qui a plusieurs valeurs
    unit: str
    timestamp: str

class SensorReading(BaseModel):
    sensor_id: int
    field_id: int
    raw_data: List[Measurement]  # ✅ Remplace `measurements`
