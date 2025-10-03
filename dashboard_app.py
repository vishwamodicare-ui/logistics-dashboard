import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Logistics Insights Dashboard", page_icon="📦", layout="wide")

BASE_DIR = os.path.dirname(__file__)

FILES = {
    "City Level Analysis": "city level analysis.xlsx",
    "Delivery Analysis": "delivery_analysis.xlsx",
    "LMD Insights": "lmd_insights.xlsx",
}

@st.cache_data
def load_excel_all_sheets(file_name):
    """Load ALL sheet names explicitly, even hidden/empty ones."""
    path = os.path.join(BASE_DIR, file_name)
    if not os.path.exists(path):
        return {}
    xls = pd.ExcelFile(path, engine="openpyxl")  # force openpyxl for modern Excel
    sheets = {}
    for sheet in xls.sheet_names:   # loop through every sheet name
        try:
            df = pd.read_excel(xls, sheet_name=sheet, engine="openpyxl")
            sheets[sheet] = df
        except Exception as e:
            # If sheet is empty or unreadable, still include it
            sheets[sheet] = pd.DataFrame({"Error": [str(e)]})
    return sheets
st.sidebar.write("📋 Detected sheets:", list(sheets.keys()))

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Controls")

report = st.sidebar.selectbox("Select Report", list(FILES.keys()))
sheets = load_excel_all_sheets(FILES[report])
st.sidebar.write("📋 Detected sheets:", list(sheets.keys()))

if not sheets:
    st.error(f"No sheets found in {FILES[report]}")
    st.stop()

# ✅ Dropdown will now list *all* sheet names
sheet_name = st.sidebar.selectbox("Select Sheet", list(sheets.keys()))
df = sheets[sheet_name]

# -----------------------------
# Main UI
# -----------------------------
st.title("📊 Logistics Insights Dashboard")
st.caption(f"{report} → {sheet_name}")

num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
if num_cols:
    cols = st.columns(min(4, len(num_cols)))
    for i, col in enumerate(num_cols[:4]):
        with cols[i]:
            st.metric(col, f"{df[col].sum():,.0f}")

tab1, tab2 = st.tabs(["📈 Summary", "📋 Raw Data"])

with tab1:
    st.subheader("Quick Summary")
    if num_cols:
        st.bar_chart(df[num_cols[0]])
    else:
        st.info("No numeric columns to chart.")

with tab2:
    st.subheader("Raw Data")
    st.dataframe(df, use_container_width=True)