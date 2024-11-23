# a = int(input("enter the number"))
# evencount = 0
# oddcount = 0
# while a > 0:
#     if a % 2 == 0:
#         evencount += 1
#     else:
#         oddcount += 1
#     a = a//10
# if oddcount == 0 or evencount == 0:
#     print("It is a perfect number")
# else:
#     print("Not a perfect number")

# d = {}
# for i in range(2):
#     key = input("enter a letter:")
#     d[key] = int(input("enter a number:"))
# print(d)

# d = {}
# for i in range(2):
#     Key = input("enter a letter:")
#     d[Key] = []
#     for i in range(2):
#         k = int(input("enter a number:"))
#         d[Key].append(k)
# print(d)

# import matplotlib.pyplot as plt
# import pandas as pd

# df = pd.DataFrame(
#     [[101, "aditya", 2000], [102, "mukesh", 3000]], columns=["code", "name", "basic"])
# print(df)
# plt.scatter(df.name, df.basic, df.code)
# plt.show()
# Use of f-string:


# class sum():

#     def input(self):
#         self.a = int(input("enter a number:"))
#         self.b = int(input("enter a number b:"))

#     def sum(self):
#         self.c = self.a+self.b

#     def disp(self):
#         print(f"The sum is: {self.c}")


# s = sum()
# s.input()
# s.sum()
# s.disp()

l = [1, 2, 3, 4, 5]
for i in l:
    f = 1
    A = i
    while A > 0:
        f = f*A
        A = A-1
    print(f)
