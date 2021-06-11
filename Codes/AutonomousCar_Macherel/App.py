#!/usr/bin/env python3

# ----------------------------------- Infos -----------------------------------
#   Author:            Rémy Macherel
#   Project:           Autonomous RC Car
#   File:              app.py
#   Link:              
#   Creation date :    10.03.2021
#   Last modif date:   
# ----------------------------------- Infos -----------------------------------

# -------------------------------- Description --------------------------------
#   Main file to compute the road detection
# -------------------------------- Description --------------------------------


import sys, getopt, os,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

import time
from evdev import InputDevice, categorize, ecodes, util
import cv2
import TB_Library
from road_follower import RoadFollower
from car import Car
import threading
import copy

CONFIG_FNAME = os.path.join(currentdir, 'conf.yaml')

class CarApp():
    def __init__(self,conf_fname):
        self.conf = TB_Library.load_configuration(conf_fname)
        self.car_state = {
            'stop_flags': {
                'no_road'     : False,
                'manual_stop' : False
            },
            'speed_limit'     : self.conf["CAR"]["real_speed_25"]
        }
        self.car_state_history = copy.deepcopy(self.car_state)
        self.threads_fps = {
            'Main'              : 0,
            'PicameraController': 0,
            'RoadFollower'      : 0,
            'ObjectsDetector'   : 0,
            'ObstacleDetector'  : 0
        }
        self.min_execution_time = 1/self.conf["APP"]["max_fps"]
        #Objects
        self.car = Car(
            conf = self.conf, 
            current_threads_fps = self.threads_fps)

        self.roadFollower =RoadFollower(
            conf= self.conf,
            camera = self.car.camera,
            steeringCtrl = self.car.SteeringCtrl,
            car_state = self.car_state,
            current_threads_fps = self.threads_fps
        )
        try:
            self.controller = InputDevice(self.conf["CONTROLLER"]["event_filename"])
            self.car_state['stop_flags']['manual_stop'] = True
        except FileNotFoundError:
            self.controller = None
            print("A wrong gamepad event filename is provided or the gamepad is not connected !")

    
    def start(self):
        if self.conf["DISPLAY"]["show_plots"]:
            cv2.namedWindow("RoadFollower",cv2.WINDOW_NORMAL)
            # cv2.namedWindow("Before Warping",cv2.WINDOW_NORMAL)
            # cv2.namedWindow("Initial Image",cv2.WINDOW_NORMAL)
            # cv2.namedWindow("HSV image",cv2.WINDOW_NORMAL)
            # cv2.namedWindow("Masked Image",cv2.WINDOW_NORMAL)
            # cv2.namedWindow("Edge Detection",cv2.WINDOW_NORMAL)
            # cv2.moveWindow("Initial Image",20,20)
            # cv2.moveWindow("Before Warping", 450,20)
            # cv2.moveWindow("RoadFollower", 450,400)
            # cv2.moveWindow("HSV image",20,400)
            # cv2.moveWindow("Masked Image",880,20)
            # cv2.moveWindow("Edge Detection",880,400)
            # cv2.namedWindow("ROI",cv2.WINDOW_NORMAL)

        with self.car:
            with self.roadFollower:
                start_time = time.time()
                while True:
                    if self.conf["DISPLAY"]["show_plots"]:
                        if self.roadFollower.drawed_img is not None :
                            print("Watch")
                            cv2.imshow("RoadFollower",cv2.cvtColor(self.roadFollower.drawed_img, cv2.COLOR_RGB2BGR))
                            #cv2.imshow("ROI", cv2.cvtColor(self.roadFollower.ROI_img, cv2.COLOR_RGB2BGR))
                            # cv2.imshow("Before Warping",cv2.cvtColor(self.roadFollower.befWarp, cv2.COLOR_RGB2BGR))
                            # cv2.imshow("Initial Image",cv2.cvtColor(self.roadFollower.initImg, cv2.COLOR_RGB2BGR))
                            # cv2.imshow("HSV image",self.roadFollower.HSV_img)
                            # cv2.imshow("Masked Image",self.roadFollower.masked_img)
                            # cv2.imshow("Edge Detection",self.roadFollower.Edges)
                            # cv2.imwrite("Warped.png",cv2.cvtColor(self.roadFollower.drawed_img, cv2.COLOR_RGB2BGR))
                        else:
                            print("images are none !")
                            time.sleep(0.5)
                    key = cv2.waitKey(1)
                    if key == ord("q"):
                        break
                    elapsed_time = time.time() - start_time
                    if (elapsed_time < self.min_execution_time):
                        time.sleep(self.min_execution_time - elapsed_time)
                    self.threads_fps['Main'] = 1/(time.time()-start_time)
                    start_time = time.time()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    App = CarApp(CONFIG_FNAME)
    App.start()