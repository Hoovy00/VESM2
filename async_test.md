```
import time
import machine
from servo import Servo
from machine import Pin
from neopixel import NeoPixel
import asyncio

neo = NeoPixel(Pin(15), 2)   #  2 x Leds
servo_pin_3 = machine.Pin(21)
servo_pin_2 = machine.Pin(41)
servo_pin_1 = machine.Pin(42)

my_servo = Servo(servo_pin_3)
vinstri_hond = Servo(servo_pin_2)
haegri_hond = Servo(servo_pin_1)

neo.fill([0, 255, 0]) # rauð augu
neo.write()

# hægri = 90° = 75
# hægri = 45° = 20
# vinstri = 90° = 80
# vinstri = 45° = 140

async def haegri():
    while True:
        haegri_hond.write_angle(75)
        await asyncio.sleep_ms(1000)
        haegri_hond.write_angle(20)
        await asyncio.sleep_ms(1000) 
        
async def vinstri():
    while True:
        vinstri_hond.write_angle(80)
        await asyncio.sleep_ms(1000)
        vinstri_hond.write_angle(140)
        await asyncio.sleep_ms(1000)

async def kjalki():
    while True:
        my_servo.write_angle(100) # 100 - lokaður munur
        await asyncio.sleep_ms(250)
        my_servo.write_angle(150) # 150 - opin munur
        await asyncio.sleep_ms(250)

async def main():
    asyncio.create_task(haegri())
    asyncio.create_task(vinstri())
    asyncio.create_task(kjalki())
    
    while True:
        await asyncio.sleep_ms(0)
        
asyncio.run(main())
```
