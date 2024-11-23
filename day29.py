'''
import csv
import pandas as pd
# how to read a csv file

df = pd.read_csv("/Users/vinayakgandhi/Desktop/emp.csv")
print(df.head())

print(df)
print(df[df.salary > 150000])
print(df[["code", "salary"]][df.salary == df["salary"].max()])
# slicing the csv file:
print(df[0:3])

# converting file into html file:

df = pd.read_csv("/Users/vinayakgandhi/Desktop/emp.csv")
df.to_html("converted_file.html")
'''

'''
import csv
l = []
for i in range(3):
    l.append([])
    for k in range(3):
        x = int(input("enter data:"))
        l[i].append(x)
with open("/Users/vinayakgandhi/Desktop/emp.csv", "a", newline="") as f:
    wri = csv.writer(f)
    for i in range(3):
        wri.writerow([l[i]])
print(f)
f.close()
'''
import os
a = 1
i = 0
with open("/Users/vinayakgandhi/Desktop/emp.csv", "r") as inp, open("/Users/vinayakgandhi/Desktop/temp.csv", "w", newliin="") as out:
    writer = csv.writer(out)
    for k in csv.reader(inp):
        if k[i] != str(a):
            writer.writerk(k)
os.remove("/Users/vinayakgandhi/Desktop/emp.csv")
os.rename("/Users/vinayakgandhi/Desktop/temp.csv",
          "/Users/vinayakgandhi/Desktop/emp.csv")
