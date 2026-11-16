import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("ola_cleaned.csv")
os.makedirs("eda_charts", exist_ok=True)

# 1. Basic overview & duplicates
print("Shape:", df.shape)
print("Duplicate Booking_IDs:", df["Booking_ID"].duplicated().sum())
print("\nNumeric Summary:")
print(df[["Booking_Value", "Ride_Distance", "V_TAT", "C_TAT", "Driver_Ratings", "Customer_Rating"]].describe().round(2))

# 2. Categorical breakdowns
print("\nBooking Status (%):")
print((df["Booking_Status"].value_counts(normalize=True) * 100).round(2))

print("\nTop 5 Pickup Locations:")
print(df["Pickup_Location"].value_counts().head(5))

print("\nPeak Ride Hours (Top 5):")
print(df["Ride_Hour"].value_counts().head(5))

# 3. Chart 1: Hourly Ride Demand
plt.figure(figsize=(10, 4))
hourly = df["Ride_Hour"].value_counts().sort_index()
sns.lineplot(x=hourly.index, y=hourly.values, marker="o", color="#2E7D32")
plt.title("Hourly Ride Demand (00:00 - 23:00)")
plt.xlabel("Hour of Day")
plt.ylabel("Total Bookings")
plt.xticks(range(0, 24))
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("eda_charts/1_hourly_demand.png")
plt.close()

# 4. Chart 2: Booking Value Distribution (Successful Rides)
plt.figure(figsize=(8, 4))
success_df = df[df["Booking_Status"] == "Success"]
sns.histplot(success_df["Booking_Value"], bins=30, kde=True, color="#1565C0")
plt.title("Booking Value Distribution (Successful Rides)")
plt.xlabel("Booking Value (Rs.)")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("eda_charts/2_booking_value_dist.png")
plt.close()

# 5. Chart 3: Ride Distance by Vehicle Type (Boxplot)
plt.figure(figsize=(9, 4))
sns.boxplot(data=df, x="Vehicle_Type", y="Ride_Distance", palette="Set2")
plt.title("Ride Distance Spread by Vehicle Type")
plt.xlabel("Vehicle Type")
plt.ylabel("Distance (km)")
plt.tight_layout()
plt.savefig("eda_charts/3_distance_by_vehicle.png")
plt.close()

# 6. Chart 4: Correlation Heatmap (Numeric Features)
plt.figure(figsize=(7, 5))
num_cols = ["Booking_Value", "Ride_Distance", "V_TAT", "C_TAT", "Driver_Ratings", "Customer_Rating"]
sns.heatmap(success_df[num_cols].corr(), annot=True, fmt=".2f", cmap="coolwarm")
plt.title("Correlation Heatmap (Successful Rides)")
plt.tight_layout()
plt.savefig("eda_charts/4_correlation_heatmap.png")
plt.close()

print("\nSaved 4 EDA charts in the 'eda_charts/' folder!")