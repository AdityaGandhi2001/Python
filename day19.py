'''
L = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28]
print(len(L))
A = int(input("enter the number: "))
i = 0
j = len(L)-1
if A in L:
    while (j >= i):
        k = (i+j)//2
        if L[k] == A:
            print("FOUND", A, k)
            break
        elif A > L[k]:
            i = k+1
        else:
            j = k-1
else:
    print("not found")
'''

A = int(input("enter a number: "))
z = str(A)
L = len(z)

while L > 1:
    sum = 0
    while A > 0:
        x = A % 10
        sum = sum + x*x
        A = A//10
    print(sum)
    A = sum
    B = sum
    if B == 1:
        print("happy")
        break
    else:
        print("Not found")

'''
A = int(input("enter a number: "))
sum = 0
while A > 0:
    x = A % 10
    sum = sum + x*x
    A = A//10
print(sum)
'''
