
class A():
    def input1(self, A):
        self.a = A


class B():
    def input(self, B):
        self.b = B


class C(A, B):

    def input(self, A, B):
        super().input1(A)
        super().input(B)

        print(self.a, "     ", self.b)

    def find(self):
        K = 0

        while K < len(self.a):
            print(self.a, "     ", self.b)
            if self.b in self.a:
                i = self.a.find(self.b, K)
                print(i)
                K = i+1
                if (i == -1):
                    break


R = C()
R.input("understande", "de")
R.find()

'''
L1 = [1, 2, 3, 4, 5,]
L2 = []
def f(x): return x if x % 2 == 0 else 0


L1 = list(map(f, L1))
print(L1)
'''
'''
l = 1
sp = 3
for i in range(4):
    for j in range(sp):
        print(" ", end="")
    for j in range(i+1):
        print(l, end=" ")
    l += 1
    print()
    sp -= 1
'''
