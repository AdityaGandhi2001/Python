'''
x = int(input("enter a number:"))
rn = 0
while x > 0:
    r = x % 10
    rn = (rn*10)+r
    x = x//10
print(rn)
'''
'''
x = int(input("Enter a number: "))
b = x
count = 0
while (b > 0):
    count += 1
    b = b//10
print(count)


def xyz(count, x):

    if x > 0:
        r = x % 10
        rvr = r*(10**count)+xyz(count-1, x//10)
        return rvr
    elif (x == 0):
        return 0


print(xyz(count-1, x))
'''
'''
S1 = []
S2 = []


def ADD(X, L):
    L.append(X)


def REMOVE(L):
    L.pop()


def disp():
    print(S1)
    print(S2)


while (True):
    Choice = int(input("enter your choice:"))
    if Choice == 1:
        X = int(input("Enter a number: "))
        ADD(X, S1)
    elif Choice == 2:
        y = S1[-1]
        REMOVE(S1)
        Choice = int(input("enter your choice:"))
        if Choice == 0:
            ADD(y, S2)
    elif Choice == 3:
        disp()
    elif Choice == 4:
        break
'''

# TWO STACK QUESTION USING A SINGLE STACK:
L = []
z = len(L)
top1 = -1
top2 = 4
for i in range(10):
    L.append(0)


def push1(X, S):
    global top1
    top1 += 1
    if top1 <= 4:
        S[top1] = X
    else:
        print("Stack is full")


def push2(X, S):
    global top2
    top2 += 1
    if top2 <= 9:
        S[top2] = X
    else:
        print("Stack is full")


def pop1(S):
    global top1
    X = S[top1]
    if top1 >= 0:
        S[top1] = 0
        top1 -= 1
        return X
    else:
        print("Stack is empty")
        S[top1] = 0
        top1 -= 1
        return X


def pop2(S):
    global top2
    Y = S[top2]
    if top2 >= 5:
        S[top2] = 0
        top2 -= 1
        return Y
    else:
        print("Stack is empty")
        S[top2] = 0
        top2 -= 1
        return S[top2]


def disp():
    print(L[0:top1+1])
    print(L[5:top2+1])


while (True):
    Choice = int(input("enter your choice:"))
    if Choice == 1:
        X = int(input("Enter a number: "))
        push1(X, L)
    elif Choice == 2:
        X = int(input("Enter a number: "))
        push2(X, L)
    elif Choice == 3:
        pop1(L)
    elif Choice == 4:
        pop2(L)
    elif Choice == 5:
        disp()
    else:
        break
