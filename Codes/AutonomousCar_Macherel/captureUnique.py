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
from road_follower import RoadFollower
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
    imgRectifier = ImgRectifier(
            imgShape = conf["ROAD_FOLLOWING"]["img_resolution"][::-1],
            calParamFile = os.path.join(currentdir, conf["ROAD_FOLLOWING"]["calibration"]["param_file"]))
    imgWarper = ImgWarper(
            imgShape = conf["ROAD_FOLLOWING"]["img_resolution"][::-1], 
            corners = conf["ROAD_FOLLOWING"]["perspective_warp"]["points"], 
            realWorldCornersDistance = conf["ROAD_FOLLOWING"]["perspective_warp"]["realworld_line_distance"], 
            margin_pc = conf["ROAD_FOLLOWING"]["perspective_warp"]["warp_margin"], 
            cornersImageResolution = conf["ROAD_FOLLOWING"]["perspective_warp"]["points_resolution"])
    key = 1
    camera.startThread()
    print('Warming up camera')
    time.sleep(2)
    idx = 0
    while int(key) != 0 :
        img = cv2.resize(src= camera.current_frame,dsize=tuple(conf["ROAD_FOLLOWING"]["img_resolution"]))
        if img is not None:
            img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
            img = imgRectifier.undistort(img)
            cv2.imwrite(F"image_{idx}.png",img)
            cv2.waitKey(1)
            idx = idx+1 
            print('Image saved')
        else:
            print('Image is none ! Check camera')
        key = input('Press any touch to capture next or 0 to quit !')
        cv2.waitKey(0)

