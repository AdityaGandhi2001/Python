n = int(input("enter a number:"))
an = n
sum = 0
while n > 0:
    r = n % 10
    cube = r**3
    sum = sum+cube
    n = n//10
print(sum)
if an == sum:
    print("It is an armstrong number")
else:
    print("It is not a armstrong number")
