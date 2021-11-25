# 
## ----------------------------------- Infos -----------------------------------
#   Author:            Rémy Macherel
#   Project:           Autonomous RC Car
#   File:              LaneNavigator.py
#   Link:              https://github.com/MacherelR/AutonomousRcCar
#   Creation date :    14.05.2021
#   Last modif date:   13.06.2021
## ----------------------------------- Infos -----------------------------------

## -------------------------------- Description --------------------------------
#   Main Class used for road following using CNN
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
import math
# from keras.models import load_model
import ML_Lib
import TB_Library
from pycoral.utils import edgetpu
from pycoral.adapters import common
_CONFNAME = os.path.join(currentdir, 'conf_MAR.yaml')
_SHOW_IMG = True

class LaneNavigator:
    stopped = False
    drawedImage = None
    OriginalImage = None
    def __init__(self,conf,steeringCtl,speedCtl,camera,current_threads_fps = None):
        self.camera = camera
        self.conf = conf
        self.steeringCtl = steeringCtl
        self.speedCtl = speedCtl
        self.currentThreadFps = current_threads_fps
        self.currentSteering = 90
        self.stopped = False
        modelPath = currentdir + conf['LANENAVIGATION']['modelFile']
        print(currentdir)
        print(modelPath)
        # ------------ PYCORAL MODEL DECLARATION -----------
        self.interpreter = edgetpu.make_interpreter(modelPath,device="usb")
        self.interpreter.allocate_tensors()
        self.input_shape = common.input_size(self.interpreter)
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.timesList = []
    
    def __enter__(self):
        self.startThread()
        return self

    def __exit__(self,exception_type, exception_value, traceback):
        self.stopThread()


    def startThread(self):
        t = Thread(target=self._run,name=self.__class__.__name__,args=())
        t.start()
        return self

    def stopThread(self):
        self.stopped = True
        print(F"Mean treatment time : {np.mean(self.timesList)}")


    def computeSteering(self,frame):
        preprocessed = ML_Lib.ImagePreprocess(frame)
        input_data = np.expand_dims(np.float32(preprocessed), axis=0)
        self.interpreter.set_tensor(self.input_details[0]['index'],input_data)
        self.interpreter.invoke()
        outputData = self.interpreter.get_tensor(self.output_details[0]['index'])
        # ------ STEERING -----
        steering = outputData[0][0]
        return steering

    def _run(self):
        print("-------------- LANE NAVIGATOR RUNNING ----------------")
        while not self.stopped:
            stTime = time.time()
            image = self.camera.current_frame
            self.OriginalImage = image
            ## CHecking Line presence :
            lImg = image[200-15:-15,:,:]
            lImgGray = cv2.cvtColor(lImg,cv2.COLOR_BGR2GRAY)
            cannyed = cv2.Canny(lImgGray,100,200)
            leftLine = np.mean(cannyed[:,0:160]) > 3
            rightLine = np.mean(cannyed[:,160:]) > 3
            if rightLine and leftLine :
                self.offRoad = False
                self.currentSteering = self.computeSteering(image)
                #print(F"Computed steering : {self.currentSteering}") #Used for debug
                if self.steeringCtl is not None:
                    self.steeringCtl.angle(TB_Library.map(self.currentSteering, 45, 135, -1, 1))
                    headingFrame = ML_Lib.drawHeadingLine(image,self.currentSteering)
                self.drawedImage = headingFrame
                # ------------ CAR SPEED ----------
                speed = 1.6
                #print(F"Speed value [main] : {speed}")
                speed = TB_Library.map(speed,self.conf['CAR']['speed_pwm_dc_min'],self.conf['CAR']['speed_pwm_dc_max'],-1,1)
                self.speedCtl.speed(speed)
            else:
                #print("off Road")
                #---------- CAR STOPPING --------
                self.offRoad = True
                self.speedCtl.stop()
                print("Stopping car because offroad !")
            
            elTime = time.time() -stTime
            self.timesList.append(elTime)
        cv2.destroyAllWindows()


if __name__ == '__main__':
    conf = TB_Library.load_configuration(_CONFNAME)
    car = Car(conf)
    nav = LaneNavigator(conf,car.SteeringCtrl,car.camera)
    with nav :
        launchTime = time.time()
        while (time.time() - launchTime)<6:
            if nav.OriginalImage is not None :
                cv2.imshow("Original ",cv2.cvtColor(nav.OriginalImage, cv2.COLOR_RGB2BGR))
            else:
                pass
                # print("Original None")

            if nav.drawedImage is not None:
                cv2.imshow("Heading",cv2.cvtColor(nav.drawedImage, cv2.COLOR_RGB2BGR))
            else:
                pass
                # print("Heading None")
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
    