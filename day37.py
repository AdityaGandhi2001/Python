import sqlite3
from tkinter import *
root = Tk()
conn = sqlite3.connect("/Users/vinayakgandhi/data.db")


L1 = Label(root, text="CODE")
E1 = Entry(root)
L1.grid(row=0)
E1.grid(row=0, column=2)
L2 = Label(root, text="NAME")
E2 = Entry(root)
L2.grid(row=1)
E2.grid(row=1, column=2)
L3 = Label(root, text="BASIC")
E3 = Entry(root)
L3.grid(row=2)
E3.grid(row=2, column=2)


def save():
    A = []
    A.append(E1.get())
    A.append(E2.get())
    A.append(E3.get())
    conn.execute("insert into emp values(?,?,?)", A)
    conn.commit()


def retrieve():
    A = []
    A.append(E1.get())
    rs = conn.execute("select *from emp where code=?", A)
    i = rs.fetchall()
    for k in i:
        E2.insert(0, (k[1]))
        E3.insert(0, (k[2]))

    conn.commit()


def update():
    A = []
    A.append(E2.get())
    A.append(E3.get())
    A.append(E1.get())
    conn.execute("update emp set name=?, basic=? where code=? ", A)
    conn.commit()


# 200 | Rahul | 300000


def delete():
    A = []
    A.append(E1.get())

    conn.execute("Delete from emp where code=? ", A)
    conn.commit()


B1 = Button(root, text="Save", command=save)
B1.grid(row=3, column=1)
B2 = Button(root, text="Retrieve", command=retrieve)
B2.grid(row=3, column=2)
B3 = Button(root, text="Delete", command=delete)
B3.grid(row=3, column=3)
B3 = Button(root, text="Update", command=update)
B3.grid(row=3, column=4)

root.mainloop()
