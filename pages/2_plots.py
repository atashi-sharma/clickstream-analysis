import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

def load_data(file_path, headers=None):
    """
    Loads a CSV file, handles errors gracefully, and ensures required columns exist.
    """
    try:
        df = pd.read_csv(file_path, on_bad_lines='skip', names=headers, encoding='utf-8')
        st.write("✅ Data loaded successfully!")
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return None

    # Ensure necessary columns exist
    required_columns = ["Source", "Device"]
    for col in required_columns:
        if col not in df.columns:
            st.warning(f"⚠️ Missing expected column: {col}")
            df[col] = "Unknown"  # Fill missing columns with default values

    return df

def plot_value_counts(df, column, title):
    """
    Plots value counts for a given column, handling empty or missing data.
    """
    if column in df.columns and not df[column].isna().all():
        fig, ax = plt.subplots()
        df[column].value_counts().plot(kind='bar', ax=ax)
        ax.set_title(title)
        ax.set_xlabel(column)
        ax.set_ylabel("Count")
        st.pyplot(fig)
    else:
        st.warning(f"⚠️ No valid data to plot for column: {column}")

# Load data
path = "data/clickstream_data.csv"  # Update with your file path
headers=["Source", "Device", "Link 1", "Link 2", "Link 3" , "Link 4", "Link 5", "Link 6", "Link 7", "Link 8", "Link 9", "Link 10", "Link 11", "Link 12", "Link 13", "Link 14", "Link 15", "Link 16"]
df = load_data(path, headers)

# Plot graphs if data is valid
if df is not None:
    plot_value_counts(df, "Source", "Source Distribution")
    plot_value_counts(df, "Device", "Device Distribution")
