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
from DataCollection import DataCollector
CONFIG_FNAME = os.path.join(currentdir, 'conf.yaml')


class TrainingApp():
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
            'DataCollector'   : 0
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

        self.DataCollector = DataCollector(
            conf = self.conf,
            camera = self.car.camera,
            rectifier = self.roadFollower.imgRectifier,
            warper = self.roadFollower.imgWarper,
            current_threads_fps = self.threads_fps)

    def start(self):
        with self.car:
            with self.roadFollower:
                i = 0
                k = 0
                time.sleep(0.1) # Let camera be online
                while i < 10:
                    if self.roadFollower.drawed_img is not None: 
                        #print(f"Number of empty images : {k}")
                        img = cv2.cvtColor(self.roadFollower.drawed_img, cv2.COLOR_RGB2BGR)
                        self.DataCollector.saveData(img,i)
                        i += 1
                        #print(f"Image nr {i} captured ! \n")
                    else :
                        #print("Empty image ! \n")
                        k+=1
                    cv2.waitKey(1)
                    #cv2.imshow("image",img)
                
                self.DataCollector.saveLogFile()

if __name__ == '__main__':
    App = TrainingApp(CONFIG_FNAME)
    App.start()

