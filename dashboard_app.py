import os
import io
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
# Helpers
# -----------------------------
BASE_DIR = os.path.dirname(__file__)

FILES = {
    "City Level Analysis": "city level analysis.xlsx",
    "Delivery Analysis": "delivery_analysis.xlsx",
    "LMD Insights": "lmd_insights.xlsx",
}

SAFE_NUM_COLS = [
    "Total_AWBs",
    "Total_Invoice_Value",
    "Total_Weight",
    "Total_Shipments",
    "Delivered",
    "In_Transit",
    "RTO",
]

GROUP_COL_CANDIDATES = [
    "courier name",
    "Courier Name",
    "courier",
    "mcnsname",
    "location",
    "city",
    "warehouse",
]

@st.cache_data(show_spinner=True)
def load_workbook_all_sheets(path: str) -> dict:
    """Return dict: {sheet_name: DataFrame}. Empty dict if file not found."""
    if not os.path.exists(path):
        return {}
    try:
        # engine=None lets pandas choose (xlrd/openpyxl depending on file)
        sheets = pd.read_excel(path, sheet_name=None)
        # Normalize column names for safer downstream usage
        normalized = {}
        for sname, df in sheets.items():
            df = df.copy()
            df.columns = [str(c).strip() for c in df.columns]
            normalized[sname] = df
        return normalized
    except Exception as e:
        st.warning(f"Could not read {os.path.basename(path)}: {e}")
        return {}

def find_first_existing_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    cols_lower = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]
    return None

def format_number(n):
    try:
        return f"{float(n):,.0f}"
    except Exception:
        return "-"

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    out = io.StringIO()
    df.to_csv(out, index=False)
    return out.getvalue().encode("utf-8")

# -----------------------------
# Sidebar: report and sheet selection
# -----------------------------
st.sidebar.header("Controls")

report = st.sidebar.selectbox(
    "Select report",
    list(FILES.keys()),
    index=0
)

file_path = os.path.join(BASE_DIR, FILES[report])
sheets = load_workbook_all_sheets(file_path)

if not sheets:
    st.error(f"File not found or unreadable: {file_path}")
    st.stop()

sheet_name = st.sidebar.selectbox(
    "Select sheet",
    list(sheets.keys()),
    index=0
)

df = sheets[sheet_name].copy()

# -----------------------------
# Optional sidebar filters (auto-detected)
# -----------------------------
# Build lightweight filter controls only for categorical columns
cat_cols = [c for c in df.columns if df[c].dtype == "object" and df[c].nunique() <= 50]
num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

if cat_cols:
    with st.sidebar.expander("Filters", expanded=False):
        for col in cat_cols:
            unique_vals = sorted([str(x) for x in df[col].dropna().unique()])
            selected = st.multiselect(f"{col}", unique_vals, default=unique_vals[:10] if len(unique_vals) > 10 else unique_vals)
            if selected and len(selected) != len(unique_vals):
                df = df[df[col].astype(str).isin(selected)]

# -----------------------------
# Header
# -----------------------------
st.title("📊 Logistics Insights Dashboard")
st.caption(f"{report} • {sheet_name}")

# -----------------------------
# KPI row (auto-detect common numeric fields)
# -----------------------------
kpi_cols = [c for c in SAFE_NUM_COLS if c in df.columns]
if kpi_cols:
    cols = st.columns(min(4, len(kpi_cols)))
    for i, col_name in enumerate(kpi_cols[:4]):
        with cols[i]:
            st.metric(col_name.replace("_", " "), format_number(df[col_name].sum()))
else:
    st.info("No standard KPI columns found (e.g., Total_AWBs, Total_Invoice_Value). Showing data and charts below.")

# -----------------------------
# Tabs: Summary, Breakdown, Raw data
# -----------------------------
tab_summary, tab_breakdown, tab_raw = st.tabs(["📈 Summary", "🧭 Breakdown", "📋 Raw data"])

# -------- Summary: quick charts on auto-detected group column --------
with tab_summary:
    st.subheader("Summary")
    if not df.empty:
        # Try to find a sensible grouping column automatically
        group_col = find_first_existing_column(df, GROUP_COL_CANDIDATES)
        value_col = None

        # Prefer Total_AWBs or Total_Invoice_Value for value
        for cand in ["Total_AWBs", "Total_Invoice_Value"]:
            if cand in df.columns and pd.api.types.is_numeric_dtype(df[cand]):
                value_col = cand
                break

        if group_col and value_col:
            # Build a clean aggregation
            agg = df.groupby(group_col, dropna=False)[value_col].sum().reset_index()
            agg = agg.sort_values(value_col, ascending=False).head(25)

            c1, c2 = st.columns([2, 1])
            with c1:
                st.bar_chart(agg.set_index(group_col)[value_col])

            with c2:
                st.write("Top groups")
                st.dataframe(
                    agg.style.format({value_col: "{:,.0f}"}),
                    use_container_width=True,
                    height=420
                )
        else:
            st.info("Couldn’t auto-detect a suitable group/value column for charts. Use Raw data or Breakdown tabs.")

    else:
        st.warning("No rows in this sheet after filters.")

# -------- Breakdown: user chooses columns to analyze --------
with tab_breakdown:
    st.subheader("Breakdown")
    if df.empty:
        st.warning("No rows to analyze.")
    else:
        # Select group/value columns manually
        group_by_col = st.selectbox("Group by", options=df.columns, index=0)
        value_col_b = st.selectbox(
            "Value (numeric)",
            options=[c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])],
        )
        if value_col_b:
            agg = df.groupby(group_by_col, dropna=False)[value_col_b].sum().reset_index()
            agg = agg.sort_values(value_col_b, ascending=False)
            st.bar_chart(agg.set_index(group_by_col)[value_col_b])
            st.dataframe(
                agg.style.format({value_col_b: "{:,.0f}"}),
                use_container_width=True,
            )

# -------- Raw data: table + export --------
with tab_raw:
    st.subheader("Raw data")
    st.dataframe(df, use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            label="⬇️ Download this sheet as CSV",
            data=df_to_csv_bytes(df),
            file_name=f"{report}__{sheet_name}.csv",
            mime="text/csv",
        )
    with c2:
        st.download_button(
            label="⬇️ Download entire workbook (all sheets) as CSV bundle",
            data=df_to_csv_bytes(pd.concat(sheets.values(), axis=0, ignore_index=True)),
            file_name=f"{report}__all_sheets_concat.csv",
            mime="text/csv",
        )

# -----------------------------
# Footer / info
# -----------------------------
with st.expander("ℹ️ Notes"):
    st.write(
        "- Place the Excel files in the same folder as this app file."
        "\n- Columns and sheets are auto-detected; charts appear when numeric and grouping columns are available."
        "\n- Use the Filters in the sidebar to narrow down categorical fields."
    )