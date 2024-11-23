from tkinter import *
root = Tk()
L1 = Label(root, text="Number 1")
E1 = Entry(root)
L1.grid(row=0)
E1.grid(row=0, column=4)
L2 = Label(root, text="Result")
E2 = Entry(root)
L2.grid(row=1)
E2.grid(row=1, column=4)


def prime():
    a = int(E1.get())
    count = 0
    for i in range(1, a+1):
        if a % i == 0:
            count += 1
    if count == 2:
        E2.delete(0, END)
        E2.insert(0, "It is a prime")
    else:
        E2.delete(0, END)
        E2.insert(0, "not a prime")


def even():
    x = int(E1.get())
    if x % 2 == 0:
        E2.delete(0, END)
        E2.insert(0, "even")
    else:
        E2.delete(0, END)
        E2.insert(0, "odd")


def fact():
    p = int(E1.get())
    f = 1
    while p > 0:
        f = f*p
        p -= 1
    E2.delete(0, END)
    E2.insert(0, f)


B1 = Button(root, text="Prime", command=prime)
B1.grid(row=2, column=1)
B2 = Button(root, text="Even", command=even)
B2.grid(row=2, column=2)
B3 = Button(root, text="fact", command=fact)
B3.grid(row=2, column=3)
root.mainloop()
