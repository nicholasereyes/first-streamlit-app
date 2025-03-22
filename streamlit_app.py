import streamlit as st
import pandas as pd
# import matplotlib.pyplot as plt
from pathlib import Path
from census import Census

# Function to pull median household income data from the Census API
def get_median_household_income(key):
    c = Census(key)
    dataset = c.acs5

    # Specify the variable for median household income
    variables = ('NAME', 'B19013_001E')
    labels = ('NAME', 'Median Household Income')

    # Choose geographic aggregation level (states)
    geo = 'state:*'
    
    # Run query
    r = dataset.get(variables, {'for': geo})
    
    # Convert to DataFrame and rename columns
    df = pd.DataFrame(r).rename(columns={v: l for v, l in zip(variables, labels)})
    
    return df

# Function to load and process the Bachelorette data
@st.cache_data
def get_bach_data():
    # Path to the dataset
    DATA_FILENAME = Path(__file__).parent / 'data/bachelorette-contestants.csv'
    
    # Read the dataset
    raw_bach_df = pd.read_csv(DATA_FILENAME)
    
    # Convert relevant columns to numeric
    raw_bach_df['Age'] = pd.to_numeric(raw_bach_df['Age'])
    raw_bach_df['ElimWeek'] = pd.to_numeric(raw_bach_df['ElimWeek'])
    raw_bach_df['Season'] = pd.to_numeric(raw_bach_df['Season'])
    
    # Split 'Hometown' into 'City' and 'State'
    raw_bach_df[['City', 'State']] = raw_bach_df['Hometown'].str.split(', ', expand=True)
    
    return raw_bach_df

# Function to merge Bachelorette data with median household income data
def merge_bach_with_income(bach_df, income_df):
    # Merge the dataframes on the 'State' column
    merged_df = pd.merge(bach_df, income_df, left_on='State', right_on='NAME', how='left')
    return merged_df

# Load API key (replace 'API_KEY' with your actual key)
key = "c8636400c789064fae9c57f141ea33b27bd1c0fa"

# Get median household income data
income_df = get_median_household_income(key)

# Get the Bachelorette contestants data
raw_bach_df = get_bach_data()

# Merge Bachelorette data with median household income data
merged_df = merge_bach_with_income(raw_bach_df, income_df)

# Streamlit UI elements
st.title("Bachelorette Analysis")

# Display the Bachelorette dataset table
st.write("### Bachelorette Contestants Data with Median Household Income")
# Create the scatter plot for Median Household Income vs Elimination Week
st.table(merged_df)

# Display the filtered DataFrame (for confirmation)
st.write("### Contestants Eliminated in Week 1")
st.table(merged_df[merged_df['ElimWeek'] == 1])