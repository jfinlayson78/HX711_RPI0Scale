#! /usr/bin/python2
# To do: 
#   put all weights in a list or dictionary
#   analyze all data for a spike and get all numbers from that spike
#   if the change in slope between a point and point +2 is positive and huge then set is on scale equal to true
#   if the change in slope between a point and point +2 is negative and huge then set is on scale equal to false


import time
import sys
import praw
import requests

#Discord Webhook Stuff
WEBHOOK_ID = '809616222194106389'
WEBHOOK_TOKEN = '0PflNSB9iiBMJkRUsz_uQsF7-AM3XXAJRKIn-K9lEZZZTvcABCu-oxNUk_jqqUiW0V-4'


data = []
isOnScale = False

EMULATE_HX711=False

referenceUnit = 22.313

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

        #limit data to like 50 or so data points
        if len(data) > 50:
            data.pop(0)

        #check for a spike in the data. 
        #print the range between point 50 and point 50 - 2
        change = (data[len(data)-1] - data[len(data)-2])/2
        print(f'Change = {change}')

        #print(len(data))
        print(val)
        #print(change)

        hx.power_down()
        hx.power_up()
        time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
