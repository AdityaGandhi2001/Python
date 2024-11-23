'''
class fac():

    def factorial(self, A):
        f = 1
        a = A
        while A > 0:
            f = f*A
            A = A-1
        print(a, '-', f)

    def result(self):
        self.L = [5, 2, 3, 4]
# print('hello')
        for i in self.L:
            self.factorial(i)
            # print("i", i)


A = fac()
A.result()
'''

l = "This is a computer aaaaaaaa"

l = l.split(" ")
print(l)


# MAXX = len(l[0])
# for i in range(len(l)):
#     x = len(l[i])
#     if x > (MAXX):
#         MAXX = x
# print(MAXX)

MAXX = max(list(map(len, l)))

for i in l:
    if len(i) == MAXX:
        print(i)
