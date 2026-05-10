import streamlit as st
import plotly.express as px
from utils import load_data, apply_global_styles, render_sidebar

st.set_page_config(page_title="Property & Host Insights", page_icon="🛏️", layout="wide")
apply_global_styles()

with st.spinner("Fetching all data from MongoDB..."):
    df = load_data()

if df.empty:
    st.warning("No data found or failed to connect to the database. Please check your connection and secrets configuration.")
    st.stop()

filtered_df = render_sidebar(df)

st.title("🛏️ Property & Host Insights")
st.markdown("Understand how property capacity and host status affect the Airbnb ecosystem.")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Superhost Status Distribution")
    host_counts = filtered_df['Superhost'].value_counts().reset_index()
    host_counts.columns = ['Superhost', 'Count']
    fig_host = px.pie(host_counts, values='Count', names='Superhost', hole=0.4, color_discrete_sequence=['#ff5a5f', '#00a699'])
    fig_host.update_layout(margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_host, use_container_width=True)
    
with col2:
    st.subheader("Price vs. Accommodation Capacity")
    fig_acc = px.box(filtered_df, x="Accommodates", y="Price ($)", color="Room Type", color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_acc.update_layout(margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_acc, use_container_width=True)
    
st.subheader("Top Hosts by Number of Listings (in filtered view)")
top_hosts = filtered_df['Host Name'].value_counts().reset_index().head(10)
top_hosts.columns = ['Host Name', 'Total Listings']
fig_top_hosts = px.bar(top_hosts, x='Host Name', y='Total Listings', text='Total Listings', color='Total Listings', color_continuous_scale='Sunset')
fig_top_hosts.update_layout(margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig_top_hosts, use_container_width=True)
