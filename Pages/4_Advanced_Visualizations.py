import streamlit as st
import plotly.express as px
from utils import load_data, apply_global_styles, render_sidebar

st.set_page_config(page_title="Advanced Visualizations", page_icon="🗺️", layout="wide")
apply_global_styles()

with st.spinner("Fetching all data from MongoDB..."):
    df = load_data()

if df.empty:
    st.warning("No data found or failed to connect to the database. Please check your connection and secrets configuration.")
    st.stop()

filtered_df = render_sidebar(df)

st.title("🗺️ Geospatial & Advanced Visualizations")
st.markdown("Explore deep dives into geographical data and hierarchical property structures.")

# --- 1. Geography Map ---
st.subheader("Global Listings Geography Map")
st.markdown("Displays the physical location of listings. Size represents number of reviews, color represents room type.")
if 'Latitude' in filtered_df.columns and 'Longitude' in filtered_df.columns and not filtered_df.empty:
    # Filter out empty or (0,0) coordinates just in case
    map_df = filtered_df[(filtered_df['Latitude'] != 0) & (filtered_df['Longitude'] != 0)]
    
    fig_map = px.scatter_mapbox(
        map_df, 
        lat="Latitude", 
        lon="Longitude", 
        color="Room Type",
        size="Reviews",
        hover_name="Name",
        hover_data=["Price ($)", "Rating", "Market"],
        color_discrete_sequence=px.colors.qualitative.Vivid,
        zoom=1,
        mapbox_style="carto-positron"
    )
    fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.info("Not enough geographical data to render the map.")

st.markdown("---")

col1, col2 = st.columns(2)

# --- 2. Sunburst Chart ---
with col1:
    st.subheader("Sunburst: Location & Room Types")
    st.markdown("Hierarchy: Country ➔ Market ➔ Room Type")
    # Sunburst needs counts or values. We'll use a constant '1' to count listings
    sunburst_df = filtered_df.copy()
    sunburst_df['Count'] = 1
    
    fig_sunburst = px.sunburst(
        sunburst_df,
        path=['Country', 'Market', 'Room Type'],
        values='Count',
        color='Country',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_sunburst.update_layout(margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_sunburst, use_container_width=True)

# --- 3. Treemap ---
with col2:
    st.subheader("Treemap: Property & Room Distribution")
    st.markdown("Hierarchy: Property Type ➔ Room Type (Sized by total listings, colored by average price)")
    
    # We aggregate the data to calculate average prices for the treemap color
    treemap_df = filtered_df.groupby(['Property Type', 'Room Type']).agg(
        Count=('Name', 'count'),
        Avg_Price=('Price ($)', 'mean')
    ).reset_index()
    
    # Filter out property types with very few listings to keep the treemap clean
    treemap_df = treemap_df[treemap_df['Count'] > 5]
    
    if not treemap_df.empty:
        fig_treemap = px.treemap(
            treemap_df, 
            path=[px.Constant("All Properties"), 'Property Type', 'Room Type'], 
            values='Count',
            color='Avg_Price', 
            hover_data=['Avg_Price'],
            color_continuous_scale='RdBu_r'
        )
        fig_treemap.update_layout(margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_treemap, use_container_width=True)
    else:
        st.info("Not enough data to display the treemap. Try expanding your filters.")
