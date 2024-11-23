# tkinter:
'''
from tkinter import *
root = Tk()

x = Label(root, text="enter your name here")
x.pack()
root.mainloop()
'''

from tkinter import *
root = Tk()
L1 = Label(root, text="code")
E1 = Entry(root)
L1.grid(row=0)
E1.grid(row=0, column=2)
L2 = Label(root, text="name")
E2 = Entry(root)
L2.grid(row=1)
E2.grid(row=1, column=2)
L3 = Label(root, text="basic")
E3 = Entry(root)
L3.grid(row=2)
E3.grid(row=2, column=2)
B1 = Button(root, text="save")
B1.grid(row=3, column=1)
root.geometry("500x200")
root.mainloop()
