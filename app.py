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
    df['year_planted'] = pd.to_numeric(df.get('year_planted', None), errors='coerce')
    if 'height_m' in df.columns:
        df['height_m'] = pd.to_numeric(df['height_m'], errors='coerce')
    return df.dropna(subset=['common_name', 'year_planted'])

data = load_tree_data()

# Utility

def random_color():
    return f'rgb({random.randint(50,200)},{random.randint(100,255)},{random.randint(50,200)})'

# Sidebar Filters
st.sidebar.header("Filters & Secret Pin")
search = st.sidebar.text_input("🔍 Search Species")
species = sorted(data['common_name'].unique())
choices = [s for s in species if search.lower() in s.lower()]
if not choices:
    choices = species
sel = st.sidebar.multiselect("Species", species, default=species)
ymin, ymax = st.sidebar.slider(
    "Year Planted Range",
    int(data['year_planted'].min()),
    int(data['year_planted'].max()),
    (int(data['year_planted'].min()), int(data['year_planted'].max()))
)
hmin, hmax = None, None
if 'height_m' in data.columns:
    hmin, hmax = st.sidebar.slider(
        "Height (m) Range",
        float(data['height_m'].min()),
        float(data['height_m'].max()),
        (float(data['height_m'].min()), float(data['height_m'].max()))
    )
pin = st.sidebar.text_input("🔒 Secret Pin", type="password")
if pin:
    if pin == '7477':
        st.sidebar.success("🔓 Unlocked!"), st.balloons()
    else:
        st.sidebar.error("❌ Wrong pin")

# Apply filters
df = data[data['common_name'].isin(sel) & data['year_planted'].between(ymin, ymax)]
if hmin is not None:
    df = df[df['height_m'].between(hmin, hmax)]

# Header
t1, t2, t3, t4, t5 = st.tabs(["Overview", "Species Counts", "Map View", "Distributions", "Data Table"])

with t1:
    total = len(df)
    uniq = df['common_name'].nunique()
    avg_h = df['height_m'].mean() if 'height_m' in df.columns else None
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Trees", total)
    c2.metric("Species Count", uniq)
    if avg_h is not None:
        c3.metric("Avg Height (m)", f"{avg_h:.1f}")

with t2:
    cnt = df['common_name'].value_counts().reset_index()
    cnt.columns = ['common_name', 'count']
    cnt['percent'] = (cnt['count'] / total * 100).round(1)
    cnt = cnt.sort_values('count', ascending=False)
    colors = [random_color() for _ in cnt['count']]
    fig = px.bar(
        cnt, x='common_name', y='count', text='count', labels={'common_name':'Species','count':'Count'},
        title="Tree Species Frequencies"
    )
    fig.update_traces(marker_color=colors, texttemplate='%{text}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, uniformtext_minsize=8)
    st.plotly_chart(fig, use_container_width=True)

with t3:
    st.subheader("Interactive Map")
    if 'latitude' in df.columns and 'longitude' in df.columns:
        map_df = df.dropna(subset=['latitude', 'longitude'])
        fig_map = px.scatter_mapbox(
            map_df, lat='latitude', lon='longitude', hover_name='common_name',
            hover_data={'year_planted':True,'height_m':True},
            color='common_name', zoom=11, height=500,
            color_discrete_sequence=cnt['percent'].apply(lambda x: random_color()).tolist()
        )
        fig_map.update_layout(mapbox_style='open-street-map', legend=dict(title='Species'))
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("Coordinate data missing for map.")

with t4:
    st.subheader("Planting Year Distribution")
    fig_hist = px.histogram(df, x='year_planted', nbins=20,
                            labels={'year_planted':'Year Planted'}, title="Year Planted Distribution")
    st.plotly_chart(fig_hist, use_container_width=True)
    if 'height_m' in df.columns:
        st.subheader("Height Distribution by Species")
        fig_box = px.box(df, x='common_name', y='height_m',
                         labels={'common_name':'Species','height_m':'Height (m)'},
                         title="Height by Species")
        st.plotly_chart(fig_box, use_container_width=True)

with t5:
    st.subheader("Data Table")
    editor = st.data_editor(df, num_rows='dynamic', use_container_width=True)
    csv = df.to_csv(index=False).encode()
    st.download_button("Download CSV", csv, "trees_filtered.csv", mime='text/csv')

st.caption("*Built with Streamlit & Plotly* 🌿")
