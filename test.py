'''
L = ['ABC', 10, 20, 5, 'PQR']
sum = 0
for i in range(len(L)):
    if type(L[i]) == int:
        sum = sum+L[i]
print(sum)
'''

'''
L = ['ABC', 10, 20, 5, 'PQR']
k = 0
for i in range(len(L)):
    if type(L[k]) == int:
        L.append(L[k])
        L.pop(k)
    else:
        k += 1
print(L)
'''

# Find the largest function:

'''
L = ['abc', 'defg', 'hijk', 'lmnop']
largest =''
for i in range(len(L)):
    if len(L[i]) > len(largest):
        largest = L[i]
print(largest)
'''

# common number in both the list:

'''
L1 = [9, 20, 30, 40]
L2 = [10, 20, 30, 40, 50, 60, 70]
L3 = []
for i in L1:
    if L2.count(i) > 0:
        L3.append(i)
print(L3)
'''

# roman number question:

'''
A = int(input("enter a number: "))
L1 = [1, 4, 5, 9, 10, 40, 50, 90]
L2 = ["I", "IV", "V", "IX", "X", 'XL', "L", "XC"]
B = ""
i = len(L1)-1
while A > 0:
    if L1[i] <= A:
        A = A-L1[i]
        B = B+L2[i]
    else:
        i -= 1
print(B)
'''
# add prime number betweeen 1 to 100 in a list:
'''
L = []
for i in range(1, 100):
    count = 0
    for j in range(1, i+1):
        if i % j == 0:
            count += 1
    if count == 2:
        L.append(i)
print(L)
'''

'''
E = []
for i in range(2):
    E.append([])
    for j in range(2):
        x = int(input("enter a number:"))
        E[i].append(x)
print(E)
'''
'''
import numpy as np
import pandas as pd
data = np.array(["a", "b", "c", "d"])
s = pd.Series(data, index=[100, 101, 102, 103])
print(s)
'''
'''
import numpy as np
import pandas as pd
data = np.array(["a", "b", "c", "d"])
s = pd.Series(data, index=[100, 101, 102, 103])
print(s)
'''

# data_dict = {
#     'key1': 'value1',
#     'key2': 'value2'
# }


# new_data = {
#     'key2': 'new_value2',
#     'key3': 'value3',
#     "key1": 'value4'
# }

# data_dict.update(new_data)
# # print(data_dict)

# l = []
# data_dict = {
#     'key1': 'value1',
#     'key2': 'value2'
# }


# new_data = {
#     'key2': 'new_value2',
#     'key3': 'value3',
#     "key1": 'value4'
# }
# start = 0
# for i in range(5):
#     l.append(data_dict)
#     start += 1
# print(l)
# print(start)

# l = ['abc', 10, 20, "efg"]
# sum = 0
# for i in l:
#     if type(i) == int:
#         sum = sum + i
# print(sum)
