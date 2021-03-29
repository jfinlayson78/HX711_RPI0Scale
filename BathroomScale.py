#! /usr/bin/python2
# To do:
#   put all weights in a list or dictionary
#   analyze all data for a spike and get all numbers from that spike
#   if the change in slope between a point and point +2 is positive and huge then set is on scale equal to true
#   if the change in slope between a point and point +2 is negative and huge then set is on scale equal to false


import l2c_LCD_driver
import time
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

# isOnscale = false
# if the user steps on the scale
#   isOnScale = true
# if the user steps off the scale
#   isOnScale = false

# if isOnScale = true
#   print("Collecting Data") on the bottom line


while True:
    try:
        val = hx.get_weight(5)
        val = val * -1
        val = val/453.59237
        lcd.lcd_clear()
        lcd.lcd_display_string(str(int(val)), 1)
        data.append(val)
        #limit data to like 50 or so data points
        if len(data) > 50:
            data.pop(0)


        #check for a spike in the data. 
        #print the range between point 50 and point 50 - 2
        change = (data[len(data)-1] - data[len(data)-2])/2
        if (change > 10 and isOnScale == False):
                isOnScale = True
                webhook.send("You Stepped On The Scale, please stay on the scale while we calculate data...")
        if (change < -10 and isOnScale == True):
                isOnScale = False
                WeightData.clear()
                webhook.send("See you tomorrow!")
        #print(f'Change = {change}')

        #print(len(data))
        sprTick = 0
        if (isOnScale):
                print(val)
                WeightData.append(val)
                lcd.lcd_display_string("Collecting Data", 2)
                if (len(data) < 50):
                    if (sprTick == 0){
                        lcd.lcd_display_string("\\", 2, 15)
                        sprTick += 1    
                    else if (sprTick == 1):
                        lcd.lcd_display_string("|", 2, 15)
                        sprTick += 1
                    else if (sprTick == 2):
                        lcd.lcd_display_string("/", 2, 15)
                        sprTick += 1
                    else if (sprTick == 3):
                        lcd.lcd_display_string("-", 2, 15)
                        sprTick = 0

        if (len(WeightData) == 12):
                wData = WeightData[2:]
                wDataMax = max(wData)
                wDataMin = min(wData)
                wDataAvg = sum(wData)/len(wData)
                lcd.lcd_display_string("Avg: ", 2)
                lcd.lcd.display_string(str(int(wDataAvg)), 2, 5)
                
                webhook.send(f'Heres the data from this weigh-in:\nMax = {wDataMax}\nMin = {wDataMin}\nAvg = {wDataAvg}')
                webhook.send(f'You may now step off of the scale...')

        hx.power_down()
        hx.power_up()
        time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
