import pandas as pd


# create df
df = pd.DataFrame({"even": [2, 4, 6, 8, 10], "odd": [1, 3, 5, 7, 9]})
# preview
# print(df)

# pre-selected data that need to be removed
SELECTED = (2, 6, 10, 3)


def row_filter(num):
    """ conditional """

    return df["even"] == num


# why does this work?
# for num in SELECTED:
#     df.drop(index=df[row_filter(num)].index, axis=0, inplace=True)
# print(df)


# why does this not work?
# why do I need it to work?
#   well, I want the speed of execution list-comprehension offers
#   again, I think it is more efficient to remove big list of selected items at one go
indexes = [df[row_filter(num)].index for num in SELECTED]
df.drop(indexes, axis=0, inplace=True)
print(df)
