```
import time
from neopixel import NeoPixel

neo = NeoPixel(Pin(15), 2)   #  2 x Leds

neo.fill([0, 255, 0]) # rauð augu
neo.write()
```

- Sandra
