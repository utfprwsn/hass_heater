from ha_mqtt_discoverable import Settings, DeviceInfo
from ha_mqtt_discoverable.sensors import Switch, SwitchInfo, Sensor, SensorInfo
from paho.mqtt.client import Client, MQTTMessage
import time
import random
import json
import base64
import struct
import paho.mqtt.client as mqtt

devID = '0012f8000000092d'
uplinkTopic = 'application/5/device/'+ devID  + '/event/up'
power = 0
warning_status = 13
power_sent = False
mqtt_host = "labscgw.eletrica.eng.br"

def lora_on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("LoRa Gateway Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    client.subscribe(uplinkTopic)  # Subscribe to the topic “labscim/example”, receive any messages published on it

def lora_on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    print("Message received-> " + msg.topic + " " + str(msg.payload))  # Print a received msg    
    global power
    global warning_status
    global power_sent  
    if msg.topic == uplinkTopic:
        y = json.loads(msg.payload)
        # the result is a Python dictionary:
        #converts the base64 encoded string y["data"] to a binary sequence
        data_decode = base64.b64decode(y["data"])
        #interprets the binary sequence as a string
        try:        
            seq_no, tempx100, compressor_power = struct.unpack('=IiH', data_decode)
            temperature_sensor.set_state(tempx100/100)
            if compressor_power != power and power_sent:
                if compressor_power == 0:
                    switch.off()
                else:
                    switch.on()


            #transforms the python variables magic_number and send_value in a byte array named ba
            ba = struct.pack('=HB', power,warning_status)
            #encodes the byte array ba to a base64 string named m
            m = base64.b64encode(ba)
            #prepares m to a payload string
            payload = m.decode("utf-8")

            #create a python dictionary named resp with the keys required by the chirpstack format
            resp = {"confirmed": False, "fPort": 2, "data": payload }
            #convert the dictionary in a JSON string named js
            js = json.dumps(resp, indent = 4)  
            #gets [ApplicationID] and [DevEUI] from the uplink topic
            topics = msg.topic.split("/")
            #creates the downlink topic
            t = 'application/{:s}/{:s}/{:s}/command/down'.format(topics[1],topics[2],topics[3])        
            #enqueue downlink using MQTT
            client.publish(t,js)
            power_sent = True
        except Exception as e:
            # Print the exception message
            print(f"An exception occurred: {str(e)}") 
    


# To receive state commands from HA, define a callback function:
def my_callback(client: Client, user_data, message: MQTTMessage):
    global power
    global warning_status
    global power_sent  
    if message.topic == switch._command_topic:
        #send ack to HASS
        client.publish(switch.state_topic,message.payload)
        #Save State to Send to Hardware
        if message.payload == 'ON':
            power = 100
            power_sent = False
        else:
            power = 0
            power_sent = False
    else:
        payload = message.payload.decode()
        print(f"Received {payload} from HA")
        # Your custom code...

id = "gabaritoPF"

# Configure the required parameters for the MQTT broker
mqtt_settings = Settings.MQTT(host=mqtt_host)


# Define the device. At least one of `identifiers` or `connections` must be supplied
device_info = DeviceInfo(name="LabSC Heater", identifiers=id)


# Information about the switch
# If `command_topic` is defined, it will receive state updates from HA
switch_info = SwitchInfo(name="Heat Element", unique_id=id, device=device_info)
switch_settings = Settings(mqtt=mqtt_settings,entity=switch_info)
switch = Switch(switch_settings, my_callback)

#Temperature Sensor
temperature_sensor_info = SensorInfo(name="Temperature",device_class="temperature",unique_id=id,device=device_info, unit_of_measurement='oC')
temperature_sensor_settings = Settings(mqtt=mqtt_settings,entity=temperature_sensor_info)
temperature_sensor = Sensor(settings=temperature_sensor_settings)


lora_client = mqtt.Client("moritz_lora_subscriber")  # Create instance of client with client ID “labscim_student_client”
lora_client.on_connect = lora_on_connect  # Define callback function for successful connection
lora_client.on_message = lora_on_message  # Define callback function for receipt of a message
lora_client.connect(mqtt_host, 1883, 60)
lora_client.loop_forever()  # Start networking daemon
 
    
