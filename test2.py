'''
L1 = [1, 4, 5, 9, 10, 40, 50, 90]
L2 = ["I", "IV", "V", "IX", "X", 'XL', "L", "XC"]
k = 0
N = input("enter a roman number: ")
sum = 0
while k < len(N):
    x = N[k:k+2]
    if x in L2:
        i = L2.index(x)
        k += 2
    else:
        x = N[k]
        i = L2.index(x)
        k += 1
    sum = sum+(L1[i])
print(sum)
'''

'''
class binary():

    def inputbn(self):
        self.bn = int(input("enter a binary number: "))

    def b2(self):
        self.l = []
        while self.bn > 0:
            self.r = self.bn % 10
            self.l.append(self.r)
            self.bn = self.bn//10
        print(self.l)

    def conv(self):
        self.sum = 0
        for i in range(len(self.l)):
            self.sum = self.sum+(2**i)*self.l[i]
        print(self.sum)


a = binary()
a.inputbn()
a.b2()
a.conv()
'''

'''
A = "SADDER"
B = "DREADS"
j = len(A)
count = 0
for i in range(len(A)):
    if A[i] in B:
        count += 1
        y = B.index(A[i])
        print(i)
        B = B[0:y]+B[y+1:]
        print(B)
print(count)
if count == j:
    print("It is an anogram")
else:
    print("It is not an anogram")
'''

# ek function dusre function ki value self s use kr skta h
# 2 alg alg class k scenerio

'''
class fact():

    def input(self, x=None):
        self.x = x

    def factorial(self, f1):
        self.f = 1
        while f1.x > 0:
            self.f = self.f*f1.x
            f1.x -= 1
        print(self.f)


f1 = fact()
f2 = fact()
f1.input(5)
f2.factorial(f1)
'''

'''
A = "this is a computer "
A = A + " "
k = 0
while (1):
    i = A.find(" ", k)
    if i == -1:
        break
    for j in range(i-1, k-1, -1):
        print(A[j], end="")
    print(end=' ')
    k = i+1
'''

'''
class power():

    def input(self, x):
        self.x = x

    def result(self, p1, p2):
        self.p = p1.x**p2.x
        print(self.p)


p1 = power()
p2 = power()
p3 = power()
p1.input(2)
p2.input(5)
p3.result(p1, p2)
'''

'''
N = int(input("Enter a number: "))
S = ""
while N > 0:
    r = N % 16
    if r < 10:
        S = S+str(r)
    else:
        S = S+str(chr(r+55))
    N = N//16
print(S)
for i in range(len(S)-1, -1, -1):
    print(S[i], end="")
'''
'''
A = "abcdefghijklm"
k = 0
while k <= len(A):
    print(A[k:k+4])
    k += 4
'''
word1 = input("Enter:")
word2 = input("Enter: ")


def function(word1, word2):
    word3 = ""
    if len(word1) == len(word2):
        for i in range(len(word1)):
            word3 = word3+word1[i]+word2[i]
        print(word3)
    elif len(word1) < len(word2):
        for i in range(len(word1)):
            word3 = word3+word1[i]+word2[i]
        word3 = word3+word2[len(word1):]
        print(word3)
    else:
        for i in range(len(word2)):
            word3 = word3+word1[i]+word2[i]
        word3 = word3+word1[len(word2):]
        print(word3)


function(word1, word2)
