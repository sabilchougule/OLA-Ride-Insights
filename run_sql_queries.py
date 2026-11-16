import sqlite3
import pandas as pd

# load cleaned data into SQLite database
df = pd.read_csv("ola_cleaned.csv")
conn = sqlite3.connect("ola_rides.db")
df.to_sql("ola_rides", conn, if_exists="replace", index=False)
print("Database created: ola_rides.db\n")

queries = {
    "Q1: Successful bookings count": """
        SELECT COUNT(*) AS successful_bookings
        FROM ola_rides
        WHERE Booking_Status = 'Success';
    """,
    "Q2: Avg ride distance by vehicle type": """
        SELECT Vehicle_Type, ROUND(AVG(Ride_Distance), 2) AS avg_distance_km
        FROM ola_rides
        GROUP BY Vehicle_Type
        ORDER BY avg_distance_km DESC;
    """,
    "Q3: Total rides cancelled by customers": """
        SELECT COUNT(*) AS customer_cancellations
        FROM ola_rides
        WHERE Booking_Status = 'Canceled by Customer';
    """,
    "Q4: Top 5 customers by total rides": """
        SELECT Customer_ID, COUNT(Booking_ID) AS total_rides
        FROM ola_rides
        GROUP BY Customer_ID
        ORDER BY total_rides DESC
        LIMIT 5;
    """,
    "Q5: Driver cancellations (personal & car issues)": """
        SELECT COUNT(*) AS driver_personal_car_cancels
        FROM ola_rides
        WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue';
    """,
    "Q6: Max and min driver ratings for Prime Sedan": """
        SELECT MAX(Driver_Ratings) AS max_rating, MIN(Driver_Ratings) AS min_rating
        FROM ola_rides
        WHERE Vehicle_Type = 'Prime Sedan' AND Driver_Ratings IS NOT NULL;
    """,
    "Q7: Total rides paid using UPI": """
        SELECT COUNT(*) AS upi_rides
        FROM ola_rides
        WHERE Payment_Method = 'UPI';
    """,
    "Q8: Avg customer rating per vehicle type": """
        SELECT Vehicle_Type, ROUND(AVG(Customer_Rating), 2) AS avg_customer_rating
        FROM ola_rides
        WHERE Customer_Rating IS NOT NULL
        GROUP BY Vehicle_Type
        ORDER BY avg_customer_rating DESC;
    """,
    "Q9: Total booking value of successful rides": """
        SELECT SUM(Booking_Value) AS total_successful_revenue
        FROM ola_rides
        WHERE Booking_Status = 'Success';
    """,
    "Q10: Incomplete rides by reason": """
        SELECT Incomplete_Rides_Reason, COUNT(*) AS total_incomplete
        FROM ola_rides
        WHERE Incomplete_Rides = 'Yes'
        GROUP BY Incomplete_Rides_Reason
        ORDER BY total_incomplete DESC;
    """
}

for name, sql in queries.items():
    print(name)
    print(pd.read_sql_query(sql, conn).to_string(index=False))
    print("-" * 45)

conn.close()