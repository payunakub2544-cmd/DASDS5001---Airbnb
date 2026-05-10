# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
import plotly.express as px
from utils import load_data, apply_global_styles, render_sidebar

st.set_page_config(page_title="Availability & Reviews", page_icon="⭐", layout="wide")
apply_global_styles()

with st.spinner("Fetching all data from MongoDB..."):
    df = load_data()

if df.empty:
    st.warning("No data found or failed to connect to the database. Please check your connection and secrets configuration.")
    st.stop()

filtered_df = render_sidebar(df)

st.title("⭐ Availability & Reviews")
st.markdown("Analyze property availability and how guests rate their stays.")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Overall Rating vs. Cleanliness")
    fig_clean = px.scatter(
        filtered_df.dropna(subset=['Rating', 'Cleanliness']), 
        x="Cleanliness", y="Rating", 
        color="Superhost",
        hover_data=["Name"],
        color_discrete_sequence=['#ff5a5f', '#00a699']
    )
    fig_clean.update_layout(margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_clean, use_container_width=True)
    
with col2:
    st.subheader("Property Availability (Days/Year)")
    fig_avail = px.histogram(filtered_df, x="Availability 365", nbins=20, color_discrete_sequence=['#00a699'])
    fig_avail.update_layout(margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_avail, use_container_width=True)
    
st.subheader("Price vs. Rating (Size = Number of Reviews)")
fig_scatter = px.scatter(
        filtered_df.dropna(subset=['Rating']), 
        x="Price ($)", y="Rating", color="Room Type", 
        size="Reviews", hover_data=["Name", "Market"], 
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
fig_scatter.update_layout(margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")
st.subheader("Raw Data View")
st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
