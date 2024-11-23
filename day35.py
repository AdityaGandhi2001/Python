from tkinter import *
root = Tk()
L1 = Label(root, text="Number 1")
E1 = Entry(root)
L1.grid(row=0)
E1.grid(row=0, column=2)
L2 = Label(root, text="Number 2")
E2 = Entry(root)
L2.grid(row=1)
E2.grid(row=1, column=2)
L3 = Label(root, text="Result")
E3 = Entry(root)
L3.grid(row=2)
E3.grid(row=2, column=2)


def add():
    a = int(E1.get())
    b = int(E2.get())
    c = a+b
    E3.delete(0, END)
    E3.insert(0, c)


def mul():
    x = int(E1.get())
    y = int(E2.get())
    z = x*y
    E3.delete(0, END)
    E3.insert(0, z)


def div():
    p = int(E1.get())
    q = int(E2.get())
    r = p/q
    E3.delete(0, END)
    E3.insert(0, r)


B1 = Button(root, text="Add", command=add)
B1.grid(row=3, column=1)
B2 = Button(root, text="Mul", command=mul)
B2.grid(row=4, column=1)
B2 = Button(root, text="Div", command=div)
B2.grid(row=5, column=1)
root.geometry("500x200")
root.mainloop()
