import streamlit as st
import pandas as pd
import math
import numpy as np
from pathlib import Path

@st.cache_data
def get_bach_data():
    DATA_FILENAME = Path(__file__).parent/'data/bachelorette-contestants.csv'
    raw_bach_df = pd.read_csv(DATA_FILENAME)
    return raw_bach_df


bach_df = get_bach_data()

# ----------------------------------------------------------------------------
st.title("Bachelorette Analysis")
st.write(
    "This is a quick analysis of the Bachelorette dataset."
)

st.link_button("View dataset here",
               "https://www.kaggle.com/datasets/brianbgonz/the-bachelorette-contestants?resource=download&select=bachelorette-contestants.csv")

st.table(data=bach_df)