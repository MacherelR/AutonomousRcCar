## ----------------------------------- Infos -----------------------------------
#   Author:            Rémy Macherel
#   Project:           Autonomous RC Car
#   File:              road_follower.py
#   Creation date :    10.03.2021
#   Last modif date:   10.03.2021
## ----------------------------------- Infos -----------------------------------

## -------------------------------- Description --------------------------------
#   Main road following class 
## -------------------------------- Description --------------------------------

import sys, getopt, os,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

import TB_Library
import cv2
import numpy as np
import time 
import math
from scipy import stats
from threading import Thread
from image_warper import ImgWarper
from image_rectifier import ImgRectifier
import datetime

YAMLCONF = os.path.join(currentdir, 'Conf_ROI.yaml')
class RoadFollower():
    # Var to stop the thread
    stopped = False
    drawed_img = None
    ROI_img = None

    def __init__(self, conf, camera, steeringCtrl, car_state, current_threads_fps=None):
        self.camera = camera
        self.steeringCtrl = steeringCtrl
        self.conf = conf
        self.car_state = car_state
        self.current_threads_fps = current_threads_fps
        self.ROI = TB_Library.load_configuration(YAMLCONF)
        self.imgRectifier = ImgRectifier(
            imgShape = self.conf["ROAD_FOLLOWING"]["img_resolution"][::-1],
            calParamFile = os.path.join(currentdir, self.conf["ROAD_FOLLOWING"]["calibration"]["param_file"]))
        self.imgWarper = ImgWarper(
            imgShape = self.conf["ROAD_FOLLOWING"]["img_resolution"][::-1], 
            corners = self.conf["ROAD_FOLLOWING"]["perspective_warp"]["points"], 
            realWorldCornersDistance = self.conf["ROAD_FOLLOWING"]["perspective_warp"]["realworld_line_distance"], 
            margin_pc = self.conf["ROAD_FOLLOWING"]["perspective_warp"]["warp_margin"], 
            cornersImageResolution = self.conf["ROAD_FOLLOWING"]["perspective_warp"]["points_resolution"])

    # To make "with" use easier
    def __enter__(self):
        """ Entering a with statement """
        self.startThread()
        return self
    
    def __exit__(self, exception_type, exception_value, traceback):
        self.stopThread()
        """ Exit a with statement"""

    def startThread(self):
        # start the thread to follow the road
        t = Thread(target=self._run, name=self.__class__.__name__, args=())
        t.start()
        return self

    def stopThread(self):
        # indicate that the thread should be stopped
        self.stopped = True

    def _run(self):
        self.car_state['stop_flags']['no_road'] = True
        # start_time = time.time() # used to adjust thread's fps
        while not self.stopped:
            img  = cv2.resize(src=self.camera.current_frame ,dsize=tuple(self.conf["ROAD_FOLLOWING"]["img_resolution"])) #self.camera.current_frame #
            self.initImg = img
            img = self.imgRectifier.undistort(img)
            self.befWarp = img
            img_warped = self.imgWarper.warp(img)
            self.drawed_img = img_warped
            #print(self.drawed_img.shape)
            # roi = self.ROI
            # self.ROI_img = self.drawed_img[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])] #Crop image

            #self.drawed_img = cv2.cvtColor(self.drawed_img,cv2.COLOR_BGR2HSV)
            # self.HSV_img = cv2.cvtColor(self.drawed_img,cv2.COLOR_BGR2HSV)
            # lower_blue = np.array([60,40,40]) 
            # upper_blue = np.array([150,255,255])
            # self.masked_img = cv2.inRange(self.HSV_img,lower_blue,upper_blue)
            # self.Edges = cv2.Canny(self.masked_img,200,400)
        # if self.current_threads_fps is not None:
        #         self.current_threads_fps[self.__class__.__name__] = 1/(time.time()-start_time)
        #         start_time = time.time()
