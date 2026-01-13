import pandas as pd
import numpy as np
import datasay

np.random.seed(42)

# Realistic company names
companies = ["MRF", "CEAT", "Apollo", "JK Tyres", "Bridgestone", "Goodyear", "Michelin", "Pirelli"]
months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
years = [2022, 2023, 2024]

rows = []

# Generate sales amount (in lakhs for realism)
for company in companies:
    for year in years:
        for month in months:
            sales_amount = np.random.randint(50, 500)  # ₹ Lakhs
            rows.append([company, year, month, sales_amount])

# Create DataFrame
df = pd.DataFrame(
    rows,
    columns=["Company", "Year", "Month", "Sales_Amount_Lakhs"]
)

print(df.head())
print("\nTotal rows:", len(df))  # 288

#testing 


mrf_sales = df[df["Company"] == "MRF"]["Sales_Amount_Lakhs"].tolist()

summary = datasay.explain(mrf_sales)

print("\nDatasay Summary for MRF:")
print(summary)
