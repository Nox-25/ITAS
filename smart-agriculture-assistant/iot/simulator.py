import paho.mqtt.client as mqtt
import time
import json
import random
import argparse

BROKER = "localhost"
PORT = 1883
TOPIC = "farm/sensors/readings"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

def simulate_data(farm_id=1):
    return {
        "farm_id": farm_id,
        "temperature": round(random.uniform(20.0, 35.0), 2),
        "humidity": round(random.uniform(40.0, 90.0), 2),
        "soil_moisture": round(random.uniform(10.0, 60.0), 2),
        "soil_ph": round(random.uniform(5.5, 7.5), 2),
        "nitrogen": round(random.uniform(20.0, 100.0), 2),
        "phosphorus": round(random.uniform(10.0, 60.0), 2),
        "potassium": round(random.uniform(10.0, 80.0), 2),
    }

def run_simulator(broker=BROKER, port=PORT, interval=5):
    client = mqtt.Client(client_id="virtual_sensor_node")
    client.on_connect = on_connect

    try:
        client.connect(broker, port, 60)
    except Exception as e:
        print(f"Error connecting to MQTT Broker: {e}")
        return

    client.loop_start()

    print(f"Publishing simulated data to {TOPIC} every {interval} seconds...")
    try:
        while True:
            data = simulate_data()
            client.publish(TOPIC, json.dumps(data))
            print(f"Published: {data}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Stopping simulator...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Virtual IoT Sensor Simulator")
    parser.add_argument("--broker", type=str, default=BROKER, help="MQTT Broker address")
    parser.add_argument("--port", type=int, default=PORT, help="MQTT Broker port")
    parser.add_argument("--interval", type=int, default=5, help="Simulation interval in seconds")

    args = parser.parse_args()
    run_simulator(args.broker, args.port, args.interval)
