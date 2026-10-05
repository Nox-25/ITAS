import paho.mqtt.client as mqtt
import json
import threading
from backend.database import SessionLocal
from backend.models import SensorReading

BROKER = "localhost"
PORT = 1883
TOPIC = "farm/sensors/readings"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Backend connected to MQTT Broker!")
        client.subscribe(TOPIC)
    else:
        print(f"Failed to connect backend MQTT subscriber, return code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        save_reading(payload)
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

def save_reading(data):
    db = SessionLocal()
    try:
        new_reading = SensorReading(
            farm_id=data.get("farm_id", 1),
            temperature=data.get("temperature"),
            humidity=data.get("humidity"),
            soil_moisture=data.get("soil_moisture"),
            soil_ph=data.get("soil_ph"),
            nitrogen=data.get("nitrogen"),
            phosphorus=data.get("phosphorus"),
            potassium=data.get("potassium"),
        )
        db.add(new_reading)
        db.commit()
    except Exception as e:
        print(f"Database error: {e}")
        db.rollback()
    finally:
        db.close()

def start_mqtt_subscriber():
    client = mqtt.Client(client_id="fastapi_backend")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()
    except Exception as e:
        print(f"Could not start backend MQTT subscriber: {e}")

def init_mqtt():
    thread = threading.Thread(target=start_mqtt_subscriber, daemon=True)
    thread.start()
