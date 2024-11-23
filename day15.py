# Use of __init__ constructor:

'''
class xyz():
    def __init__(self):
        self.a = int(input("enter a number:"))
        self.b = int(input("enter a number:"))

    def sum(self):
        self.c = self.a + self.b
        print(self.c)


X1 = xyz()
X1.sum()
'''

# HW

'''
class ADD():

    def __init__(self, a=None, b=None):
        self.a = a
        self.b = b

    def sum(self, a1, a2):
        self.SA = a1.a + a2.a
        self.SB = a1.b+a2.b

    def disp(self):
        print(" The sum is:  ", self.SA, self.SB)


A1 = ADD(10, 20)
A2 = ADD(5, 8)
A3 = ADD()
A3.sum(A1, A2)
A3.disp()
'''

# none means blank:

'''
class area():

    def __init__(self, a=None, b=None):
        if isinstance(a, int) and b is None:
            print(" area of sqaure is ", a*a)
        elif isinstance(a, float) and b is None:
            print(" area of circle is ", 3.14*a*a)
        else:
            print(" area of rectangle is ", a*b)


A1 = area(10, 0)
A2 = area(10, 20)
A3 = area(10.5)


'''

'''
class volume():

    def __init__(self, a=None, b=None, c=None):
        if isinstance(a, int) and b is None and c is None:
            print(" volume of cube is is ", a**3)
        elif isinstance(a, int) and isinstance(b, float) and c is None:
            print(" volume of cylinder is ", 3.14*a**2*b)
        else:
            print(" volume of cubeoid is ", a*b*c)


A1 = volume(10)
A2 = volume(10, 10.5)
A3 = volume(10, 10.5, 20)
'''
