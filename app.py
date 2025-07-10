import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
import os
from PIL import Image

st.set_page_config(
    page_title="🌳 Fun Urban Forest Explorer",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_tree_data(path="trees-with-species-and-dimensions-urban-forest.xlsx"):
    df = pd.read_excel(path, sheet_name=0)
    df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()
    df['year_planted'] = pd.to_numeric(df['year_planted'], errors='coerce')
    return df.dropna(subset=['common_name', 'year_planted'])

data = load_tree_data()

def random_color():
    return f'rgb({random.randint(50,200)},{random.randint(100,255)},{random.randint(50,200)})'

st.sidebar.header("Filters & Options")
search = st.sidebar.text_input("🔍 Search Species", '')
species_list = sorted(data['common_name'].unique())
filtered_species = [s for s in species_list if search.lower() in s.lower()]
selected_species = st.sidebar.multiselect("Species", filtered_species, default=filtered_species[:5])

year_min, year_max = st.sidebar.slider(
    "Year Planted Range",
    int(data['year_planted'].min()),
    int(data['year_planted'].max()),
    (int(data['year_planted'].min()), int(data['year_planted'].max()))
)

pin = st.sidebar.text_input("🔒 Secret Pin", type="password")
if pin:
    if pin == '7477': st.sidebar.balloons(); st.sidebar.success("Secret Unlocked!")
    else: st.sidebar.error("Incorrect Pin")

height_min = None
if 'height_m' in data.columns:
    height_min, height_max = st.sidebar.slider(
        "Height (m) Range",
        float(data['height_m'].min()),
        float(data['height_m'].max()),
        (float(data['height_m'].min()), float(data['height_m'].max()))
    )
else:
    height_min, height_max = None, None

filtered = data[
    data['common_name'].isin(selected_species) &
    data['year_planted'].between(year_min, year_max)
]
if height_min is not None:
    filtered = filtered[filtered['height_m'].between(height_min, height_max)]

col1, col2 = st.columns([3,1])
with col1:
    st.title("🌳 Fun Urban Forest Explorer")
    st.markdown("Explore Melbourne's urban trees with interactive filters, charts, and maps.")
with col2:
    if os.path.exists('forest_icon.png'):
        st.image(Image.open('forest_icon.png'), width=64)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview","Charts","Map","Distribution","Data"])

with tab1:
    total = len(filtered)
    unique_sp = filtered['common_name'].nunique()
    avg_height = filtered['height_m'].mean() if 'height_m' in filtered.columns else None
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Trees", total)
    c2.metric("Unique Species", unique_sp)
    if avg_height is not None:
        c3.metric("Avg Height (m)", f"{avg_height:.1f}")

with tab2:
    counts = filtered['common_name'].value_counts().reset_index()
    counts.columns = ['common_name','count']
    colors = [random_color() for _ in counts.index]
    fig = px.bar(counts, x='common_name', y='count', color='common_name', title="Species Counts", text='count')
    fig.update_traces(marker_color=colors, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    if 'latitude' in filtered.columns and 'longitude' in filtered.columns:
        m = pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=pdk.ViewState(
                latitude=filtered['latitude'].mean(),
                longitude=filtered['longitude'].mean(),
                zoom=11
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=filtered,
                    get_position='[longitude, latitude]',
                    get_radius=50,
                    get_fill_color='[0, 200, 100, 140]',
                    pickable=True
                )
            ],
            tooltip={'text': '{common_name}\nHeight: {height_m} m'}
        )
        st.pydeck_chart(m)
    else:
        st.warning("No coordinate data for map view.")

with tab4:
    if 'height_m' in filtered.columns:
        fig_hist = px.histogram(filtered, x='year_planted', nbins=20, title="Planting Year Distribution")
        st.plotly_chart(fig_hist, use_container_width=True)
        fig_box = px.box(filtered, x='common_name', y='height_m', title="Height by Species")
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info("Additional distribution charts unavailable.")

with tab5:
    st.data_editor(filtered, num_rows="dynamic", use_container_width=True)
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "trees_filtered.csv", mime='text/csv')

st.caption("*Built with Streamlit & Plotly* 🌿")
