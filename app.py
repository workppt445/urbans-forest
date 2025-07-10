import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import altair as alt

# Optional imports
try:
    import folium
    from folium.plugins import HeatMap
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

import json, os

st.set_page_config(page_title="Melbourne House Price Explorer", layout="wide", initial_sidebar_state="expanded")

# Load datasets
DATA_DIR = "data"

def load_data():
    prices_path = os.path.join(DATA_DIR, "house-prices-by-small-area-sale-year.csv")
    dwell_path = os.path.join(DATA_DIR, "city-of-melbourne-dwellings-and-household-forecasts-by-small-area-2020-2040.csv")
    try:
        prices = pd.read_csv(prices_path).rename(columns=lambda c: c.strip().lower().replace(' ', '_'))
    except FileNotFoundError:
        st.error(f"Price data file not found: {prices_path}")
        return pd.DataFrame(), pd.DataFrame()
    try:
        dwell = pd.read_csv(dwell_path).rename(columns=lambda c: c.strip().lower().replace(' ', '_'))
    except FileNotFoundError:
        st.error(f"Dwellings data file not found: {dwell_path}")
        dwell = pd.DataFrame()
    if 'type' in prices.columns:
        prices = prices.rename(columns={'type': 'property_type'})
    prices['latitude'] = prices.get('latitude', -37.8136)
    prices['longitude'] = prices.get('longitude', 144.9631)
    if 'geography' in dwell.columns:
        dwell = dwell.rename(columns={'geography': 'small_area'})
    dwell = dwell.rename(
        columns={k: v for k, v in [('category', 'dwelling_type'), ('households', 'dwelling_number')] if k in dwell.columns}
    )
    return prices, dwell

prices_df, dwell_df = load_data()

# Sidebar filters
st.sidebar.header("Data Filters")
suburbs = sorted(prices_df['small_area'].dropna().unique())
prop_types = sorted(prices_df['property_type'].dropna().unique())
selected_suburbs = st.sidebar.multiselect("Suburb", suburbs, default=suburbs[:5])
selected_types = st.sidebar.multiselect("Property Type", prop_types, default=prop_types[:2])
year_min, year_max = st.sidebar.slider(
    "Sale Year Range",
    int(prices_df['sale_year'].min()),
    int(prices_df['sale_year'].max()),
    (int(prices_df['sale_year'].min()), int(prices_df['sale_year'].max()))
)

# Apply filters
df = prices_df[
    prices_df['small_area'].isin(selected_suburbs) &
    prices_df['property_type'].isin(selected_types) &
    prices_df['sale_year'].between(year_min, year_max)
].reset_index(drop=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview", "Map & Trends", "Heatmap", "Data Table"
])

with tab1:
    total = len(df)
    unique_suburbs = df['small_area'].nunique()
    avg_price = df['median_price'].mean() if total else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("Filtered Records", total)
    c2.metric("Unique Suburbs", unique_suburbs)
    c3.metric("Average Price", f"${avg_price:,.0f}")

with tab2:
    st.subheader("📊 Price Trends")
    sub = st.selectbox("Suburb", sorted(df['small_area'].unique()))
    ptype = st.selectbox("Property Type", sorted(df['property_type'].unique()))
    df_st = df[(df['small_area'] == sub) & (df['property_type'] == ptype)]
    if not df_st.empty:
        ct = st.radio("Chart Type", ["Line", "Bar", "Area"], horizontal=True)
        base = alt.Chart(df_st).encode(
            x='sale_year:O',
            y='median_price:Q'
        )
        if ct == 'Line':
            chart = base.mark_line(point=True)
        elif ct == 'Bar':
            chart = base.mark_bar()
        else:
            chart = base.mark_area(opacity=0.5)
        st.altair_chart(
            chart.properties(width=700, height=350), use_container_width=True
        )
    else:
        st.warning("No data for selection.")

with tab3:
    st.subheader("📍 Price Heatmap")
    if not FOLIUM_AVAILABLE:
        st.error("Folium not installed; heatmap unavailable.")
    else:
        midpoint = (
            df['latitude'].mean(),
            df['longitude'].mean()
        )
        m = folium.Map(location=midpoint, zoom_start=12)
        hdata = df[['latitude', 'longitude', 'median_price']].dropna()
        hdata['i'] = (
            hdata['median_price'] - hdata['median_price'].min()
        ) / (
            hdata['median_price'].max() - hdata['median_price'].min()
        )
        HeatMap(
            hdata[['latitude', 'longitude', 'i']].values.tolist(), radius=15
        ).add_to(m)
        st_folium(m, width=700, height=500)

with tab4:
    st.subheader("📋 Interactive Data Table")
    st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True
    )
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download CSV", csv, "filtered_house_prices.csv", mime='text/csv'
    )

st.markdown("---")
st.write("*Data source: City of Melbourne Open Data Portal*.")
