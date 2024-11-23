# check whether the number is prime or not
'''
a = int(input("enter a number:"))
count = 0
for i in range(1, a+1):
    if a % i == 0:
        count += 1
if count == 2:
    print("it is a prime nummber")
else:
    print("it is not a prime number")
'''
# print function by default enters value in next line . So to avoid it we use a command end="\t"
'''
for i in range(1, 11):
    print(2*i, end="\t")
'''

# Using a for loop over a for loop
'''
for k in range(2, 11):
    for i in range(1, 11):
        print(k*i, end="\t")
    print()
'''
# Example:
'''
for k in range(1, 11):
    for i in range(1, 5):
        print(i, end="\t")
    print()
'''

# Example1: Building a pattern:
'''
for i in range(5, 1, -1):
    for j in range(1, i):
        print(j, end="\t")
    print()
'''

# Example2: Building a pattern:
'''
for i in range(2, 6):
    for j in range(1, i):
        print(j, end="\t")
    print()
'''
# Example3: Building a pattern:
# -1 should be written for decrement
'''
for i in range(4, 9):
    for j in range(9, i, -1):
        print(j, end="\t")
    print()
'''
# Homework:
'''
for i in range(2, 9, 2):
    for j in range(1, i, 2):
        print(j, end="\t")
    print()
'''

# ex:5
'''
for i in range(8, 3, -1):
    for j in range(9, i, -1):
        print(j, end="\t")
    print()
'''

# Ex:6
'''
for i in range(0, 4):
    for j in range(4, i, -1):
        print(j, end="\t")
    print()
'''


# Ex: 7

'''
total = 0
for i in range(2, 101):
    count = 0
    for j in range(1, i+1):
        if i % j == 0:
            count += 1
    if count == 2:
        print(i, end="\t")
        total += 1
print()
print(total)
'''

# Building a star pattern:
'''
for i in range(5):
    for j in range(i+1):
        print("*", end="")
    print()
'''

'''
sp = 4
for i in range(5):
    for j in range(sp):
        print(" ", end="")
    for j in range(i+1):
        print("*", end="")
    print()
    sp -= 1
'''

'''
l = 1
sp = 3
for i in range(4):
    for j in range(sp):
        print(" ", end="")
    for j in range(i+1):
        print(l, end=" ")
    l += 1
    print()
    sp -= 1
'''
'''
N = 65
sp = 4
for i in range(5):
    for j in range(sp):
        print(" ", end="")
    for j in range(i+1):
        print(chr(N), end="")
    N += 1
    print()
    sp -= 1
'''
'''
N = 65
for i in range(5):
    for j in range(i+1):
        print(chr(N), end="")
        N += 1
    print()
'''

'''
N = 65
for i in range(5):
    for j in range(i+1):
        print(chr(N), end="")
    N += 1
    print()
'''

'''
sp = 4
N = 65
for i in range(5):
    for j in range(sp):
        print(" ", end="")
    for j in range(i+1):
        print(chr(N), end=" ")
        N += 1
    N = 65
    print()
    sp -= 1
'''

'''
sp = 4
L = 1
for i in range(5):
    for j in range(sp):
        print(" ", end="")
    for j in range(i+1):
        print(L, end=" ")
    print()
    sp -= 1
'''
