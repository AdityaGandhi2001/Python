# Greedy Algorithm based question:
'''
class activity():

    def input(self):
        self.a = input("enter the activity: ")
        self.b = int(input("enter the start time: "))
        self.c = int(input("enter the finish time:"))

    def dispa(self):
        print(self.a, end="\t")

    def dispb(self):
        print(self.b, end="\t")

    def dispc(self):
        print(self.c, end="\t")


A = []
for i in range(10):
    A.append(activity())
    A[i].input()
for i in range(10):
    A[i].dispa()
print()
for i in range(10):
    A[i].dispb()
print()
for i in range(10):
    A[i].dispc()


for i in range(len(A)-1):
    for j in range(i+1, 10):
        if A[i].c > A[j].c:
            A[i], A[j] = A[j], A[i]
print()
for i in range(10):
    A[i].dispa()
print()
for i in range(10):
    A[i].dispb()
print()
for i in range(10):
    A[i].dispc()
print()

str = "A1"
K = 0
for i in range(len(A)-1):
    if A[K].c <= A[i+1].b:
        str = str+" "+A[i+1].a
        K += 1
print(str)
'''

# Fractional Knapsack  problem:


class Totalprofit():

    def input(self):
        self.profit = int(input("Enter the Profit: "))
        self.weight = int(input("enter the weight: "))
        self.ratio = (self.profit/self.weight)

    def disp(self):
        print("PROFIT", "WEIGHT", "PROFIT PER UNIT")
        print(self.profit, self.weight, self.ratio)


l = []
for i in range(1):
    l.append(Totalprofit())
    l[i].input()

for i in range(1):
    l[i].disp()
# FOR DESC SORTING:JUST SIGN CHANGES
for i in range(len(l)-1):
    for j in range(i+1, 1):
        if l[i].ratio < l[j].ratio:
            l[i], l[j] = l[j], l[i]
print()
print("SORTED")
print()

for i in range(1):
    l[i].disp()

w = int(input("enter the weight of bag:"))
p = 0
for i in range(len(l)):
    if w != 0:
        if w >= l[i].weight:
            p = p+l[i].profit
            w = w-l[i].weight
        else:
            p = p+(w/l[i].weight)*l[i].profit
            w = w-w
    else:
        break
print(p)
