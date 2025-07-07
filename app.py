import streamlit as st
import pandas as pd
import plotly.express as px
import random

# --- Fun Urban Forest Explorer with Dynamic Checklist & Secret Pin V2 ---

# Page config
st.set_page_config(page_title="Fun Urban Forest Explorer 2.0", page_icon="🌳", layout="centered")

# Header
st.title("🌳 Fun Urban Forest Explorer 2.0 🌳")
st.markdown("Explore Melbourne's trees with dynamic filters, secret secrets, and your own custom checklist! 🎉")

# Load data
def load_data(path="trees-with-species-and-dimensions-urban-forest.xlsx"):
    return pd.read_excel(path, sheet_name='Feuil1')

@st.cache_data
def get_data():
    return load_data()

data = get_data()

# Initialize session state for custom species list
if 'custom_species' not in st.session_state:
    st.session_state.custom_species = []

# Secret Pin
with st.sidebar.expander("🔒 Enter Secret Pin", expanded=False):
    pin = st.text_input("Enter the secret code:", key='pin_input')
    if pin:
        if pin == "7477":
            st.balloons()
            st.success("✨ Secret unlocked! You rock! ✨")
        else:
            st.error("❌ Wrong code, try again.")

# Sidebar fun options
st.sidebar.header("🎛️ Controls & Filters")
# Input to add custom species
species_input = st.sidebar.text_input("Type a tree species to add:", key='species_text')
if st.sidebar.button("➕ Add to checklist"):
    if species_input and species_input not in st.session_state.custom_species:
        st.session_state.custom_species.append(species_input)

# Year planted slider
year_min, year_max = st.sidebar.slider(
    "Planting Year Range:",
    int(data['Year Planted'].min()), int(data['Year Planted'].max()),
    (2000, 2020)
)
# Toggle percent labels
show_percent = st.sidebar.checkbox("Show percentages on bars", value=True)
# Random fun fact generator
if st.sidebar.button("🎲 Surprise me!"):
    fact = random.choice([
        "Melbourne has over 70,000 street trees!",
        "The oldest recorded tree in Melbourne is over 150 years old.",
        "Native species like River red gum can live over 200 years.",
        "London Plane trees were introduced in the 19th century."
    ])
    st.sidebar.info(f"💡 {fact}")

# Filter data by year and built-in species selection + custom list
def filter_data():
    df = data[data['Year Planted'].between(year_min, year_max)]
    # If custom species exist, filter to those only
    if st.session_state.custom_species:
        df = df[df['Common Name'].isin(st.session_state.custom_species)]
    return df

filtered = filter_data()

# Display record count
st.subheader(f"📋 Showing {len(filtered)} trees")

# Compute counts and percentages
counts = filtered['Common Name'].value_counts().reset_index()
counts.columns = ['Common Name', 'Count']
counts['Percent'] = (counts['Count'] / len(data) * 100).round(1)

# Random bar colors
def random_color():
    return f"rgb({random.randint(50,200)},{random.randint(50,255)},{random.randint(50,200)})"
colors = [random_color() for _ in range(len(counts))]

# Plot chart
st.subheader("📊 Your Custom Species Chart")
if not counts.empty:
    fig = px.bar(
        counts, x='Common Name', y='Count', text='Percent' if show_percent else None,
        labels={'Count':'# Trees', 'Common Name':'Species'}, title="Tree Species Distribution"
    )
    fig.update_traces(marker_color=colors, texttemplate='%{text}%')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data matches your filters or your custom list!")

# Checklist display
st.subheader("📝 Your Species Checklist")
if st.session_state.custom_species:
    for name in st.session_state.custom_species:
        st.markdown(f"- ✅ {name}")
else:
    st.info("Add species above to build your checklist!")

# Data sample
st.subheader("🔍 Sample Data")
st.dataframe(filtered.sample(min(10, len(filtered))))

# Download button
if st.button("📥 Download filtered data CSV"):
    csv = filtered.to_csv(index=False)
    st.download_button("Download CSV", csv, "my_trees.csv")

# Footer
st.markdown("---")
st.caption("*Built with Streamlit & Plotly – now with secrets & checklists!* 🌿")
