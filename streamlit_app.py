import streamlit as st
import pandas as pd
import altair as alt
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

# Step 1: Count total contestants per state
total_state_counts = raw_bach_df['State'].value_counts().reset_index()
total_state_counts.columns = ['State', 'TotalCount']

# Step 2: Create a histogram by State for total contestants
histogram = alt.Chart(total_state_counts).mark_bar().encode(
    x=alt.X('State:N', sort='-y', title='State'),
    y=alt.Y('TotalCount:Q', title='Total Contestants'),
    tooltip=['State', 'TotalCount']
).properties(
    title="Distribution of Contestants by State",
    width=700,
    height=400
)

# Display the histogram in Streamlit
st.write("### Distribution of Contestants by State")
st.altair_chart(histogram)

# Step 1: Count total contestants per state
total_state_counts = raw_bach_df['State'].value_counts().reset_index()
total_state_counts.columns = ['State', 'TotalCount']

# Step 2: Count Week 1 eliminations per state
elim_week1_df = merged_df[merged_df['ElimWeek'] == 1]
week1_state_counts = elim_week1_df['State'].value_counts().reset_index()
week1_state_counts.columns = ['State', 'Week1Count']

# Step 3: Merge the total and Week 1 elimination counts on 'State'
state_counts_df = pd.merge(total_state_counts, week1_state_counts, on='State', how='left')

# Step 4: Filter out rows where 'State' or 'Week1Count' is null
state_counts_df = state_counts_df.dropna(subset=['State', 'Week1Count'])

# Step 5: Calculate remaining contestants per state
state_counts_df['RemainingCount'] = state_counts_df['TotalCount'] - state_counts_df['Week1Count']

# Step 6: Calculate percentage of Week 1 eliminations and remaining contestants
state_counts_df['PercentWeek1'] = (state_counts_df['Week1Count'] / state_counts_df['TotalCount']) * 100
state_counts_df['PercentRemaining'] = (state_counts_df['RemainingCount'] / state_counts_df['TotalCount']) * 100

# Step 7: Reshape the data to make it suitable for stacked bar chart (melt the data)
melted_df = state_counts_df.melt(id_vars='State', value_vars=['PercentWeek1', 'PercentRemaining'],
                                  var_name='Status', value_name='Percent')

# Step 8: Create the Altair stacked bar chart
base = alt.Chart(melted_df).mark_bar().encode(
    x=alt.X('State:N', sort=alt.EncodingSortField(field='PercentWeek1', order='descending'), title='State'),
    y=alt.Y('Percent:Q', title='% of Total Contestants'),
    color='Status:N',
    tooltip=['State', 'Status', 'Percent']
).properties(
    title="Percent of Total Contestants Eliminated in Week 1 vs Remaining by State",
    width=700,
    height=400
)

# Display the chart in Streamlit
st.write("### Percent of Total Contestants Eliminated in Week 1 vs Remaining by State")
st.altair_chart(base)

import pandas as pd
import numpy as np
import altair as alt

# Step 1: Calculate the median and standard deviation of age
median_age = merged_df['Age'].median()
std_dev_age = merged_df['Age'].std()

# Step 2: Define the age buckets based on deviations from the median
# Define the bins based on the median and standard deviations
bins = [
    float('-inf'), median_age - std_dev_age,  # Below median - 1 SD
    median_age - std_dev_age, median_age,     # Below median
    median_age, median_age + std_dev_age,     # Median ± 1 SD
    median_age + std_dev_age, float('inf')    # Above median + 1 SD
]
labels = ['Below Median - 1 SD', 'Below Median', 'Median ± 1 SD', 'Above Median', 'Above Median + 1 SD']

# Step 1: Calculate the median and standard deviation of age
median_age = merged_df['Age'].median()
std_dev_age = merged_df['Age'].std()

# Step 2: Define the age buckets based on deviations from the median
# Define the bins based on the median and standard deviations, making sure edges are unique
bins = [
    float('-inf'), median_age - std_dev_age - 0.1,  # Below median - 1 SD
    median_age - std_dev_age, median_age,           # Below median
    median_age, median_age + std_dev_age,           # Median ± 1 SD
    median_age + std_dev_age, float('inf')          # Above median + 1 SD
]
labels = ['Below Median - 1 SD', 'Below Median', 'Median ± 1 SD', 'Above Median', 'Above Median + 1 SD']

# Manually define the age buckets based on the data provided
bins = [23, 26, 29, 34, 39, 42]  # Manually defined bins
labels = ['Below 26', '26-29 (Median)', '30-34', '35-39', '40+']

# Create the 'AgeBucket' column by applying pd.cut() based on the manually defined bins
merged_df['AgeBucket'] = pd.cut(merged_df['Age'], bins=bins, labels=labels, right=False)

# Step 3: Count total contestants per age bucket
total_age_counts = merged_df['AgeBucket'].value_counts().reset_index()
total_age_counts.columns = ['AgeBucket', 'TotalCount']

# Step 4: Count Week 1 eliminations per age bucket
elim_week1_age_df = merged_df[merged_df['ElimWeek'] == 1]
week1_age_counts = elim_week1_age_df['AgeBucket'].value_counts().reset_index()
week1_age_counts.columns = ['AgeBucket', 'Week1Count']

# Step 5: Merge the total and Week 1 elimination counts on 'AgeBucket'
age_counts_df = pd.merge(total_age_counts, week1_age_counts, on='AgeBucket', how='left')

# Step 6: Filter out rows where 'AgeBucket' or 'Week1Count' is null
age_counts_df = age_counts_df.dropna(subset=['AgeBucket', 'Week1Count'])

# Step 7: Calculate remaining contestants per age bucket
age_counts_df['RemainingCount'] = age_counts_df['TotalCount'] - age_counts_df['Week1Count']

# Step 8: Calculate percentage of Week 1 eliminations and remaining contestants
age_counts_df['PercentWeek1'] = (age_counts_df['Week1Count'] / age_counts_df['TotalCount']) * 100
age_counts_df['PercentRemaining'] = (age_counts_df['RemainingCount'] / age_counts_df['TotalCount']) * 100

# Step 9: Sort the DataFrame by PercentWeek1 in descending order
age_counts_df = age_counts_df.sort_values(by='PercentWeek1', ascending=False)

# Step 10: Reshape the data to make it suitable for stacked bar chart (melt the data)
melted_age_df = age_counts_df.melt(id_vars='AgeBucket', value_vars=['PercentWeek1', 'PercentRemaining'],
                                    var_name='Status', value_name='Percent')

# Step 11: Ensure 'Percent' column is numeric to prevent any sorting issues
melted_age_df['Percent'] = pd.to_numeric(melted_age_df['Percent'], errors='coerce')

# Step 12: Create the Altair stacked bar chart for Age Buckets
base_age = alt.Chart(melted_age_df).mark_bar().encode(
    x=alt.X('AgeBucket:N', title='Age Bucket'),
    y=alt.Y('Percent:Q', title='% of Total Contestants'),
    color='Status:N',
    tooltip=['AgeBucket', 'Status', 'Percent']
).properties(
    title="Percent of Total Contestants Eliminated in Week 1 vs Remaining by Age Bucket",
    width=700,
    height=400
)

# Display the chart in Streamlit
st.write("### Percent of Total Contestants Eliminated in Week 1 vs Remaining by Age Bucket")
st.altair_chart(base_age)
