l = [1, 2, 3, 2, 2, 4, 5, 5, 6, 7]
i = 0
while i < len(l):
    j = i+1
    while j < len(l):
        if l[i] == l[j]:
            del (l[j])
        else:
            j += 1
    i += 1
print(l)
