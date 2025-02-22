import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def load_data():
    df=pd.read_csv('energy_data_cleaned.csv')
    return df  # Using your existing dataframe

def create_dashboard():
    st.title('Energy Customer Trends Dashboard')
    
    # Load data
    df = load_data()
    
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
    
    # Filter data based on selection
    filtered_df = df[
        (df['stateid'].isin(selected_states)) & 
        (df['sectorid'].isin(selected_sectors))
    ].sort_values('period')
    
    # Create the plot
    fig = px.line(filtered_df, 
                  x='period', 
                  y='customers',
                  color='stateid',
                  line_dash='sectorid',
                  labels={'period': 'Year', 
                         'customers': 'Number of Customers',
                         'stateid': 'State',
                         'sectorid': 'Sector'})
    
    # Update layout
    fig.update_layout(
        title='Customer Trends by State and Sector',
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
            "Total Customers", 
            f"{filtered_df['customers'].iloc[-1]:,.0f}",
            f"{filtered_df['customers'].iloc[-1] - filtered_df['customers'].iloc[-2]:,.0f}"
        )
    
    with col2:
        st.metric(
            "Average Customers", 
            f"{filtered_df['customers'].mean():,.0f}"
        )
    
    # Show raw data if desired
    if st.checkbox('Show Raw Data'):
        st.write(filtered_df)

    @st.cache
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

    # Model for Prediction (Linear Regression Example)
    st.subheader('Future Predictions')
    if st.button('Generate Predictions'):
        # Preparing data for prediction
        df_for_prediction = filtered_df[['period', 'customers']].copy()

        # Convert 'period' to datetime format for model
        df_for_prediction['period'] = pd.to_datetime(df_for_prediction['period'])
        df_for_prediction['period'] = df_for_prediction['period'].apply(lambda x: x.month + 12*x.year)

        # Create features (X) and target (y)
        X = df_for_prediction[['period']]  # Feature: month/year
        y = df_for_prediction['customers']  # Target: number of customers

        # Train a Linear Regression Model
        model = LinearRegression()
        model.fit(X, y)

        # Predict for the next 12 months
        future_periods = np.arange(X['period'].max() + 1, X['period'].max() + 13).reshape(-1, 1)
        future_predictions = model.predict(future_periods)

        # Create future periods (dates)
        future_dates = [datetime(2025, 1, 1) + timedelta(days=30 * (x - X['period'].max())) for x in future_periods.flatten()]

        # Display predictions
        future_df = pd.DataFrame({
            'period': future_dates,
            'predicted_customers': future_predictions
        })

        # Plot predictions alongside historical data
        predicted_fig = px.line(filtered_df, 
                                x='period', 
                                y='customers',
                                color='stateid',
                                line_dash='sectorid',
                                labels={'period': 'Year', 
                                       'customers': 'Number of Customers',
                                       'stateid': 'State',
                                       'sectorid': 'Sector'})
        
        predicted_fig.add_scatter(x=future_df['period'], 
                                  y=future_df['predicted_customers'], 
                                  mode='lines', 
                                  name='Predicted', 
                                  line=dict(color='red', dash='dot'))

        predicted_fig.update_layout(
            title='Customer Trends and Predictions',
            xaxis_title="Year",
            yaxis_title="Number of Customers",
            hovermode='x unified'
        )

        st.plotly_chart(predicted_fig, use_container_width=True)



if __name__ == "__main__":
    st.set_page_config(
        page_title="Energy Customer Trends",
        page_icon="⚡",
        layout="wide"
    )
    create_dashboard()