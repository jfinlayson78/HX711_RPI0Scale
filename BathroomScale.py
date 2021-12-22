#! /usr/bin/python2
# To do:
#   put all weights in a list or dictionary
#   analyze all data for a spike and get all numbers from that spike
#   if the change in slope between a point and point +2 is positive and huge then set is on scale equal to true
#   if the change in slope between a point and point +2 is negative and huge then set is on scale equal to false

import l2c_LCD_driver
import time
import datetime
import hx711 as HX711
from discord import Webhook, RequestsWebhookAdapter, File

#Discord Webhook Stuff
#Remove this from 
WEBHOOK_ID = '809616222194106389'
WEBHOOK_TOKEN = '0PflNSB9iiBMJkRUsz_uQsF7-AM3XXAJRKIn-K9lEZZZTvcABCu-oxNUk_jqqUiW0V-4'
webhook = Webhook.partial(WEBHOOK_ID, WEBHOOK_TOKEN, adapter = RequestsWebhookAdapter())

# calibration unit
referenceUnit = 23.71929362

#create an lcd object
lcd = l2c_LCD_driver.lcd()

# use pins 5 and 6 for HX711 sensors
hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()

print("Tare done! Add weight now...")

#data to detect fluctuations from the scale
data = []
#data to process
WeightData = []
wDataMin = 0.0
wDataMax = 0.0
wDataAvg = 0.0

isOnScale = False

sprTick = 0

while True:
    try:
        # get the weight from the scale
        val = hx.get_weight(5)
        val = (val/453.59237) * -1

        #print the value on the the l2c LCD screen
        lcd.lcd_clear()
        lcd.lcd_display_string(str(int(val)), 1)
        
        #append the value to the data array, limit values to 4 or so entries, we're only checking the first two I think...
        data.append(val)
        if len(data) > 4:
            data.pop(0)

        #check for a spike in the data (occurs when someone steps on the scale).
        dWeight = (data[len(data)-1] - data[len(data)-2])/2
        #if there's an increasing change start weighing and turn on the backlight
        if (dWeight > 10):
            lcd.backlight(1)
            isOnScale = True

        #if there's enough weightdata to process
        if (len(WeightData) >= 12):

            #get the min, max avg of that data
            wData = WeightData[2:]
            wDataMax = max(wData)
            wDataMin = min(wData)
            wDataAvg = sum(wData)/len(wData)

            #display wDataAvg on line 2
            #TODO put this on one line
            lcd.lcd_display_string("Avg: ", 2)
            lcd.lcd_display_string(str(int(wDataAvg)), 2, 5)

            #When the user steps off the scale
            if (dWeight < -10):

                isOnScale = False
                
                # send the data to the discord channel
                x = datetime.datetime.now()
                webhook.send(f'Heres the data from weigh-in at {x.day}/{x.month}/{x.year}:\nMax = {wDataMax}\nMin = {wDataMin}\nAvg = {wDataAvg}')
                
                # log the data in the text file
                with open('scaleData.txt', 'a') as f:
                    f.write(f'{x.timestamp()},{wDataMin},{wDataAvg},{wDataMax}\n')
                
                # Clear Weightdata, clear the lcd, turn off the backlight
                WeightData.clear()
                lcd.lcd_clear()
                lcd.backlight(0)

                # Sleep for five seconds so the user has time to step off the scale and move around without triggering another weighin
                time.sleep(5)
                
        elif(isOnScale):
                # Append the user's weight to WeightData, print collecting weight and the animation
                WeightData.append(val)
                lcd.lcd_display_string("Collecting Data", 2)
                
                # weighing animation
                if (sprTick == 0):
                    lcd.lcd_display_string("|", 2, 15)
                    sprTick += 1
                elif (sprTick == 1):
                    lcd.lcd_display_string("/", 2, 15)
                    sprTick += 1
                elif (sprTick == 2):
                    lcd.lcd_display_string("-", 2, 15)
                    sprTick += 1
                elif (sprTick == 3):
                    lcd.lcd_display_string("\\", 2, 15)
                    sprTick = 0                   

        hx.power_down()
        hx.power_up()
        time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit):
        exit
