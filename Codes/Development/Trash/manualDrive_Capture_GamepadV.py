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
import Gamepad

"""Pin declaration with BCM format"""
PIN_SPEED = 18
PIN_STEERING = 19
CONFIG_FNAME = os.path.join(currentdir, 'conf.yaml')

# Gamepad settings 
gamepadType = Gamepad.PS4
buttonExit = 'CIRCLE'
joystickSpeed = 'RIGHT-Y'
joystickSteering = 'LEFT-X'
pollInterval = 0.1

def print_error():
     print(f"{os.path.basename(__file__)} -e <Controller event filename>")


def exitButtonPressed():
    global running
    print('EXIT')
    running = False

def main(argv):
    #event_filename = '/dev/input/event2'
    conf = TB_Library.load_configuration(CONFIG_FNAME)
    ManualCar = Car(conf)
    Collector = DataCollector(ManualCar,freqMs=100)
    # Wait for a connection
    if not Gamepad.available():
        print('Please connect your gamepad...')
        while not Gamepad.available():
            time.sleep(1.0)
    gamepad = gamepadType()
    print('Gamepad connected')
    global running
    running = True

    with Collector:
        startTime = time.time()
        ManualCar.SpeedCtrl.startPwm()
        ManualCar.SteeringCtrl.startPwm()
        gamepad.startBackgroundUpdates()
        gamepad.addButtonPressedHandler(buttonExit, exitButtonPressed)
        try:
            while running and gamepad.isConnected():
                ManualCar.SteeringCtrl.angle(gamepad.axis(joystickSteering))
                #ManualCar.SpeedCtrl.speed(-gamepad.axis(joystickSpeed)) 
                print(F"Speed : {gamepad.axis(joystickSteering)}")
                time.sleep(pollInterval)
        finally:
            gamepad.disconnect()
        print(F"Duration : {time.time()-startTime}")
if __name__ == "__main__":
   main(sys.argv[1:])