# OLA Ride Insights — End-to-End Data Analytics Project

**Live Streamlit Dashboard:** [ola-ride-insights-2kz2uyzgpwyhragmpkjoam.streamlit.app](https://ola-ride-insights-2kz2uyzgpwyhragmpkjoam.streamlit.app)

An end-to-end ride-sharing analytics project analyzing **103,024 OLA ride bookings** from Bengaluru (July 2024) using **Python**, **SQLite / SQL**, **Power BI**, and **Streamlit**.

## Tech Stack
- **Data Cleaning & EDA:** Python, Pandas, Matplotlib, Seaborn
- **Database & Querying:** SQLite (`ola_rides.db`), SQL
- **BI Dashboard:** Power BI Desktop (5-page interactive report + DAX)
- **Web App:** Streamlit, Plotly (deployed on Streamlit Community Cloud)

## Project Structure
```text
OLA RIDE/
├── OLA_DataSet.xlsx        # Raw dataset (103,024 rows, 20 columns)
├── clean_data.py           # Data cleaning & feature engineering -> ola_cleaned.csv
├── eda.py                  # Exploratory Data Analysis -> eda_charts/
├── eda_charts/             # Saved Matplotlib/Seaborn EDA plots
├── run_sql_queries.py      # Loads ola_cleaned.csv into ola_rides.db & runs 10 SQL queries
├── ola_queries.sql         # Standalone SQL queries for all 10 project questions
├── app.py                  # Interactive Streamlit dashboard + SQL Query Explorer
├── ola_cleaned.csv         # Cleaned dataset
├── ola_rides.db            # SQLite database
├── requirements.txt        # Python dependencies
└── .gitignore              # Excludes .venv/, .env, and __pycache__/
```

## Key Findings
- **Overall Volume & Success Rate:** Out of **103,024 bookings**, **63,967 (62.09%)** succeeded, generating **Rs. 35,080,467 (~Rs. 35.08M)** in completed booking value.
- **Cancellations:** **28.08%** of all bookings were cancelled (**18,434** by drivers; **10,499** by customers), and **10,124 (9.83%)** failed due to *Driver Not Found*.
- **Top Cancellation Drivers:** Customer cancellations were largely caused by *"Driver is not moving towards pickup location"* (3,175) and *"Driver asked to cancel"* (2,670). Driver cancellations were led by *"Personal & Car related issue"* (6,542).
- **Vehicle Distance:** **Prime Sedan** averaged the longest trip (**15.76 km**), while **Auto** averaged **6.24 km** for short neighborhood trips.
- **Payments & Ratings:** **Cash** (Rs. 19.26M) and **UPI** (Rs. 14.17M across 25,881 rides) account for over 95% of revenue. Average Driver and Customer ratings cluster tightly around **4.00** across all vehicle types.

## Business Recommendations
1. **Reduce Pickup Friction:** Auto-reassign rides if GPS shows a driver is stationary for 3+ minutes after accepting, and penalize driver-initiated cancellation requests.
2. **Lower Driver Rejections:** Show upfront destination and fare estimates to drivers before acceptance and offer partner garage maintenance support.
3. **Accelerate Digital Payments:** Introduce UPI cashback or pass incentives to shift Cash riders toward digital payments.
4. **Smart Fleet Allocation:** Position Autos near metro stations and local markets for short hops (~6 km), while prioritizing Prime Sedans and eBikes for longer 15+ km commutes.

## How to Run Locally
```bash
# 1. Clone the repository
git clone https://github.com/sabilchougule/OLA-Ride-Insights.git
cd OLA-Ride-Insights

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows PowerShell

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run ETL, EDA, and SQLite setup
python clean_data.py
python eda.py
python run_sql_queries.py

# 5. Launch the Streamlit dashboard
streamlit run app.py
```

## Author
**Sabil Chougule** — [GitHub](https://github.com/sabilchougule)
