'''
l = [10, 9, 7, 5, 2]
l.insert(2, 15)
print(l)
'''

'''
l = [10, 9, 7, 5, 2]
A = int(input("enter a number"))
y = 3
l.append(0)
for i in range(len(l)):
    if i >= 2:
        k = l[i]
        l[i] = A
        A = k
        print(l)
'''

'''
l = [10, 9, 7, 5, 2]
A = int(input("enter a number: "))
y = 3
l.append(0)
for i in range(len(l)-2, y-2, -1):
    l[i+1] = l[i]
    print(l)
l[y-1] = A
print(l)
'''

'''
l = [10, 5, 9, 7, 2]
A = int(input("enter a number: "))
B = []
y = l.index(A)
for i in range(0, y):
    B.append(l[i])
for i in range(y+1, len(l)):
    B.append(l[i])
print(B)
'''

'''
l = [10, 5, 9, 7, 2]
A = int(input("enter a number: "))
y = l.index(A)
for i in range(y, len(l)-1):
    l[i+1], l[i] = l[i], l[i+1]
l.pop(-1)
print(l)
'''

'''
l = [10, 5, 9, 7, 2]
A = int(input("enter a number: "))
y = l.index(A)
for i in range(y, len(l)-1):
    l[i] = l[i+1]
    print(l)
l.pop(-1)
print(l)
'''


'''
def list(X):
    for i in range(5):
        Y = int(input("enter a number: "))
        X.append(Y)


A = []
B = []
list(A)
list(B)


def sort(l):
    for i in range(len(l)-1):
        for j in range(i+1, 5):
            if l[i] > l[j]:
                l[i], l[j] = l[j], l[i]


sort(A)
sort(B)
print(A)
print(B)
'''
# Merging Of Two Sorted Arrays:
'''
A = [1, 3, 9, 15, 20]
B = [2, 5, 10, 25, 30]
C = []
i = 0
j = 0
while (i < len(A) and j < len(B)):
    if A[i] < B[j]:
        P = A[i]
        C.append(P)
        print(C)
        i += 1
    elif B[j] < A[i]:
        Q = B[j]
        C.append(Q)
        j += 1
print(C)
while i < len(A):
    C.append(A[i])
    i += 1

while j < len(B):
    C.append(B[j])
    j += 1

print(C)
'''
'''
class sorting():

    def list(self):
        self.L = []
        for i in range(5):
            X = int(input("enter a number: "))
            self.L.append(X)

    def sort(self):
        for i in range(len(self.L)-1):
            for j in range(i+1, 5):
                if self.L[i] > self.L[j]:
                    self.L[i], self.L[j] = self.L[j], self.L[i]

    def disp(self):
        print("THE SORTED LIST IS", self.L)


A = sorting()
B = sorting()
A.list()
B.list()
A.sort()
B.sort()
A.disp()
B.disp()
'''
'''
x = "abcabc"
Y = ""
for i in range(len(x)):
    data = x[i]
    if data not in Y:
        Y = Y+data
print(Y)
'''
'''
x = "abcabca"
y = input(" enter: ")
count = 0
for i in range(len(x)):
    if y == x[i]:
        count += 1
print(count)
'''


'''
x = "abcabca"
Y = ""
for i in range(len(x)):
    data = x[i]
    if data not in Y:
        Y = Y+data
print(Y)
for i in range(len(Y)):
    z = 0
    count = 0
    for j in range(len(x)):
        if Y[i] == x[j]:
            count += 1
    print(Y[i], count)
'''
# FINDING THE KTH SMALLEST ELEMENT:
'''
A = [1, 3, 9, 15, 20]
B = [2, 5, 10, 25, 30]
i = 0
j = 0
k = int(input("enter the kth element:"))
count = 0
while (i < len(A) and j < len(B) and count < k):
    if A[i] < B[j]:
        P = A[i]
        i += 1
        count += 1
    elif B[j] < A[i]:
        P = B[j]
        j += 1
        count += 1
print(P)
'''

# CREATE MAXIMUM NUMMBER OF COMBINATION
# wrong:
'''
A = [1, 2, 3]
for i in A:
    for j in A:
        for k in A:
            print(i, j, k)
'''
'''
print(list(itertools.permutations([4, 5, 6])))
'''
# outer i and mentioned i in range is different:
'''
i = 0
for i in range(1, 4):
    for j in range(1, 4):
        for k in range(1, 4):
            if i != j and j != k and k != i:
                print(i, j, k)
'''
'''
# Insert element in a list in a reverse order:
l = []


def insert(num):
    global l
    l.append(0)
# len command use :
# Slicing and loop difference: In slicing we have to use either negative or positive index and in loop case when can use both together otherwise it will shoe an error:
    for i in range(len(l)-2, -1, -1):
        l[i+1] = l[i]
    l[0] = num
    print(l)


for i in range(4):
    num = int(input("enter a number: "))
    insert(num)
print(l)
'''
'''
l = []


def insert(num):
    global l
    l.append(0)
    for i in range(len(l)-2, -1, -1):
        l[i+1] = l[i]
    l[0] = num


def delete():
    global l
    if not l:
        print("list is empty")
        return
    for i in range(0, len(l)-1):
        l[i] = l[i+1]
    l.pop(-1)


def disp():
    for i in l:
        print(i)


while (True):
    x = int(input("enter Your choice   :   "))
    if x == 1:
        num = int(input("enter a number: "))
        insert(num)
    elif x == 2:
        delete()
    elif x == 3:
        disp()
    elif x == 0:
        break
print(l)
'''
'''
i = 1
j = 1
k = 1
l = []
for i in range(2):
    for j in range(2):
        for k in range(3):
            if i+j+k != 2:
                l.append(i)
                l.append(j)
                l.append(k)
print(l)
'''
''''
z = "aabbbccde"
x = z.count("b")
y = z.count("a")
p = z.count("c")
print(x)
if y == p:
    print(y)
    print(p)
'''
