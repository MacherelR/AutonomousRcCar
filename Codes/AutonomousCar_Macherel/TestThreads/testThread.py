import threading
import time

class myThread(threading.Thread):
    def __init__(self,threadID,name,counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.stopped = False
    # def run(self):
    #     print("Starting " + self.name)
    #     #Get lock
        
    #     print_time(self.name,self.counter,5)
    #     #Free lock
    def __enter__(self):
        self.startThread()
        return self
    def __exit__(self, exception_type, exception_value, traceback):
        self.stopThread()
        #print(F"Exiting thread {self.name}")
    def startThread(self):
        t = threading.Thread(target=self._run,name=self.__class__.__name__,args=())
        t.start()
        self.stopped = False
        return self
    def stopThread(self):
        self.stopped = True
    def _run(self):
        while not self.stopped:
            print_time(self.name,self.counter,5)




def print_time(threadName, delay, counter):
    while counter:
      time.sleep(delay)
      #threadlock.acquire()
      print(F"{threadName} : {time.ctime(time.time())}")
      counter -= 1
      #threadlock.release()
    print(F"End of {threadName}")


threadlock = threading.Lock()
threads = []

if __name__ == '__main__':
    th1 = myThread(1,"Thread 1",1)
    th2 = myThread(2,"Thread 2",2)
    th3 = myThread(3,"Thread 3",3)
    with th1 :
        with th2:
            with th3:
                print("both threads running ")
    # threads.append(th1)
    # threads.append(th2)

    # for t in threads:
    #     t.join()
