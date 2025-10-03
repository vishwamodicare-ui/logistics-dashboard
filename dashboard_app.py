import os
import pandas as pd
import streamlit as st

# Get the folder where this script is running
BASE_DIR = os.path.dirname(__file__)

# Build file paths relative to the app folder
city_file = os.path.join(BASE_DIR, "city level analysis.xlsx")
delivery_file = os.path.join(BASE_DIR, "delivery_analysis.xlsx")
lmd_file = os.path.join(BASE_DIR, "lmd_insights.xlsx")

# Load the Excel files
df_city = pd.read_excel(city_file)
df_delivery = pd.read_excel(delivery_file)
df_lmd = pd.read_excel(lmd_file)

# Example Streamlit UI
st.title("Logistics Insights Dashboard")

report = st.sidebar.selectbox(
    "Select Report",
    ["City Level Analysis", "Delivery Analysis", "LMD Insights"]
)

if report == "City Level Analysis":
    st.subheader("City Level Analysis")
    st.dataframe(df_city)

elif report == "Delivery Analysis":
    st.subheader("Delivery Analysis")
    st.dataframe(df_delivery)

elif report == "LMD Insights":
    st.subheader("LMD Insights")
    st.dataframe(df_lmd)