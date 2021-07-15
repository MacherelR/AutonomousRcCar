import pigpio
import time
pi = pigpio.pi()
# 1000000
pi.hardware_PWM(18,50,int(1000000*0.08))# Correspond to 1.68ms --> 7.875 %

time.sleep(10)
#pi.set_PWM_dutycycle(18,255*0.075)
pi.stop()