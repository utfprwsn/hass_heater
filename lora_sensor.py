from ha_mqtt_discoverable import Settings, DeviceInfo
from ha_mqtt_discoverable.sensors import Switch, SwitchInfo, Sensor, SensorInfo
from paho.mqtt.client import Client, MQTTMessage
import time
import random

# To receive state commands from HA, define a callback function:
def my_callback(client: Client, user_data, message: MQTTMessage):
    payload = message.payload.decode()
    print(f"Received {payload} from HA")
    # Your custom code...

id = "CRIE_UM_ID_NOVO"

# Change the state of the sensor, publishing an MQTT message that gets picked up by HA
while True:    
    time.sleep(5)    
