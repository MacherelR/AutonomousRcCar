"""
- This module saves images and a log file.
- Images are saved in a folder.
- Folder should be created manually with the name "DataCollected"
- The name of the image and the steering angle is logged
in the log file.
- Call the saveData function to start.
- Call the saveLog function to end.
- If runs independent, will save ten images as a demo.
"""
# 
## ----------------------------------- Infos -----------------------------------
#   Author:            Rémy Macherel
#   Project:           Autonomous RC Car
#   File:              DataCollection.py
#   Link:              https://github.com/MacherelR/AutonomousRcCar
#   Creation date :    14.05.2021
#   Last modif date:   13.06.2021
## ----------------------------------- Infos -----------------------------------

## -------------------------------- Description --------------------------------
#   Class defined to collect data from the manual driving operation, 
#   inspired by https://github.com/murtazahassan/Neural-Networks-Self-Driving-Car-Raspberry-Pi/blob/main/Step1-Data-Collection/DataCollectionModule.py
#   Adapted and modified on purpose
## -------------------------------- Description --------------------------------

import sys, getopt, os,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
import pandas as pd
import time
import os
import cv2
from threading import Thread
from datetime import datetime
from cameraController import PicameraController
from image_warper import ImgWarper
from image_rectifier import ImgRectifier
from car import Car
import TB_Library
CONFIG_FNAME = os.path.join(currentdir, 'conf_MAR.yaml')
CONFIG_ROI_FNAME = os.path.join(currentdir,'Conf_ROI.yaml')
from multiprocessing.connection import Listener
class DataCollector():
    stopped = False
    done = False
    def __init__(self,car,Listen=None,alone = False,freqMs = 10,current_threads_fps=None):
        self.worksAlone = alone
        self.car = car
        self.camera = self.car.camera
        self.freq = freqMs/1000 # Convert in s for sleep
        self.address = Listen
        self.imagesList = []
        self.steeringList = []
        self.timesList = []
        self.folderCount = 0
        self.count = 0
        self.initialID = self.car.conf['DATACOLLECTION']['ID']
        self.currentDirectory = os.path.join(os.getcwd(),'DataCollected')
        self.meanCapture = 0
        # CREATE A NEW FOLDER BASED ON THE PREVIOUS FOLDER COUNT
        while os.path.exists(os.path.join(self.currentDirectory,f'SET{str(self.folderCount)}')):
            self.folderCount += 1
        self.newPath = self.currentDirectory +"/SET"+str(self.folderCount)
        os.makedirs(self.newPath)
    
    def saveData(self,img,steering):
        imName = "Image_{}.png".format(self.count+self.initialID)
        self.count+=1
        filename = os.path.join(self.newPath,imName)
        cv2.imwrite(filename,img)
        self.imagesList.append(imName) # Or filename, see which one's best but filename is with directory path
        self.steeringList.append(steering)

    def saveLogFile(self):
        self.rawData = {'Image': self.imagesList,
                'Steering': self.steeringList}
        df = pd.DataFrame(self.rawData)
        df.to_csv(os.path.join(self.newPath,f'log_{str(self.folderCount)}.csv'), index=False, header=False)
        print('Log Saved')
        print('Total Images: ',len(self.imagesList))
    
    def __enter__(self):
        self.startThread()
        return self
    def __exit__(self, exception_type, exception_value, traceback):
        self.stopThread()

    def startThread(self):
        t = Thread(target= self._run, name=self.__class__.__name__,args=())
        t.start()
        return self

    def saveTimeFile(self):
        if len(self.timesList) != 0:
            self.meanCapture = sum(self.timesList)/len(self.timesList)
        else:
            self.meanCapture = 0
        self.data = {'Durations : ': self.timesList,
                    'Mean : ': self.meanCapture}
        df = pd.DataFrame(self.data)
        df.to_csv(os.path.join(currentdir,'Capturetimes.csv'), index=False, header=False)

    def stopThread(self):
        self.stopped = True
        print("End recording")
        self.saveLogFile()
        self.saveTimeFile()
        self.car.conf['DATACOLLECTION']['ID'] = self.count+self.initialID
        TB_Library.write_configuration(CONFIG_FNAME,self.car.conf)
        
    
    def _run(self):
        if self.worksAlone: #Used for tests
            for i in range (10):
                image = self.camera.capture_np()
                self.saveData(image,0.5)
                cv2.waitKey(1)
            self.done = True
        else: # Normal functionning
                while (not self.stopped):
                    stTime = time.time()
                    img = self.camera.capture_np()
                    if self.stopped :
                        break
                    self.saveData(img,TB_Library.map(self.car.SteeringCtrl.currentSteering,1,-1,135,45))
                    elapsedtime = time.time() - stTime
                    self.timesList.append(elapsedtime)



if __name__ == '__main__':
    config = TB_Library.load_configuration(CONFIG_FNAME)
    myCar = Car(config)
    Collector = DataCollector(myCar,alone=True)
    with Collector :
        print("DataCollecting...")
        while (not Collector.done):
            print("...")

    cv2.destroyAllWindows()

