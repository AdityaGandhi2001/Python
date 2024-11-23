# bitwise operators:
# AND $,OR |, XOR^.
'''
import pandas as pd
import numpy as np
s = pd.Series(5, index=["a", "b", "c", "d"])
print(s)
x = 0
for i in range(len(s)):
    x = x+s[i]
print(max(s))
print(min(s))
'''
#
'''
import pandas as pd
import numpy as np
s = pd.Series([1, 2, 3, 4, 5])
print(s)
max1 = s[0]
max2 = s[1]
for i in range(len(s)):
    if s[i] > max1:
        max2 = max1
        max1 = s[i]
    elif s[i] > max2:
        max2 = s[i]
print(max1)
print(max2)
'''
