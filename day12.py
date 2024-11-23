# Class, Data Members(Methods), Objects, Use of Multiple Objects :

'''
class add():
    a = 10
    b = 20


A1 = add()
print(A1.a)
print(A1.b)


'''

'''
class Add():
    def input(self):
        x = 10
        self.a = 15

    def disp(self):
        print(self.a)
        print(x)


# while writng print(x) its gonna show an error
a1 = Add()
a1.input()
a1.disp()
'''

'''
class Add:
    def input(self):
        self.a = int(input("enter a number:   "))
        self.b = int(input("enter a number: "))

    def sum(self):
        self.c = self.a+self.b

    def disp(self):
        print("addition  ", self.c)


A1 = Add()
A2 = Add()
A1.input()
A2.input()
A1.sum()
A2.sum()
A1.disp()
A2.disp()
'''

'''
class book():

    def input(self):
        self.name = input("enter the name of the book:   ")
        self.author = input("enter the author's name:   ")
        self.page = int(input("enter the number of pages:   "))

    def disp(self):
        print("%s\t%s\t%d" % (self.name, self.author, self.page))


b1 = book()
b2 = book()
b3 = book()
b1.input()
b2.input()
b3.input()
b1.disp()
b2.disp()
b3.disp()
'''

'''
class book():

    def input(self):
        self.name = input("enter the name of the book:   ")
        self.author = input("enter the author's name:   ")
        self.page = int(input("enter the number of pages:   "))

    def disp(self):
        print("%s\t%s\t%d" % (self.name, self.author, self.page))


B = []
for i in range(3):
    B.append([])
    B[i] = book()
    B[i].input()

for i in range(3):
    B[i].disp()
print(B)

# Used boolean in this case because it would printed not found in every condition:
flag = False
data = input("enter the name of the book: ")
for i in range(3):
    if data == B[i].name:
        flag = True
        B[i].disp()
        break
if (not flag):
    print("not found")
'''

# attributes are the variable of the object:

'''

class emp():

    def input(self):
        self.code = input(" enter the code :    ")
        self.name = input(" enter the name of the employee:   ")
        self.basicsalary = int(input("enter the salary of the employee:    "))

    def calculate(self):
        self.HRA = (30*self.basicsalary)/100
        self.DA = (20*self.basicsalary)/100
        self.CONV = (10*self.basicsalary)/100
        self.TOTAL = self.basicsalary + self.HRA + self.DA + self.CONV
        self.PF = (12*self.basicsalary)/100

        if self.basicsalary < 10000:
            self.ESI = (self.basicsalary*1.75)/100
        else:
            self.ESI = 0
        self.NETSALARY = (self.TOTAL-(self.PF+self.ESI))

    def disp(self):
        print(" The net salary is:  ", self.NETSALARY)


E = []
for i in range(2):
    E.append([])
    E[i] = emp()
    E[i].input()
    E[i].calculate()

for i in range(2):
    E[i].disp()
'''
