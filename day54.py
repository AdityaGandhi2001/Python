'''
a = 105
b = 106
e = str(a)
f = str(b)
c = a+b
d = str(c)
x = "0"
z1 = ""
z2 = ""
z3 = ""
if x in d:
    y = d.index(x)
    z1 = d[0:y]+d[y+1:]
    print(z1)
else:
    z1 = d
    print(z1)

y = e.index(x)
z2 = e[0:y]+e[y+1:]
print(z2)

y = f.index(x)
z3 = f[0:y]+f[y+1:]
print(z3)

z4 = (int(z2)+int(z3))
print(z4)
if int(z1) == z4:
    print("yes")
else:
    print("not found")
'''
# Use return instead of print:
'''
a = "102"
b = "103"
z = "0"
c = int(a)+int(b)
c = str(c)


def function(x):
    if z in x:
        y = x.index(z)
        d = x[0:y]+x[y:]
    else:
        d = x
    return d


if int(function(a))+int(function(b)) == int(function(c)):
    print("True")
else:
    print("false")
'''
'''
a = 102
b = 103
c = a+b


def function(x):
    z = 0
    while x > 0:
        r = x % 10
        if r != 0:
            z = (z*10)+r
        x = x//10
    return z


a = (function(a))
print(function(a))
b = (function(b))
print(function(b))
c = (function(c))
print(function(c))
if function(a)+function(b) == function(c):
    print("true")
else:
    print("False")
'''


q = []
f = 0
r = -1


def insert1(s, x):
    global q
    global r
    s.insert(r, x)


def remove(s):
    global f
    s[f] = 0
    f += 1


def disp():
    print(q)


while (True):
    choice = int(input("enter a choice : "))
    if choice == 1:
        x = int(input("enter a number:"))
        insert1(q, x)
    elif choice == 2:
        remove(q)
    elif choice == 3:
        disp()
    elif choice == 4:
        break
