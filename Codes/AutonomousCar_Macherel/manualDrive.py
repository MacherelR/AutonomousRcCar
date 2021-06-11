import sys, getopt, os,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import asyncio
from evdev import InputDevice, categorize, ecodes, util
import TB_Library
from actuator_controller import SteeringController, SpeedController
from multiprocessing.connection import Client

"""Pin declaration with BCM format"""
PIN_SPEED = 18
PIN_STEERING = 19

def print_error():
     print(f"{os.path.basename(__file__)} -e <Controller event filename>")


def main(argv):
    #launch socket connection
    address = ('localhost', 6000)
    with Client(address,authkey=None) as c:
        event_filename = '/dev/input/event5'
        #Get arguments
        try:
            opts, args = getopt.getopt(argv, "h?e:", ["help", "event="])
        except getopt.GetoptError:
            print_error()
            sys.exit(2)
        for opt, arg in opts:
            if opt in ('-h', '-?', '--help'):
                print_error()
                sys.exit()
            elif opt in ("-e", "--event"):
                event_filename = arg
        run_manually(event_filename,c) 

def run_manually(event_filename,c):
    controller = InputDevice(event_filename)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(event_manager(controller,c))
    except KeyboardInterrupt:
        print("Received exit, exiting")
        # c.send('close')
        loop.close()
        
    loop.run_in_executor
async def event_manager(device,c):
    SpeedCtrl = SpeedController(PIN_SPEED,1.2,1.4,True)#1.4 pour limiter la vitesse, voire moins
    SteeringCtrl = SteeringController(PIN_STEERING,1.2,1.8,True) 
    SteeringCtrl.startPwm()
    SpeedCtrl.startPwm()
    c.send('Ready')
    async for event in device.async_read_loop():
        if event.type == ecodes.EV_ABS:
            if  event.code == ecodes.ABS_X:  #Joy Gauche / Gauche- Droite+
                val = TB_Library.map(event.value, 0, 255, 2, 0)
                c.send(val)
                SteeringCtrl.angle(val) #Inverse des limites afin de tourner a gauche lorsque l'on pointe le joystick à gauche
                #print("X: ", event.value)
            elif  event.code == ecodes.ABS_RY: #Joy Droite / Haut- Bas+
                SpeedCtrl.speed(TB_Library.map(event.value, 0, 255, 1, -1)) # AVANT --> Marche avant , Mappage en % du max pour régler la vitesse ATTENTION voir pour arret urgence
                #print("Y: ", event.value)
        elif event.type == ecodes.EV_KEY :
            if event.code == ecodes.BTN_B : # If button B (xBox) or circle (ps4) is pressed, exiting loop !
                c.send('close')
                raise KeyboardInterrupt

if __name__ == "__main__":
   main(sys.argv[1:])