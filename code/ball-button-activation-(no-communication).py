from machine import Pin
from neopixel import NeoPixel
from time import sleep
import random
import time

button = Pin(21, Pin.IN, Pin.PULL_DOWN)
neo = NeoPixel(Pin(45), 35) # 35 leds, DI pin 45

neo.fill([0, 0, 0]) # turns off ring
neo.write()
sleep(1) # Waits a second

while True:
    #state = button.value()
    #print("Pressed" if state == 0 else "Not pressed")  # LOW = pressed
    if button.value() == 1:
        choice = random.randint(1,3) # Picks 1, 2, or 3. Which equate to a "good" good, a "bad" prediction, or "neautral"
    else:
        choice = 0
    time.sleep(0.15)
    
    if choice == 0:
        pass

    if choice == 1:
        # Good
        neo.fill([0, 100, 0]) #fills with a darker green
        neo.write()
        sleep(1) # remains for 10 seconds
        
    if choice == 2:
        # bad
        neo.fill([100, 0, 0]) #fills with a darker red
        neo.write()
        sleep(1) # remains for 10 seconds

    if choice == 3:
        # neutral
        neo.fill([100, 100, 100]) #fills with a darker white
        neo.write()
        sleep(1) # remains for 10 seconds

    neo.fill([0, 0, 0]) # turns off ring
    neo.write()
