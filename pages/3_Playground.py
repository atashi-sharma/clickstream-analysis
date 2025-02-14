import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter


st.title("Visitor Clickstream Analysis")

path = "data/clickstream_data.csv"

headers=["Source", "Device", "Link 1", "Link 2", "Link 3" , "Link 4", "Link 5", "Link 6", "Link 7", "Link 8", "Link 9", "Link 10", "Link 11", "Link 12", "Link 13", "Link 14", "Link 15", "Link 16"]

try:
    df = pd.read_csv(path, on_bad_lines='skip', names=headers,  encoding='utf-8')
    st.success("Database loaded successfully")
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

if st.toggle("Dataframe Summary"):
    st.write(df.describe())



def bounce_rate_by_source(df):
  bounce_rates = {}
  for source, group in df.groupby('Source'):
    single_page_visits = group['Link 2'].isnull().sum()
    bounce_rate = (single_page_visits / len(group)) * 100
    bounce_rates[source] = bounce_rate
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

link_cols = [f"Link {i}" for i in range(1, 17)]
df['path'] = df[link_cols].apply(lambda row: [link for link in row.dropna().tolist()], axis=1)

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
 # Use isin for multiple sources
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

bounce_rates_by_source = bounce_rate_by_source(df)

st.sidebar.header("Select Source")

st.title("Analytics")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["All", "Advertisement (Campaign)", "Social Shares", "Organic Outreach", "Pages"])

with tab1:
    st.header("Analytics for all")
    col1, col2, col3 = st.columns(3)
    with col1:
        single_page_visits = df['Link 2'].isnull().sum()
        bounce_rate = (single_page_visits / len(df)) * 100
        st.write(f"**Bounce Rate:** {bounce_rate:.2f}%")
        st.write("-----")
        selected_sources=["direct", "linkedin_advert", "partner_advert", "facebook_advert", "linkedin_share", "facebook_share", "search"]
        if selected_sources:  # For multiselect
            for source in selected_sources:
                st.write(f"{source}: {bounce_rates_by_source[source]:.2f}%")
    with col2:
        df['links_visited'] = df.notnull().sum(axis=1) - 2  # Subtract 2 for 'Source' and 'Device'
        average_links_visited = df['links_visited'].mean()
        st.write(f"**Average Links Visited:** {average_links_visited:.2f}")
        selected_source_filter=None
        # Path to Purchase Success (Bounce Rate Removed)
        avg_links = avg_links_to_purchase(df, selected_source_filter)
        purchase_success_rate = calculate_purchase_success_rate(df, selected_source_filter)
        st.write(f"Average Links Visited to Purchase: {avg_links:.2f}")
        st.write(f"Purchase Success Rate: {purchase_success_rate:.2f}%")

    st.write("----")
    st.header("Takeaways")
    st.write("1 - Hii")
    st.write("2 - Second Takeaway")
with tab2:
    st.header("Campaigns (Facebook/Linkedin/Partner)")
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_sources=["linkedin_advert", "partner_advert", "facebook_advert"]
        st.write("**Bounce Rates:**")
        if selected_sources:  # For multiselect
            for source in selected_sources:
                st.write(f"{source}: {bounce_rates_by_source[source]:.2f}%")#
    with col2:
        avg_links=avg_links_visited_by_source(df, selected_source_filter)
        st.write("Linkedin Advert -")
        selected_source_filter="linkedin_advert"
        # Path to Purchase Success (Bounce Rate Removed)
        avg_links = avg_links_to_purchase(df, selected_source_filter)
        purchase_success_rate = calculate_purchase_success_rate(df, selected_source_filter)
        avg_links_visited=avg_links_visited_by_source(df, selected_source_filter)
        st.caption(f"Average Links Visited: {avg_links_visited:.2f}")
        st.caption(f"Average Links Visited to Purchase: {avg_links:.2f}")
        st.caption(f"Purchase Success Rate: {purchase_success_rate:.2f}%")
        st.write("Facebook Advert -")
        selected_source_filter="facebook_advert"
        # Path to Purchase Success (Bounce Rate Removed)
        avg_links = avg_links_to_purchase(df, selected_source_filter)
        purchase_success_rate = calculate_purchase_success_rate(df, selected_source_filter)
        avg_links_visited=avg_links_visited_by_source(df, selected_source_filter)
        st.caption(f"Average Links Visited: {avg_links_visited:.2f}")
        st.caption(f"Average Links Visited to Purchase: {avg_links:.2f}")
        st.caption(f"Purchase Success Rate: {purchase_success_rate:.2f}%")
        st.write("Partner Advert -")
        selected_source_filter="partner_advert"
        # Path to Purchase Success (Bounce Rate Removed)
        avg_links = avg_links_to_purchase(df, selected_source_filter)
        purchase_success_rate = calculate_purchase_success_rate(df, selected_source_filter)
        avg_links_visited=avg_links_visited_by_source(df, selected_source_filter)
        st.caption(f"Average Links Visited: {avg_links_visited:.2f}")
        st.caption(f"Average Links Visited to Purchase: {avg_links:.2f}")
        st.caption(f"Purchase Success Rate: {purchase_success_rate:.2f}%")
with tab3:
    st.header("Social Shares (Facebook/Linkedin)")
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_sources=["linkedin_share", "facebook_share"]
        st.write("**Bounce Rates:**")
        if selected_sources:  # For multiselect
            for source in selected_sources:
                st.write(f"{source}: {bounce_rates_by_source[source]:.2f}%")
    with col2:
        st.write("Linkedin Share -")
        selected_source_filter="linkedin_share"
        # Path to Purchase Success (Bounce Rate Removed)
        avg_links = avg_links_to_purchase(df, selected_source_filter)
        purchase_success_rate = calculate_purchase_success_rate(df, selected_source_filter)
        st.write(f"Average Links Visited to Purchase: {avg_links:.2f}")
        st.write(f"Purchase Success Rate: {purchase_success_rate:.2f}%")
        st.write("Facebook Share -")
        selected_source_filter="facebook_share"
        # Path to Purchase Success (Bounce Rate Removed)
        avg_links = avg_links_to_purchase(df, selected_source_filter)
        purchase_success_rate = calculate_purchase_success_rate(df, selected_source_filter)
        st.write(f"Average Links Visited to Purchase: {avg_links:.2f}")
        st.write(f"Purchase Success Rate: {purchase_success_rate:.2f}%")
with tab4:
    st.header("Organic(Direct / Search)")
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_sources=["direct", "search"]
        st.write("**Bounce Rates:**")
        if selected_sources:  # For multiselect
            for source in selected_sources:
                st.write(f"{source}: {bounce_rates_by_source[source]:.2f}%")
    with col2:
        st.write("Direct")
        selected_source_filter="direct"
        # Path to Purchase Success (Bounce Rate Removed)
        avg_links = avg_links_to_purchase(df, selected_source_filter)
        purchase_success_rate = calculate_purchase_success_rate(df, selected_source_filter)
        st.write(f"Average Links Visited to Purchase: {avg_links:.2f}")
        st.write(f"Purchase Success Rate: {purchase_success_rate:.2f}%")
        st.write("Search - ")
        selected_source_filter="search"
        # Path to Purchase Success (Bounce Rate Removed)
        avg_links = avg_links_to_purchase(df, selected_source_filter)
        purchase_success_rate = calculate_purchase_success_rate(df, selected_source_filter)
        st.write(f"Average Links Visited to Purchase: {avg_links:.2f}")
        st.write(f"Purchase Success Rate: {purchase_success_rate:.2f}%")



st.write("-----")


