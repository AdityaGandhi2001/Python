'''
import pandas as pd
s = pd.Series()
print(s)
'''

'''
import pandas as pd
import numpy as np
data = np.array(["a", "b", "c", "d"])
s = pd.Series(data)
print(s)
'''

'''
import numpy as np
import pandas as pd
data = np.array(["a", "b", "c", "d"])
s = pd.Series(data, index=[100, 101, 102, 103])
print(s)
'''
'''
import numpy as np
import pandas as pd
data = np.array(["a", "b", "c", "d"])
s = pd.Series(data, index=[100, 101, 102, 103])
print(s)
'''

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
