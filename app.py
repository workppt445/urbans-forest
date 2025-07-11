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

# Utility function
def random_color():
    return f'rgb({random.randint(50,200)},{random.randint(100,255)},{random.randint(50,200)})'

# Sidebar filters and secret pin
st.sidebar.header("Filters & Secret Pin")
search = st.sidebar.text_input("🔍 Search Species")
species = sorted(data['common_name'].unique())
def_filter = species
filtered_list = [s for s in species if search.lower() in s.lower()]
if not filtered_list:
    filtered_list = species
sel = st.sidebar.multiselect("Species (choose one or more)", options=filtered_list, default=def_filter)

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
        st.sidebar.success("🔓 Secret Unlocked!"); st.balloons()
    else:
        st.sidebar.error("❌ Incorrect Pin")

filtered = data[
    data['common_name'].isin(sel) &
    data['year_planted'].between(ymin, ymax)
]
if hmin is not None:
    filtered = filtered[filtered['height_m'].between(hmin, hmax)]

col1, col2 = st.columns([4,1])
with col1:
    st.title("🌳 Fun Urban Forest Explorer")
    st.markdown("Explore Melbourne's trees: filters, charts, maps, and data.")
with col2:
    if os.path.exists('forest_icon.png'):
        st.image(Image.open('forest_icon.png'), width=64)

# Tabs layout
t1, t2, t3, t4, t5 = st.tabs([
    "Overview", "Species Counts", "Map View", "Distributions", "Data Table"
])

with t1:
    total = len(filtered)
    uniq = filtered['common_name'].nunique()
    avg_h = filtered['height_m'].mean() if 'height_m' in filtered.columns else None
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Trees", total)
    c2.metric("Unique Species", uniq)
    if avg_h is not None:
        c3.metric("Avg Height (m)", f"{avg_h:.1f}")

with t2:
    cnt = filtered['common_name'].value_counts().reset_index()
    cnt.columns = ['common_name', 'count']
    cnt['percent'] = (cnt['count'] / total * 100).round(1) if total else 0
    cnt = cnt.sort_values('count', ascending=False)
    colors = [random_color() for _ in cnt['common_name']]
    fig = px.bar(
        cnt, x='common_name', y='count', text='count',
        title="Tree Species Frequencies",
        labels={'common_name':'Species','count':'Count'}
    )
    fig.update_traces(marker_color=colors, texttemplate='%{text}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, uniformtext_minsize=8)
    st.plotly_chart(fig, use_container_width=True)

with t3:
    st.subheader("Interactive Map")
    if 'latitude' in filtered.columns and 'longitude' in filtered.columns:
        map_df = filtered.dropna(subset=['latitude','longitude'])
        if not map_df.empty:
            fig_map = px.scatter_mapbox(
                map_df, lat='latitude', lon='longitude', hover_name='common_name',
                hover_data={'year_planted':True, 'height_m':True},
                color_discrete_sequence=[random_color()],
                zoom=11, height=500
            )
            fig_map.update_layout(mapbox_style='open-street-map', legend_title_text='')
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("No coordinate data available for chosen filters.")
    else:
        st.warning("Latitude/Longitude not in data.")

with t4:
    st.subheader("Distributions")
    fig_hist = px.histogram(
        filtered, x='year_planted', nbins=20,
        labels={'year_planted':'Year Planted'}, title="Year Planted Distribution"
    )
    st.plotly_chart(fig_hist, use_container_width=True)
    if 'height_m' in filtered.columns:
        fig_box = px.box(
            filtered, x='common_name', y='height_m',
            labels={'common_name':'Species','height_m':'Height (m)'},
            title="Height by Species"
        )
        st.plotly_chart(fig_box, use_container_width=True)

with t5:
    st.subheader("Data Table")
    st.dataframe(filtered, use_container_width=True)
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "trees_filtered.csv", mime='text/csv')

st.caption("*Built with Streamlit & Plotly* 🌿")
