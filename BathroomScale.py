#! /usr/bin/python2
# To do: 
#   put all weights in a list or dictionary
#   analyze all data for a spike and get all numbers from that spike


import time
import sys

data = []

EMULATE_HX711=False

referenceUnit = 22.7873473

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()

hx = HX711(5, 6)

hx.set_reading_format("MSB", "MSB")

hx.set_reference_unit(referenceUnit)

hx.reset()

hx.tare()

print("Tare done! Add weight now...")

while True:
    try:
        val = hx.get_weight(5)
        val = val/453.59237
        data.append(val)
        if len(data) > 500:
            data.pop(0)

        print(len(data))
        print(val)

        hx.power_down()
        hx.power_up()
        time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
