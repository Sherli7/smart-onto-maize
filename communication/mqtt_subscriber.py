# communication/mqtt_subscriber.py

import paho.mqtt.client as mqtt
import json
from inference.inference_engine import InferenceEngine

# Configuration du broker MQTT
BROKER_ADDRESS = "localhost"
BROKER_PORT = 1883
TOPIC = "irrigation_system/sensors"
RESPONSE_TOPIC = "irrigation_system/decision"

# Initialisation du moteur d'inférence
inference_engine = InferenceEngine("../data/model.pkl")

# Callback lors de la connexion au broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connexion réussie au broker MQTT")
        client.subscribe(TOPIC)
    else:
        print(f"❌ Échec de connexion au broker MQTT, code de retour : {rc}")

# Callback lors de la réception de données
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"📥 Données reçues : {payload}")

        # Lancer l'inférence automatiquement
        decision = inference_engine.predict_action(payload)
        print(f"🤖 Décision prise : {decision}")

        # Publier la décision sur un topic MQTT
        response_payload = json.dumps({"decision": decision})
        client.publish(RESPONSE_TOPIC, response_payload)
        print(f"📤 Décision envoyée : {response_payload}")

    except Exception as e:
        print(f"⚠️ Erreur lors du traitement des données : {e}")

# Configuration du client MQTT
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message

# Connexion au broker
client.connect(BROKER_ADDRESS, BROKER_PORT)

# Boucle infinie pour écouter les messages
client.loop_forever()