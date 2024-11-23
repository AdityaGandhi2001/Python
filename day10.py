#

'''
D = {'Name': ["A", "B", "C"], 'Age': ["10", "20", "30"]}
A = {'Class': ["V"], 'Address': ["Ggn"]}
D.update(A)
print(D)
'''

# set give s unique elemnets despite of the presence of multiple duplicate elements:
'''
s = {1, 2, 3, 2, 5}
print(s)
'''

# conversion of list into set:

'''
L = [1, 2, 2, 3, 4]
L = set(L)
print(L)
'''

# Functions:
# def= define function

'''
def disp():
    print("hello")


disp()
'''

'''
a = 10


def disp():
    print(a)


disp()
'''

# Will show error if not mentioned in local variable:

'''
a = 10


def disp():
    a = a+5
    print(a)


disp()
'''

'''
A = 10


def disp():
    A = 10
    A = A+5
    print(A)


disp()
print(A)
'''

# We have to metion as a global to change the value of global:

'''
A = 10


def disp():
    global A
    A = A+5
    print(A)


disp()
print(A)
'''

'''
def Add(x, y):
    print(x+y)


Add(10, 20)
'''

'''
def Add(x, y):
    return (x+y)


Sum = Add(10, 20)
print("Addition :", Sum)
'''

'''
A = int(input("enter a number: "))
N = int(input("enter the power: "))


def total(A, N):

    return (A**N)


sum = 0
for i in range(1, N+1):
    sum = sum+total(A, i)
print(" addition:", sum)
'''

'''
def fact(a):
    f = 1
    while (a > 0):
        f = f*a
        a -= 1
    return (f)


X = int(input("enter a variable: "))
n = int(input("enter value of n"))
sum = 0
for i in range(1, n+1):
    sum = sum+fact(X+i)//(i+1)
print(sum)
'''

'''
def fact(a):
    f = 1
    while (a > 0):
        f = f*a
        a -= 1
    return (f)


sum = 0
A = int(input("enter a number:"))
B = A

while (A > 0):
    r = A % 10
    sum = sum+fact(r)
    A = A//10
print(sum)
if sum == B:
    print("It is a perfect number ")
else:
    print("it is not a perfect number")
'''
