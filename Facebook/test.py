from drive_functions import *
import pandas as pd
import numpy as np

def create_dataframe(start_year, end_year):
    years = list(range(start_year, end_year + 1))
    df = pd.DataFrame(np.random.rand(len(years), 5))
    df["Time"] = years
    return df

df = create_dataframe(2000, 2020)

df.columns = ["Jan", "Lena", "Francesca", "Bea", "Richard", "Time"]
df=df[["Time","Jan", "Lena", "Francesca", "Bea", "Richard"]]
print(df)

save_dataframe_to_drive(df, "first_ex.xlsx", "1UV2WZY6ldkTQlP7_OIIpaCU--mgkKHoB")

def create_dataframe(start_year, end_year):
    years = list(range(start_year, end_year + 1))
    df = pd.DataFrame(np.random.rand(len(years), 5), index=years)
    return df
df.columns = ["Jan", "Lena", "Francesca", "Bea", "Richard", "Time"]
df=df[["Time","Jan", "Lena", "Francesca", "Bea", "Richard"]]
df = create_dataframe(2000, 2020)
save_dataframe_to_drive(df, "second_ex.xlsx", "1UV2WZY6ldkTQlP7_OIIpaCU--mgkKHoB")
