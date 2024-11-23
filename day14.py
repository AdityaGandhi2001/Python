# Maintaining a pand l report:

'''

class stock():

    def buyday(self):
        self.L = [7, 1, 5, 3, 6, 2]
        self.min = self.L[0]
        for k in range(len(self.L)):
            if self.L[k] < self.min:
                self.min = self.L[k]
        self.buyingday = self.L.index(self.min)

    def sellday(self):
        self.max = 0
        for i in range(self.buyingday+1, len(self.L)):
            if self.L[i] > self.max:
                self.max = self.L[i]
        self.sellingday = self.L.index(self.max)

    def pandl(self):
        self.profit = self.max-self.min

    def disp(self):
        print("The p ans l is ", self.profit)
        print("The stock was purchased on ", self.buyingday)
        print("The stock was sold on ", self.sellingday)


SP = stock()
SP.buyday()
SP.sellday()
SP.pandl()
SP.disp()

'''

# HW

'''
class EMP():

    def input(self):
        self.code = int(input("enter the code of the employee:   "))
        self.name = input(" enter the  name of the employee:    ")
        self.address = input(" enter the address of the employee:    ")
        self.basicsalary = int(input("enter the salary:      "))

    def disp(self):
        X = "A"
        X1 = "a"
        if X in self.name or X1 in self.name and self.basicsalary > 50000:
            print("the name and the salary of the employee is:  ",
                  self.name, self.basicsalary)
        else:
            print("not found")


E = []
for i in range(2):
    E.append([])
    E[i] = EMP()
    E[i].input()
for i in range(2):
    E[i].disp()
'''

'''
class reverse():

    def input(self):
        self.number = int(input(" enter a number: "))

    def find(self):
        self.L = [1, 2, 3, 4, 5]

        self.B = []
        if self.number in self.L:
            I = self.L.index(self.number)
            K = 0
            for i in range(0, I+1):
                self.B.append(self.L[K])
                print(self.B)
                self.L.remove(self.L[K])
                print(self.L)

        else:
            print("not found")

    def sort(self):
        self.L.reverse()
        self.B.reverse()

    def disp(self):
        self.finallist = self.B + self.L
        print(" the list is ", self.finallist)


A = reverse()
A.input()
A.find()
A.sort()
A.disp()
'''

# In the below program we got to see that function can also be used as a member data in other function
# Python is a smart language in which we can call the function earlier also. Its not neccesory for the function to be aligned at the top:


class reverse():

    def input(self):
        self.number = int(input(" enter a number: "))
        self.L = [1, 2, 3, 4, 5]
        if self.number in self.L:
            i = self.L.index(self.number)
            print(i)
            self.xyz(0, i)
            self.xyz(i+1, len(self.L)-1)

    def xyz(self, x, y):
        for i in range(y, x-1, -1):
            print(self.L[i], end="")


A = reverse()
A.input()
