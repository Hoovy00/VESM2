```
import time
import machine
from servo import Servo
from machine import Pin
import asyncio

servo_pin_1 = machine.Pin(42)
servo_pin_2 = machine.Pin(41)

vinstri_hond = Servo(servo_pin_2)
haegri_hond = Servo(servo_pin_1)

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
        
async def main():
    asyncio.create_task(haegri())
    asyncio.create_task(vinstri())
    
    while True:
       
        await asyncio.sleep_ms(0)
        
asyncio.run(main())
```
