
class ADD():

    def input(self):
        self.a = int(input("enter a number : "))
        self.b = int(input("enter a number:  "))

    def sum(self):
        self.c = self.a+self.b

    def disp(self):
        print("the result is :", self.c)


class MUL(ADD):

    def mul(self):
        self.c = self.a*self.b


A1 = ADD()
A1.input()
A1.sum()
A1.disp()
B1 = MUL()
B1.input()
B1.mul()
B1.disp()


'''
class student():

    def inputdata(self):

        self.name = input("enter name of the student:")
        self.rollno = int(input("enter the rollno:   "))


class test(student):

    def inputmarks(self):

        self.p = int(input("enter  the marks in physics :"))
        self.c = int(input("enter the marks in chemistry:   "))
        self.m = int(input("enter the marks in maths:"))


class result(test):

    def total(self):

        self.totalmarks = self.p+self.c+self.m

    def disp(self):
        print(" Student Profile:", self.name, self.rollno,
              self.p, self.c, self.m, self.totalmarks)


A1 = result()
A1.inputdata()
A1.inputmarks()
A1.total()
A1.disp()
'''

'''
class A:

    def inputa(self):
        self.a = int(input("enter the number:"))


class B:

    def inputb(self):
        self.b = int(input("enter the number:"))


class C(A, B):

    def hcf(self):
        if self.a > self.b:
            self.a, self.b = self.b, self.a
        for i in range(self.a, 0, -1):
            if self.a % i == 0 and self.b % i == 0:
                self.c = i
                break
        print("the hcf is :", self.c)


A1 = C()
A1.inputa()
A1.inputb()
A1.hcf()
'''

'''
class A():
    def inputa(self):
        self.a = int(input("enter  number a: "))


class B(A):
    def inputb(self):
        self.b = int(input("enter number b:"))

    def power(self):
        self.resultab = self.a**self.b

    def disp(self):
        print("the result is:", self.resultab)


class C(A):

    def inputc(self):
        self.c = int(input("enter the number c:"))

    def greater(self):
        if self.a > self.c:
            self.greater = self.a
        else:
            self.greater = self.c

    def disp(self):
        print("the result is:", self.greater)


B1 = B()
B1.inputa()
B1.inputb()
B1.power()
B1.disp()
C1 = C()
C1.inputa()
C1.inputc()
C1.greater()
C1.disp()
'''
