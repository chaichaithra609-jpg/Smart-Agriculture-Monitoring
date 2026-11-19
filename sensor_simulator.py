
import json
import random
import time
from datetime import datetime

import paho.mqtt.client as mqtt

BROKER = "broker.emqx.io"
PORT = 1883
TOPIC = "smart_agriculture_demo/chaitra/farm01"

connected = False


def on_connect(client, userdata, flags, reason_code, properties):
    global connected

    if reason_code == 0:
        connected = True
        print("Connected to EMQX MQTT broker!")
    else:
        connected = False
        print("Connection failed:", reason_code)


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    global connected
    connected = False
    print("Disconnected. Reconnecting...")


client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.reconnect_delay_set(min_delay=2, max_delay=10)

print("Starting Smart Agriculture Sensor Simulator...")

client.connect(BROKER, PORT, 60)
client.loop_start()

try:
    while True:
        if connected:
            data = {
                "timestamp": datetime.now().isoformat(),
                "soil_moisture": round(random.uniform(10, 80), 2),
                "temperature": round(random.uniform(20, 45), 2),
                "humidity": round(random.uniform(30, 90), 2),
                "light_intensity": round(random.uniform(1000, 10000), 2)
            }

            result = client.publish(TOPIC, json.dumps(data))

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print("Published:", json.dumps(data))
            else:
                print("Publishing failed.")

        else:
            print("Waiting for broker connection...")

        time.sleep(5)

except KeyboardInterrupt:
    print("Simulator stopped.")

finally:
    client.loop_stop()
    client.disconnect()
