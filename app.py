import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random
import os
from PIL import Image

st.set_page_config(
    page_title="🌳 Fun Urban Forest Explorer",
    page_icon="🌳",
    layout="wide"
)

@st.cache_data

def load_tree_data(path="trees-with-species-and-dimensions-urban-forest.xlsx"):
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()
    df['year_planted'] = pd.to_numeric(df['year_planted'], errors='coerce')
    if 'height_m' in df.columns:
        df['height_m'] = pd.to_numeric(df['height_m'], errors='coerce')
    return df.dropna(subset=['common_name', 'year_planted'])

data = load_tree_data()

# Helper
def random_color():
    return f'rgb({random.randint(50,200)},{random.randint(100,255)},{random.randint(50,200)})'

# Sidebar
st.sidebar.header("Filters & Secret Pin")
search = st.sidebar.text_input("🔍 Search Species")
species = sorted(data['common_name'].dropna().unique())
filtered_species = [s for s in species if search.lower() in s.lower()] or species
selected = st.sidebar.multiselect("Species", filtered_species, default=filtered_species)

ymin, ymax = st.sidebar.slider(
    "Year Planted Range", int(data['year_planted'].min()), int(data['year_planted'].max()),
    (int(data['year_planted'].min()), int(data['year_planted'].max()))
)
hmin, hmax = None, None
if 'height_m' in data.columns and not data['height_m'].dropna().empty:
    hmin, hmax = st.sidebar.slider(
        "Height (m) Range", float(data['height_m'].min()), float(data['height_m'].max()),
        (float(data['height_m'].min()), float(data['height_m'].max()))
    )
pin = st.sidebar.text_input("🔒 Secret Pin", type="password")
if pin:
    if pin == '7477':
        st.sidebar.success("🔓 Secret Unlocked!"); st.balloons()
    else:
        st.sidebar.error("❌ Incorrect Pin")

# Filter data
df = data[data['common_name'].isin(selected) & data['year_planted'].between(ymin, ymax)]
if hmin is not None:
    df = df[df['height_m'].between(hmin, hmax)]

# Header
t1, t2, t3, t4, t5 = st.tabs(["Overview","Counts","Map","Distributions","Table"])

with t1:
    total = len(df)
    uniq = df['common_name'].nunique()
    avg_h = df['height_m'].mean() if 'height_m' in df.columns else None
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Trees", total)
    c2.metric("Unique Species", uniq)
    if avg_h is not None:
        c3.metric("Avg Height (m)", f"{avg_h:.1f}")

with t2:
    counts = df['common_name'].value_counts().reset_index()
    counts.columns = ['common_name', 'count']
    counts['percent'] = (counts['count'] / total * 100).round(1) if total else 0
    counts = counts.sort_values('count', ascending=False)
    colors = [random_color() for _ in counts['common_name']]
    fig = px.bar(counts, x='common_name', y='count', text='count', labels={'common_name':'Species','count':'Count'}, title="Species Frequencies")
    fig.update_traces(marker_color=colors, texttemplate='%{text}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

with t3:
    st.subheader("Interactive Map")
    if 'latitude' in df.columns and 'longitude' in df.columns:
        map_df = df.dropna(subset=['latitude','longitude'])
        if not map_df.empty:
            fig_map = px.scatter_mapbox(
                map_df,
                lat='latitude',
                lon='longitude',
                hover_name='common_name',
                hover_data={"year_planted": True, "height_m": True},
                zoom=10,
                height=500
            )
            fig_map.update_layout(mapbox_style='open-street-map', margin={'r':0,'t':0,'l':0,'b':0})
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("No coordinate data for selected filters.")
    else:
        st.warning("Latitude/Longitude columns missing.")

with t4:
    if not df.empty:
        hist = px.histogram(df, x='year_planted', nbins=20, labels={'year_planted':'Year Planted'}, title="Planting Year")
        st.plotly_chart(hist, use_container_width=True)
        if 'height_m' in df.columns:
            box = px.box(df, x='common_name', y='height_m', labels={'height_m':'Height (m)'}, title="Height by Species")
            st.plotly_chart(box, use_container_width=True)
    else:
        st.warning("No data available for plotting.")

with t5:
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "trees.csv", mime='text/csv')

st.caption("*Built with Streamlit & Plotly* 🌿")
