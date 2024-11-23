# l = [[1, 0], [0, 1]]
# flag = True
# for i in range(len(l)):
#     for j in range(len(l)):
#         if i == j and l[i][j] != 1 or i != j and l[i][j] != 0:
#             flag = False
# if flag:
#     print("identity ")
# else:
#     print("Not an identity matrix")


# l = [[1, 2, 3], [4, 5, 6]]
# for i in range(len(l)):
#     for j in range(len(l[i])):
#         print(l[i][j], end="")
#     print()

# r = [[0, 0],
#      [0, 0],
#      [0, 0]]
# for i in range(len(l)):
#     for j in range(len(l[0])):
#         r[j][i] = l[i][j]
# for i in r:
#     print(i)

# l = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
# for i in range(len(l)-1):
#     for j in range(i+1, len(l)):
#         l[i][j], l[j][i] = l[j][i], l[i][j]
# print(l)
