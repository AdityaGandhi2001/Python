class queue():

    def input(self, alp, prn):
        self.alp = alp
        self.prn = prn

    def disp(self):
        print(self.alp, " ", self.prn)


q = []


def insertion(i):
    q.append(queue())
    alp = input("Enter the alphabet: ")
    prn = int(input("Enter the priority number: "))
    if i == 0:
        q[i].input(alp, prn)
    else:
        print(len(q))
        for j in range(len(q)-2, -1, -1):
            if q[i-1].prn <= prn:
                j = i
                break
            q[i].alp = q[i-1].alp
            q[i].prn = q[i-1].prn
            i -= 1
        q[j].input(alp, prn)


def remove():
    q.pop(0)


def disp():
    for i in range(len(q)):
        print(q[i].alp, q[i].prn)


i = 0
while (True):
    choice = int(input("Enter the choice:"))
    if choice == 1:
        insertion(i)
        i += 1
    elif choice == 2:
        remove()
    elif choice == 3:
        disp()
