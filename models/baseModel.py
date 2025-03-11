# baseModel.py

from enum import Enum

# ✅ Enum pour les rôles des utilisateurs
class UserRole(str, Enum):
    admin = "admin"
    farmer = "farmer"
    other = "other"  # ✅ Assurez-vous que cette valeur est bien définie


# ✅ Enum pour les types de capteurs
class SensorType(str, Enum):
    HUMIDITY = "humidity"
    TEMPERATURE = "temperature"
    NPK = "npk"
    PLUVIOMETRY = "pluviometry",
    PH= "potential_hudrogen"

# ✅ Enum pour le statut des capteurs
class SensorStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

# ✅ Enum pour le statut de la planification
class ScheduleStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
