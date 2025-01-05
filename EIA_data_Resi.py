import requests
import pandas as pd

# Your EIA API key
API_KEY = "hCjY4AAYMqVZvYwPppQ1XpeWhSRBgbFgB1ppzT5s"
BASE_URL = "https://api.eia.gov/v2"

# Example: Querying residential electricity consumption data
url = "https://api.eia.gov/v2/electricity/retail-sales/data/"
params = {
    "api_key": API_KEY,
    "frequency": "monthly",
    "data[]": ["customers", "price", "revenue", "sales"],
    "facets[sectorid][]": ["ALL", "COM", "IND", "OTH", "RES", "TRA"],
    "offset": 0,
    "length": 5000
}

response = requests.get(url, params=params)
data = response.json()
#print(data)

# Convert to DataFrame
df = pd.DataFrame(data['response']['data'])
df.drop(['customers-units','price-units','revenue-units','sales-units'], axis=1, inplace=True)
df.to_csv("energy_data.csv", index=False)
res_df = df[df['sectorid'] == 'RES']
com_df = df[df['sectorid'] == 'COM']
ind_df = df[df['sectorid'] == 'IND']
tra_df = df[df['sectorid'] == 'TRA']
oth_df = df[df['sectorid'] == 'OTH']
all_df = df[df['sectorid'] == 'ALL']
res_df.to_csv("res_energy_data.csv", index=False)
com_df.to_csv("com_energy_data.csv", index=False)
ind_df.to_csv("ind_energy_data.csv", index=False)
tra_df.to_csv("tra_energy_data.csv", index=False)
oth_df.to_csv("oth_energy_data.csv", index=False)
all_df.to_csv("all_energy_data.csv", index=False)
print(res_df)
