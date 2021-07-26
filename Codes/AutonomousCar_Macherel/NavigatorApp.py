## ----------------------------------- Infos -----------------------------------
#   Author:            Rémy Macherel
#   Project:           Autonomous RC Car
#   File:              NavigatorApp.py
#   Link:              https://github.com/MacherelR/AutonomousRcCar
#   Creation date :    14.05.2021
#   Last modif date:   16.07.2021
## ----------------------------------- Infos -----------------------------------

## -------------------------------- Description --------------------------------
#   Main project's app for road following using CNN and displaying Direction
## -------------------------------- Description --------------------------------

from car import Car
import sys, getopt, os,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

import cv2
import numpy as np
import time
import tensorflow as tf
from PIL import Image
from threading import Thread
import threading
from LaneNavigator import LaneNavigator
import math
# from keras.models import load_model
import ML_Lib
import TB_Library
_CONFNAME = os.path.join(currentdir, 'conf_MAR.yaml')
_SHOW_IMG = True


class NavigationApp():
    def __init__(self,confName):
        self.conf = TB_Library.load_configuration(confName)
        self.threads_fps = {
            'Main'                  : 0,
            'PicameraController'    : 0,
            'LaneNavigator'         : 0
        }
        self.minExecTime = 1/self.conf['APP']['maxFps']
        self.car = Car(
            conf= self.conf,
            current_threads_fps=self.threads_fps,
            hardSpeed= True,
            hardSteer= False
        )
        self.LaneNavigator = LaneNavigator(
            conf=self.conf,
            steeringCtl= self.car.SteeringCtrl,
            camera= self.car.camera,
            current_threads_fps=self.threads_fps
        )

    def computeSpeed(self,steering):
        if steering <= 90:
            a = (self.conf['CAR']['low_speed']-self.conf['CAR']['full_speed'])/(-45)
            b = self.conf['CAR']['full_speed']-(a*90)
            
        elif steering > 90:
            a = (self.conf['CAR']['low_speed']-self.conf['CAR']['full_speed'])/45
            b = self.conf['CAR']['full_speed'] -(a*90)
        return  a*steering + b

    def start(self):
        with self.car:
            with self.LaneNavigator:
                print('----------------  ACTIVE THREAD  ----------------')
                for thread in threading.enumerate():
                    print(thread)
                startTime = time.time()
                launchTime = startTime
                while (time.time() - launchTime) < 30:
                    # Display Datas
                    if self.LaneNavigator.OriginalImage is not None:
                        cv2.imshow("Original",cv2.cvtColor(self.LaneNavigator.OriginalImage,cv2.COLOR_RGB2BGR))
                    if self.LaneNavigator.drawedImage is not None:
                        cv2.imshow("Heading",cv2.cvtColor(self.LaneNavigator.drawedImage,cv2.COLOR_RGB2BGR))
                    # --------- CAR SPEED ----------
                    if self.LaneNavigator.offRoad == False:

                    #speed = self.computeSpeed(self.LaneNavigator.currentSteering)
                        speed = 1.68
                    #print(F"Speed value [main] : {speed}")
                        speed = TB_Library.map(speed,self.conf['CAR']['speed_pwm_dc_min'],self.conf['CAR']['speed_pwm_dc_max'],-1,1)
                        self.car.SpeedCtrl.speed(speed)
                    else:
                        self.car.SpeedCtrl.stop()
                        print("Stopping car because offroad !")
                    key = cv2.waitKey(1)
                    if key == ord('q'):
                        break

                    elapsedTime = time.time() -startTime
                    startTime = time.time()
        
        cv2.destroyAllWindows()

if __name__ == '__main__':
    app = NavigationApp(_CONFNAME)
    app.start()

                    