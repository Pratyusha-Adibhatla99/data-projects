import pandas as pd

# Load all datasets
craigslist = pd.read_csv("data/craigslist.csv")
rent = pd.read_csv("data/rent.csv")
realtor = pd.read_csv("data/realtor.csv")
census = pd.read_csv("data/census_income.csv")

# Combine housing data
housing = pd.concat([craigslist, rent, realtor], ignore_index=True)

# Save merged housing dataset
housing.to_csv("data/all_housing.csv", index=False)
print(f"Combined dataset saved: {len(housing)} listings")

# (Optional) Later: join housing with census data on ZIP codes if you extract ZIPs from 'location'
