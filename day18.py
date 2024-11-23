'''
class student():

    def input(self):
        self.rollno = int(input("enter the roll number: "))
        self.name = input("enter the name of the student: ")


class test(student):

    def input(self):
        super().input()
        self.p = int(input("enter marks in physics: "))
        self.c = int(input("enter marks in chemistry: "))
        self.m = int(input("enter marks in maths: "))


class sports(student):

    def input(self):
        super().input()
        self.score = int(input("enter the score: "))


class result(sports, test):

    def result1(self):
        self.total = self.p+self.c+self.m+self.score
        print("The overall details of the student are: ", self.rollno,
              self.name, self.p, self.c, self.m, self.score, self.total)


R1 = result()
R1.input()
R1.result1()
'''

# Function overloading:
'''

class student():

    def input(self):
        self.rollno = int(input("enter the roll number: "))
        self.name = input("enter the name of the student: ")


class test(student):

    def input(self, P, C, M):
        super().input()
        self.P = int(input("enter marks in physics: "))
        self.C = int(input("enter marks in chemistry: "))
        self.M = int(input("enter marks in mths: "))


class sports(student):

    def input(self, score):
        super().input()
        self.score = int(input("enter the score: "))


class result(sports, test):

    def input(self, total):
        super().input()
        self.total = self.P+self.C+self.M+self.score

    def result1(self):
        print("The overall details of the student are: ", self.rollno,
              self.name, self.p, self.c, self.m, self.score, self.total)


R1 = result()
R1.input()
R1.result1()


# function overloading: OCCURS IN BOTH INHERITANCE AND NON INHERITANCE:
# at time of passing or calling function we not need to mention self inside the function:
# DOUBT:
'''
# Overloading:
'''
class A:
    def disp(self, x):
        print(x)


class B(A):
    def disp(self):
        super().disp(10)
        print("hello")


B1 = B()
B1.disp()
'''

'''
class A():

    def input(self):
        self.A = input("enter  a:")


class B(A):

    def input(self):
        super().input()
        self.B = input("enter b:")

    def findB(self):
        if self.B in self.A:
            self.bi = self.A.index(self.B)

    def disp(self):
        print("The result:", self.bi)


class C(A):

    def input(self):
        super().input()
        self.C = input("enter c:")

    def findC(self):
        if self.C in self.A:
            self.ci = self.A.index(self.C)
        for i in range(0, self.ci+1):
            print(i)
            if (self.A[i] == "a" or self.A[i] == "e" or self.A[i] == "i" or self.A[i] == "o" or self.A[i] == "u"):
                break
        if self.ci == i:
            print("found")
        else:
            print("not found")


b1 = B()
b1.input()
b1.findB()
b1.disp()
c1 = C()
c1.input()
c1.findC()
'''


class A:
    def disp(self):
        print("A")


class B(A):
    def disp(self):
        super().disp()
        print("hello")


B1 = B()
B1.disp()
