q1 = []
q2 = []
fr = 0
A = 0


def insert(x, s):
    s.append(x)


def delete(s):
    global fr
    global A
    A = q1[fr]
    s.pop(fr)
    q2.insert(0, A)


def disp():
    print(q1)
    print(q2)


while (True):
    Choice = int(input("enter your choice:"))
    if Choice == 1:
        X = int(input("Enter a number: "))
        insert(X, q1)
    elif Choice == 2:
        delete(q1)
        # insert(A, q2)
    elif Choice == 3:
        disp()
    elif Choice == 4:
        break
