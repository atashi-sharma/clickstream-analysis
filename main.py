import streamlit as st
import pandas as pd
import numpy as np


st.title("Visitor Clickstream Analysis")

path = "data/clickstream_data.csv"

headers=["Source", "Device", "Link 1", "Link 2", "Link 3" , "Link 4", "Link 5", "Link 6", "Link 7", "Link 8", "Link 9", "Link 10", "Link 11", "Link 12", "Link 13", "Link 14", "Link 15", "Link 16"]
df = pd.read_csv(path, on_bad_lines='skip', names=headers,  encoding='utf-8')

# df=df.dropna()


st.dataframe(df)

# unique_sources = df["Source"].unique()
# st.write("Unique Sources: ", unique_sources)
# unique_devices = df["Device"].unique()
# st.write("Unique Devices: ", unique_devices)

# count_sources = df["Source"].value_counts()
# st.write("Count of Sources: ", count_sources)

# count_devices = df["Device"].value_counts()
# st.write("Count of Devices: ", count_devices)

df["Source"].value_counts().plot(kind='bar')
st.pyplot()

df["Device"].value_counts().plot(kind='bar')
st.pyplot()
