# in case of inherirance at the end we have to call each and every function:

'''
class A():

    def inputa(self):
        self.a = int(input("enter a number a: "))


class B(A):

    def inputb(self):
        self.b = int(input("enter a number b: "))


class C(A):

    def inputc(self):
        self.c = int(input("enter a number c: "))


class D(B, C):

    def result(self):
        if self.a >= self.b and self.a >= self.c:
            self.greatest = self.a
        elif self.b >= self.a and self.b >= self.c:
            self.greatest = self.b
        else:
            self.greatest = self.c
        print("The greatest number is: ", self.greatest)


D1 = D()
D1.inputa()
D1.inputb()
D1.inputc()
D1.result()
'''

# Without inheritance:

'''
class A():

    def disp(self):
        print("Im in A")


class B():

    def disp(self):
        A.disp(self)
        print("Im in B")


B1 = B()
B1.disp()
'''
# we have to use self inside function always to use other function variables:
# in overriding we use super().func() else we have to use different function name
# if we dont use super function then at time of calliing its gonna take the latest value in the function skipping the earlier one:
'''

class furniture():

    def input(self):
        self.C = input("enter the color: ")
        self.W = input("enter the width: ")
        self.H = input("enter the height: ")

    def disp(self):
        print("The details of the furniture are:", self.C, self.W, self.H)


class chair(furniture):
    def input(self):
        super().input()
        self.NOL = int(input("enter the number of legs: "))

    def disp(self):
        super().disp()
        print("the number of legs are: ", self.NOL)


class bookshelf(furniture):
    def input(self):
        super().input()
        self.NOS = int(input("enter the number of shelfs: "))

    def disp(self):
        super().disp()
        print("the number of shelfs  are: ", self.NOS)


C1 = chair()
C1.input()
C1.disp()
B1 = bookshelf()
B1.input()
B1.disp()
'''

# DOUBTTT

'''
class A():
    def __init__(self):
        self.a = int(input("enter the number A: "))


class B(A):

    def __init__(self):
        super().__init__()
        self.b = int(input("enter a number B: "))


class C(A):

    def __init__(self):
        super().__init__()
        self.c = int(input("enter a number C: "))


class D(C, B):

    def __init__(self):
        super().__init__()
        self.d = int(input("enter a number D: "))

    def result(self):
        print("The values of A and B and C and D are: ",
              self.a, self.b, self.c, self.d)


D1 = D()
D1.result()
'''

# OVERRIDING IS SEEN IN CASE OF INHERITANCE : FOR THAT WE CAN USE SUPER FUNCTION:
'''
class A():

    def disp(self):
        print("Im in A")


class B(A):

    def disp(self):
        super().disp()
        print("Im in B")


B1 = B()
B1.disp()
'''
a = (1, 2)
print(a[1])
