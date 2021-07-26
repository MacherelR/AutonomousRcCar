## ----------------------------------- Infos -----------------------------------
#   Author:            Rémy Macherel
#   Project:           Autonomous RC Car
#   File:              manualDrive_Capture.py
#   Link:              
#   Creation date :    19.04.2021
#   Last modif date:   
## ----------------------------------- Infos -----------------------------------

## -------------------------------- Description --------------------------------
#   Script conceived to drive the car manually and automatically save images 
#   and a log file containing steering value for each image
## -------------------------------- Description --------------------------------
#!/usr/bin/env python3
import sys, getopt, os,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import asyncio
from evdev import InputDevice, categorize, ecodes, util
import TB_Library
from actuator_controller import SteeringController, SpeedController
from DataCollection import DataCollector
from car import Car
import time
import threading
from signal import pause

"""Pin declaration with BCM format"""
PIN_SPEED = 18
PIN_STEERING = 19
CONFIG_FNAME = os.path.join(currentdir, 'conf_MAR.yaml')

def print_error():
     print(f"{os.path.basename(__file__)} -e <Controller event filename>")


def main(argv):
    conf = TB_Library.load_configuration(CONFIG_FNAME)
    event_filename = conf["CONTROLLER"]["event_filename"]
    ManualCar = Car(conf)
    Collector = DataCollector(ManualCar,freqMs=100)
    #Get arguments
    try:
       opts, args = getopt.getopt(argv, "h?e:", ["help", "event="])
    except getopt.GetoptError:
       print_error()
       sys.exit(2)
    for opt, arg in opts:
       if opt in ('-h', '-?', '--help'):
          print_error()
          sys.exit()
       elif opt in ("-e", "--event"):
           event_filename = arg

    with Collector:
        for thread in threading.enumerate():
            print(thread)
        startTime = time.time()
        run_manually(event_filename,ManualCar,Collector) 
        print(F"Duration : {time.time()-startTime}")


def run_manually(event_filename,car,Collector):
    controller = InputDevice(event_filename)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(event_manager(controller,car))
    except KeyboardInterrupt:
        print("Received exit, exiting")
        Collector.stopThread()
        loop.close()
        
    loop.run_in_executor
async def event_manager(device,car):
    car.SteeringCtrl.startPwm()
    car.SpeedCtrl.startPwm()
    async for event in device.async_read_loop():
        if event.type == ecodes.EV_ABS:
            if  event.code == ecodes.ABS_X:  #Joy Gauche / Gauche- Droite+
                car.SteeringCtrl.angle(TB_Library.map(event.value, 0, 255, -1, 1)) #Inverse des limites afin de tourner a gauche lorsque l'on pointe le joystick à gauche
            elif  event.code == ecodes.ABS_RY: #Joy Droite / Haut- Bas+
                if event.value > 0 and event.value < 20 :
                    val = 0
                else:
                    val = event.value
                car.SpeedCtrl.speed(TB_Library.map(val, 0, 255, 1, -1)) 
        elif event.type == ecodes.EV_KEY :
            if event.code == ecodes.BTN_B : # If button B (xBox) or circle (ps4) is pressed, exiting loop !
                raise KeyboardInterrupt


if __name__ == "__main__":
   main(sys.argv[1:])