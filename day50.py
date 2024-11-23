'''
s = "This is computer"
l = s.split()
print(l)
x = ""
for i in l:
    x = x+i[-1::-1]
    x = x+" "
    print(x)
'''
'''
s = "nitin"
z = " "
for i in s:
    z = s[-1::-1]
print(z)
count = 0
j = 0
for i in range(len(s)):
    if s[i] == z[j]:
        count += 1
        j += 1
print(count)
if len(z) == count:
    print("It is a pallindrome")
'''
'''
A = "SILENS"
B = "LISSEN"
D = ""
C = 0
for i in range(len(A)):
    if A[i] in B:
        z = B.index(A[i])
        print(z)
        D = D+B[0:z]+B[z+1::1]
        print(D)
        B = D
        D = ""
        C += 1
if len(A) == C:
    print("It is a anagram")
else:
    print("It is not a anagram")
'''
'''
A = int(input("Enter a number:"))
Z = A*A
Z = str(Z)
A = str(A)
print(Z)
t = 0
j = -1
for i in range(len(A)-1, -1, -1):
    if A[i] == Z[j]:
        t += 1
        j += 1
if len(A) == t:
    print("It is an automorphic number")
'''

# Automorphic Number:

'''
def automorphic_number(A):
    B = A
    D = 1
    while B > 0:
        D = D*10
        B = B//10

    return D


for i in range(1, 500):
    if i == (i*i) % automorphic_number(i):
        print(i)
'''


def prime_number(A):
    for i in range(2, (A//2)+1):
        if A % i == 0:
            return False

    return True


for i in range(2, 100):
    if prime_number(i):
        print(i, end='\t')
