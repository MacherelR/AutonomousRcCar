import sys, getopt, os,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
import cv2
import TB_Library
import yaml

CONFIG_FNAME = os.path.join(currentdir, 'conf_MAR.yaml')

from cameraController import PicameraController

if __name__ == '__main__':
    conf = TB_Library.load_configuration(CONFIG_FNAME)
    camera = PicameraController(
        cam_param_dict=[(arg, value) for (arg, value) in conf['CAMERA']['parameters'].items() if value != None],
        current_threads_fps = None
    )  
    img = camera.capture_np()
    roi = cv2.selectROI("ROI selection",img,showCrosshair=True,fromCenter=False)
    img_cropped = img[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]
    cv2.imshow("Initial", img)
    cv2.imshow("ROI cropped",img_cropped)
    cv2.waitKey(1)
    #print(roi)
    data = {"ROI": roi}
    file = open("Conf_ROI.yaml",'w')
    yaml.dump(data,file)
    file.close()
    #cv2.destroyAllWindows()
    




