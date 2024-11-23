# Dictionary:

'''
D = {'Name': ["A", "B", "C"], 'Age': [10, 20, 30]}
print(D["Name"])
print(len(D))
data = input("enter: ")
if data in D["Name"]:
    i = D["Name"].index(data)
    print(D["Age"][i])
else:
    print("not found")



D = {}
for i in range(2):
    key = input("enter key: ")
    D[key] = int(input("enter value: "))
print(D)


D = {}
for i in range(2):
    key = input("enter key: ")
    D[key] = []
    for j in range(3):
        x = input("enter the value")
        D[key].append(x)
print(D)
'''
