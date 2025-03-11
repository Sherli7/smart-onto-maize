import paho.mqtt.client as mqtt
import json
import time
from inference.inference_engine import InferenceEngine

# Configuration du broker MQTT
BROKER_ADDRESS = "localhost"
BROKER_PORT = 1883


def generate_topic(base, sensor_type, location, data_type):
    """
    Génère un topic MQTT basé sur le type de capteur, la localisation et le type de données.
    :param base: Base du topic (ex: "irrigation_system")
    :param sensor_type: Type de capteur (ex: "humidity", "temperature")
    :param location: Localisation du capteur (ex: "field_A", "zone_1")
    :param data_type: Type de données (ex: "sensors", "decision")
    :return: Topic MQTT complet
    """
    return f"{base}/{location}/{sensor_type}/{data_type}"



# Initialisation du moteur d'inférence
inference_engine = InferenceEngine("../data/model.pkl")

# Gestion des états des capteurs
sensor_status = {}
sensor_data = {}  # Stockage des dernières données reçues
SENSOR_TIMEOUT = 60  # Temps en secondes avant de considérer un capteur comme inactif


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("👌 Connexion réussie au broker MQTT")
        client.subscribe("irrigation_system/+/sensors")  # Souscription à tous les capteurs
    else:
        print(f"❌ Échec de connexion au broker MQTT, code de retour : {rc}")


# Callback lors de la réception de données
def on_message(client, userdata, msg):
    try:
        if not msg.payload:
            print("⚠️ Données MQTT vides reçues.")
            return

        payload = json.loads(msg.payload.decode())
        sensor_id = payload.get("sensor_id", "unknown")
        timestamp = time.time()

        # Mise à jour du statut du capteur
        sensor_status[sensor_id] = timestamp
        sensor_data[sensor_id] = payload  # Stockage des données brutes du capteur
        print(f"📥 Données reçues de {sensor_id}: {payload}")

        # Extraction des caractéristiques pour l'inférence
        features = [
            payload.get('volumetric_water_content', 0),
            payload.get('soil_temperature', 0),
            payload.get('electrical_conductivity', 0),
            payload.get('ambient_temperature', 0),
            payload.get('rainfall_intensity', 0),
            payload.get('NPK_concentration', 0)
        ]

        # Lancer l'inférence automatiquement
        decision = inference_engine.predict_action(features)
        print(f"🤖 Décision prise : {decision}")

        # Générer le topic de réponse dynamiquement
        response_topic = generate_topic("irrigation_system", sensor_id, "decision")

        # Publier la décision sur un topic MQTT
        response_payload = json.dumps({"sensor_id": sensor_id, "decision": decision})
        client.publish(response_topic, response_payload)
        print(f"📤 Décision envoyée pour {sensor_id} sur {response_topic}: {response_payload}")

    except json.JSONDecodeError:
        print("⚠️ Erreur : Données JSON invalides.")
    except Exception as e:
        print(f"⚠️ Erreur lors du traitement des données : {e}")


# Fonction de vérification des capteurs inactifs
def check_sensor_status():
    current_time = time.time()
    for sensor, last_seen in list(sensor_status.items()):
        if current_time - last_seen > SENSOR_TIMEOUT:
            print(f"❌ Capteur {sensor} inactif depuis {SENSOR_TIMEOUT} secondes.")
            del sensor_status[sensor]
            del sensor_data[sensor]


# Fonction pour récupérer les dernières données des capteurs
def get_latest_sensor_data():
    """
    Retrieve the latest sensor data received via MQTT.
    :return: Dictionary containing sensor data or error message.
    """
    if not sensor_data:
        return {"error": "No sensor data available."}

    return {
        sensor_id: {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(sensor_status[sensor_id])),
            "data": data
        }
        for sensor_id, data in sensor_data.items()
    }


# Configuration du client MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

# Connexion au broker
client.connect(BROKER_ADDRESS, BROKER_PORT)

# Boucle infinie pour écouter les messages et surveiller les capteurs
if __name__ == "__main__":
    print("🚀 Démarrage de l'écoute MQTT...")
    while True:
        client.loop(timeout=1.0)
        check_sensor_status()
        time.sleep(5)