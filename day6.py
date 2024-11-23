# Printing the first 2 letters of the element of the list :

'''
l = ['ABC', 'PQR', 'LMNO', 'XYZ']
for i in range(len(l)):
    print(l[i][0:2])
'''

# Important question:***********:

'''

l = ['ABC', 'PQR', 'LMNO', 'XYZ']
for i in range(0, len(l)//2):
    print(l[i][0:2]+l[-1-i][0:2])
    print(l[i][2:]+l[-1-i][2:])

'''

'''

L = [10, 15, 5, 2, 18]
max = L[0]
min = L[0]
for i in range(1, len(L)):
    if L[i] > max:
        max = L[i]
    elif L[i] < min:
        min = L[i]
print("maximum number is ", max)
print("minimum number is ", min)

'''

# Print the factorial of the number in the list:

'''
L = [10, 5, 2, 6]
for i in range(len(L)):
    f = 1
    A = L[i]
    while (A > 1):
        f = f*A
        A -= 1
    print(L[i], '-', f)
'''
# Remove even number from list and place them in the beginning of the list:
# pop removes the last element in the list:

'''
l = [10, 5, 9, 7, 2]
k = 0
for i in range(5):
    if l[k] % 2 != 0:
        l.append(l[k])
        l.pop(k)
    else:
        k += 1
print(l)
'''
