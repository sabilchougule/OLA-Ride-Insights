import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="OLA Ride Insights", layout="wide")


@st.cache_data
def get_data():
    conn = sqlite3.connect("ola_rides.db")
    df = pd.read_sql_query("SELECT * FROM ola_rides", conn)
    conn.close()
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def run_query(sql):
    conn = sqlite3.connect("ola_rides.db")
    res = pd.read_sql_query(sql, conn)
    conn.close()
    return res


df = get_data()

# Sidebar navigation and filters
st.sidebar.title("OLA Ride Insights")
view = st.sidebar.radio(
    "Select View",
    ["Overall", "Vehicle Type", "Revenue", "Cancellation", "Ratings", "SQL Queries"]
)

st.sidebar.subheader("Filters")
min_d = df["Date"].min().date()
max_d = df["Date"].max().date()
date_range = st.sidebar.date_input("Date Range", (min_d, max_d), min_value=min_d, max_value=max_d)

vehicles = st.sidebar.multiselect(
    "Vehicle Type",
    sorted(df["Vehicle_Type"].unique()),
    default=sorted(df["Vehicle_Type"].unique())
)

statuses = st.sidebar.multiselect(
    "Booking Status",
    sorted(df["Booking_Status"].unique()),
    default=sorted(df["Booking_Status"].unique())
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_d, max_d

filtered = df[
    (df["Date"].dt.date >= start_date)
    & (df["Date"].dt.date <= end_date)
    & (df["Vehicle_Type"].isin(vehicles))
    & (df["Booking_Status"].isin(statuses))
]

# Top KPI metrics
total_rides = len(filtered)
success_rides = filtered[filtered["Booking_Status"] == "Success"]
total_rev = success_rides["Booking_Value"].sum()
cancel_count = filtered["Booking_Status"].isin(["Canceled by Driver", "Canceled by Customer"]).sum()
cancel_pct = (cancel_count / total_rides * 100) if total_rides > 0 else 0
avg_cust_rating = filtered["Customer_Rating"].mean()

st.title(f"OLA Ride Insights - {view}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Bookings", f"{total_rides:,}")
c2.metric("Successful Booking Value", f"Rs. {total_rev:,.0f}")
c3.metric("Cancellation Rate", f"{cancel_pct:.2f}%")
c4.metric("Avg Customer Rating", f"{avg_cust_rating:.2f}" if pd.notna(avg_cust_rating) else "N/A")

if view == "Overall":
    col1, col2 = st.columns([2, 1])
    with col1:
        daily = filtered.groupby("Ride_Date", as_index=False)["Booking_ID"].count()
        fig1 = px.line(daily, x="Ride_Date", y="Booking_ID", title="Ride Volume Over Time", markers=True)
        st.plotly_chart(fig1, use_container_width=True)
        st.info(
            "**Business Insight:** Daily booking volume stays steady around 3,300+ rides per day across July 2024, showing consistent urban commute demand without extreme mid-month drops.\n\n"
            "**Future Recommendation:** Introduce peak-hour driver shift bonuses on high-demand days to convert more daily ride requests into completed trips."
        )

    with col2:
        status_df = filtered["Booking_Status"].value_counts().reset_index()
        status_df.columns = ["Booking_Status", "Count"]
        fig2 = px.pie(status_df, names="Booking_Status", values="Count", hole=0.45, title="Booking Status Breakdown")
        st.plotly_chart(fig2, use_container_width=True)
        st.info(
            "**Business Insight:** Only 62.09% (63,967) of bookings succeed, while 28.08% are cancelled (17.89% by drivers, 10.19% by customers) and 9.83% fail due to 'Driver Not Found'.\n\n"
            "**Future Recommendation:** Use predictive heatmaps in high 'Driver Not Found' zones to pre-position drivers 15 minutes before rush hour."
        )

elif view == "Vehicle Type":
    veh_table = (
        filtered.groupby("Vehicle_Type", as_index=False)
        .agg(
            Total_Bookings=("Booking_ID", "count"),
            Total_Distance_km=("Ride_Distance", "sum"),
            Avg_Distance_km=("Ride_Distance", "mean"),
            Total_Booking_Value=("Booking_Value", "sum")
        )
        .sort_values("Total_Distance_km", ascending=False)
    )
    veh_table["Avg_Distance_km"] = veh_table["Avg_Distance_km"].round(2)
    st.subheader("Vehicle Type Summary")
    st.dataframe(veh_table, use_container_width=True)

    fig_v = px.bar(
        veh_table.head(5),
        x="Vehicle_Type",
        y="Total_Distance_km",
        color="Vehicle_Type",
        title="Top 5 Vehicle Types by Ride Distance"
    )
    st.plotly_chart(fig_v, use_container_width=True)
    st.info(
        "**Business Insight:**Bookings are evenly distributed (~14.5K-14.8K per vehicle type), but Prime Sedan (15.76 km avg) and eBike (15.58 km avg) cover the longest distances, whereas Auto is strictly used for short hops (6.24 km avg).\n\n"
        "**Future Recommendation:** Position Autos near metro stations and local markets for last-mile connectivity, and prioritize Prime Sedans and EVs/eBikes for long-corridor IT office commutes."
    )

elif view == "Revenue":
    col1, col2 = st.columns(2)
    with col1:
        pay_df = (
            success_rides.groupby("Payment_Method", as_index=False)["Booking_Value"]
            .sum()
            .sort_values("Booking_Value", ascending=False)
        )
        fig_p = px.bar(pay_df, x="Payment_Method", y="Booking_Value", title="Revenue by Payment Method")
        st.plotly_chart(fig_p, use_container_width=True)
        st.info(
            "**Business Insight:** Cash (Rs. 19.26M across 35,022 rides) and UPI (Rs. 14.17M across 25,881 rides) generate over 95% of completed ride revenue, while Cards make up less than 5%.\n\n"
            "**Future Recommendation:** Offer small UPI cashback rewards or auto-pay wallet credits to shift Cash riders to digital payments, reducing driver cash-handling issues."
        )

    with col2:
        cust_df = (
            success_rides.groupby("Customer_ID", as_index=False)["Booking_Value"]
            .sum()
            .sort_values("Booking_Value", ascending=False)
            .head(5)
        )
        fig_c = px.bar(cust_df, x="Customer_ID", y="Booking_Value", title="Top 5 Customers by Total Booking Value")
        st.plotly_chart(fig_c, use_container_width=True)
        st.info(
            "**Business Insight:** Top high-value customers spend nearly Rs. 6,000 each within a single month across repeat high-fare rides.\n\n"
            "**Future Recommendation:** Launch an 'OLA VIP / Pass' loyalty tier for top-spending commuters with priority driver matching and zero surge fees."
        )

    dist_daily = filtered.groupby("Ride_Date", as_index=False)["Ride_Distance"].sum()
    fig_d = px.bar(dist_daily, x="Ride_Date", y="Ride_Distance", title="Ride Distance Distribution Per Day")
    st.plotly_chart(fig_d, use_container_width=True)
    st.info(
        "**Business Insight:** Total daily fleet distance tracks closely with daily completed bookings (~31K-34K km/day), proving stable trip lengths throughout the month.\n\n"
        "**Future Recommendation:** Bundle mileage-based fuel and EV charging discounts for drivers who consistently cross daily distance targets."
    )

elif view == "Cancellation":
    col1, col2 = st.columns(2)
    with col1:
        cc = (
            filtered[filtered["Booking_Status"] == "Canceled by Customer"]["Canceled_Rides_by_Customer"]
            .value_counts()
            .reset_index()
        )
        cc.columns = ["Reason", "Count"]
        fig_cc = px.pie(cc, names="Reason", values="Count", hole=0.4, title="Cancelled Rides Reasons (Customer)")
        st.plotly_chart(fig_cc, use_container_width=True)
        st.info(
            "**Business Insight:** Over 55% of customer cancellations are actually triggered by driver behavior: 'Driver not moving towards pickup' (3,175) and 'Driver asked to cancel' (2,670). Another 1,568 are due to non-working AC.\n\n"
            "**Future Recommendation:** Auto-reassign rides if GPS shows a driver hasn't moved toward pickup within 3 minutes, and penalize drivers who ask riders to cancel."
        )

    with col2:
        dc = (
            filtered[filtered["Booking_Status"] == "Canceled by Driver"]["Canceled_Rides_by_Driver"]
            .value_counts()
            .reset_index()
        )
        dc.columns = ["Reason", "Count"]
        fig_dc = px.pie(dc, names="Reason", values="Count", hole=0.4, title="Cancelled Rides Reasons (Drivers)")
        st.plotly_chart(fig_dc, use_container_width=True)
        st.info(
            "**Business Insight:** Driver cancellations (18,434) are 1.75x higher than customer cancellations. The top reason is 'Personal & Car related issue' (6,542), followed by 'Customer related issue' (5,413).\n\n"
            "**Future Recommendation:** Show destination area and fare upfront to drivers before acceptance to cut post-match rejections, and provide partner garage maintenance support."
        )

elif view == "Ratings":
    rat_df = (
        filtered.groupby("Vehicle_Type", as_index=False)[["Driver_Ratings", "Customer_Rating"]]
        .mean()
        .round(2)
    )
    st.subheader("Customer vs. Driver Ratings by Vehicle Type")
    st.dataframe(rat_df, use_container_width=True)

    melted = rat_df.melt(id_vars="Vehicle_Type", var_name="Rating_Type", value_name="Avg_Rating")
    fig_r = px.bar(
        melted,
        x="Vehicle_Type",
        y="Avg_Rating",
        color="Rating_Type",
        barmode="group",
        title="Customer vs. Driver Ratings"
    )
    fig_r.update_yaxes(range=[3.5, 4.2])
    st.plotly_chart(fig_r, use_container_width=True)
    st.info(
        "**Business Insight:** Both Driver and Customer average ratings sit tightly around 3.98 to 4.01 across all 7 vehicle types (ranging from 3.0 to 5.0).\n\n"
        "**Future Recommendation:** Automatically flag drivers or vehicles dropping below 3.5 for AC/vehicle quality checks, and reward 4.5+ rated drivers with lower commission rates."
    )

elif view == "SQL Queries":
    sql_list = {
        "1. Retrieve all successful bookings (Sample 100)": (
            "SELECT * FROM ola_rides WHERE Booking_Status = 'Success' LIMIT 100;",
            "63,967 rides (62.09%) succeeded. Focus on converting the remaining 37.91% unfulfilled/cancelled demand."
        ),
        "2. Average ride distance for each vehicle type": (
            "SELECT Vehicle_Type, ROUND(AVG(Ride_Distance), 2) AS avg_distance_km FROM ola_rides GROUP BY Vehicle_Type ORDER BY avg_distance_km DESC;",
            "All cab/bike categories average ~15.3-15.8 km, while Auto averages 6.24 km for short neighborhood trips."
        ),
        "3. Total number of cancelled rides by customers": (
            "SELECT COUNT(*) AS customer_cancellations FROM ola_rides WHERE Booking_Status = 'Canceled by Customer';",
            "10,499 rides cancelled by customers—mostly because the driver wasn't moving or asked them to cancel."
        ),
        "4. Top 5 customers who booked the highest number of rides": (
            "SELECT Customer_ID, COUNT(Booking_ID) AS total_rides FROM ola_rides GROUP BY Customer_ID ORDER BY total_rides DESC LIMIT 5;",
            "Top repeat customers booked 4-5 rides in July; targeted ride passes can lock in their daily commute."
        ),
        "5. Rides cancelled by drivers due to personal & car-related issues": (
            "SELECT COUNT(*) AS driver_personal_car_cancels FROM ola_rides WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue';",
            "6,542 rides failed due to personal/car issues. Preventive vehicle checks can recover a large share of these trips."
        ),
        "6. Max and min driver ratings for Prime Sedan": (
            "SELECT MAX(Driver_Ratings) AS max_rating, MIN(Driver_Ratings) AS min_rating FROM ola_rides WHERE Vehicle_Type = 'Prime Sedan' AND Driver_Ratings IS NOT NULL;",
            "Prime Sedan ratings span from 3.0 to 5.0; coaching 3.0-rated drivers on AC and punctuality will lift the 4.00 average."
        ),
        "7. Rides where payment was made using UPI (Sample 100)": (
            "SELECT * FROM ola_rides WHERE Payment_Method = 'UPI' LIMIT 100;",
            "25,881 rides (40.5% of completed trips) used UPI, making it the second largest payment mode after Cash."
        ),
        "8. Average customer rating per vehicle type": (
            "SELECT Vehicle_Type, ROUND(AVG(Customer_Rating), 2) AS avg_customer_rating FROM ola_rides WHERE Customer_Rating IS NOT NULL GROUP BY Vehicle_Type ORDER BY avg_customer_rating DESC;",
            "Prime Plus leads slightly at 4.01, while all categories maintain a steady ~4.00 rating."
        ),
        "9. Total booking value of rides completed successfully": (
            "SELECT SUM(Booking_Value) AS total_successful_revenue FROM ola_rides WHERE Booking_Status = 'Success';",
            "Successful rides generated Rs. 35,080,467 (~Rs. 35.08M). Cutting cancellations by just 20% could add ~Rs. 4M+ monthly."
        ),
        "10. Incomplete rides along with the reason": (
            "SELECT Incomplete_Rides_Reason, COUNT(*) AS count FROM ola_rides WHERE Incomplete_Rides = 'Yes' GROUP BY Incomplete_Rides_Reason ORDER BY count DESC;",
            "3,926 completed bookings ended incomplete: Customer Demand (1,601), Vehicle Breakdown (1,591), and Other Issue (734)."
        )
    }

    choice = st.selectbox("Choose a SQL Question", list(sql_list.keys()))
    default_sql, takeaway = sql_list[choice]
    query_text = st.text_area("Query", default_sql, height=100)

    if st.button("Run Query"):
        out = run_query(query_text)
        st.write(f"Rows returned: {len(out):,}")
        st.dataframe(out, use_container_width=True)
        st.success(f"**Business & Future Insight:** {takeaway}")