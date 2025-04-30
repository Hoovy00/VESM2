# This code determines the color of the light ring, so far there is no multi device communication, meaning we have to update it to also tell the other computer whether to give a good, bad, or neutral result

from machine import Pin
from neopixel import NeoPixel
from time import sleep
import random

neo = NeoPixel(Pin(45), 35) # 35 leds, DI pin 45

choice = random.randint(1,3) # Picks 1, 2, or 3. Which equate to a "good" good, a "bad" prediction, or "neautral"

neo.fill([0, 0, 0]) # turns off ring
neo.write()
sleep(1) # Waits a second

if choice == 1:
    # Good
    neo.fill([0, 50, 0]) #fills with a darker green
    neo.write()
    sleep(10) # remains for 10 seconds
    
if choice == 2:
    # bad
    neo.fill([50, 0, 0]) #fills with a darker red
    neo.write()
    sleep(10) # remains for 10 seconds

if choice == 3:
    # neutral
    neo.fill([50, 50, 50]) #fills with a darker white
    neo.write()
    sleep(10) # remains for 10 seconds

neo.fill([0, 0, 0]) # turns off ring
neo.write()
