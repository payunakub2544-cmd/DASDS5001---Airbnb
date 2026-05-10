import streamlit as st
import plotly.express as px
from utils import load_data, apply_global_styles, render_sidebar

st.set_page_config(page_title="Market Overview", page_icon="🌍", layout="wide")
apply_global_styles()

with st.spinner("Fetching all data from MongoDB..."):
    df = load_data()

if df.empty:
    st.warning("No data found or failed to connect to the database. Please check your connection and secrets configuration.")
    st.stop()

filtered_df = render_sidebar(df)

st.title("🌍 Market Overview")
st.markdown("Analyze high-level pricing and property trends across global markets.")

st.markdown("### 📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
with col1: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(filtered_df):,}</div><div class="metric-label">Total Listings</div></div>', unsafe_allow_html=True)
with col2: st.markdown(f'<div class="metric-card"><div class="metric-value">${filtered_df["Price ($)"].mean():,.0f}</div><div class="metric-label">Average Price</div></div>', unsafe_allow_html=True)
with col3: st.markdown(f'<div class="metric-card"><div class="metric-value">{filtered_df["Rating"].mean():.1f}/100</div><div class="metric-label">Average Rating</div></div>', unsafe_allow_html=True)
with col4: st.markdown(f'<div class="metric-card"><div class="metric-value">{filtered_df["Reviews"].sum():,}</div><div class="metric-label">Total Reviews</div></div>', unsafe_allow_html=True)
    
st.markdown("---")

col_chart1, col_chart2 = st.columns(2)
with col_chart1:
    st.subheader("Price Distribution")
    fig_price = px.histogram(filtered_df, x="Price ($)", nbins=30, color="Room Type", color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_price.update_layout(margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_price, use_container_width=True)
    
with col_chart2:
    st.subheader("Property Types Breakdown")
    prop_counts = filtered_df['Property Type'].value_counts().reset_index()
    prop_counts.columns = ['Property Type', 'Count']
    fig_prop = px.pie(prop_counts.head(7), values='Count', names='Property Type', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
    fig_prop.update_layout(margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_prop, use_container_width=True)
    
st.subheader("Average Price by Market")
market_price = filtered_df.groupby('Market')['Price ($)'].mean().reset_index().sort_values(by='Price ($)', ascending=False).head(15)
fig_market = px.bar(market_price, x='Market', y='Price ($)', color='Price ($)', color_continuous_scale='Viridis')
fig_market.update_layout(margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig_market, use_container_width=True)