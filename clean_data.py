import pandas as pd

df = pd.read_excel("OLA_DataSet.xlsx")
print("Loaded:", df.shape)

# check which columns have nulls
print(df.isnull().sum()[df.isnull().sum() > 0])

# remove spaces from column names so SQL & Power BI handle them cleanly
df.columns = [c.strip().replace(" ", "_") for c in df.columns]

# parse date and extract hour/day for time-based charts
df["Date"] = pd.to_datetime(df["Date"])
df["Ride_Date"] = df["Date"].dt.date
df["Day_Name"] = df["Date"].dt.day_name()
df["Is_Weekend"] = df["Date"].dt.day_of_week.isin([5, 6]).astype(int)
df["Ride_Hour"] = pd.to_datetime(df["Time"].astype(str), format="mixed").dt.hour

# fill text reason columns instead of dropping rows,
# since the 39,057 null rows are canceled/unfulfilled rides we still need
df["Canceled_Rides_by_Customer"] = df["Canceled_Rides_by_Customer"].fillna("Not Applicable")
df["Canceled_Rides_by_Driver"] = df["Canceled_Rides_by_Driver"].fillna("Not Applicable")
df["Incomplete_Rides"] = df["Incomplete_Rides"].fillna("No")
df["Incomplete_Rides_Reason"] = df["Incomplete_Rides_Reason"].fillna("Not Applicable")
df["Payment_Method"] = df["Payment_Method"].fillna("Not Paid")

df.to_csv("ola_cleaned.csv", index=False)
print("Saved ola_cleaned.csv")