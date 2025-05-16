from machine import Pin
from neopixel import NeoPixel
from time import sleep
import random
import time

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
TOPIC_START = b"vesm/start"

mqtt_client = MQTTClient(CLIENT_ID, MQTT_BROKER, keepalive=60)
mqtt_client.connect()

def send(message):
    state = f"{message}".encode()
    mqtt_client.publish(TOPIC_START, state)
    print(message)
    sleep_ms(100)


button = Pin(21, Pin.IN, Pin.PULL_DOWN)
neo = NeoPixel(Pin(45), 35) # 35 leds, DI pin 45

neo.fill([0, 0, 0]) # turns off ring
neo.write()
sleep(1) # Waits a second

while True:
    if button.value() == 1:
        choice = random.randint(1,3) # Picks 1, 2, or 3. Which equate to a "good" good, a "bad" prediction, or "neautral"
    else:
        choice = 0
    time.sleep(0.15) # Arbitrary number based on how long I pressed the button
    
    if choice == 0:
        pass

    if choice == 1:
        # Good
        send(choice)
        neo.fill([0, 100, 0]) #fills with a darker green
        neo.write()
        sleep(10) # remains for 10 seconds
        
    if choice == 2:
        # bad
        send(choice)
        neo.fill([100, 0, 0]) #fills with a darker red
        neo.write()
        sleep(10) # remains for 10 seconds

    if choice == 3:
        # neutral
        send(choice)
        neo.fill([100, 100, 100]) #fills with a darker white
        neo.write()
        sleep(10) # remains for 10 seconds

    neo.fill([0, 0, 0]) # turns off ring
    neo.write()
