# practice questions:

# 1

'''
import itertools
from random import shuffle
'''

'''
dictionary = {}
dictionary[1] = 1
dictionary['1'] = 2
dictionary[1] += 1

sum = 0
for k in dictionary:
    sum += dictionary[k]
print(sum)
print(dictionary)
'''
# 2
# spaces are also counted in indexes:
'''
def f1():
    "this is a computer"
    return 1


print(f1.__doc__[11:14])
'''

# 3 enumerate print the value the value with the index:
'''
l1 = ["abc", "pqr", "wxyz"]
for i in enumerate(l1):
    print(i)
for count, i in enumerate(l1, 100):
    print(count, i)
'''

# 4
'''
temp = dict()
temp["key1"] = {"key": 44, "key2": 566}
temp["key2"] = [1, 2, 3, 4]
for (key, values) in temp.items():
    print(key, values)
print(temp)
'''

# 5
'''
color = ["red", "green", "white", "black", "pink", "yellow"]
shuffle(color)
print(color)
'''

# 6
'''
print(list(itertools.permutations([4, 5, 6])))
'''

# 7
'''
s = ["a", "b", "c", "d"]
str1 = "z".join(s)
print(str1)
'''

# 8
'''
d = dict()
for x in range(1, 6):
    d[x] = x*x
print(d)
'''

# 9

'''
l = ["abc", "wxyz", "lmno", "pqr"]
print(list(map(len, l)))
'''

# 10
'''

class A():
    pass


class B(A):
    pass


print(issubclass(B, A))
print(issubclass(A, B))
b = B()
a = A()
print(isinstance(a, B))
print(isinstance(b, B))
print(isinstance(a, A))
print(isinstance(b, A))
'''
'''
a = "this is a computer"
a = a.split()
print(a)
y = "-".join(a)
print(y)
'''
