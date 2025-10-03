import os
import pandas as pd
import streamlit as st

# ----------------------------
# 1) Configuration
# ----------------------------
BASE_PATH = r"C:\python\output"

# Explicit mapping of your three files
REPORTS = {
    "City Level Analysis": os.path.join(BASE_PATH, "city level analysis.xlsx"),
    "Delivery Analysis":   os.path.join(BASE_PATH, "delivery_analysis.xlsx"),
    "LMD Insights":        os.path.join(BASE_PATH, "lmd_insights.xlsx"),
}

# ----------------------------
# 2) Streamlit UI
# ----------------------------
st.set_page_config(page_title="Logistics Insights Dashboard", layout="wide")
st.title("📊 Logistics Insights Dashboard")

# Sidebar navigation
report_choice = st.sidebar.radio("Select Report", list(REPORTS.keys()))
file_path = REPORTS[report_choice]

st.subheader(f"Report: {report_choice}")
st.caption(file_path)

if not os.path.exists(file_path):
    st.error(f"File not found: {file_path}")
else:
    try:
        # Load Excel and list sheets
        xls = pd.ExcelFile(file_path)
        sheet_choice = st.selectbox("Select Sheet", xls.sheet_names)

        df = pd.read_excel(file_path, sheet_name=sheet_choice)
        st.dataframe(df, use_container_width=True)

        # KPI metrics if available
        kpi_cols = [c for c in ["On-Time %", "Delayed Non-NDR %", "NDR %"] if c in df.columns]
        if kpi_cols:
            st.markdown("### Key Metrics")
            cols = st.columns(len(kpi_cols))
            for i, col in enumerate(kpi_cols):
                try:
                    val = df[col].iloc[0]
                except Exception:
                    val = "-"
                cols[i].metric(col, val)

        # Quick charts
        if "Total AWBs" in df.columns:
            st.markdown("### Total AWBs by Group")
            st.bar_chart(df.set_index(df.columns[0])["Total AWBs"])

        if "On-Time %" in df.columns:
            st.markdown("### On-Time % by Group")
            vals = df["On-Time %"].astype(str).str.rstrip("%").astype(float)
            st.bar_chart(pd.DataFrame({"On-Time %": vals.values}, index=df[df.columns[0]]))

    except Exception as e:
        st.error(f"Error reading {file_path}: {e}")