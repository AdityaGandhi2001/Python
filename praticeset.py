'''
import random
L = [1, 2, 3, 4]
print(random.choice(L))
'''
'''
import random
for i in range(5):
    print(random.random())
'''


# l = [1, 2, 3, 4, 5,]
# Min = l[0]
# secondmin = l[3]
# for i in range(1, len(l)):
#     if Min > l[i]:
#         secondmin = Min
#         Min = l[i]
#     elif secondmin > l[i]:
#         secondmin = l[i]
# print(Min)
# print(secondmin)

'''
class A():
    def input(self, A):
        self.A = A


class B():
    def input(self, B):
        self.B = B


class C(A, B):

    def input(self, A, B):
        # B.input(self, B)
        # A.input(self, A)

        self.A = A
        self.B = B
        print(A, "     ", B)
# DOUBTTTTTTTTTTT:

    def find(self):
        for i in range(len(self.A)):
            if self.B in self.A:
                k = self.A.index(self.B)
                print(k)
            i = k+20
            print(i)


r1 = C()
r1.input("understande", "de")
r1.find()
'''
l = [1, 2, 3, 3, 3, 4, 4]
count_list = set(l)
d = {}
for i in count_list:
    mode_count = l.count(i)
    index = l.index(i)
    print(mode_count, l[index])
    d[l[index]] = mode_count
print(d)
mode = 0
final = []
for k, v in d.items():
    if v > mode:
        mode = v
        final = [k]
    elif v == mode:
        final.append(v)
print(mode)
print(final)
