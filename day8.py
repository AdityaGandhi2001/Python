

# import copy
# l = [5, 4, 9, 2, 1, [3, 5, 7], 9]
# a = l
# b = l.copy()
# c = copy.copy(l)
# d = copy.deepcopy(l)
# l[1] = "PQR"
# l[5][1] = "XYZ"
# print(l)
# print(a)
# print(b)
# print(c)
# print(d)

'''
l = [5, 4, 9, 2]
a = l.index(9)
print(a)
l.sort()
print(l)
l.reverse()
print(l)
'''

# 1D list:

'''
l = []
n = 3
for i in range(n):
    x = int(input("enter the number"))
    l.append(x)
print(l)
'''


# 2D list:
# 3 AND #4 GIVE SAME RESULTS IN THE BELOW PROGRAM:
#
# 1

l = []
n = 3
for i in range(n):
    l.append([])
    for j in range(n):
        x = int(input("enter the number"))
        l[i].append(x)
print(l)

# 2
for i in l:
    print(i)
print(l)
# 3
for i in l:
    for j in i:
        print(j, end=" ")
    print()
# 4
for i in range(n):
    for j in range(n):
        print(l[i][j], end=" ")
    print()

# 3 AND #4 GIVE SAME RESULTS IN THE ABOVE PROGRAM
