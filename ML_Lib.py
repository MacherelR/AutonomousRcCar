# python standard libraries
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
%matplotlib inline
from PIL import Image



import csv

def findSteering(df,fName):
  row = df.loc[df[0] == fName]
  return row.iat[0,1]
  
  
def imreadModif(imgPath):
  image = cv2.imread(imgPath)
  image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
  return image
  
def zoom(image):
  zoom = img_aug.Affine(scale= (1,1.3)) # zoom to 130%
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

def ImagePreprocess (image):
  height, _, _ = image.shape
  image = image[int(height/2):,:,:]  # remove top half of the image, as it is not relevant for lane following
  image = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)  # Nvidia model said it is best to use YUV color space
  image = cv2.GaussianBlur(image, (3,3), 0)
  image = cv2.resize(image, (200,66)) # input image size (200,66) Nvidia model
  image = image / 255 # normalizing, the processed image becomes black for some reason.  do we need this?
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

      image = ImagePreprocess(image)
      batchImages.append(image)
      batchSteering.append(steeringAngle)
    yield (np.asarray(batchImages),np.asarray(batchSteering))

