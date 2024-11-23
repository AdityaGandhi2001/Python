# Infix to Postfix:
'''
def priority(x):
    if x == "^":
        return 3
    elif x == "*" or x == "/" or x == "%":
        return 2
    elif x == "+" or x == "-":
        return 1


s = "((A+B)*C/D^E)"
postfix = ""
stk = []
for i in s:
    if (ord(i) >= 65 and ord(i) <= 90) or (ord(i) >= 97 and ord(i) <= 122):
        postfix = postfix+i
    elif (i == "("):
        stk.append(i)
    elif (i == ")"):
        Top = len(stk)-1
        while (stk[Top] != "("):
            postfix = postfix+stk[Top]
            Top -= 1
            stk.pop()
        stk.pop(Top)
    else:
        Top = len(stk)-1
        while (stk[Top] != "(" and priority(i) <= priority(stk[Top])):
            postfix = postfix+stk[Top]
            Top -= 1
            stk.pop()
        stk.append(i)
print(postfix)
print(stk)
'''
'''
# Inifix to Prefix:


def priority(x):
    if x == "^":
        return 3
    elif x == "*" or x == "/" or x == "%":
        return 2
    elif x == "+" or x == "-":
        return 1


s = "((A+B)*C/D^E)"
postfix = ""
stk = []
z = ""
y = ""
# for i in range(len(s)-1, -1, -1):
#     if s[i] == "(":
#         y = y+")"
#     elif s[i] == ")":
#         y = y+"("
#     else:
#         y = y+s[i]
# print(y)

y = ''


def convert(l):
    global y
    for i in range(len(l)-1, -1, -1):
        if l[i] == "(":
            y = y+")"
        elif l[i] == ")":
            y = y+"("
        else:
            y = y+l[i]
    print(y)


convert(s)

for i in y:
    if (ord(i) >= 65 and ord(i) <= 90) or (ord(i) >= 97 and ord(i) <= 122):
        postfix = postfix+i
    elif (i == "("):
        stk.append(i)
    elif (i == ")"):
        Top = len(stk)-1
        while (stk[Top] != "("):
            postfix = postfix+stk[Top]
            Top -= 1
            stk.pop()
        stk.pop(Top)
    else:
        Top = len(stk)-1
        while (stk[Top] != "(" and priority(i) <= priority(stk[Top])):
            postfix = postfix+stk[Top]
            Top -= 1
            stk.pop()
        stk.append(i)
print(postfix)
print(stk)
for i in range(len(postfix)-1, -1, -1):
    z = z+postfix[i]
print(z)
'''
# Postfix to Infix:
'''
s = [40, 5, 2, "^", 12, 3, "/", "+", "-"]
stk = []
for i in range(len(s)):
    if s[i] == "^":
        stk[-2] = stk[-2]**stk[-1]
        stk.pop(-1)
    elif s[i] == "/":
        stk[-2] = stk[-2]//stk[-1]
        stk.pop(-1)
    elif s[i] == "+":
        stk[-2] = stk[-2]+stk[-1]
        stk.pop(-1)
    elif s[i] == "-":
        stk[-2] = stk[-2]-stk[-1]
        stk.pop(-1)
    else:
        stk.append(s[i])
print(stk[0])
'''
# Queue:
'''
l = []
f = -1
r = -1

max = int(input("enter a max:"))


def insert(num):
    global f
    global r
    if (len(l) == max):
        print("Stack is full")
        return
    if len(l) < 1:
        f = 0
        r = r+1
    else:
        r = r+1
    l.append(num)


def delete():
    global f
    global r
    if f == -1 and r == -1:
        print("list is empty")
        return
    print("the element deleted is: ", l[f])
    if f == r:
        f = -1
        r = -1
    else:
        f = f+1


def disp():
    for i in range(f, r+1):
        print(l[i], end=' ')
    print()


while (True):
    x = int(input("enter your choice:"))
    if x == 1:
        num = int(input("enter a number :"))
        insert(num)
    elif x == 2:
        delete()
    elif x == 3:
        disp()
    elif x == 4:
        break
print(l)
print(f)
print(r)
'''

'''
l = []

max = int(input("enter a max:"))


def insert(num):
    global l
    if (len(l) == max):
        print("Stack is full")
        return
    else:
        l.append(num)


def delete():
    global l
    if len(l) == 0:
        print("list is empty")
        return
    else:
        print("the deleted element is ", l[0])
        l.pop(0)


def disp():
    print(l)


while (True):
    x = int(input("enter your choice:"))
    if x == 1:
        num = int(input("enter a number :"))
        insert(num)
    elif x == 2:
        delete()
    elif x == 3:
        disp()
    elif x == 4:
        break
print(l)
'''

Q1 = [1, 2, 3, 4]
Q2 = []
N = Q1[0]


def insert(n):
    global Q2
    Q2.append(n)
    count = len(Q2)
    while (count > 1):
        Q2.append(Q2[0])
        Q2.pop(0)
        count -= 1


def delete():
    global Q1
    insert(Q1[0])
    Q1.pop(0)


for i in range(4):
    delete()

print(Q2)
