import os
import pandas as pd
import streamlit as st

# -----------------------------
# App config
# -----------------------------
st.set_page_config(
    page_title="Logistics Insights Dashboard",
    page_icon="📦",
    layout="wide"
)

# -----------------------------
# File mapping
# -----------------------------
BASE_DIR = os.path.dirname(__file__)

FILES = {
    "City Level Analysis": "city level analysis.xlsx",
    "Delivery Analysis": "delivery_analysis.xlsx",
    "LMD Insights": "lmd_insights.xlsx",
}

# -----------------------------
# Load all sheets from Excel
# -----------------------------
@st.cache_data
def load_excel_all_sheets(file_name):
    path = os.path.join(BASE_DIR, file_name)
    if not os.path.exists(path):
        return {}
    try:
        xls = pd.ExcelFile(path, engine="openpyxl")
        sheets = {}
        for sheet in xls.sheet_names:
            try:
                df = pd.read_excel(xls, sheet_name=sheet, engine="openpyxl")
                sheets[sheet.strip()] = df  # strip spaces from sheet names
            except Exception as e:
                sheets[sheet.strip()] = pd.DataFrame({"Error": [str(e)]})
        return sheets
    except Exception as e:
        return {}

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("Controls")

# Step 1: Choose report
report = st.sidebar.selectbox("Select Report", list(FILES.keys()))

# Step 2: Load sheets
sheets = load_excel_all_sheets(FILES[report])

# Step 3: Debug panel
with st.sidebar.expander("🛠 Debug Info", expanded=True):
    st.write("📋 Detected sheets:", list(sheets.keys()))
    st.write(f"✅ Total sheets loaded: {len(sheets)}")

# Step 4: Stop if no sheets found
if not sheets:
    st.sidebar.warning("⚠️ No sheets found in this file.")
    st.stop()

# -----------------------------
# Main UI
# -----------------------------
st.title("📊 Logistics Insights Dashboard")
st.caption(f"{report} — {len(sheets)} sheets")

# Create tabs for each sheet
sheet_tabs = st.tabs(list(sheets.keys()))

for tab, sheet_name in zip(sheet_tabs, sheets.keys()):
    df = sheets[sheet_name]
    with tab:
        st.subheader(f"📄 Sheet: {sheet_name}")

        # KPIs if numeric columns exist
        num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        if num_cols:
            cols = st.columns(min(4, len(num_cols)))
            for i, col in enumerate(num_cols[:4]):
                with cols[i]:
                    st.metric(col, f"{df[col].sum():,.0f}")

        # Tabs for Summary and Raw Data
        subtab1, subtab2 = st.tabs(["📈 Summary", "📋 Raw Data"])

        with subtab1:
            st.subheader("Quick Summary")
            if num_cols:
                st.bar_chart(df[num_cols[0]])
            else:
                st.info("No numeric columns to chart.")

        with subtab2:
            st.subheader("Raw Data")
            st.dataframe(df, use_container_width=True)