'''
x = "celebai"
a = "1"
c = x+a
c = c*2
print(c)
'''

'''
def sf(a):
    return a % 3 != 0 and a % 5 != 0


M = filter(sf, range(1, 31))
print(list(M))
'''

'''
l = [1, 2, 3, 4, 5]


def f1(x):
    return x < 0


M1 = filter(f1, l)
print(list(M1))
'''
'''
print(list(map((lambda x: x**2), range(10))))
'''

'''
print(list(map((lambda x: x**2), filter((lambda x: x % 2 == 0), range(10)))))
'''

'''
l1 = [1, 2, 2, 4]
l2 = [1, 2, 3, 8]
count = 0
for i in range(4):
    if l1[i] in l2:
        count += 1
        y = l2.index(l1[i])
        l2.pop(y)
print(count)

if count >= 1:
    print("true")
else:
    print("false")
'''

'''
l = [1, 2, 3, 4, 5, 6]
k = 0
for i in range(len(l)):
    if l[k] % 2 == 0:
        l.pop(k)
    else:
        k += 1
print(l)
'''

'''
d = {1: "a", 2: "b", 3: "c"}
for i in range(1):
    key = int(input("enter a number: "))
    d[key] = input("enter a character")
print(d)
'''
'''
d = {"A": 1, "B": 2, "C": 3, "D": 4}
max1 = (d["A"])
min2 = (d["A"])
k1 = 'A'
k2 = 'B'
for k, v in d.items():
    if v > max1:
        max1 = v
        k1 = k
    elif v <= min2:
        min2 = v
        k2 = k
print(k1, '-', max1)
print(k2, '-', min2)
'''
'''
d = {"M": 98, "C": 92, "P": 95}
d1 = {}
for k, v in d.items():
    if d1:
        for k1, v1 in d1.items():
            if v1 > v:
                del (d[k1])
                d.update(d1)
                d1.clear()
                d1[k] = v
    else:
        d1[k] = v
print(d)
'''
'''
l = [["A", 98], ["B", 92], ["C", 95]]

for i in range(len(l)-1):
    if l[i][1] > l[i+1][1]:
        l[i], l[i+1] = l[i+1], l[i]
print(l)
'''
'''
word = " python programming"
a = word.upper()
b = word.lower()
print(a)
print(b)
n = len(word)
x = ""
for i in range(len(word)):
    if i % 2 == 0:
        x = x+a[i]
    else:
        x = x+b[i]
print(x)
'''

'''
i = 0
if i % 2 == 0:
    print("t")
else:
    print("f")
'''
'''
UB = 10
LB = -10
BA = 400
W = 2


def address(A):
    ADD = BA+(A-LB)*W
    print(ADD)


address(-3)
'''


LB = 0
BA = 100
W = 4
c = 20
r = 10


def rowaddress(A, B):
    ADD = BA+(c*(A-LB)+(B-LB))*W
    print(ADD)


rowaddress(8, 15)


def coladdress(A, B):
    ADD = BA+((A-LB)+(B-LB)*r)*W
    print(ADD)


coladdress(8, 15)


s = "This is a computer"
l = (s.split())
print(l)
for i in range(len(l)):
    print(len(l[i]), l[i])
