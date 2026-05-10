import streamlit as st

pg = st.navigation([
    st.Page("1_Market_Overview.py", title="Market Overview", default=True),
    st.Page("pages/2_Property_and_Host_Insights.py", title="Property and Host Insights"),
    st.Page("pages/3_Availability_and_Reviews.py", title="Availability and Reviews"),
    st.Page("pages/4_Advanced_Visualizations.py", title="Advanced Visualizations"),
])
pg.run()