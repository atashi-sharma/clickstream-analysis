import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter

st.set_page_config(page_title="Visitor Clickstream Analysis", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

st.title("Visitor Clickstream Analysis -- W&SNA")
st.caption("Atashi Sharma -- S2669393")


if 'df' not in st.session_state:  # Check if 'df' is already in session_state
    try:
        path = "data/clickstream_data.csv"
        headers = ["Source", "Device", "Link 1", "Link 2", "Link 3", "Link 4", "Link 5", "Link 6", "Link 7", "Link 8", "Link 9", "Link 10", "Link 11", "Link 12", "Link 13", "Link 14", "Link 15", "Link 16"]
        df = pd.read_csv(path, on_bad_lines='skip', names=headers, encoding='utf-8')

        link_cols = [f"Link {i}" for i in range(1, 17)]
        df['path'] = df[link_cols].apply(lambda row: [link for link in row.dropna().tolist()], axis=1)
        df.drop(link_cols, axis=1, inplace=True) # Drop link columns
        
        st.session_state.df = df  # Store the processed DataFrame in session_state
        st.success("Database loaded and processed successfully (one time).")

    except Exception as e:
        st.error(f"❌ Error loading/processing data: {e}")
        st.stop()

else:
    df = st.session_state.df  # Retrieve the DataFrame from session_state

if st.toggle("Dataframe Summary"):
    st.write(df.describe())



if st.toggle("Show Frequent User Paths"):
    st.write("FrequentU ser Paths:")
    path_counts = Counter(tuple(path) for path in df['path'])  
    most_common_paths = path_counts.most_common(10)  # Get top 10 most frequent paths (adjust number as needed)
    st.write("Most Frequent User Paths:")
    for path, count in most_common_paths:
        st.write(f"{' -> '.join(path)} (Count: {count})")
st.write("---")

## Functions
def bounce_rate_by_source(df):
  bounce_rates = {}
  for source, group in df.groupby('Source'):
    single_page_visits = group['Link 2'].isnull().sum()
    bounce_rate = (single_page_visits / len(group)) * 100
    bounce_rates[source] = bounce_rate
  return bounce_rate

def bounce_rate_by_source_device(df, selected_sources=None, selected_devices=None):
    """Calculates bounce rate by source and device, with filtering options."""
    filtered_df = df.copy()

    if selected_sources:
        filtered_df = filtered_df[filtered_df['Source'].isin(selected_sources)]
    if selected_devices:
        filtered_df = filtered_df[filtered_df['Device'].isin(selected_devices)]

    bounce_rates = {}
    for (source, device), group in filtered_df.groupby(['Source', 'Device']):
        single_page_visits = group['path'].apply(lambda x: len(x) == 1).sum()
        bounce_rate = (single_page_visits / len(group)) * 100
        bounce_rates[(source, device)] = bounce_rate

    # Calculate overall bounce rate for each source:
    for source in filtered_df['Source'].unique():
        all_devices_group = filtered_df[filtered_df['Source'] == source]
        single_page_visits_all = all_devices_group['path'].apply(lambda x: len(x) == 1).sum()
        bounce_rate_all = (single_page_visits_all / len(all_devices_group)) * 100
        bounce_rates[(source, 'all')] = bounce_rate_all

    return bounce_rates

def pages_before_event(df, target_event='purchase_start'):
    pages_before = Counter()
    for _, row in df.iterrows():
        for i in range(1, 17):  # Check from Link 1 to Link 16
            if row[f'Link {i}'] == target_event:
                try:
                    next_page = row[f'Link {i-1}']
                    pages_before[next_page] += 1
                except:
                    next_page = "start"
                    pages_before[next_page] += 1
                break  # Move to the next row once the target event is found
    return pages_before

def pages_after_event(df, target_event='purchase_start'):
    pages_after = Counter()
    for _, row in df.iterrows():
        for i in range(1, 17):  # Check from Link 1 to Link 16
            if row[f'Link {i}'] == target_event:
                next_page = row[f'Link {i+1}']
                pages_after[next_page] += 1
                break  # Move to the next row once the target event is found
    return pages_after

def avg_links_to_purchase(df, selected_source=None):
    if selected_source:
        filtered_df = df[df['Source'] == selected_source]
    else:
        filtered_df = df
    successful_paths = filtered_df[filtered_df['path'].apply(lambda p: 'purchase_success' in p)]
    if not successful_paths.empty:
        avg_links = successful_paths['path'].apply(len).mean()
        return avg_links
    else:
        return 0

def calculate_purchase_success_rate(df, selected_source=None):
    if selected_source:
        filtered_df = df[df['Source'] == selected_source]
    else:
        filtered_df = df
    if not filtered_df.empty:
        purchase_success_rate = (filtered_df['path'].apply(lambda p: 'purchase_success' in p).sum() / len(filtered_df)) * 100
        return purchase_success_rate
    else:
        return 0

def avg_links_visited_by_source(df, selected_sources=None):
    if selected_sources:
        filtered_df = df[df['Source'] == selected_sources]
    else:
        filtered_df = df
    if not filtered_df.empty:
        filtered_df['links_visited'] = filtered_df[link_cols].notna().sum(axis=1)  # Count non-null links
        avg_links = filtered_df['links_visited'].mean()
        return avg_links
    else:
        return 0

def conversion_rate_by_device(df, selected_sources=None):
    if selected_sources:
        filtered_df = df[df['Source'] == selected_sources]
    else:
        filtered_df = df
    if not filtered_df.empty:
        conversion_rates = filtered_df.groupby('Device')['path'].apply(lambda x: (x.apply(lambda p: 'purchase_success' in p).sum() / len(x)) * 100).to_dict()
        return conversion_rates
    else:
        return {}

def conversion_rate_by_page(df, selected_sources=None, pages=None):
    if selected_sources:
        filtered_df = df[df['Source'].isin(selected_sources)]
    else:
        filtered_df = df
    if pages:
        filtered_df['last_page'] = filtered_df['path'].apply(lambda x: x[-1] if x else None)
        filtered_df = filtered_df[filtered_df['last_page'].isin(pages)]
    if not filtered_df.empty:
        conversion_rates = (filtered_df['path'].apply(lambda p: 'purchase_success' in p).sum() / len(filtered_df)) * 100
        return conversion_rates
    else:
        return 0

def conversion_rate_by_first_page(df, selected_sources=None, pages=None):
    filtered_df = df.copy()
    if selected_sources:
        filtered_df = filtered_df[filtered_df['Source'].isin(selected_sources)]

    if pages:
        filtered_df['first_page'] = filtered_df['path'].apply(lambda x: x if x else None)  # Get the FIRST page
        filtered_df = filtered_df[filtered_df['first_page'].isin(pages)]

    if not filtered_df.empty:
        conversion_rates = (filtered_df['path'].apply(lambda p: 'purchase_success' in p).sum() / len(filtered_df)) * 100
        return conversion_rates
    else:
        return 0

def bounce_rate_by_source_device(df, selected_sources=None, selected_devices=None):
    """Calculates bounce rate by source and device, with filtering options."""
    filtered_df = df.copy()  # Create a copy to avoid modifying the original DataFrame

    if selected_sources:
        filtered_df = filtered_df[filtered_df['Source'].isin(selected_sources)]
    if selected_devices:
        filtered_df = filtered_df[filtered_df['Device'].isin(selected_devices)]

    bounce_rates = {}
    for (source, device), group in filtered_df.groupby(['Source', 'Device']):
        single_page_visits = group['path'].apply(lambda x: len(x) == 1).sum()
        bounce_rate = (single_page_visits / len(group)) * 100
        bounce_rates[(source, device)] = bounce_rate
    return bounce_rates

def dropoff_page_by_source_device(df, selected_sources=None, selected_devices=None):
    """Calculates drop-off page by source and device, with filtering."""
    filtered_df = df.copy()

    if selected_sources:
        filtered_df = filtered_df[filtered_df['Source'].isin(selected_sources)]
    if selected_devices:
        filtered_df = filtered_df[filtered_df['Device'].isin(selected_devices)]

    dropoff_pages = {}
    for (source, device), group in filtered_df.groupby(['Source', 'Device']):
        last_pages = group['path'].apply(lambda x: x[-1] if x and x[-1]!= 'purchase_success' else None).dropna()
        if not last_pages.empty:
            most_common_dropoff = last_pages.mode()
            dropoff_pages[(source, device)] = most_common_dropoff
        else:
            dropoff_pages[(source, device)] = None
    return dropoff_pages


# Example usage:
# Assuming you have your DataFrame 'df' with 'Source', 'Device', and 'path' columns

st.header("Campaign Performance Analytics")
campaign_sources = ['facebook_advert', 'linkedin_advert', 'partner_advert']

for source in campaign_sources:
    st.header(f"Campaign: {source}")

    # 1. Bounce Rate
    bounce_rate = bounce_rate_by_source_device(df, selected_sources=[source])
    st.write(f"Bounce Rate: {bounce_rate[(source, 'all')]:.2f}%")  # Assuming 'all' for all devices

    # 2. Conversion Rate (Purchase Success Rate)
    conversion_rate = calculate_purchase_success_rate(df, selected_source=source)
    st.write(f"Conversion Rate: {conversion_rate:.2f}%")

    # 3. Average Links to Purchase Success
    avg_links = avg_links_to_purchase(df, selected_source=source)
    st.write(f"Average Links to Purchase Success: {avg_links:.2f}")

    # 4. Purchase Success Rate by Device
    success_by_device = conversion_rate_by_device(df, selected_sources=[source])
    st.write("Purchase Success Rate by Device:")
    for device, rate in success_by_device.items():
        st.write(f"- {device}: {rate:.2f}%")

    # 5. Drop-off Page Ranking
    dropoff_pages = dropoff_page_by_source_device(df, selected_sources=[source])
    st.write("Drop-off Page Ranking:")
    sorted_dropoffs = sorted(dropoff_pages.items(), key=lambda item: item, reverse=True) # Sort by drop-off count
    for (source, device), dropoff_count in sorted_dropoffs:
        st.write(f"Source: {source}, Device: {device}, Count: {dropoff_count}")

st.write("---")
st.header("Platform Behavior Analytics")

st.write("---")
st.header("Source Comparison Analytics")

st.write("---")
st.header("Blog Performance Analytics")

st.write("---")