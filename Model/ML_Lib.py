#!/usr/bin/env python3

## ----------------------------------- Infos -----------------------------------
#   Author:            RÃƒÆ’Ã‚Â©my Macherel
#   Project:           Autonomous RC Car
#   File:              ML_Lib.py
#   Creation date :    25.05.2021
#   Last modif date:   23.06.2021
## ----------------------------------- Infos -----------------------------------

## -------------------------------- Description --------------------------------
#   This file contains all my useful functions that I often use for machine Learning
## -------------------------------- Description --------------------------------
import os
import random
import fnmatch
import datetime
import pickle

# data processing
import numpy as np
np.set_printoptions(formatter={'float_kind':lambda x: "%.4f" % x})

import pandas as pd
pd.set_option('display.width', 300)
pd.set_option('display.float_format', '{:,.4f}'.format)
pd.set_option('display.max_colwidth', 200)

# tensorflow
import tensorflow as tf
import keras
from keras.models import Sequential  # V2 is tensorflow.keras.xxxx, V1 is keras.xxx
from keras.layers import Conv2D, MaxPool2D, Dropout, Flatten, Dense
from keras.optimizers import Adam
from keras.models import load_model

# sklearn
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split

# imaging
import cv2
from imgaug import augmenters as img_aug
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
#%matplotlib inline
from PIL import Image


import copy
import csv

def findSteering(df,fName):
    row = df.loc[df[0] == fName]
    return row.iat[0,1]
  
  
def imreadModif(imgPath):
    image = cv2.imread(imgPath)
    image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    return image
  
def zoom(image):
    zoom = img_aug.Affine(scale= (1,1.2)) # zoom to 120%
    img = zoom.augment_image(image)
    return img
  
def pan (image) :
    pan = img_aug.Affine(translate_percent={"x" : (-0.1,0.1), "y" : (-0.1,0.1)})
    img = pan.augment_image(image)
    return img
  
def GaussianBlur (image):
    kernelSize = random.randint(1,5) # 5 is the blurry limit
    img = cv2.blur(image,(kernelSize,kernelSize))
    return img
  
def flipImage(image,steeringValue):
    isFlip = random.randint(0,1) #randomly flip the image
    if isFlip == 1:
    #flip the horizon
        image = cv2.flip(image,1)
        steeringValue = 180 - steeringValue
    return image,steeringValue
  
def adjustBrightness(image):
    # increase or decrease brightness by 30%
    brightness = img_aug.Multiply((0.7, 1.3))
    image = brightness.augment_image(image)
    return image

def randomModify (image,steeringAngle):
#   if np.random.rand() < 0.5:
#     image = pan(image)
#     if np.random.rand() < 0.5:
#         print("random zoom done \n")
#         image = zoom(image)
    if np.random.rand() < 0.5:
        image = GaussianBlur(image)
#         print("random blur done \n")
    if np.random.rand() < 0.5:
        image = adjustBrightness(image)
#         print("random brightness adjustment done \n")
    image, steeringAngle = flipImage(image, steeringAngle)

    return image,steeringAngle


# def eraseNoises(lineY):
#     newLine = copy.deepcopy(lineY)
#     m = np.mean(newLine[75:125])
#     mean = np.mean(lineY)
#     idL = np.where(newLine[0:110] < 0.2)
#     idL = idL[0]
#     startPeakLeft = idL[-1]
#     endPeakLeft = idL[-1]- 5 #Sur image de 320x240 largeur ligne = 8 pixels --> 8 * 200/320
#     idR = np.where(newLine[100:200] < 0.25)
#     idR = idR[0]+100
#     startPeakRight = idR[0]
#     endPeakRight = idR[0] + 5
#     newLine[endPeakRight:] = m
#     newLine[0:endPeakLeft] = m
#     return newLine
    
def eraseNoises(lineY):
    newLine = copy.deepcopy(lineY)
    leftB = 125
    rightB = 125
    #print(newLine.shape)
    mid = int(np.amax(np.where(newLine < 0.35))/2) + 20
    m = np.mean(newLine[75:125])
#     print(F"mid : {mid}")
    idL = np.where(newLine[0:mid] < 0.35)
    idL = idL[0]
    startPeakLeft = idL[-1]
    #newLine[startPeakLeft:startPeakLeft+80] = m
#     print(F"start peak left : {startPeakLeft}")
    endPeakLeft = idL[-1]- 5 #Sur image de 320x240 largeur ligne = 8 pixels --> 8 * 200/320
    idR = np.where(newLine[mid:] < 0.35)
    idR = idR[0]+mid
    startPeakRight = idR[0]
#     print(F"start peak Right : {startPeakRight}")
    endPeakRight = idR[0] + 5
    
    newLine[endPeakRight:] = m
    newLine[0:endPeakLeft] = m
    return newLine


def secondProcess(image):
    nLines = 58#image.shape[0]
    yPlan = image[:,:,0]
    newImg = copy.deepcopy(image)   
    newImg[:,:,0] = np.apply_along_axis(eraseNoises,axis=1,arr = yPlan)
    return newImg   

def ImagePreprocess (image):
    height, _, _ = image.shape
    image = image[200-15:-15,:,:]  # remove top half of the image, as it is not relevant for lane following --> int(height/2)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)  # Nvidia model said it is best to use YUV color space
    image = cv2.GaussianBlur(image, (3,3), 0)
    image = cv2.resize(image, (200,66)) # input image size (200,66) Nvidia model
    image = image / 255 
#   img = secondProcess(image)
    return image

def dataGenerator(imagePaths, steeringAngles,batchSize,isTraining):
    while True:
        batchImages = []
        batchSteering = []
        for i in range(batchSize):
            randomIdx = random.randint(0,len(imagePaths)-1)
            imagePath = imagePaths[randomIdx]
            image = imreadModif(imagePath)
            steeringAngle = steeringAngles[randomIdx]
            if isTraining:
                # Image modification for training
                image,steeringAngle = randomModify(image,steeringAngle)
            # print(randomIdx)
            # print(imagePath)
            image = ImagePreprocess(image) #Potentially secondProcess(ImagePreprocess(...))
            batchImages.append(image)
            batchSteering.append(steeringAngle)
        yield (np.asarray(batchImages),np.asarray(batchSteering))

def findLogFile(dirPath):
    for file in os.listdir(dirPath):
            if file.endswith(".csv"):
                logFile = os.path.join(dirPath,file)
                logFile = logFile.replace(os.sep,'/')
    return logFile

def readFiles(fPath):
    steeringList = []
    img_path = []
    namesList = []
    for subdir, dirs, files in os.walk(fPath):
        for dirw in dirs:
            file_list = os.listdir(os.path.join(fPath,dirw))
            dirPath = os.path.join(fPath,dirw)
            logsDirectory = findLogFile(dirPath)
            #print(logsDirectory)
            fimg_path = []
            fsteeringList = []
            fnamesList = []
            pattern = "*.png"
            dfRead = pd.read_csv(logsDirectory,header=None)
            for fName in file_list:
                if fnmatch.fnmatch(fName,pattern):
                    img_path.append(os.path.join(dirPath,fName))
                    namesList.append(fName)
                    a = findSteering(dfRead,fName)
                    steeringList.append(a)
    #     steeringList.append(fsteeringList[:])
    #     img_path.append(fimg_path[:])
    #     namesList.append(fnamesList[:])
    df = pd.DataFrame()
    df['ImagePath'] = img_path
    df['Angle'] = steeringList  
    return steeringList,img_path,namesList