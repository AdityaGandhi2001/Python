# Exception Handeling:
'''
a = 10
b = 0
try:
    c = a/b
    print(c)
except ZeroDivisionError:
    print("BYE")
'''

'''
A = [10, 20, 30, 40, 50]
try:
    c = a[1]/"a"
    print(c)
except ZeroDivisionError:
    print("divsion error")
except IndexError:
    print("index error")
except TypeError:
    print("type error")
print("good going")
'''

'''
a = [10, 20, 30, 40]
try:
    c = a[1]/"a"
    print(c)
except ZeroDivisionError:
    print("divsion error")
except IndexError:
    print("index error")
except TypeError:
    print("type error")
finally:
    print("good going")
'''

a = [10, 20, 30, 40]
try:
    c = a[1]/"a"
except:
    print("catch all error")
print("ram ram")


a = [10, 20, 30, 40]
try:
    c = a[1]/a
    print(c)
except TypeError:
    pass
finally:
    print("ram ram ji")


'''
a = [10, 20, 30]
try:
    c = a[1]/"a"
except (ZeroDivisionError, IndexError, TypeError):
    print("exception")
print("ram ram")
'''

'''
a = [10, 20, 30, 40]
for i in range(10):
    try:
        if (i >= len(a)):
            raise IndexError
    except IndexError:
        print("error")
        break
    print(a[i])
'''

'''
class outofrangeerror(Exception):
    pass


a = [10, 20, 30, 40]
for i in range(10):
    try:
        if (i >= len(a)):
            raise outofrangeerror
    except outofrangeerror:
        print("error"
        break
    print(a[i])
'''

'''
class A(Exception):
    pass


a = int(input("enter a number:"))
b = int(input("enter a number: "))
try:
    if a > b:
        for i in range(b, 0, -1):
            if b % i == 0 and a % i == 0:
                k = i
                break
        print(i)
    else:
        raise A
except A:
    print("A IS LESSS THAN B")
'''
