L = [6, 7, 81, 2, 1]


def insert(element):
    L.append(element)


insert(3)
insert(4)


def remover(x):
    y = L.index(x)
    if x in L:
        L.pop(y)


remover(6)


def sum():
    sum = 0
    for i in range(len(L)):
        sum = sum+L[i]
    print(sum)


sum()
print(L)

'''
a = 2


def add():
    a = 5
    a = a+5
    print(a)


add()
print(a)
'''
