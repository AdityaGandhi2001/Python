# FIND OUT GREATER NO:

'''
A = int(input("enter a number : "))
B = int(input(" enter a number: "))
if (A > B):
    print(" Greater number is ", A)

else:
    print(" Greater number is ", B)
'''


# ENTER TWO NUMBERS AND SWAP THEM: ***********

'''
A = int(input("enter a number : "))
B = int(input(" enter a number: "))
A, B = B, A
print("After swap the value of a is %d and b is %d" % (A, B))
print(f"After swap the value of A is {A} AND B is {B}")
'''

# Find out whether the number is even or odd:

'''

A = int(input(" enter a number : "))
if (A % 2 == 0):
    print(" The number is even ")
else:
    print(" The number is odd")

'''
# Find out whether number is positive or negative:

'''

A = int(input(" enter a number : "))
if (A > 0):
    print("The number is positive ")
elif (A < 0):
    print("  The number is negative ")
else:
    print(" The number is zero")

'''

# Maintain the student record
# Priorty order of arithmetic operations should be taken into consideration

'''

P = int(input("enter the marks in physics: "))
C = int(input("enter the marks in chemistry: "))
M = int(input(" enter the marks in maths: "))
TOTAL = P+C+M
print('Total Marks  :  ', TOTAL)
PERCENTAGE = (TOTAL/300)*100
print('Percentage : ', PERCENTAGE)
X = PERCENTAGE
if (X >= 60):
    print("Ranked in Ist divsion")
elif (X >= 50):
    print("Ranked in IInd divison")
elif (X >= 40):
    print("Ranked in IIIrd divsion")
else:
    print("FAIL")

'''

# Maintain a stock record:********

'''
Stock_Name = input(" enter the stock name: ")
Q = int(input(" enter the quantity: "))
R = int(input("enter the rate: "))
A = (Q*R)
print(" The amount is ", A)
if (A >= 20000):
    dis = A*20/100
elif (A >= 10000):
    dis = A*10/100
elif (A >= 5000):
    dis = A*5/100
else:
    dis = 0
print("Discount : ", dis)
Paid_amount = A-dis
print("Paid_amount   :   ", Paid_amount)
'''

# Tell whether the student is pass or fail:

'''
Student_name = input("enter the name of the student:")
P = int(input("enter the marks in physics : "))
C = int(input("enter the marks in chemistry : "))
M = int(input("enter the marks in maths: "))
if (P >= 40 and C >= 40 and M >= 40):
    print(" PASSED")
else:
    print(" FAIL")
'''

# Show the p/l report:*******

'''
Stock_Name = input(" Enter the name of the stock:  ")
Cost_price = int(input(" enter the cost price: "))
Selling_price = int(input(" enter the selling price: "))
Profitandloss_REPORT = (Selling_price - Cost_price)
if (Profitandloss_REPORT > 0):
    print("Your account is in profit of ", Profitandloss_REPORT)
elif (Profitandloss_REPORT < 0):
    print("Your account is in a loss of ", -Profitandloss_REPORT)
else:
    print(" Your account is at breakeven level ", Profitandloss_REPORT)

'''

# sp = 4
# for i in range(5):
#     for j in range(sp):
#         print(" ", end="")
#     for j in range(i+1):
#         print("*", end=" ")
#     sp -= 1
#     print()

# hh = int(input("enter the time hh is showing:"))
# mh = int(input("enter the time mh is showing: "))
# hour_angle = (hh/12)*360+0.5*mh
# minute_angle = (mh/60)*360
# print(hour_angle)
# print(minute_angle)
# net = abs(hour_angle-minute_angle)
# angle = min(360-net, net)
# print(angle)
