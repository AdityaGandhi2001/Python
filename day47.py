'''
def input1(l):
    for i in range(3):
        x = int(input("enter a number: "))
        l.append(x)


def sort1(l):
    l.sort()


a = []
b = []
input1(a)
input1(b)
sort1(a)
sort1(b)
print(a+b)
'''
'''
class sort:
    def input(self):
        self.l = []
        for i in range(3):
            x = int(input("enter a number: "))
            self.l.append(x)

    def sort1(self):
        self.l.sort()
        print(self.l)

    def merge(self, a, b):
        self.l = []
        i = 0
        j = 0
        while (i < len(a.l) and j < len(b.l)):
            if a.l[i] < b.l[j]:
                p = a.l[i]
                self.l.append(a.l[i])
                i += 1
            elif b.l[j] < a.l[i]:
                p = a.l[i]
                self.l.append(b.l[j])
                j += 1

        while (i < len(a.l)):
            self.l.append(a.l[i])
            i += 1
        while (j < len(b.l)):
            self.l.append(b.l[j])
            j += 1
        print(self.l)


a = sort()
a.input()
b = sort()
b.input()
a.sort1()
b.sort1()
c = sort()
c.merge(a, b)
'''

'''
class sort:
    def inputa(self):
        self.a = []
        for i in range(3):
            x = int(input("enter a number: "))
            self.a.append(x)

    def inputb(self):
        self.b = []
        for i in range(3):
            x = int(input("enter a number: "))
            self.b.append(x)

    def sorta(self):
        self.a.sort()
        print(self.a)

    def sortb(self):
        self.b.sort()
        print(self.b)

    def merge(self):
        self.l = []
        i = 0
        j = 0
        while (i < len(self.a) and j < len(self.b)):
            if self.a[i] < self.b[j]:
                p = self.a[i]
                self.l.append(self.a[i])
                i += 1
            elif self.b[j] < self.a[i]:
                p = self.b[j]
                self.l.append(self.b[j])
                j += 1

        while (i < len(self.a)):
            self.l.append(self.a[i])
            i += 1
        while (j < len(self.b)):
            self.l.append(self.b[j])
            j += 1
        print(self.l)


A = sort()
A.inputa()
A.inputb()
A.sorta()
A.sortb()
A.merge()
'''

'''
class sort:
    def input(self, l):
        for i in range(3):
            x = int(input("enter a number: "))
            l.append(x)

    def sort(self, l):
        l.sort()


    def merge(self, a, b):
        self.l = []
        i = 0
        j = 0
        while (i < len(a) and j < len(b)):
            if a[i] < b[j]:
                p = a[i]
                self.l.append(a[i])
                i += 1
            elif b[j] < a[i]:
                p = b[j]
                self.l.append(b[j])
                j += 1

        while (i < len(a)):
            self.l.append(a[i])
            i += 1
        while (j < len(b)):
            self.l.append(b[j])
            j += 1
        print(self.l)


A = sort()
a = []
b = []
A.input(a)
A.input(b)
A.sort(a)
A.sort(b)
A.merge(a, b)
print(a)
print(b)
'''
