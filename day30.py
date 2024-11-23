'''
import csv
import os
a = 1
i = 0
with open("/Users/vinayakgandhi/Desktop/emp.csv", "r") as inp, open("/Users/vinayakgandhi/Desktop/temp.csv", "w", newline="") as out:
    writer = csv.writer(out)
    for k in csv.reader(inp):
        if k[i] != str(a):
            writer.writerow(k)
os.remove("/Users/vinayakgandhi/Desktop/emp.csv")
os.rename("/Users/vinayakgandhi/Desktop/temp.csv",
          "/Users/vinayakgandhi/Desktop/emp.csv")
'''
