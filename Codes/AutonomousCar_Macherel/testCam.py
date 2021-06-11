import sys, getopt, os,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
from TB_Library import load_configuration
from cameraController import PicameraController
import cv2
import time
CONFIG_FNAME = os.path.join(currentdir, 'conf.yaml')


conf = load_configuration(CONFIG_FNAME)
current_threads_fps = None
camera = PicameraController(
    cam_param_dict = [(arg, value) for (arg, value) in conf['CAMERA']['parameters'].items() if value != None],
    current_threads_fps = current_threads_fps,
    conf= conf
)
camera.startThread()
print("Warming up camera")
time.sleep(1)
print("Camera ready")
size = tuple(conf['ROAD_FOLLOWING']['img_resolution'])
print(size)
input("Press Enter to continue...")
img  = camera.capture_np()

if img is not None :
    cv2.imshow("Image",cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    cv2.waitKey(1)
else:
    print("img None")
    time.sleep(0.5)