# Conversion of number into binary number :

'''
a = int(input(" enter a number: "))
s = ''
while a > 0:
    s = s + str(a % 2)
    a = a//2
print(s)
for i in range(len(s)-1, -1, -1):
    print(s[i], end="")
'''

# Question :
'''
a = int(input(" Enter a number:"))
s = ''
while a > 0:
    r = a % 16
    if (r < 10):
        s = s + str(r)
    else:
        s = s + str(chr(r+55))
    a = a//16
print(s)
for i in range(len(s)-1, -1, -1):
    print(s[i])
'''
