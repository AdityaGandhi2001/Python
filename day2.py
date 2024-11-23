# find the largest  number:
'''
num1 = int(input(" enter the number 1 : "))
num2 = int(input(" enter the number 2 : "))
num3 = int(input(" enter the number 3 : "))

if (num1 >= num2) and (num1 >= num3):
    largest = num1
elif (num2 >= num1) and (num2 >= num3):
    largest = num2
else:
    largest = num3

print("The largest number is", largest)
'''
# find the leap year


'''
A = int(input(" enter the year: "))
if ( A % 400 == 0):
    print(" It is a leap year")
elif (A % 100 != 0 and A % 4 == 0):
    print(" It is an leap year")
else:
    print(" it is not a leap year")
'''
# using while loop
'''
Number = int(input(" enter a number "))
i = 1
while i <= 10:
    print(Number*i)
    i = i+1
'''
# using for loop
'''
for i in (10, 0, -1):
    print(i)
'''
# reverse counting using while loop
# In this print option is inside the while so we will be getting a sequence of numbers

'''
i = 10
while i >= 1:
    print(i)
    i -= 1
'''

# Calculating the factorial of a number:
# In this print option is outside so we will be getting a single value

'''
a = int(input("enter a number: "))
f = 1
while (a > 1):
    f = f*a
    a -= 1
print(f)
'''

# Example:

'''
a = 1
b = 5
while (a <= 5):
    print(a*b)
    a += 1
    b -= 1
'''

# Sum of natural numbers upto 10 using while loop:

'''
sum = 0
i = 1
while (i <= 10):
    sum = sum+i
    i += 1
print(sum)
'''

# Sum of natural numbers upto 10 using for loop:

'''
sum = 0
for i in range(1, 11):
    sum = sum+i
print("Sum of  natural numbers  upto 10 is ", sum)
'''
