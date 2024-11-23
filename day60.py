import threading
import time
from concurrent.futures import ThreadPoolExecutor


def func(seconds):
    print(f"Sleeping for {seconds}",end="\n")
    time.sleep(seconds)
# Normal code:

# func(4)
# func(3)
# func(1)

# here comes the concept of threading:
t1=threading.Thread(target=func,args=[4])
t2=threading.Thread(target=func,args=[2])
t3=threading.Thread(target=func,args=[1])

t1.start()
t2.start()
t3.start()

def poolingdemo():
    with ThreadPoolExecutor() as executor:
        l=[1,2,3,4]
        results=executor.map(func,l)
        for i in results:
            print(i,end="\n")
poolingdemo()
            
