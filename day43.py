'''
l = [1, 2, 3, 3]
mx = l[0]
mx1 = l[0]
for i in range(len(l)):
    if l[i] > mx:
        mx1 = mx
        mx = l[i]
    elif l[i] > mx1 and l[i] < mx:
        mx1 = l[i]
print(mx)
print(mx1)
'''


# How to create a dictionary inside dictionary:

'''
d = {}
for i in range(1, 3):
    key = input("enter key")
    if i == 1:
        d[key] = {}
        for j in range(2):
            key1 = input(" enter key1")
            d[key][key1] = int(input("enter"))
    else:
        d[key] = []
        for i in range(2):
            x = int(input("enter a number:"))
            d[key].append(x)
print(d)
'''
d = {1: {2: 'abc', 3: 'pqr'}}
print(d[1][2])
