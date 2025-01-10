import pandas as pd
import requests
import time
from datetime import datetime, timedelta

class EIADataFetcher:
    def __init__(self, api_key):
        """
        Initialize the EIA data fetcher
        api_key: Your EIA API key
        """
        self.api_key = api_key
        self.base_url = "https://api.eia.gov/v2"
        
    def fetch_data_in_chunks(self, route, params=None, offset_size=5000, max_retries=3, sleep_time=1):
        """
        Fetch all data from EIA API using pagination
        
        Parameters:
        route: API endpoint route (e.g., '/electricity/retail-sales')
        params: Additional query parameters
        offset_size: Number of records per request
        max_retries: Maximum number of retry attempts for failed requests
        sleep_time: Time to wait between requests in seconds
        """
        all_data = []
        offset = 0
        total_records = None
        
        # Initialize params dictionary if None
        if params is None:
            params = {}
        
        while True:
            # Add pagination parameters
            current_params = {
                "frequency": "monthly",
                "data[]": ["customers", "price", "revenue", "sales"],
                "facets[sectorid][]": ["ALL", "COM", "IND", "OTH", "RES", "TRA"],
                'offset': offset,
                'length': offset_size,
                'api_key': self.api_key
            }
            
            # Make request with retries
            for attempt in range(max_retries):
                try:
                    response = requests.get(
                        f"{self.base_url}{route}",
                        params=current_params
                    )
                    response.raise_for_status()
                    data = response.json()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        print(f"Failed after {max_retries} attempts: {e}")
                        return pd.DataFrame(all_data)
                    time.sleep(sleep_time * (attempt + 1))
            
            # Get total number of records if first request
            if total_records is None:
                total_records = data.get('response').get('total')
                print(f"Total records available: {total_records}")
            
            # Extract data
            current_data = data.get('response').get('data', [])
            all_data.extend(current_data)
            
            # Print progress
            print(f"Fetched {len(all_data)} of {total_records} records")
            
            # Check if we've got all data
            if len(current_data) < offset_size or len(all_data) >= total_records:
                break
                
            # Increment offset for next batch
            offset += offset_size
            
            # Sleep to avoid hitting rate limits
            time.sleep(sleep_time)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_data)
        print(f"Successfully fetched {len(df)} records")
        return df

    def fetch_electricity_data(self, start_date=None, end_date=None, state=None, sector=None):
        """
        Fetch electricity retail sales data with specific filters
        """
        params = {}
        
        # Add date filters
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
            
        # Add state filter
        if state:
            params['state'] = state.upper()
            
        # Add sector filter
        if sector:
            params['sector'] = sector.upper()
        
        return self.fetch_data_in_chunks(
            '/electricity/retail-sales',
            params=params
        )

    def fetch_capacity_data(self, start_date=None, end_date=None, state=None, technology=None):
        """
        Fetch electricity capacity data with specific filters
        """
        params = {}
        
        # Add date filters
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
            
        # Add state filter
        if state:
            params['state'] = state.upper()
            
        # Add technology filter
        if technology:
            params['technology'] = technology
        
        return self.fetch_data_in_chunks(
            '/electricity/operating-generator-capacity',
            params=params
        )

# Example usage
def fetch_complete_dataset(api_key):
    """
    Fetch both retail sales and capacity data
    """
    api_key = "hCjY4AAYMqVZvYwPppQ1XpeWhSRBgbFgB1ppzT5s"
    fetcher = EIADataFetcher(api_key)
    
    # Set date range
    end_date = datetime.now().strftime('%Y-%m')
    start_date = '2001-01'  # Or whatever start date you need
    
    print("Fetching retail sales data...")
    retail_sales = fetcher.fetch_electricity_data(
        start_date=start_date,
        end_date=end_date
    )
    
    print("\nFetching capacity data...")
    capacity = fetcher.fetch_capacity_data(
        start_date=start_date,
        end_date=end_date
    )
    
    return retail_sales, capacity
retail_sales,capacity = fetch_complete_dataset(api_key="hCjY4AAYMqVZvYwPppQ1XpeWhSRBgbFgB1ppzT5s")
print(retail_sales)
print(capacity)