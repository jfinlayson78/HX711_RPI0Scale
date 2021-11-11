#! /usr/bin/python2
# To do:
#   put all weights in a list or dictionary
#   analyze all data for a spike and get all numbers from that spike
#   if the change in slope between a point and point +2 is positive and huge then set is on scale equal to true
#   if the change in slope between a point and point +2 is negative and huge then set is on scale equal to false


import l2c_LCD_driver
import time
import datetime
import sys
import praw
import requests
from discord import Webhook, RequestsWebhookAdapter, File

lcd = l2c_LCD_driver.lcd()

#Discord Webhook Stuff
WEBHOOK_ID = '809616222194106389'
WEBHOOK_TOKEN = '0PflNSB9iiBMJkRUsz_uQsF7-AM3XXAJRKIn-K9lEZZZTvcABCu-oxNUk_jqqUiW0V-4'
webhook = Webhook.partial(WEBHOOK_ID, WEBHOOK_TOKEN, adapter = RequestsWebhookAdapter())

data = []
isOnScale = False

EMULATE_HX711=False

referenceUnit = 23.71929362

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

WeightData = []
wDataMin = 0.0
wDataMax = 0.0
wDataAvg = 0.0

sprTick = 0

while True:
    try:

        # get the value from the scale
        val = hx.get_weight(5)
        val = val * -1
        val = val/453.59237

        #print the value on the the scale
        lcd.lcd_clear()
        lcd.lcd_display_string(str(int(val)), 1)
        
        #append the value to the data array
        data.append(val)

        #limit data to like 50 or so data points
        if len(data) > 50:
            data.pop(0)

        #check for a spike in the data (occurs when someone steps on the scale).
        change = (data[len(data)-1] - data[len(data)-2])/2

        # If there's an increasing change start weighing stuff and turn on the light
        if (change > 10):
                lcd.backlight(1)
                isOnScale = True

        if (len(WeightData) >= 12):
                wData = WeightData[2:]
                wDataMax = max(wData)
                wDataMin = min(wData)
                wDataAvg = sum(wData)/len(wData)

                lcd.lcd_display_string("Avg: ", 2)
                lcd.lcd_display_string(str(int(wDataAvg)), 2, 5)

                if (change < -10):
                    x = datetime.datetime.now()
                    isOnScale = False
                    WeightData.clear()
                    webhook.send(f'Heres the data from weigh-in at {x.day}/{x.month}/{x.year}:\nMax = {wDataMax}\nMin = {wDataMin}\nAvg = {wDataAvg}')
                    lcd.lcd_clear()
                    time.sleep(3)
                    lcd.backlight(0)
                    
                    with open('bioData.txt', 'a') as f:
                        f.write(f'{x.timestamp()},{wDataMin},{wDataAvg},{wDataMax}\n')
                        #f.write(f'{x.hour}:{x.minute}:{x.second},{x.day}/{x.month}/{x.year},{wDataMin},{wDataAvg},{wDataMax}\n')
                        
        elif(isOnScale):
                WeightData.append(val)
                lcd.lcd_display_string("Collecting Data", 2)
                if (sprTick == 0):
                    lcd.lcd_display_string("|", 2, 15)
                    sprTick += 1
                elif (sprTick == 1):
                    lcd.lcd_display_string("/", 2, 15)
                    sprTick += 1
                elif (sprTick == 2):
                    lcd.lcd_display_string("-", 2, 15)
                    sprTick = 0

        hx.power_down()
        hx.power_up()
        time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
