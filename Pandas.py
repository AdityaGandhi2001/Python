import pandas as pd
import numpy as np

# How to create a dataframe:
'''
dict = {"Name": ["ADITYA", "RUDRA"], "Marks": [
    99, 100], "City": ["Ggn", "Delhi"]}
df = pd.DataFrame(dict)
print(df)
# How to convert df into csv file:
df.to_csv("friend.csv")
df.to_csv("friends_no_index.csv", index=False)
# Basic commands: head: gives top values
print(df.head(1))
# Tail gives last values:
print(df.tail(2))
# Describe: Analyzes the numerical values and gives mean,count and many more mathematical relations:
print(df.describe())
# How to read a csv file:We can write the path or name of the csv file:
harry = pd.read_csv("/Users/vinayakgandhi/PYTHON/harry.csv")
print(harry)
print(harry["speed"])
print(harry["speed"][0])
# Changing value of a particular index of the column:
"""harry["speed"][0] = 50"""
harry.index = ["First", "Second"]
print(harry)
# Creating a series:
ser = pd.Series(np.random.rand(34))
print(ser)
print(type(ser))
'''
# arange is similar to range function in python:
newdf = pd.DataFrame(np.random.rand(334, 5), index=np.arange(334))
print(newdf)
print(newdf.head())
print(type(newdf))
print(newdf.describe())
newdf[0][0] = "harry"
print(newdf.dtypes)
print(newdf.head())
print(newdf.index)
print(newdf.columns)
# Converting into a numpy array:
print(newdf.to_numpy())
# T attribute does the transpose:rows changes to columns and columns into rows:
print(newdf.T)
# sorting: axis 0 is for rows and for columns is 1:
print(newdf.sort_index(axis=0, ascending=False))
print(newdf.sort_index(axis=1, ascending=False))

# View: Any changes made in newdf2 will be reflected in newdf too:

newdf2 = newdf
newdf2[0][0] = "653"
print(newdf)

# Copy: Changes made will not be reflected in newdf
newdf2 = newdf.copy()
newdf2[0][0] = "1234"
print(newdf)

# Loc function to set he value: First zero indicates row and second zero indicates columns
newdf.loc[0, 0] = "699"
print(newdf)
newdf.columns = list("ABCDE")
print(newdf.head(2))
newdf.loc[0, "A"] = 700
print(newdf)
# Slicing to get desired columns or rows we use: 1 AND 2 REPRESENTS ROWS AND C AND D REPRESENTS COLUMNS loc is used by using name of columns:
print(newdf.loc[[1, 2], ["C", "D"]])
# print all rows along with the desired columns:
print(newdf.loc[:, ["C", "D"]])
# print all columns along with the desired columns:
print(newdf.loc[[1, 2], :])
# query:returning rows with desired value :
print(newdf.loc[(newdf["A"] < 0.3) & newdf["C"] > 0.1])
# using range:
print(newdf.iloc[0:4])
# using iloc and comma between values gives you  single value of that particular details: iloc is used for integer indexing
print(newdf.iloc[0, 4])
print(newdf.iloc[[0, 2], [1, 2]])
print(newdf)
# dropping rows: inplace function actually removes it from the the dataframe: else it just shows the copy of the dataset when we give a query:
print(newdf.drop(0, inplace=True))
# droping columns:
print(newdf.drop("A", axis=1))
print(newdf)
# Reseting index  and we used drop to remove the index named column that was being created while reseting index:
print(newdf.reset_index(drop=True))
# Null function shows is there any null value:
print(newdf["A"].isnull())
# TO CHANGE THE VALUE OF COLUMN: well we should prefer loc while changing columns:
newdf["B"] = None
print(newdf.loc[:, ["B"]])
print(newdf)
# dropna drop all the columns and rows having na:
"df.dropna()"
# Untill and unless all the columns and rows have na in the set the below fuction will not drop the coloumn or row:
# keep=first leeps first record and delete duplicates
# kee=false deletes all duplicate records:
"df.dropna(how=all)"
"""df.drop_duplicates(subset=["name"], keep="first")"""
# Shape: tell the number of rows and columns:
print(newdf.shape)
# Info:
print(newdf.info())
print(newdf["A"].value_counts)
# Use of is null and not null:
print(newdf.notnull())
print(newdf.isnull())
# How to read an excel:
d2 = pd.read_excel("Name of excel:")
# To update the excel:
d2.to_excel()
# If any module is not found just use pip install module name:
