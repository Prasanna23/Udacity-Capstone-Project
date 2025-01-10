import streamlit as st
import plotly.express as px
import pandas as pd

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

if __name__ == "__main__":
    st.set_page_config(
        page_title="Energy Customer Trends",
        page_icon="⚡",
        layout="wide"
    )
    create_dashboard()