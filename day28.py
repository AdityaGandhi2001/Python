
'''
import pandas as pd
df = pd.read_csv("/Users/vinayakgandhi/Desktop/Book1.csv")
print(df)
'''

'''
import csv
with open("/Users/vinayakgandhi/Desktop/Book1.csv", newline="") as file:
    reader = csv.reader(file)
    for i in reader:
        print(i)
'''
D = {"{": "}", "[": "]", "(": ")"}

str = input("enter a string:")
print(str)
l = []
for i in (str):
    if i in D:
        l.append(i)
    elif i == D[l[-1]]:
        l.pop()
if (not l):
    print("t")
else:
    print("f")
