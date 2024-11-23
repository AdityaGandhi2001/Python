# DATA VISUALISATION
import pandas as pd
import matplotlib.pyplot as plt
data = [[101, "a", 100000], [102, "b", 120000], [103, "c", 140000]]
df = pd.DataFrame(
    data, columns=["Code", "Name", "Basic"])
print(df)
df.hist()
plt.show()

# df.plot.bar()
# plt.bar(df["name"], df["basic"], color=("pink"))
# plt.xlabel("name")
# plt.ylabel("basic")
# plt.show()

# df.plot.box()
# plt.boxplot(df["basic"])
# plt.show()

# plt.pie(df["basic"], labels=df["code"], autopct="%1.1f%%", shadow=True)
# plt.show()
'''
plt.scatter(df["basic"], df["code"])
plt.show()
'''
