from fastapi import APIRouter, HTTPException
from models.sensorsReadingsModel import SensorReadingsModel
from schema.sensorReadingsSchema import SensorReading
import paho.mqtt.client as mqtt
import json
import random
import time

MQTT_BROKER = "localhost"  # Vérifiez que c'est correct
MQTT_PORT = 1883  # Port MQTT
REQUEST_TOPIC = "irrigation_system/+/request"
RESPONSE_TOPIC_TEMPLATE = "irrigation_system/{}/response"

router = APIRouter(prefix="", tags=["sensors Readings"])

@router.get("/all")
def get_all_sensor_readings():
    """ Récupère toutes les mesures des capteurs avec les noms des capteurs et champs. """
    readings = SensorReadingsModel.get_all_sensor_readings_with_names()
    if readings:
        return readings
    raise HTTPException(status_code=404, detail="Aucune mesure trouvée.")


@router.get("/latest")
def get_latest_sensor_readings():
    """ Récupère uniquement la dernière mesure de chaque capteur """
    readings = SensorReadingsModel.get_latest_sensor_readings()
    if readings:
        return readings
    raise HTTPException(status_code=404, detail="Aucune mesure trouvée.")

@router.post("/add")
def create_sensor_reading(sensor_data: SensorReading):
    """ Ajoute une mesure à un capteur """
    if not SensorReadingsModel.is_sensor_active(sensor_data.sensor_id):
        raise HTTPException(status_code=400, detail=f"Le capteur {sensor_data.sensor_id} est inactif ou inexistant.")
    SensorReadingsModel.save_sensor_data(sensor_data)
    return {"message": f"Données du capteur {sensor_data.sensor_id} enregistrées avec succès."}

@router.get("/{sensor_id}")
def get_sensor_reading(sensor_id: int):
    """ Récupère les données d'un capteur spécifique """
    data = SensorReadingsModel.get_sensor_data(sensor_id)
    if data:
        return data
    raise HTTPException(status_code=404, detail=f"Aucune donnée trouvée pour le capteur {sensor_id}.")

@router.get("/status")
def get_all_sensors_status():
    """ Récupère la liste des capteurs et leur statut """
    sensors = SensorReadingsModel.get_all_sensors_status()
    if sensors:
        return sensors
    raise HTTPException(status_code=404, detail="Aucun capteur trouvé.")

@router.post("/request_measures")
def request_measures_from_active_sensors():
    """ Envoie une requête aux capteurs actifs pour récupérer de nouvelles mesures """
    active_sensors = SensorReadingsModel.get_active_sensors()
    if not active_sensors:
        raise HTTPException(status_code=404, detail="Aucun capteur actif trouvé.")

    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    for sensor_id in active_sensors:
        topic = f"irrigation_system/{sensor_id}/request"
        message = json.dumps({"command": "take_measurement"})
        client.publish(topic, message)
        print(f"📤 Demande envoyée à {topic} : {message}")

    client.disconnect()
    return {"message": "Requêtes envoyées aux capteurs actifs."}

def generate_fake_measurements(sensor_id, sensor_type):
    """ Génère des mesures cohérentes en fonction du type de capteur. """
    sensor_data_map = {
        "humidity": {"type": "Humidité", "min": 10, "max": 50, "unit": "%"},
        "temperature": {"type": "Température", "min": 15, "max": 40, "unit": "°C"},
        "pluviometry": {"type": "Pluviométrie", "min": 0, "max": 20, "unit": "mm"},
        "potential_hydrogen": {"type": "pH", "min": 5, "max": 8, "unit": ""}
    }

    # ✅ Récupérer le vrai `field_id` du capteur
    field_id = SensorReadingsModel.get_field_id_by_sensor(sensor_id)
    if field_id is None:
        print(f"⚠️ Impossible de récupérer le champ pour le capteur {sensor_id}, valeur par défaut: 1")
        field_id = 1  # Valeur de secours

    raw_data = []

    # ✅ Gestion spéciale du NPK (3 valeurs en 1)
    if sensor_type == "npk":
        raw_data.append({
            "type": "NPK",
            "valeur": {
                "N": round(random.uniform(1, 10), 2),
                "P": round(random.uniform(1, 10), 2),
                "K": round(random.uniform(1, 10), 2)
            },
            "unit": "mg/kg",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })

    # ✅ Génération de données pour les autres capteurs
    elif sensor_type in sensor_data_map:
        measure = sensor_data_map[sensor_type]
        raw_data.append({
            "type": measure["type"],
            "valeur": round(random.uniform(measure["min"], measure["max"]), 2),
            "unit": measure["unit"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })

    return {
        "sensor_id": sensor_id,
        "field_id": field_id,  # ✅ Maintenant, on prend le vrai `field_id`
        "raw_data": raw_data
    }

def on_message(client, userdata, msg):
    """ Fonction déclenchée lorsqu'un message MQTT est reçu """
    try:
        payload = json.loads(msg.payload.decode())
        topic_parts = msg.topic.split("/")
        if len(topic_parts) < 3:
            print(f"⚠️ Format de topic invalide: {msg.topic}")
            return

        sensor_id = int(topic_parts[1])
        sensor_type = SensorReadingsModel.get_sensor_type(sensor_id)

        if payload.get("command") == "take_measurement":
            print(f"📡 Capteur {sensor_id} ({sensor_type}) a reçu une demande de mesure.")
            sensor_data = generate_fake_measurements(sensor_id, sensor_type)
            response_topic = RESPONSE_TOPIC_TEMPLATE.format(sensor_id)
            client.publish(response_topic, json.dumps(sensor_data))
            print(f"📤 Réponse envoyée à {response_topic} : {sensor_data}")
            SensorReadingsModel.save_sensor_data(SensorReading(**sensor_data))
    except Exception as e:
        print(f"❌ Erreur dans le listener MQTT : {e}")

mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.subscribe(REQUEST_TOPIC)
mqtt_client.loop_start()
