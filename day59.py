# Threading in Python:

import threading

def square(num):
    print("Square: {}".format(num*num))

def cube(num):
    print("Cube: {}".format(num*num*num))
    
t1=threading.Thread(target=square,args=(10,))
t2=threading.Thread(target=cube,args=(10,))
t1.start()
t2.start()

t1.join()
t2.join()

print("Done!")