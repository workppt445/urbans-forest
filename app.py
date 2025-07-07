
import streamlit as st
import pandas as pd
import plotly.express as px

# Title
st.title("Interactive Urban Forest Explorer")

# Load data
def load_data(path="trees-with-species-and-dimensions-urban-forest.xlsx"):
    df = pd.read_excel(path, sheet_name='Feuil1')
    return df

data = load_data()

# Sidebar filters
st.sidebar.header("Filters")
species_list = data['Common Name'].unique().tolist()
selected = st.sidebar.multiselect("Select species to include:", species_list, default=species_list[:5])

# Filter data
filtered = data[data['Common Name'].isin(selected)]

# Options
st.sidebar.markdown("---")
show_percent = st.sidebar.checkbox("Show percentage labels", value=True)

# Compute counts and percentages
counts = filtered['Common Name'].value_counts().reset_index()
counts.columns = ['Common Name', 'Count']
counts['Percent'] = (counts['Count'] / data.shape[0] * 100).round(1)

# Main chart
st.header("Top Tree Species Distribution")
if show_percent:
    fig = px.bar(counts, x='Common Name', y='Count', text='Percent',
                 labels={'Count':'Number of Trees', 'Common Name':'Tree Species'},
                 title="Interactive Bar Chart of Tree Species")
    fig.update_traces(texttemplate='%{text}%')
else:
    fig = px.bar(counts, x='Common Name', y='Count',
                 labels={'Count':'Number of Trees', 'Common Name':'Tree Species'},
                 title="Interactive Bar Chart of Tree Species")
st.plotly_chart(fig, use_container_width=True)

# Data table
st.header("Data Preview")
st.dataframe(filtered.head(20))

# Export
st.markdown("---")
if st.button("Download filtered data as CSV"):
    csv = filtered.to_csv(index=False)
    st.download_button(label="Download CSV", data=csv, file_name="filtered_trees.csv", mime="text/csv")

st.markdown("\n---\n*Built with Streamlit & Plotly* 🏞️")
