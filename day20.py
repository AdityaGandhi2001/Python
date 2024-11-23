#
'''
class A():

    def input(self):

        self.a = int(input("enter a number: "))


class B(A):

    def input(self):
        super().input()
        self.b = int(input("enter a number: "))

    def hcf(self):
        if self.a > self.b:
            self.a, self.b = self.b, self.a
        while (1):
            self.k = self.b % self.a
            if self.k == 0:
                break

            self.b = self.a
            self.a = self.k
        print(self.a)


b1 = B()
b1.input()
b1.hcf()
'''

'''
class stock():

    def input(self):
        self.name = input("enter the stock name: ")


class amount(stock):

    def input(self):
        super().input()
        self.q = int(input("enter the quantity: "))
        self.r = int(input("enter the rate: "))

    def calculate(self):
        self.amount = self.q*self.r


class paid_amount(amount):

    def calculate(self):
        super().calculate()
        if self.amount >= 20000:
            self.discount = 0.2*self.amount
        else:
            self.discount = 0.1*self.amount
        self.PA = self.amount-self.discount

    def disp(self):
        print("The stock details are: ", self.name, self.q,
              self.r, self.amount, self.discount, self.PA)


b = paid_amount()
b.input()
b.calculate()
b.disp()
'''
