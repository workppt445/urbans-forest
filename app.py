import streamlit as st
import pandas as pd
import plotly.express as px
import random

# --- Fun Urban Forest Explorer with Info Panel, Checklist & Secret Pin ---

st.set_page_config(page_title="Urban Forest Explorer+", page_icon="🌳", layout="centered")
st.title("🌳 Fun Urban Forest Explorer 3.0 🌳")
st.markdown("Explore Melbourne's trees with filters, fun facts, and species insights! 🎉")

# Load data
def load_data(path="trees-with-species-and-dimensions-urban-forest.xlsx"):
    return pd.read_excel(path, sheet_name='Feuil1')

@st.cache_data
def get_data():
    return load_data()

data = get_data()

# Static mock species info database
species_info = {
    "London Plane": {
        "Water Needs": "Moderate",
        "Temperature Range": "-5°C to 40°C",
        "Soil Type": "Loamy, well-drained",
        "Fun Fact": "Known for its bark that peels like puzzle pieces."
    },
    "River Red Gum": {
        "Water Needs": "Low",
        "Temperature Range": "0°C to 45°C",
        "Soil Type": "Clay or sandy",
        "Fun Fact": "Can live for hundreds of years in the wild."
    },
    "Golden Elm": {
        "Water Needs": "Medium to high",
        "Temperature Range": "-10°C to 35°C",
        "Soil Type": "Fertile, moist",
        "Fun Fact": "Known for its golden-yellow foliage in autumn."
    }
    # Add more species as needed
}

# Session state
if 'custom_species' not in st.session_state:
    st.session_state.custom_species = []

# Secret PIN
with st.sidebar.expander("🔒 Enter Secret Pin", expanded=False):
    pin = st.text_input("Enter the secret code:", key='pin_input')
    if pin:
        if pin == "7477":
            st.balloons()
            st.success("✨ Secret unlocked! You rock! ✨")
        else:
            st.error("❌ Wrong code, try again.")

# Sidebar Filters
st.sidebar.header("🎛️ Filters & Tools")
species_input = st.sidebar.text_input("Type a species to add:", key='species_text')
if st.sidebar.button("➕ Add to checklist"):
    if species_input and species_input not in st.session_state.custom_species:
        st.session_state.custom_species.append(species_input)

year_min, year_max = st.sidebar.slider(
    "Planting Year Range:",
    int(data['Year Planted'].min()), int(data['Year Planted'].max()),
    (2000, 2020)
)
show_percent = st.sidebar.checkbox("Show % labels on bars", value=True)

if st.sidebar.button("🎲 Surprise me!"):
    st.sidebar.info(random.choice([
        "Melbourne has over 70,000 public trees!",
        "River Red Gums are native and iconic.",
        "Tree roots help fight erosion.",
        "Urban trees cool cities by up to 5°C!"
    ]))

# Filter data
filtered = data[data['Year Planted'].between(year_min, year_max)]
if st.session_state.custom_species:
    filtered = filtered[filtered['Common Name'].isin(st.session_state.custom_species)]

st.subheader(f"📋 Showing {len(filtered)} tree records")

# Bar chart
counts = filtered['Common Name'].value_counts().reset_index()
counts.columns = ['Common Name', 'Count']
counts['Percent'] = (counts['Count'] / len(data) * 100).round(1)
colors = [f"rgb({random.randint(50,200)}, {random.randint(100,255)}, {random.randint(50,200)})" for _ in range(len(counts))]

st.subheader("📊 Your Custom Species Chart")
if not counts.empty:
    fig = px.bar(
        counts, x='Common Name', y='Count', text='Percent' if show_percent else None,
        labels={'Count':'# Trees', 'Common Name':'Species'},
        title="Tree Species Distribution"
    )
    fig.update_traces(marker_color=colors, texttemplate='%{text}%')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data matches your filters or custom list.")

# Checklist
st.subheader("📝 Your Species Checklist")
if st.session_state.custom_species:
    selected_species = st.selectbox("📌 Select a species to view info:", st.session_state.custom_species)
    for name in st.session_state.custom_species:
        st.markdown(f"- ✅ {name}")
else:
    selected_species = None
    st.info("Add species above to start building your list.")

# Species info panel
if selected_species:
    st.markdown("---")
    st.subheader(f"🌿 Info for {selected_species}")
    info = species_info.get(selected_species)
    if info:
        st.markdown(f"""
        **Water Needs**: {info['Water Needs']}  
        **Temp Range**: {info['Temperature Range']}  
        **Soil Type**: {info['Soil Type']}  
        **Fun Fact**: _{info['Fun Fact']}_
        """)
    else:
        st.info("No info available yet for this species. Add it to the database!")

# Data sample
st.subheader("🔍 Sample of Filtered Data")
st.dataframe(filtered.sample(min(10, len(filtered))))

# Download
if st.button("📥 Download filtered data"):
    csv = filtered.to_csv(index=False)
    st.download_button("Download CSV", csv, file_name="my_filtered_trees.csv")

st.markdown("---")
st.caption("Made with 🍃 and ☕ using Streamlit & Plotly – now with species info!")
