'''
class A():

    def input(self, A):
        self.A = A


class B(A):

    def input(self, A, B):
        super().input(A)
        self.B = B

    def findB(self):
        if self.B in self.A:
            self.bi = self.A.index(self.B)

    def disp(self):
        print("The result:", self.bi)


class C(A):

    def input(self, A, C):
        super().input(A)
        self.C = C

    def findC(self):
        if self.C in self.A:
            self.ci = self.A.index(self.C)
        for i in range(0, self.ci+1):
            if (self.A[i] == "a" or self.A[i] == "e" or self.A[i] == "i" or self.A[i] == "o" or self.A[i] == "u"):
                break
        if self.ci == i:
            print("found")
        else:
            print("not found")


b1 = B()
b1.input("computer", "om")
b1.findB()
b1.disp()
c1 = C()
c1.input("computer", "om")
c1.findC()
'''

# Use lambda function instead of using user defined function:

'''
fun=lambda x : x*x
print(fun(2))

f=lambda x,y: x*y
print(f(5,2))
'''

'''
f=lambda x,y: x if x >y else y 

print(f(10,20))
'''

'''
def f(x):
    return x*x

L=[4,5,9,2,8]
for i in L:
    print(f(i))
'''

'''
f=lambda x: x*x
L=[4,5,9,2,8]
for i in L:
    print(f(i))
'''

'''
f=lambda x:x*x
L=[4,5,9,2,8]
print(list(map(f,L)))
'''

'''

f=lambda x,y,z: x if x>y and x>z else y if y>z else z
print(f(10,20,30))

'''
