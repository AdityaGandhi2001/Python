'''
for i in range(2, 9, 2):
    for j in range(1, i, 2):
        print(j, end="\t")
    print()
'''
# Printing a star pattern:
'''
for i in range(2, 6):
    for j in range(1, i):
        print("-*", end="\t")
    print()
'''

# Question:
'''
L = [10, 2, 9, 5, 7, 13]
Total = 0
for k in range(len(L)):
    count = 0
    for i in range(1, L[k]+1):
        if L[k] % i == 0:
            count += 1
    if count == 2:
        print(L[k], end="")
        Total += 1
print()
print("THE TOTAL IS", Total)
'''

'''
D = {'Name': ["A", "B", "C "], 'Age': ["10", "20", "30"]}
for k, v in D.items():
    print(k, "", v)
'''

# doubt:

L1 = [1, 2, 3, 4, 5, 6]
L2 = []


def even(A):
    if A % 2 == 0:
        L2.append(A)


for i in range(len(L1)):
    even(L1[i])
print(L2)


class ADD():

    def __init__(self, a=None, b=None):
        self.a = a
        self.b = b

    def sum(self, a1, a2):
        self.SA = a1.a + a2.a
        self.SB = a1.b+a2.b

    def disp(self):
        print(" The sum is:  ", self.SA, self.SB)


A1 = ADD(10, 20)
A2 = ADD(5, 8)
A3 = ADD()
A3.sum(A1, A2)
A3.disp()
