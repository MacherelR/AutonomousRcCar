## ----------------------------------- Infos -----------------------------------
#   Author:            Rémy Macherel
#   Project:           Autonomous RC Car
#   File:              UndistortImage.py
#   Link:              
#   Creation date :    19.04.2021
#   Last modif date:   
## ----------------------------------- Infos -----------------------------------

## -------------------------------- Description --------------------------------
#   Class used to read parameters from pickle file and undistort image with those 
#   parameters
## -------------------------------- Description --------------------------------

import cv2
import pickle

class ImageCalibrator():
    def __init__(self,ParamFile,imageShape):
        try :
            with open(ParamFile,mode='rb') as fileDescriptor:
                file = pickle.load(fileDescriptor)
                self.mtx = file['mtx']
                self.dist = file['dist']
                calibrationShape = file['calImgShape']
                self.mtx_new = file['mtx_new']
                if(imageShape != calibrationShape): 
                    self.mtx[0,0] *= (imageShape[1] / calibrationShape[1]) #fx
                    self.mtx[1,1] *= (imageShape[0] / calibrationShape[0]) #fy
                    self.mtx[0,2] *= (imageShape[1] / calibrationShape[1]) #cx
                    self.mtx[1,2] *= (imageShape[0] / calibrationShape[0]) #cy

                    self.mtx_new[0,0] *= (imageShape[1] / calibrationShape[1]) #fx
                    self.mtx_new[1,1] *= (imageShape[0] / calibrationShape[0]) #fy
                    self.mtx_new[0,2] *= (imageShape[1] / calibrationShape[1]) #cx
                    self.mtx_new[1,2] *= (imageShape[0] / calibrationShape[0]) #cy
                    
        except FileNotFoundError:
            raise FileNotFoundError("Pickle file with calibration parameters not found !")
    def undistort(self,image,crop=True):
        return cv2.undistort(image,self.mtx,self.dist,None,None if crop else self.mtx_new)