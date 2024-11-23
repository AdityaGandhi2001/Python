'''
class ADD():
    def input(self, A, B):
        self.A = A
        self.B = B

    def sum(self, A1, A2):
        self.SA = A1.A + A2.A
        self.SB = A1.B+A2.B

    def disp(self):
        print("the sum is : ", self.SA, self.SB)


A1 = ADD()
A2 = ADD()
A3 = ADD()
A1.input(10, 20)
A2.input(5, 8)
A3.sum(A1, A2)
A3.disp()
'''

'''
class ADD():
    def input(self, A, B):
        self.A = A
        self.B = B

    def __add__(self, A2):
        TEMP = ADD()
        TEMP.A = self.A + A2.A
        TEMP.B = self.B+A2.B
        return TEMP

    def disp(self):
        print("the sum is : ", self.A, self.B)


A1 = ADD()
A2 = ADD()
A3 = ADD()
A1.input(10, 20)
A2.input(5, 8)
A3 = A1+A2
A3.disp()
'''


class Add():

    def input(self, A):
        self.A = A

    def __gt__(self, A2):
        TEMP = Add()
        if self.A > A2.A:
            TEMP.A = self.A
        else:
            TEMP.A = A2.A
        return TEMP

    def disp(self):
        print("The greater is : ", self.A)


A1 = Add()
A2 = Add()
A3 = Add()
A1.input(1)
A2.input(5)
A3 = A1 > A2
A3.disp()


'''
class Add():

    def input(self, A):
        self.A = A

    def __gt__(self, A2):
        if self.A > A2.A:
            return True
        else:
            return False

    def disp(self):
        print("The greater is : ", self.A)


A1 = Add()
A2 = Add()
A1.input(10)
A2.input(5)
if A1 > A2:
    print('hello')
else:
    print('bye')
'''


class mul():
    def input(self, A):
        self.A = A

    def __mul__(self, X):
        TEMP = mul()
        TEMP.A = self.A*X
        return TEMP

    def disp(self):
        print("THE RESULT IS: ", self.A)


A1 = mul()
A2 = mul()
A1.input(10)
A2 = A1*12
A2.disp()
