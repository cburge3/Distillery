import wget
import multiprocessing
import time

def checkport(port):
    file = wget.download("http://portquiz.net:" + port)

# bar
def bar():
    for i in range(100):
        checkport(i)

if __name__ == '__main__':
    # Start bar as a process
    p = multiprocessing.Process(target=bar)
    p.start()

    # Wait for 10 seconds or until process finishes
    p.join(10)

    # If thread is still active
    if p.is_alive():
        print "running... let's kill it..."

        # Terminate
        p.terminate()
        p.join()