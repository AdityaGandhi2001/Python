# print all the pallindrome in between 101 to 200
'''
for i in range(101, 201):
    number = 0
    a = i
    while a > 0:
        r = a % 10
        number = (number*10)+r
        a = a//10
    if number == i:
        print(i)
'''

# print all the armstrong number in bwtween 1 to 500:

'''
for i in range(1, 501):
    a = i
    number = 0
    while a > 0:
        r = a % 10
        cube = r*r*r
        number = (number)+cube
        a = a//10
    if number == i:
        print(i)
        
'''
# LIST:
# Either use all positive index or negative index in range:
'''
L = [10, 5, 9, 2, 7]
print(L[-1:-6:-1])
'''

# using slice function:

'''
L = [10, 5, 9, 2, 7]
i = slice(1, 4, 1)
print(L[i])
L.append(20)
print(L)
'''

# Creating a list using a loop:
'''
N = int(input("enter the length of the list: "))
l = []
for i in range(N):
    X = int(input("enter the number: "))
    l.append(X)
print(l)
'''

'''
N = int(input(" enter the length of the list: "))
l = []
for i in range(N):
    l.append(int(input("enter the number:")))
sum = 0
for i in range(0, N):
    sum = sum+l[i]
print(sum)
'''
'''
N = int(input(" enter the length of the list: "))
l = []
sum = 0
for i in range(N):
    l.append(int(input("enter the number:")))
sum = 0
for j in range(0, N):
    if l[j] % 2 == 0:
        sum = sum + l[j]
print(sum)
'''

'''
N = int(input(" enter the length of the list: "))
l = []
for i in range(N):
    l.append(int(input("enter the number:")))
evensum = 0
oddsum = 0
for j in range(0, N):
    if l[j] % 2 == 0:
        evensum = evensum + l[j]
    else:
        oddsum = oddsum + l[j]
print(evensum)
print(oddsum)
'''

# using for loop for printing the list . In this i is the element

'''
l = [1, 2, 3, 4]
for i in l:
    print(i, end="\t")
'''

# Searching data in list:
'''
l = [1, 2, 3, 4]

data = int(input("enter the number:"))
if data in l:
    print("found")
else:
    print("not found")
'''

s = "1 0 1"
l = s.split(" ")
print(l)
