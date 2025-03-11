import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from database.init_db import init_database
from routes.auth import router as auth_router
from routes.cropRouter import router as crop_router
from routes.fieldRouter import router as field_router
from routes.iotDataRouter import router as iot_data_router  # Ajout de la route IoT Data
from routes.pumpRouter import router as pump_router
from routes.scheduleRouter import router as schedule_router
from routes.notificationsRoute import router as notifications_router
from routes.sensorRouter import router as sensor_router
from routes.sensorsReadingsRoute import router as sensorsReadings_router

# ✅ Configuration du logging
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)

init_database()
# ✅ Initialisation de FastAPI
app = FastAPI(
    title="Smart Irrigation System API",
    description="API de gestion intelligente de l'irrigation avec capteurs et planification.",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ✅ Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autoriser toutes les origines (à adapter en production)
    allow_methods=["*"],  # Autoriser toutes les méthodes (GET, POST, etc.)
    allow_headers=["*"],  # Autoriser tous les en-têtes
)

# ✅ Ajout des routes API
app.include_router(auth_router, prefix="/api/auth", tags=["Authentification"])
app.include_router(pump_router, prefix="/api/pumps", tags=["Pumps"])
app.include_router(sensorsReadings_router, prefix="/api/sensorsReadings", tags=["sensors Readings"])
app.include_router(schedule_router, prefix="/api/schedules", tags=["Schedules"])
app.include_router(field_router, prefix="/api/fields", tags=["Fields"])
app.include_router(crop_router, prefix="/api/crops", tags=["Crops"])
app.include_router(sensor_router, prefix="/api/sensors", tags=["Sensors"])
app.include_router(notifications_router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(iot_data_router, prefix="/api/iot-data", tags=["ioTDataReader"])  # Intégration de la route IoT Data

# ✅ Route principale pour vérifier l'état de l'API
@app.get("/", tags=["Root"])
def root():
    return {"message": "Bienvenue sur l'API de Smart Irrigation System 🚀"}



# ✅ Personnalisation de l'interface OpenAPI/Swagger
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Smart Irrigation System API",
        version="1.1.0",
        description="API permettant la gestion intelligente de l'irrigation avec intégration des capteurs, gestion des pompes, planification avancée et suivi des utilisateurs.",
        routes=app.routes,
    )
    openapi_schema["info"]["contact"] = {
        "name": "Support Smart Irrigation",
        "email": "support@smartirrigation.com",
        "url": "https://smartirrigation.com/contact",
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema
app.openapi = custom_openapi
