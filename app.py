import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random

st.set_page_config(
    page_title="Fun Urban Forest Explorer",
    page_icon="🌳",
    layout="centered"
)

@st.cache_data
def load_data(path="trees-with-species-and-dimensions-urban-forest.xlsx"):
    return pd.read_excel(path, sheet_name=0)

data = load_data()

def random_color():
    return f'rgb({random.randint(50,200)},{random.randint(100,255)},{random.randint(50,200)})'

st.title("🌳 Fun Urban Forest Explorer 🌳")
st.markdown("Welcome! Explore Melbourne's urban trees with interactive filters and a secret surprise! 🎉")

st.sidebar.header("Filters & Options")
species = data['Common Name'].dropna().unique().tolist()
selected_species = st.sidebar.multiselect("Select species:", species, default=species[:5])

year_min, year_max = st.sidebar.slider(
    "Filter by planting year:",
    int(data['Year Planted'].min()),
    int(data['Year Planted'].max()),
    (int(data['Year Planted'].min()), int(data['Year Planted'].max()))
)

pin = st.sidebar.text_input("🔒 Enter Secret Pin:", type="password")
if pin:
    if pin == '7477': st.sidebar.success("✨ Secret code accepted! 🎉")
    else: st.sidebar.error("❌ Incorrect pin.")

filtered = data[
    data['Common Name'].isin(selected_species) &
    data['Year Planted'].between(year_min, year_max)
]

st.subheader(f"Displaying {len(filtered)} of {len(data)} records")

counts = filtered['Common Name'].value_counts().reset_index()
counts.columns = ['Common Name','Count']
counts['Percent'] = (counts['Count']/len(filtered)*100).round(1)
colors = [random_color() for _ in range(len(counts))]
show_pct = st.sidebar.checkbox("Show % labels", True)

chart_type = st.sidebar.selectbox("Chart type:", ["Bar","Pie","Line"])
with st.spinner("Rendering chart..."):
    if counts.empty:
        st.warning("No data matches filters.")
    else:
        if chart_type == 'Bar':
            fig = px.bar(counts, x='Common Name', y='Count', text='Percent' if show_pct else None,
                         title="Tree Species Distribution", labels={'Count':'Number of Trees'})
            fig.update_traces(marker_color=colors, texttemplate='%{text}%')
        elif chart_type == 'Pie':
            fig = px.pie(counts, names='Common Name', values='Count', title="Species Share",
                         hole=0.3, color_discrete_sequence=colors)
        else:
            fig = px.line(counts, x='Common Name', y='Count', title="Trend by Species")
        st.plotly_chart(fig, use_container_width=True)

st.subheader("🔍 Sample Data Preview")
with st.expander("Show sample rows"): 
    st.dataframe(filtered.sample(min(10,len(filtered))))

st.markdown("---")
if st.download_button("Click to download CSV 🗕️", filtered.to_csv(index=False), file_name="trees.csv"):
    pass

st.caption("*Built with Streamlit & Plotly* 🌿")

