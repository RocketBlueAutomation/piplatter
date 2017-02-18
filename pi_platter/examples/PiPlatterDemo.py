#!/usr/bin/env python
# Pi Platter Demo
# This program demonstrates 4 things
# 1. Report battery voltage
# 2. Shut down when battery is low
# 3. Restart once battery voltage has recovered
# 4. Setting Pi Platter Real Time Clock
# To run this program at startup:
# In the command line terminal edit rc.local with :
# sudo nano /etc/rc.local
# add the following line:
# python /honme/pu/PiPlatterDemo.py &
# This of course, presumes that you have talkpp and PiPlatterDemo.py in the named places
# To make the startup on boot more robust, check out daemontools
# For lots more cool ideas on using the Pi Platter, go to RocketBlueAutomation.com

import os
import sys
import subprocess
from   subprocess import Popen, PIPE
from   datetime import datetime
import time

user = os.getuid()
if user != 0:
    print("Please run script as root")
    sys.exit()

def main(argv):
    if datetime.today().year > 2016: # if the OS time is current then set the RTC
        ticks = time.time()
        settimecmd = "talkpp -c T=" + str(int(ticks))
        print("Setting Pi Platter RTC")
        os.system(settimecmd)  # set the system time 
    else:
        cmd = Popen('talkpp -c T', shell=True, stdout=PIPE)  # read date from piplatter
        alloutput = cmd.stdout.read()
        alloutput.splitlines()
        mytime = int(alloutput.splitlines()[0])
        #print mytime
        if mytime > 148000000:  #only set the os time if the RTC was previously set
            print ("Setting OS time")
            datecmd = Popen('sudo date %s' % mytime, shell=True, stdout=PIPE) # set os date
            dateoutput = datecmd.stdout.readlines()
    
    print("Pi Platter Demo")
    print("By RocketBlueAutomation.com")
    previous_second = 0
    last_good_battery_voltage = 0
    while True:  #monitor battery and log voltage once a minute
        now = datetime.today()
        
        battery_voltage = subprocess.check_output("talkpp -c B", shell=True)  # read battery voltage

        if is_float(battery_voltage) :  # talkpp does not always return a value - put in last known value if not   
            last_good_battery_voltage = battery_voltage
        else:    
            battery_voltage = last_good_battery_voltage
        battery_volt = float(battery_voltage)
        if (battery_volt < 3.67) and (battery_volt > 1.50):  # shut down if battery voltage is getting to low
            print("Powering down now")
            # Threshold=(1.024/(Restart_Voltage-0.15))*1023
            os.system("talkpp -c E3=272") # start back up at 4.00 volts
            os.system("talkpp -c C7=1")  # set to restart
            os.system("talkpp -c E7=1")  # set to restart every time
            os.system("talkpp -c O=30")  # Turn off Pi Platter in 30 seconds
            os.system("sudo halt")       # shut down Pi Zero now
        with open('voltage_date.txt','a+') as fb:
            fb.write( '{} {}\n'.format(str(now)[:-7], battery_volt) )
        print (str(now)[:-7]),battery_volt
        time.sleep(60)  # check and log about once a minute

def is_float(volts):  # test to see if the returned value looks like a proper floating point number
    try:
        newVolts = float(volts)
        return newVolts
    except ValueError:
        return None

# main
if "__main__" == __name__:
    if len(sys.argv) < 1:
        sys.exit('usage: {p:s}'.format(p=sys.argv[0]))

    try:  # exit cleanly on keyboard interrupt. 
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit('interrupted')
        pass
