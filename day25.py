# use of filter and reduce in place of map while using lambda function:

'''
f=lambda x: x if x%2==0 else 0
L=[5,9,2,4,3]
M=list(filter(f,L))
print(M)
'''

'''
import functools
f=lambda x.y: x*y
L = [1, 2, 3, 4, 5]
M = functools.reduce(f, L)
print(M)
'''
# Assignment:

'''
def odd(x): return bool(x % 2)


numbers = [n for n in range(10)]
print(numbers)
n = list()
for i in numbers:
    if odd(i):
        continue
    else:
        break
'''

'''
def f(x): return bool(x % 2)


print(f(20), f(21))
'''

'''
import  functools
L = [1, 2, 3, 4]
print(functools.reduce(lambda x, y: x*y, L))
'''

'''
L=[1,-2,-3,4,5]
def f1(x):
    return x<2
m1=list(filter(f1,L))
print(m1)
'''

'''
l = [-2, 4]
m = list(map(lambda x: x*2, l))
print(m)
'''
'''
l = [1, -2, -3, 4, 5]


def f(x):
    if x < -1:
        return x
    else:
        return 0


m = list(map(f, l))
print(m)
'''

'''
L = [1, 2, 3, 4, 5]
m = list(map(lambda x: 2**x, L))
print(m)
'''

'''
import functools
L = [1, 2, 3, 4, 5]
m = functools.reduce(lambda x, y: x if x < y else y, L)
print(m)
'''
'''
l = [n for n in range(5)]
def f(x): return bool(x % 2)


print(f(3), f(1))
for i in range(len(l)):
    if f(l[i]):
        del l[i]
        print(i)
'''

'''
import functools
M=functools.reduce(lambda x: x<3 in range(4,10))
print(list(M))
'''
