'''
l = [1, 2, 3, 4, 5]
flag = False
data = int(input("enter a number : "))
for i in range(len(l)):
    if data == l[i]:
        flag = True
        break

if (flag):
    print("data found at %d position" % (i+1))
else:
    print("not found")
'''
'''
l = [1, 5, 9, 15, 20, 22, 28, 30, 40]
data = int(input("enter a number:  "))
A = len(l)
LB = 0
UB = len(l)-1
if data in l:
    while UB >= LB:
        X = (LB+UB)//2
        if data == l[X]:
            print("found", l[X])
            break
        elif data > l[X]:
            LB = X+1
        else:
            UB = X-1
else:
    print("not found")
'''

'''
l = [1, 5, 9, 15, 20, 22, 28, 30, 40]
data = int(input("enter a number:  "))
A = len(l)
LB = 0
UB = len(l)-1
flag = False
while UB >= LB:
    X = (LB+UB)//2
    if data == l[X]:
        flag = True
        break
    elif data > l[X]:
        LB = X+1
    else:
        UB = X-1
if (flag):
    print("found", X)
else:
    print("not found")
'''

# SIMPLE SELECTION SORTING:

'''
l = [4, 3, 5, 2, 1]
for i in range(len(l)-1):
    for j in range(i+1, 5):
        if l[i] > l[j]:
            l[i], l[j] = l[j], l[i]
print(l)
'''


# BUBBLE SORTING:

'''
l = [4, 3, 5, 2, 1]
for i in range(0, len(l)-1):
    for j in range(0, len(l)-1-i):
        if l[j] > l[j+1]:
            l[j], l[j+1] = l[j+1], l[j]
print(l)
'''


# INSERTION SORT:

l = [8, 6, 3, 4, 2]
for i in range(1, len(l)):
    flag = True
    k = l[i]
    for j in range(i-1, -1, -1):
        if l[j] > k:
            l[j+1] = l[j]
        else:
            flag = False
            break
    if (not flag):
        l[j+1] = k
    else:
        l[0] = k
print(l)
