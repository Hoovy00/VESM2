from machine import Pin, unique_id
from binascii import hexlify
from time import sleep_ms
from umqtt.simple import MQTTClient

# ------------ Tengjast WIFI -------------
WIFI_SSID = "TskoliVESM"
WIFI_LYKILORD = "Fallegurhestur"

def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(WIFI_SSID, WIFI_LYKILORD)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    
do_connect()

# ---------------- MQTT ------------------

MQTT_BROKER = "broker.emqx.io" # eða broker.emqx.io (þarf að vera það sama á sendir og móttakara)
CLIENT_ID = hexlify(unique_id())
TOPIC = b"vesm/start" # Settu fyrstu fjóra stafinu úr kennitölunni þinni stað í X-anna

# Callback fall, keyrir þegar skilaboð berast með MQTT
def fekk_skilabod(topic, skilabod):
    #print(f"TOPIC: {topic.decode()}, skilaboð: {skilabod.decode()}")
    state = int(skilabod.decode())
    
    if state == 1:
        print("good")
              
    if state == 2:
        print("Bad")
              
    if state == 3:
        print("neutral")

mqtt_client = MQTTClient(CLIENT_ID, MQTT_BROKER, keepalive=60)
mqtt_client.set_callback(fekk_skilabod) # callback fallið skilgreint
mqtt_client.connect()
mqtt_client.subscribe(TOPIC)

while True:
   try:
        mqtt_client.check_msg()
   except:
        print("endurtengjast")
        mqtt_client = MQTTClient(CLIENT_ID, MQTT_BROKER, keepalive=60)
        mqtt_client.set_callback(fekk_skilabod) # callback fallið skilgreint
        mqtt_client.connect()
        mqtt_client.subscribe(TOPIC)
   sleep_ms(1000)