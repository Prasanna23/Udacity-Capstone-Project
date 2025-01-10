import requests
import pandas as pd

# Your EIA API key
API_KEY = "hCjY4AAYMqVZvYwPppQ1XpeWhSRBgbFgB1ppzT5s"
BASE_URL = "https://api.eia.gov/v2"

# Example: Querying residential electricity consumption data
offset = 0
length = 5000
url = "https://api.eia.gov/v2/electricity/retail-sales/data/"
params = {
    "api_key": API_KEY,
    "frequency": "monthly",
    "data[]": ["customers", "price", "revenue", "sales"],
    "facets[sectorid][]": ["ALL", "COM", "IND", "OTH", "RES", "TRA"],
    "offset": 0,
    "length": 1
}

response = requests.get(url, params=params)
data = response.json()
total_records = int(data["response"]["total"])
print(type(offset))
print(type(total_records))

#print(total_records)
#offset = offset + length
#print(data)
all_data = []
while offset <= total_records:
    params["offset"] = offset
    params['length'] = length
    response = requests.get(url, params=params)
    data_chunk = response.json()["response"]["data"]
    all_data.extend(data_chunk)
    print(offset,length,total_records)
    offset = offset + length

# Convert to DataFrame
df = pd.DataFrame(all_data)
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
