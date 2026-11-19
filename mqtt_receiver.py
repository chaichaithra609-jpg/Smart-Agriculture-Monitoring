
import json
import sqlite3
import paho.mqtt.client as mqtt

BROKER = "broker.emqx.io"
PORT = 1883
TOPIC = "smart_agriculture_demo/chaitra/farm01"
DATABASE = "agriculture.db"


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to MQTT broker!")
        client.subscribe(TOPIC)
        print("Listening for sensor readings...")
    else:
        print("Connection failed:", reason_code)


def on_message(client, userdata, message):
    try:
        data = json.loads(message.payload.decode())

        connection = sqlite3.connect(DATABASE, timeout=10)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO sensor_readings
            (timestamp, soil_moisture, temperature, humidity, light_intensity)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data["timestamp"],
            data["soil_moisture"],
            data["temperature"],
            data["humidity"],
            data["light_intensity"]
        ))

        connection.commit()
        connection.close()

        print("Saved sensor reading:", data)

    except Exception as error:
        print("Error:", error)


client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = on_connect
client.on_message = on_message

print("Starting MQTT Receiver...")

client.connect(BROKER, PORT, 60)
client.loop_forever()
