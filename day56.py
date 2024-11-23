'''
q = []
f = 0
r = len(q)-1


def insertfromfront(s, x):
    global f
    global r
    s.insert(f, x)
    r += 1


def insertfromrear(s, x):
    global r
    r += 1
    s.insert(r, x)


def deletefromfront(s):
    global f
    global r
    s.pop(f)
    r -= 1


def deletefromrear(s):
    global r
    s.pop(r)
    r -= 1


def disp():
    print(q)


while (True):
    choice = int(input("Enter the Choice: "))
    if choice == 1 and len(q) < 4:
        x = int(input("Enter the number: "))
        insertfromfront(q, x)
        print(f, r)
    elif choice == 2 and len(q) < 4:
        x = int(input("Enter the number: "))
        insertfromrear(q, x)
        print(f, r)
    elif choice == 3 and len(q) > 0:
        deletefromfront(q)
        print(f, r)
    elif choice == 4 and len(q) > 0:
        deletefromrear(q)
        print(f, r)
    elif choice == 5:
        disp()
        print(f, r)
'''

a = [6, 0, 2, 0, 1, 3, 4, 6, 1, 3, 2]
maxa = max(a)
print(maxa)
l = []
for i in range(maxa+1):
    l.append(0)
print(l)
for i in range(7):
    c = a.count(i)
    l[i] = c
print(l)
s = ""
for i in range(7):
    count = l[i]
    s = s+str(i)*count
print(s)
