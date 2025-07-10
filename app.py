import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import pydeck as pdk
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
    return df.dropna(subset=['common_name','year_planted'])

data = load_tree_data()

def random_color():
    return f'rgb({random.randint(50,200)},{random.randint(100,255)},{random.randint(50,200)})'

# Theme toggle
theme = st.sidebar.selectbox("Theme", ["Light","Dark"])
if theme == "Dark": st.markdown("<style>body{background:#111;color:#eee;}</style>",unsafe_allow_html=True)

# Filters sidebar
st.sidebar.header("Filters & Secret Pin")
search = st.sidebar.text_input("🔍 Search species")
species = sorted(data['common_name'].unique())
choices = [s for s in species if search.lower() in s.lower()]
sel = st.sidebar.multiselect("Species", choices, default=choices[:5])
ymin, ymax = st.sidebar.slider("Year Planted Range",
    int(data['year_planted'].min()),int(data['year_planted'].max()),
    (int(data['year_planted'].min()),int(data['year_planted'].max()))
)
if 'height_m' in data.columns:
    hmin, hmax = st.sidebar.slider("Height (m) Range",float(data['height_m'].min()),float(data['height_m'].max()),
        (float(data['height_m'].min()),float(data['height_m'].max())))
else:
    hmin,hmax = None,None
pin = st.sidebar.text_input("🔒 Secret Pin",type="password")
if pin:
    if pin=='7477': st.sidebar.success("🔓 Unlocked!"), st.balloons()
    else: st.sidebar.error("❌ Wrong pin")

# Filter data
df = data[data['common_name'].isin(sel)&data['year_planted'].between(ymin,ymax)]
if hmin is not None: df = df[df['height_m'].between(hmin,hmax)]

# Header
col1,col2=st.columns([4,1])
with col1:
    st.title("🌳 Fun Urban Forest Explorer")
    st.markdown("Explore Melbourne's urban canopy: stats, charts, maps, and data.")
with col2:
    icon='forest_icon.png'
    if os.path.exists(icon): st.image(Image.open(icon),width=64)

# Tabs
t1,t2,t3,t4,t5 = st.tabs(["Overview","Charts","Map","Distribution","Data"])

with t1:
    total=len(df); uniq=df['common_name'].nunique()
    avg_h=df['height_m'].mean() if 'height_m' in df else 0
    c1,c2,c3=st.columns(3)
    c1.metric("Total Trees",total)
    c2.metric("Unique Species",uniq)
    c3.metric("Avg Height (m)",f"{avg_h:.1f}")
    if 'dbh_mm' in df.columns:
        avg_dbh=df['dbh_mm'].mean()
        st.metric("Avg DBH (mm)",f"{avg_dbh:.0f}")

with t2:
    cnt = df['common_name'].value_counts().reset_index()
    cnt.columns=['common_name','count']
    cnt['color'] = [random_color() for _ in cnt['count']]
    fig=px.bar(cnt,x='common_name',y='count',color='common_name',text='count',title="Species Counts")
    fig.update_traces(marker_color=cnt['color'],showlegend=False)
    st.plotly_chart(fig)

with t3:
    if 'latitude' in df.columns and 'longitude' in df.columns:
        view=pdk.ViewState(latitude=df['latitude'].mean(),longitude=df['longitude'].mean(),zoom=11)
        layer=pdk.Layer('ScatterplotLayer',data=df,get_position='[longitude,latitude]',get_fill_color='[0,200,100,160]',get_radius=50,pickable=True)
        st.pydeck_chart(pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',layers=[layer],initial_view_state=view,tooltip={'text':'{common_name}\nHeight: {height_m} m'}))
    else:
        st.warning("No coordinate data")

with t4:
    fig1=px.histogram(df,x='year_planted',nbins=20,title="Planting Year Distribution")
    fig2=px.box(df,x='common_name',y='height_m',title="Height by Species") if 'height_m' in df else None
    st.plotly_chart(fig1)
    if fig2: st.plotly_chart(fig2)

with t5:
    st.data_editor(df,num_rows='dynamic')
    csv=df.to_csv(index=False).encode()
    st.download_button("Download CSV",csv,"trees.csv",mime='text/csv')

st.caption("*Built with Streamlit & Plotly* 🌿")
