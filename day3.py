# calculate the  number of digits in a given value

'''
a=189
count= 0
while a>0:
    count+=1
    a=a//10
print(count)
'''
# calulate the sum of digits in a given value
'''
sum = 0
a = 2145
while (a > 0):
    r = a % 10
    sum = sum+r
    a = a//10
print("Sum of digits", sum)
'''

# Reverse the number

'''
New_number = 0
a = 101
b = a
while (a > 0):
    r = a % 10
    New_number = (New_number*10) + r
    a = a//10
print(New_number)


if (New_number == b):
    print(" It is a pallindrome", New_number)
else:
    print(" It is not a pallindrome")
'''

# find the armstrong number:
'''
arm_strongno = 0
a = 153
b = a
while (a > 0):
    r = a % 10
    cube = r*r*r
    arm_strongno = arm_strongno+cube
    a = a//10

print(arm_strongno)
if (b == arm_strongno):
    print("It is an armstrong number")

else:
    print(" It is not an armstrong number")
'''
# find a neon number:
'''
a = 9
n = a
a = a*a
neon_number = 0
while (a > 0):
    r = a % 10
    neon_number = neon_number+r
    a = a//10
print(neon_number)
if (neon_number == n):
    print("yes it is neon number")
else:
    print(" it is not")
'''

# check whether the number is perfect or non perfect
# IMPORTANT

a = int(input("Enter a number:"))
even = 0
odd = 0
while (a > 0):

    r = a % 10
    if r % 2 == 0:
        even += 1
    else:
        odd += 1
    a = a//10

if even == 0 or odd == 0:
    print(" it is a perfect number")
else:
    print("it is not a perfect number")
