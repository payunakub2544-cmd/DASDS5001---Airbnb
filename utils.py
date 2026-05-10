# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
# pyrefly: ignore [missing-import]
from pymongo import MongoClient

@st.cache_data(ttl=3600)
def load_data():
    try:
        uri = st.secrets["mongo"]["uri"]
        client = MongoClient(uri)
        db = client['sample_airbnb']
        collection = db['listingsAndReviews']
        
        projection = {
            "name": 1, "property_type": 1, "room_type": 1, "price": 1,
            "bedrooms": 1, "accommodates": 1, "number_of_reviews": 1,
            "review_scores.review_scores_rating": 1,
            "review_scores.review_scores_cleanliness": 1,
            "address.market": 1, "address.country": 1,
            "address.location.coordinates": 1,
            "host.host_name": 1, "host.host_is_superhost": 1,
            "availability.availability_365": 1
        }
        cursor = collection.find({}, projection)
        data = list(cursor)
        
        if not data: return pd.DataFrame()
            
        clean_data = []
        for doc in data:
            review_scores = doc.get("review_scores", {})
            address = doc.get("address", {})
            host = doc.get("host", {})
            availability = doc.get("availability", {})
            
            location = address.get("location", {})
            coords = location.get("coordinates", [0, 0])
            lon = coords[0] if len(coords) >= 1 else 0
            lat = coords[1] if len(coords) >= 2 else 0
            
            clean_data.append({
                "Name": doc.get("name"),
                "Property Type": doc.get("property_type"),
                "Room Type": doc.get("room_type"),
                "Price ($)": float(str(doc.get("price", 0))),
                "Bedrooms": doc.get("bedrooms", 0),
                "Accommodates": doc.get("accommodates", 0),
                "Reviews": doc.get("number_of_reviews", 0),
                "Rating": review_scores.get("review_scores_rating", None),
                "Cleanliness": review_scores.get("review_scores_cleanliness", None),
                "Market": address.get("market", "Unknown"),
                "Country": address.get("country", "Unknown"),
                "Longitude": lon,
                "Latitude": lat,
                "Host Name": host.get("host_name", "Unknown"),
                "Superhost": "Yes" if host.get("host_is_superhost") else "No",
                "Availability 365": availability.get("availability_365", 0)
            })
            
        df = pd.DataFrame(clean_data)
        df['Price ($)'] = pd.to_numeric(df['Price ($)'], errors='coerce')
        df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
        df['Cleanliness'] = pd.to_numeric(df['Cleanliness'], errors='coerce')
        df['Bedrooms'] = pd.to_numeric(df['Bedrooms'], errors='coerce')
        df['Accommodates'] = pd.to_numeric(df['Accommodates'], errors='coerce')
        df['Availability 365'] = pd.to_numeric(df['Availability 365'], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return pd.DataFrame()

def apply_global_styles():
    st.markdown("""
    <style>
        .reportview-container { background: #f0f2f6; }
        .main .block-container { padding-top: 2rem; }
        h1 { color: #ff5a5f; font-family: 'Inter', sans-serif; }
        .metric-card { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); text-align: center; border-top: 4px solid #ff5a5f; }
        .metric-value { font-size: 2rem; font-weight: bold; color: #00a699; }
        .metric-label { font-size: 1rem; color: #484848; font-weight: 600; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

def render_sidebar(df):
    st.sidebar.header("Global Filters")
    
    countries = df['Country'].dropna().unique().tolist()
    countries.sort()

    room_types = df['Room Type'].dropna().unique().tolist()

    min_price, max_price = int(df['Price ($)'].min()), int(df['Price ($)'].max())
    slider_max = min(max_price, 2000)

    # Initialize session state for persistent filters
    if "global_countries" not in st.session_state:
        st.session_state.global_countries = countries
    if "global_room_types" not in st.session_state:
        st.session_state.global_room_types = room_types
    if "global_price_range" not in st.session_state:
        st.session_state.global_price_range = (min_price, slider_max)

    def sync_filters():
        st.session_state.global_countries = st.session_state._countries
        st.session_state.global_room_types = st.session_state._rooms
        st.session_state.global_price_range = st.session_state._price

    selected_countries = st.sidebar.multiselect(
        "Select Country", 
        options=countries, 
        default=st.session_state.global_countries,
        key="_countries",
        on_change=sync_filters
    )

    selected_room_types = st.sidebar.multiselect(
        "Select Room Type", 
        options=room_types, 
        default=st.session_state.global_room_types,
        key="_rooms",
        on_change=sync_filters
    )

    price_range = st.sidebar.slider(
        "Price Range ($)", 
        min_price, slider_max, 
        value=st.session_state.global_price_range,
        key="_price",
        on_change=sync_filters
    )

    filtered_df = df[
        (df['Country'].isin(selected_countries)) & 
        (df['Room Type'].isin(selected_room_types)) &
        (df['Price ($)'] >= price_range[0]) & 
        (df['Price ($)'] <= price_range[1])
    ]
    
    st.sidebar.markdown("---")
    @st.cache_data
    def convert_df(dataframe):
        return dataframe.to_csv(index=False).encode('utf-8-sig')

    csv = convert_df(df)
    st.sidebar.download_button(
        label="📥 Download Full Dataset (CSV)",
        data=csv,
        file_name='airbnb_full_data.csv'
    )
    
    return filtered_df
