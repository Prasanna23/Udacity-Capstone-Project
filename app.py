import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
from datetime import datetime, timedelta
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import LinearRegression



def load_data():
    df=pd.read_csv('energy_data_cleaned.csv')
    return df  # Using your existing dataframe

def make_future_dates(last_date, periods):
    """Generate future dates for predictions"""
    date_list = []
    current_date = last_date
    for _ in range(periods):
        current_date = current_date + pd.DateOffset(months=1)
        date_list.append(current_date)
    return pd.DatetimeIndex(date_list)

def predict_metric(data, metric, method, periods=12):
    """Generate predictions using selected method"""
    y = data[metric].values
    
    if method == 'Holt-Winters':
        try:
            model = ExponentialSmoothing(y, seasonal_periods=12, trend='add', seasonal='add')
            fitted_model = model.fit()
            forecast = fitted_model.forecast(periods)
        except:
            # Fallback to simpler method if Holt-Winters fails
            forecast = np.repeat(y[-1], periods)
    
    elif method == 'ARIMA':
        try:
            model = ARIMA(y, order=(1,1,1))
            fitted_model = model.fit()
            forecast = fitted_model.forecast(periods)
        except:
            forecast = np.repeat(y[-1], periods)
    
    elif method == 'Linear':
        X = np.arange(len(y)).reshape(-1, 1)
        model = LinearRegression()
        model.fit(X, y)
        X_future = np.arange(len(y), len(y) + periods).reshape(-1, 1)
        forecast = model.predict(X_future)
    
    else:  # Simple Moving Average
        window = min(12, len(y))
        last_mean = y[-window:].mean()
        forecast = np.repeat(last_mean, periods)
    
    return forecast

def add_predictions_section():
    st.sidebar.header('Predictions')
    prediction_enabled = st.sidebar.checkbox('Enable Predictions')
    
    if prediction_enabled:
        pred_method = st.sidebar.selectbox(
            'Prediction Method',
            ['Holt-Winters', 'ARIMA', 'Linear', 'Moving Average']
        )
        
        pred_periods = st.sidebar.slider(
            'Forecast Periods (Months)',
            min_value=1,
            max_value=24,
            value=12
        )
        
        return pred_method, pred_periods
    return None, None

def create_dashboard():
    st.title('Energy Customer Trends Dashboard')
    
    # Load data
    df = load_data()
    
    df['period'] = pd.to_datetime(df['period'])
    
    # Sidebar filters
    st.sidebar.header('Data Filters')
    
    # Date range selector
    min_date = df['period'].min()
    max_date = df['period'].max()
    date_range = st.sidebar.date_input(
        'Select Date Range',
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Get prediction parameters
    pred_method, pred_periods = add_predictions_section()

    # Sidebar for filters
    st.sidebar.header('Filter Data')
    
    # Multi-select for states
    selected_states = st.sidebar.multiselect(
        'Select States',
        options=df['stateid'].unique(),
        default=['US']
    )
    
    # Multi-select for sectors
    selected_sectors = st.sidebar.multiselect(
        'Select Sectors',
        options=df['sectorid'].unique(),
        default=['RES']
    )
    
    metric_options = {
        'customers': 'Number of Customers',
        'price': 'Price (cents/kWh)',
        'revenue': 'Revenue (thousand dollars)',
        'sales': 'Sales (MWh)'
    }
    
    # Main content
    selected_metric = st.selectbox(
        'Select Metric to Analyze',
        options=list(metric_options.keys()),
        format_func=lambda x: metric_options[x]
    )

    #selected_metric = st.sidebar.selectbox(
    #    "Select Metric to Display",
    #    options=["customers", "sales","revenue"],  # Assuming "sales" exists in the dataset
    #    index=0
    #)

    # Filter data based on selection
    filtered_df = df[
        (df['stateid'].isin(selected_states)) & 
        (df['sectorid'].isin(selected_sectors)) &
        (df['period'].dt.date >= date_range[0]) &
        (df['period'].dt.date <= date_range[1])
    ].sort_values('period')
    
    # Create the plot
    fig = px.line(filtered_df, 
                  x='period', 
                  y=selected_metric,
                  color='stateid',
                  line_dash='sectorid',
                  labels={'period': 'Year', 
                          selected_metric: f'Number of {selected_metric.capitalize()}',
                         #'customers': 'Number of Customers',
                         'stateid': 'State',
                         'sectorid': 'Sector'})
    
    if pred_method:
        future_dates = make_future_dates(filtered_df['period'].max(), pred_periods)

        st.subheader(f'{metric_options[selected_metric]} Analysis and Predictions')
    
        fig1 = go.Figure()
    
    # Add historical data
        for state in selected_states:
                for sector in selected_sectors:
                    temp_df = filtered_df[
                        (filtered_df['stateid'] == state) & 
                        (filtered_df['sectorid'] == sector)
                    ]
                    
                    # Generate predictions
                    forecast = predict_metric(
                        temp_df,
                        selected_metric,
                        pred_method,
                        pred_periods
                    )
                    
                    # Add prediction trace
                    fig1.add_trace(
                        go.Scatter(
                            x=future_dates,
                            y=forecast,
                            name=f"{state}-{sector} (Predicted)",
                            line=dict(dash='dash')
                        )
                    )
                    
                    # Add confidence interval (simple implementation)
                    std_dev = temp_df[selected_metric].std()
                    fig1.add_trace(
                        go.Scatter(
                            x=future_dates,
                            y=forecast + 2*std_dev,
                            fill=None,
                            line=dict(color='rgba(0,0,0,0)'),
                            showlegend=False
                        )
                    )
                    fig1.add_trace(
                        go.Scatter(
                            x=future_dates,
                            y=forecast - 2*std_dev,
                            fill='tonexty',
                            fillcolor='rgba(0,100,255,0.2)',
                            line=dict(color='rgba(0,0,0,0)'),
                            name=f"{state}-{sector} (95% CI)",
                        )
                    )
    
                fig1.update_layout(
                    title=f"{metric_options[selected_metric]} - Historical Data and Predictions",
                    xaxis_title="Date",
                    yaxis_title=metric_options[selected_metric],
                    hovermode='x unified',
                    height=600
                )
    
                st.plotly_chart(fig1, use_container_width=True)
    # Update layout
    fig.update_layout(
        title=f'{selected_metric.capitalize()} Trends by State and Sector',  # **NEW CHANGE: Dynamic title**
        #title='Customer Trends by State and Sector',
        xaxis_title="Year",
        yaxis_title="Number of Customers",
        hovermode='x unified'
    )
    
    fig.update_xaxes(dtick='M6')
    
    # Display the plot
    st.plotly_chart(fig, use_container_width=True)
    
    # Add summary statistics
    st.subheader('Summary Statistics')
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            f"Total {selected_metric.capitalize()}",  # **NEW CHANGE: Dynamic metric**
            f"{filtered_df['customers'].iloc[-1]:,.0f}",
            f"{filtered_df['customers'].iloc[-1] - filtered_df['customers'].iloc[-2]:,.0f}"
        )
    
    with col2:
        st.metric(
            f"Average {selected_metric.capitalize()}",  # **NEW CHANGE: Dynamic metric**
            f"{filtered_df['customers'].mean():,.0f}"
        )
    
    # Show raw data if desired
    if st.checkbox('Show Raw Data'):
        st.write(filtered_df)

    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False)

    # Download button
    csv_data = convert_df_to_csv(filtered_df)
    st.download_button(
        label="Download Data",
        data=csv_data,
        file_name="filtered_data.csv",
        mime="text/csv"
    )


if __name__ == "__main__":
    st.set_page_config(
        page_title="Energy Customer Trends",
        page_icon="⚡",
        layout="wide"
    )
    create_dashboard()