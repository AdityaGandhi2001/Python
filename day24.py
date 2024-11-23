'''
a = {1, 2, 3, 4, 5}
a.add(7)
print(a)
a.pop()
print(a)
b = sum(a)
print(b)
a.pop()
print(a)
c=list(a)
'''

'''
A = int(input("enter a number:"))
B = A
S = 0
while A > 0:
    S = S*10+1
    A = A//10
print(S)
print(B+S)
'''
import csv
import os
a = 101
i = 0
with open("/Users/vinayakgandhi/Desktop/Book3.csv", "r") as inp, open("/Users/vinayakgandhi/Desktop/Book5.csv", "w", newline="") as out:
    writer = csv.writer(out)
    for row in csv.reader(inp):
        if row[i] != str(a):
            writer.writerow(row)
os.remove("/Users/vinayakgandhi/Desktop/Book3.csv")
os.rename("/Users/vinayakgandhi/Desktop/Book5.csv",
          "/Users/vinayakgandhi/Desktop/book7.csv")
