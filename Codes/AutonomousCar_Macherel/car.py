import sys, getopt, os,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
from actuator_controller import SteeringController,SpeedController
from cameraController import PicameraController
#
# from image_warper import ImgWarper
# from image_rectifier import ImgRectifier
# from UndistortImage import ImageCalibrator
#
import time


class Car():
    def __init__(self,conf,current_threads_fps=None,hardSteer = False,hardSpeed = False):
        self.conf = conf
        self.SteeringCtrl = SteeringController(
            pin=self.conf["PIN"]["pwm_steering"],
            minDutyCycle = self.conf["CAR"]["steering_pwm_dc_min"],
            maxDutyCycle = self.conf["CAR"]["steering_pwm_dc_max"], 
            hardware=hardSteer
        )
        self.SpeedCtrl = SpeedController(
            pin=self.conf["PIN"]["pwm_speed"],
            minDutyCycle = self.conf["CAR"]["speed_pwm_dc_min"],
            maxDutyCycle = self.conf["CAR"]["speed_pwm_dc_max"],
            hardware=hardSpeed
        )
        self.camera = PicameraController(
            cam_param_dict = [(arg, value) for (arg, value) in self.conf['CAMERA']['parameters'].items() if value != None],
            current_threads_fps = current_threads_fps,
            conf= self.conf,
            #resolution= self.conf["ROAD_FOLLOWING"]["img_resolution"][::-1]
        )

        print("Camera warming up \n")
        time.sleep(1) # Time for camera to be ready
        print("Camera warmed up \n")

    def __enter__(self):
        """ Entering a with statement """
        self.start()
        return self
    
    def __exit__(self, exception_type, exception_value, traceback):
        self.stop()
        """ Exit a with statement"""

    def start(self):
        self.SteeringCtrl.startPwm()
        self.SpeedCtrl.startPwm()
        self.camera.startThread()
        # Start a fullscreen raw preview
        # if self.conf["DISPLAY"]["show_cam_preview"]:
        #     self.camera.start_preview()

    def stop(self):
        self.camera.stopThread()
        self.camera.stop_preview()
        # self.steeringCtrl.stopPwm()