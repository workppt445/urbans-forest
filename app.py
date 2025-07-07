import streamlit as st
import pandas as pd
import plotly.express as px
import random

# --- Interactive Urban Forest Explorer with Secret Pin ---

# Page configuration
st.set_page_config(
    page_title="Fun Urban Forest Explorer",
    page_icon="🌳",
    layout="centered",
)

# Header
st.title("🌳 Fun Urban Forest Explorer 🌳")
st.markdown("Welcome! Explore Melbourne's urban trees with interactive filters and a secret surprise! 🎉")

# Load data
@st.cache_data
def load_data(path="trees-with-species-and-dimensions-urban-forest.xlsx"):
    return pd.read_excel(path, sheet_name='Feuil1')

data = load_data()

# Secret Pin Section
with st.sidebar.expander("🔒 Enter Secret Pin", expanded=False):
    pin_input = st.text_input("Type the secret code and press Enter:")
    if pin_input == "7477":
        st.success("✨ Thank you for entering the secret pin! Good luck for being cool! ✨")
    elif pin_input:
        st.error("❌ Incorrect code. Try again!")

# Sidebar - Filters & Options
st.sidebar.header("Filter Your View")
species_choices = data['Common Name'].unique().tolist()
selected_species = st.sidebar.multiselect(
    "Select tree species:", species_choices, default=species_choices[:5]
)

year_min, year_max = st.sidebar.slider(
    "Filter by planting year range:",
    int(data['Year Planted'].min()), int(data['Year Planted'].max()),
    (2000, 2020)
)

show_percent = st.sidebar.checkbox("Show percentages on bars", value=True)

# Apply filters
filtered = data[
    data['Common Name'].isin(selected_species) &
    data['Year Planted'].between(year_min, year_max)
]

# Summary stats
total_visible = len(filtered)
st.subheader(f"Displaying {total_visible} tree records")

# Compute counts and percentages
counts = filtered['Common Name'].value_counts().reset_index()
counts.columns = ['Common Name', 'Count']
counts['Percent'] = (counts['Count'] / len(data) * 100).round(1)

# Fun random color picker for bars
def random_color():
    return 'rgb({}, {}, {})'.format(random.randint(50,200), random.randint(100,255), random.randint(50,200))
colors = [random_color() for _ in range(len(counts))]

# Plot
st.subheader("📊 Top Species Chart")
if not counts.empty:
    if show_percent:
        fig = px.bar(
            counts, x='Common Name', y='Count', text='Percent',
            labels={'Count':'Number of Trees', 'Common Name':'Tree Species'},
            title="Tree Species Distribution"
        )
        fig.update_traces(marker_color=colors, texttemplate='%{text}%')
    else:
        fig = px.bar(
            counts, x='Common Name', y='Count',
            labels={'Count':'Number of Trees', 'Common Name':'Tree Species'},
            title="Tree Species Distribution"
        )
        fig.update_traces(marker_color=colors)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data matches your filters. Try broadening your selections.")

# Data preview
st.subheader("🔍 Sample Data Preview")
st.dataframe(filtered.sample(min(10, total_visible)))

# Download option
st.markdown("---")
if st.button("Download filtered data as CSV 📥"):
    csv_data = filtered.to_csv(index=False)
    st.download_button("Click to download CSV", csv_data, file_name="filtered_trees.csv")

# Footer
st.markdown("---")
st.caption("*Built with ❤️ using Streamlit & Plotly* 🌿")
