# Udacity Capstone Project: Energy Consumption Analysis

## Project Overview

This project focuses on analyzing energy consumption across various sectors using data from the U.S. Energy Information Administration (EIA). The goal is to explore trends, perform temporal analyses, and develop predictive models to understand energy usage patterns better.

## Repository Structure

- **Data_fetcher.py**: Script to fetch and preprocess energy data from the EIA API.
- **EIA_data_Resi.py**: Module dedicated to handling residential energy data.
- **Energy_exploration.py**: Script for exploratory data analysis on the energy datasets.
- **Energy_exploration_prediction.ipynb**: Jupyter Notebook containing predictive modeling and analysis.
- **Temporal_Analysis.py**: Script to perform temporal analysis on energy consumption data.
- **app.py**: Flask application to visualize and interact with the energy data.
- **requirements.txt**: List of Python dependencies required to run the project.
- **data/**: Directory containing various CSV files with energy data for different sectors.

## Data Sources

The primary data source for this project is the [U.S. Energy Information Administration (EIA)](https://www.eia.gov/) API. The dataset includes energy consumption statistics across residential, commercial, industrial, transportation, and other sectors.

## Installation and Usage

1. **Clone the Repository**:
   git clone https://github.com/Prasanna23/Udacity-Capstone-Project.git
#### Navigate to the Project Directory:
cd Udacity-Capstone-Project
#### Install Dependencies:
pip install -r requirements.txt
#### Fetch and Prepare Data:

Ensure you have an API key from the EIA.
Update the Data_fetcher.py script with your API key.
Run the script to download and preprocess the data:
python Data_fetcher.py
#### Perform Exploratory Data Analysis:

Use the Energy_exploration.py script or open the Energy_exploration_prediction.ipynb notebook in Jupyter to explore the data and build predictive models.
#### Run the Streamlit Application:

Start the web application to visualize the data:
python streamlit run app.py
Open your browser and navigate to http://127.0.0.1:5000/ to interact with the application.

Alternatively, the webapp is deployed and can be accessed using https://energy-metrics-explorer.streamlit.app/ website. 
Web app has the ability to visualize different metrics with date filters, State and Sector filters.
It also has the functionality to show predictions for future dates. 

### Project Structure
The project is organized as follows:

Udacity-Capstone-Project/
├── data/
│   ├── all_energy_data.csv
│   ├── com_energy_data.csv
│   ├── ind_energy_data.csv
│   ├── res_energy_data.csv
│   ├── tra_energy_data.csv
│   └── oth_energy_data.csv
├── Data_fetcher.py
├── EIA_data_Resi.py
├── Energy_exploration.py
├── Energy_exploration_prediction.ipynb
├── Temporal_Analysis.py
├── app.py
├── requirements.txt
└── README.md
### Acknowledgments
This project is part of the Udacity Data Science Nanodegree program. Special thanks to the U.S. Energy Information Administration for providing the data and to the Udacity team for their guidance.