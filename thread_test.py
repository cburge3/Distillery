from threading import Thread, Event
import time


class ControlExecution(Thread):
    def __init__(self, function, scan_time):
        Thread.__init__(self)
        self.function = function
        self.event = Event()
        self.scan_time = scan_time

    def run(self):
        print("running")
        while not self.event.is_set():
            self.function('ygb','pdq',troll=True,mason='dog')
            self.event.wait(self.scan_time)
        print("stopped")
        self.event.clear()
        Thread.__init__(self)

    def stop(self):
        self.event.set()
        print("stopping")

def q(*args,**kwargs):
    print(type(args),type(kwargs))
    for l in args:
        print(l, args, kwargs)


print(q)
z = ControlExecution(q, 3)
z.start()
print("sleeping")
time.sleep(10)
z.stop()

time.sleep(5)
z.start()
print("end of main execution")

