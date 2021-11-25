## ----------------------------------- Infos -----------------------------------
#   Author:            Rémy Macherel
#   Project:           Autonomous RC Car
#   File:              captureUnique.py
#   Link:              https://github.com/MacherelR/AutonomousRcCar
#   Creation date :    12.04.2021
#   Last modif date:   12.04.2021
## ----------------------------------- Infos -----------------------------------

## -------------------------------- Description --------------------------------
#   File used in the project's development to capture an unique image and save
#   it directly in the folder.
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

import datetime

from cameraController import PicameraController
CONFIG_FNAME = os.path.join(currentdir, 'conf.yaml')


if __name__ == '__main__':
    conf  = TB_Library.load_configuration(CONFIG_FNAME)
    current_threads_fps = None
    camera = PicameraController(
            cam_param_dict = [(arg, value) for (arg, value) in conf['CAMERA']['parameters'].items() if value != None],
            current_threads_fps = current_threads_fps,
            conf= conf
    )
    key = 1
    camera.startThread()
    print('Warming up camera')
    time.sleep(2)
    idx = 0
    while int(key) != 0 :
        img = camera.current_frame
        if img is not None:
            img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
            cv2.imwrite(F"image_{idx}.png",img)
            cv2.waitKey(1)
            idx = idx+1 
            print('Image saved')
        else:
            print('Image is none ! Check camera')
        key = input('Press any touch to capture next or 0 to quit !')
        cv2.waitKey(0)
    camera.stopThread()

