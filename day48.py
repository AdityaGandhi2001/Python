
l = ["abc", "pqr", "lmno", "xyz"]
x = []
for i in l:
    X = len(i)
    x.append(i[len(i)-1::-1])
print(x)


'''
s1 = "aditya"
s2 = "alex"
s3 = ""

x = len(s1)//2

for i in range(len(s1)):
    if i == x:
        s3 = s3+s2
        s3 = s3+s1[i]
    else:
        s3 = s3+s1[i]
print(s3)
'''

'''
class vehicle():

    def __init__(self, c, m):
        self.color = c
        self.m = m


class car(vehicle):
    def car_detail(self, d):
        self.noofdoors = d

    def disp(self):
        print("The car details are: ", self.color, self.m, self.noofdoors)


class bike(vehicle):
    def motorcycle_detail(self, e):
        self.enginecapcity = e

    def disp(self):
        print("The bike details are: ", self.color, self.m, self.enginecapcity)


c1 = car("Red", 2001)
c1.car_detail(4)
b1 = bike("Blue", 2002)
b1.motorcycle_detail("1000 HP")
c1.disp()
b1.disp()
'''
'''
l1 = [1, 2, 3, 4, 5]
l2 = [4, 5, 6, 7, 8]
sum1 = 0


def sum(l):
    Total = 0
    for i in range(len(l)):
        Total = Total+l[i]
    return Total


sum1 = sum(l1)+sum(l2)
print(sum1)
'''


class queue():

    def q(self, num, prn):
        self.num = num
        self.prn = prn

    def disp(self):
        print(self.num, self.prn)


l = []
n = 5
for i in range(n):
    l.append(queue())
    num = (input("Enter name: "))
    prn = int(input("Enter priority number"))

    if (i == 0):
        l[i].q(num, prn)
    else:
        j = i-1
        while (j >= 0):
            if l[j].prn > prn:
                l[j+1].num = l[j].num
                l[j+1].prn = l[j].prn
            else:
                break
            j -= 1

        l[j+1].q(num, prn)
for i in range(n):
    l[i].disp()


# l = [1, 2, 3, 4, 5]
# l[1] = l[0]
# l[1] = 8
# print(l)
