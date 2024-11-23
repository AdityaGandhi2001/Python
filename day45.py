'''
def disp(x=None, y=None):

    if isinstance(x, int) and isinstance(y, int):
        print(x, y)
    elif isinstance(x, int):
        print(x)
    elif isinstance(y, float):
        print(y)


disp(10)
disp(10, 20)
disp(None, 0.5)
'''

'''
class A():

    def disp(self, x=None, y=None):

        if isinstance(x, int) and isinstance(y, int):
            print(x, y)
        elif isinstance(x, int):
            print(x)
        elif isinstance(y, float):
            print(y)


A1 = A()
A1.disp(10)
A1.disp(10, 20)
A1.disp(None, 0.5)
'''

'''
class A():

    def disp(self, x):
        print(x)


class B(A):
    def disp(self, x, y):
        super().disp(10)
        print(x, y)


class C(B):
    def disp(self, x):
        super().disp(10, 20)
        print(x)


C1 = C()
C1.disp(0.5)

'''

'''
class A():

    def disp(self):
        print("A")


class B(A):
    def disp(self):
        super().disp()
        print("B")


class C(B):
    def disp(self):
        super().disp()
        print("C")


C1 = C()
C1.disp()
'''

l = []
max = int(input("enter list size:"))


def push(num):
    if len(l) < max:
        l.append(num)
    else:
        print("Stack is full")


def disp():
    print(l)


while (True):
    x = int(input("enter your choice:"))
    if x == 1:
        num = int(input("enter a number"))
        push(num)
    elif x == 2:
        if len(l) > 0:
            l.pop()
        else:
            print("stack is empty")
    elif x == 3:
        disp()
    elif x == 4:
        break
