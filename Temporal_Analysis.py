import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import requests

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
# Set plotly to display in notebook if you're using Jupyter
pio.renderers.default = "notebook"

def temporal_analysis_plots(df, selected_metric):
    """
    Perform temporal analysis and display plots directly
    
    Parameters:
    df (pandas.DataFrame): DataFrame with 'period' column and metric columns
    selected_metric (str): Column name to analyze ('customers', 'price', 'revenue', 'sales')
    """
    # Ensure period is datetime
    df['period'] = pd.to_datetime(df['period'])
    
    # Add derived time features
    df['year'] = df['period'].dt.year
    df['month'] = df['period'].dt.month
    df['quarter'] = df['period'].dt.quarter
    
    metric_options = {
        'customers': 'Number of Customers',
        'price': 'Price (cents/kWh)',
        'revenue': 'Revenue (thousand dollars)',
        'sales': 'Sales (MWh)'
    }
    
    # 1. Year-over-Year Growth
    yearly_data = df.groupby('year')[selected_metric].mean().reset_index()
    yearly_data['YoY_Growth'] = yearly_data[selected_metric].pct_change() * 100
    
    fig_yoy = go.Figure()
    fig_yoy.add_trace(
        go.Bar(x=yearly_data['year'], y=yearly_data['YoY_Growth'],
               name='YoY Growth')
    )
    fig_yoy.add_trace(
        go.Scatter(x=yearly_data['year'], y=yearly_data['YoY_Growth'],
                  name='Trend', mode='lines')
    )
    fig_yoy.update_layout(
        title=f'Year-over-Year Growth in {metric_options[selected_metric]}',
        xaxis_title='Year',
        yaxis_title='Growth Rate (%)'
    )
    fig_yoy.show()
    
    # 2. Seasonal Patterns
    monthly_avg = df.groupby('month')[selected_metric].mean().reset_index()
    fig_seasonal = px.line(monthly_avg, x='month', y=selected_metric,
                          title=f'Average {metric_options[selected_metric]} by Month')
    fig_seasonal.update_xaxes(tickmode='linear')
    fig_seasonal.show()
    
    # 3. Quarterly and Monthly Distributions
    fig_quarterly = px.box(
        df.groupby(['year', 'quarter'])[selected_metric].mean().reset_index(),
        x='quarter', 
        y=selected_metric,
        title=f'Quarterly Distribution of {metric_options[selected_metric]}'
    )
    fig_quarterly.show()
    
    fig_monthly_dist = px.box(
        df, 
        x='month', 
        y=selected_metric,
        title=f'Monthly Distribution of {metric_options[selected_metric]}'
    )
    fig_monthly_dist.show()
    
    # 4. Moving Averages Analysis
    df_sorted = df.sort_values('period')
    ma_3 = df_sorted[selected_metric].rolling(window=3).mean()
    ma_6 = df_sorted[selected_metric].rolling(window=6).mean()
    ma_12 = df_sorted[selected_metric].rolling(window=12).mean()
    
    fig_ma = go.Figure()
    fig_ma.add_trace(go.Scatter(x=df_sorted['period'], y=df_sorted[selected_metric],
                               name='Original', mode='lines'))
    fig_ma.add_trace(go.Scatter(x=df_sorted['period'], y=ma_3,
                               name='3-Month MA', line=dict(dash='dash')))
    fig_ma.add_trace(go.Scatter(x=df_sorted['period'], y=ma_6,
                               name='6-Month MA', line=dict(dash='dot')))
    fig_ma.add_trace(go.Scatter(x=df_sorted['period'], y=ma_12,
                               name='12-Month MA', line=dict(dash='longdash')))
    
    fig_ma.update_layout(title='Moving Averages Analysis')
    fig_ma.show()
    
    # 5. Print Summary Statistics
    yearly_stats = df.groupby('year')[selected_metric].agg([
        'mean', 'std', 'min', 'max'
    ]).round(2)
    
    print("\nYearly Statistics:")
    print(yearly_stats)
    
    # Print Key Insights
    total_growth = ((yearly_data[selected_metric].iloc[-1] / 
                    yearly_data[selected_metric].iloc[0] - 1) * 100)
    
    peak_month = monthly_avg.loc[monthly_avg[selected_metric].idxmax(), 'month']
    trough_month = monthly_avg.loc[monthly_avg[selected_metric].idxmin(), 'month']
    
    print("\nKey Insights:")
    print(f"Total Growth Rate: {total_growth:.1f}%")
    print(f"Last Year Growth: {yearly_data['YoY_Growth'].iloc[-1]:.1f}%")
    print(f"Peak Month: Month {peak_month} (Value: {monthly_avg[selected_metric].max():.2f})")
    print(f"Trough Month: Month {trough_month} (Value: {monthly_avg[selected_metric].min():.2f})")

# Example usage:
"""
# Assuming your DataFrame is called 'df'
temporal_analysis_plots(df, 'sales')
"""


def temporal_analysis(df):
    st.header("Temporal Analysis")
    
    # Ensure period is datetime
    df['period'] = pd.to_datetime(df['period'])
    
    # Add derived time features
    df['year'] = df['period'].dt.year
    df['month'] = df['period'].dt.month
    df['quarter'] = df['period'].dt.quarter
    
    # Metric selection
    metric_options = {
        'customers': 'Number of Customers',
        'price': 'Price (cents/kWh)',
        'revenue': 'Revenue (thousand dollars)',
        'sales': 'Sales (MWh)'
    }
    
    selected_metric = st.selectbox(
        'Select Metric for Analysis',
        options=list(metric_options.keys()),
        format_func=lambda x: metric_options[x]
    )

    # 1. Year-over-Year Growth
    st.subheader("Year-over-Year Growth")
    yearly_data = df.groupby('year')[selected_metric].mean().reset_index()
    yearly_data['YoY_Growth'] = yearly_data[selected_metric].pct_change() * 100
    
    fig_yoy = go.Figure()
    fig_yoy.add_trace(
        go.Bar(x=yearly_data['year'], y=yearly_data['YoY_Growth'],
               name='YoY Growth')
    )
    fig_yoy.add_trace(
        go.Scatter(x=yearly_data['year'], y=yearly_data['YoY_Growth'],
                  name='Trend', mode='lines')
    )
    fig_yoy.update_layout(
        title=f'Year-over-Year Growth in {metric_options[selected_metric]}',
        xaxis_title='Year',
        yaxis_title='Growth Rate (%)'
    )
    st.plotly_chart(fig_yoy, use_container_width=True)

    # 2. Seasonal Patterns
    st.subheader("Seasonal Patterns")
    monthly_avg = df.groupby('month')[selected_metric].mean().reset_index()
    
    fig_seasonal = px.line(monthly_avg, x='month', y=selected_metric,
                          title=f'Average {metric_options[selected_metric]} by Month')
    fig_seasonal.update_xaxes(tickmode='linear')
    st.plotly_chart(fig_seasonal, use_container_width=True)

    # 3. Trend and Seasonality Decomposition
    st.subheader("Trend and Seasonality Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Quarterly trends
        quarterly_avg = df.groupby(['year', 'quarter'])[selected_metric].mean().reset_index()
        fig_quarterly = px.box(quarterly_avg, x='quarter', y=selected_metric,
                             title=f'Quarterly Distribution of {metric_options[selected_metric]}')
        st.plotly_chart(fig_quarterly)

    with col2:
        # Monthly distribution
        fig_monthly_dist = px.box(df, x='month', y=selected_metric,
                                title=f'Monthly Distribution of {metric_options[selected_metric]}')
        st.plotly_chart(fig_monthly_dist)

    # 4. Time Series Decomposition
    st.subheader("Moving Averages Analysis")
    
    # Calculate moving averages
    df_sorted = df.sort_values('period')
    ma_3 = df_sorted[selected_metric].rolling(window=3).mean()
    ma_6 = df_sorted[selected_metric].rolling(window=6).mean()
    ma_12 = df_sorted[selected_metric].rolling(window=12).mean()
    
    fig_ma = go.Figure()
    fig_ma.add_trace(go.Scatter(x=df_sorted['period'], y=df_sorted[selected_metric],
                               name='Original', mode='lines'))
    fig_ma.add_trace(go.Scatter(x=df_sorted['period'], y=ma_3,
                               name='3-Month MA', line=dict(dash='dash')))
    fig_ma.add_trace(go.Scatter(x=df_sorted['period'], y=ma_6,
                               name='6-Month MA', line=dict(dash='dot')))
    fig_ma.add_trace(go.Scatter(x=df_sorted['period'], y=ma_12,
                               name='12-Month MA', line=dict(dash='longdash')))
    
    fig_ma.update_layout(title='Moving Averages Analysis')
    st.plotly_chart(fig_ma, use_container_width=True)

    # 5. Summary Statistics
    st.subheader("Temporal Summary Statistics")
    
    # Yearly summary
    yearly_stats = df.groupby('year')[selected_metric].agg([
        'mean', 'std', 'min', 'max'
    ]).round(2)
    
    st.write("Yearly Statistics:")
    st.dataframe(yearly_stats)

    # Key insights
    st.subheader("Key Temporal Insights")
    
    # Calculate insights
    total_growth = ((yearly_data[selected_metric].iloc[-1] / 
                    yearly_data[selected_metric].iloc[0] - 1) * 100)
    
    peak_month = monthly_avg.loc[monthly_avg[selected_metric].idxmax(), 'month']
    trough_month = monthly_avg.loc[monthly_avg[selected_metric].idxmin(), 'month']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Growth Rate", 
                 f"{total_growth:.1f}%",
                 f"{yearly_data['YoY_Growth'].iloc[-1]:.1f}% (Last Year)")
    
    with col2:
        st.metric("Peak Month", 
                 f"Month {peak_month}",
                 f"Value: {monthly_avg[selected_metric].max():.2f}")
    
    with col3:
        st.metric("Trough Month",
                 f"Month {trough_month}",
                 f"Value: {monthly_avg[selected_metric].min():.2f}")
        

    return None


# Your EIA API key
API_KEY = "hCjY4AAYMqVZvYwPppQ1XpeWhSRBgbFgB1ppzT5s"
BASE_URL = "https://api.eia.gov/v2"

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

df = pd.DataFrame(all_data)
df.drop(['customers-units','price-units','revenue-units','sales-units'], axis=1, inplace=True)

df['period'] = pd.to_datetime(df['period'], errors='coerce')
df['customers'] = pd.to_numeric(df['customers'], errors='coerce')
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
df['sales'] = pd.to_numeric(df['sales'], errors='coerce')
### converting category columns to categories
df['stateid'] = df['stateid'].astype('category')
df['stateDescription'] = df['stateDescription'].astype('category')
df['sectorid'] = df['sectorid'].astype('category')
df['sectorName'] = df['sectorName'].astype('category')

Overall_df = df[df['stateid'] == 'US']
# Convert period to datetime if not already
Overall_df['period'] = pd.to_datetime(Overall_df['period'])

# Create year and month columns
Overall_df['year'] = Overall_df['period'].dt.year
Overall_df['month'] = Overall_df['period'].dt.month

# Sort by date to ensure proper line connection
df_sorted = Overall_df.sort_values('period')
df_sorted.dropna(inplace=True)
temporal_analysis_plots(df)
#temporal_analysis(df)

# Add this function to your main dashboard
# In your main.py, you can call it like:
# temporal_analysis(df)