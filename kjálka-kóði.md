```
import time
import machine
from servo import Servo

servo_pin = machine.Pin(4)
my_servo = Servo(servo_pin)

while True:
    my_servo.write_angle(100) # 100 - lokaður munur
    time.sleep(0.1)
    my_servo.write_angle(125)
    time.sleep(0.1)
    my_servo.write_angle(150) # 150 - opin munur
    time.sleep(0.1)
```
