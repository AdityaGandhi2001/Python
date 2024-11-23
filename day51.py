'''
def fact(r):
    f = 1
    while r > 0:
        f = f*r
        r = r-1
    return f


x = int(input("enter a number:"))
n = int(input("enter a number:"))
sum = 0
for i in range(1, n+1):
    sum = sum+fact(x+i)//(i+1)
    print(sum)
'''

'''
def fact(r):
    f = 1
    while r > 0:
        f = f*r
        r = r-1
    return f


x = int(input("enter a number:"))
n = int(input("enter a number:"))
sum = 0
for i in range(1, n+1):
    if i % 2 != 0:
        sum = sum+fact(x+i)//(i+1)
    else:
        sum = sum-fact(x+i)//(i+1)
    print(sum)
'''

'''
def factors(R):
    for i in range(1, R+1):
        if R % i == 0:
            print(i, end=" ")


A = int(input("enter a number 1: "))
B = int(input("enter a number 2: "))

if A > B:
    A, B = B, A
for i in range(A, B):
    print(i, end='=')
    factors(i)
    print()
'''

'''
A = int(input("Enter a number: "))


def table(B, i):
    if i <= 10:
        print(2*i)
        i += 1
        table(B, i)


table(A, 1)
'''
'''
a = int(input("enter a number: "))
b = int(input("enter a number: "))
sum = 0


def result(a, b):
    global sum
    if b >= 0:
        sum = sum+(a*1)
        b -= 1
        result(a, b)
    if b == 0:
        print(sum)


result(a, b)
'''
'''
a = int(input("enter a number: "))
b = int(input("enter a number: "))


def result(a, b):
    if b == 1:
        return a
    else:
        return (a*result(a, b-1))


print(result(a, b))
'''

'''
def sd(A):
    if A > 0:
        r = A % 10
        A = A//10
        sum = r+sd(A)
        return (sum)
    elif (A == 0):
        return 0


print(sd(189))

'''
'''
sum = 0
count = 8
L = [0, 1]

while count > 0:
    X = len(L)-1
    sum = L[X-1]+L[-1]
    L.append(sum)
    count -= 1
print(L)
'''

'''
a = int(input("Enter a number 1: "))
b = int(input("Enter a number 2: "))
sum = 0
count = 8
print(a)
print(b)
while count > 0:
    sum = a+b
    print(sum)
    a = b
    b = sum
    count -= 1
'''
'''
count = 8


def sum1(a, b):
    global count
    if count > 0:
        sum = a+b
        print(sum)

        count -= 1
        sum1(b, sum)


print(0)
print(1)
sum1(0, 1)
'''

# Making Fibonacci Series Using Recursion:


def xyz(i):
    if i == 0 or i == 1:
        return i
    else:
        return (xyz(i-1)+xyz(i-2))


for i in range(12):
    print(xyz(i))
