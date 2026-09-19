import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import google.generativeai as genai

# ---------------------------------------------------------
# Page Config - Wide & Clean Excel Layout
# ---------------------------------------------------------
st.set_page_config(
    page_title="Microsoft Excel - AI Enterprise Edition",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# Custom CSS: Authentic MS Excel Desktop UI Styling
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Global Excel Theme */
    .stApp {
        background-color: #f3f3f3;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Top Title Bar (Excel Header Green) */
    .excel-header {
        background-color: #107C41;
        color: white;
        padding: 8px 16px;
        font-size: 16px;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid #0b592e;
    }

    /* Ribbon Tabs Bar */
    .ribbon-menu {
        background-color: #f3f2f1;
        padding: 6px 12px;
        border-bottom: 1px solid #e1dfdd;
    }

    /* Formula Bar Styling */
    .formula-bar-container {
        background-color: #ffffff;
        border: 1px solid #c8c6c4;
        padding: 4px 10px;
        margin: 6px 0px;
        display: flex;
        align-items: center;
        border-radius: 2px;
    }
    .fx-label {
        font-weight: bold;
        color: #107C41;
        font-style: italic;
        padding-right: 10px;
        border-right: 1px solid #e1dfdd;
        margin-right: 10px;
    }

    /* Bottom Status Bar */
    .excel-status-bar {
        background-color: #107C41;
        color: white;
        padding: 4px 15px;
        font-size: 12px;
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        display: flex;
        justify-content: space-between;
        z-index: 999;
    }

    /* Hide default Streamlit padding */
    .block-container {
        padding-top: 0rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Default Sample Data Initialization
# ---------------------------------------------------------
if 'df' not in st.session_state:
    data = {
        "Order ID": [f"IN24010{i:03d}" for i in range(1, 16)],
        "Order Date": ["01-Jan-2024"] * 8 + ["02-Jan-2024"] * 7,
        "Customer Name": ["Aditya Jadhav", "Rajesh Kapoor", "Tanvi Kumar", "Myra Gupta", "Rutuja Kulkarni", 
                         "Aadhya Kadam", "Myra Kadam", "Karan Rathod", "Deepak Yadav", "Mansi Shinde",
                         "Shruti Tiwari", "Prachi Pillai", "Kabir Sharma", "Meera Pawar", "Ishaan Deshmukh"],
        "City": ["Ranchi", "Ranchi", "Kerala", "Uttar Pradesh", "Kerala", "Jharkhand", "Maharashtra", "Gujarat", "Bengaluru", "Kolkata", "Bhopal", "Coimbatore", "Kochi", "Kolkata", "Jaipur"],
        "Category": ["Sports & Fitness", "Home & Kitchen", "Mobiles", "Stationery", "Fashion", "Mobiles", "Home & Kitchen", "Fashion", "Sports", "Fashion", "Electronics", "Electronics", "Fashion", "Electronics", "Home"],
        "Quantity": [3, 1, 1, 1, 3, 1, 1, 1, 1, 5, 2, 1, 1, 3, 1],
        "Unit Price": [5099, 1499, 493, 204, 2799, 11599, 6999, 1999, 1099, 4399, 3899, 53399, 4099, 1899, 1899]
    }
    st.session_state.df = pd.DataFrame(data)

# ---------------------------------------------------------
# Top Header Bar (MS Excel Title)
# ---------------------------------------------------------
st.markdown("""
    <div class="excel-header">
        <div>📊 <b>Sales_Data.xlsx</b> - Excel AI Suite</div>
        <div style="font-size:12px;">👤 Premium License Activated</div>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Ribbon Tabs Header (Excel Ribbon Menu)
# ---------------------------------------------------------
menu_tab = st.radio(
    "",
    ["🏠 Home / Data", "📊 Dashboard Builder", "🤖 Ask ChatGPT / AI", "🧹 Power Query", "🗄️ SQL Engine"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("---")

# ---------------------------------------------------------
# Sidebar for Uploads & API Key
# ---------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Software Settings")
    api_key = st.text_input("🔑 Gemini API Key", type="password", help="Enter Gemini API Key")
    if api_key:
        genai.configure(api_key=api_key)

    uploaded_file = st.file_uploader("📂 Open Excel File (.xlsx, .csv)", type=["csv", "xlsx"])
    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            st.session_state.df = pd.read_csv(uploaded_file)
        else:
            st.session_state.df = pd.read_excel(uploaded_file)
        st.success("File Loaded!")

# ---------------------------------------------------------
# Formula Bar Component (fx)
# ---------------------------------------------------------
selected_cell = "A1"
selected_val = st.session_state.df.iloc[0, 0] if not st.session_state.df.empty else ""

col_cell, col_fx = st.columns([1, 11])
with col_cell:
    st.text_input("Cell", value="A1", disabled=True, label_visibility="collapsed")
with col_fx:
    formula_input = st.text_input("Formula Bar", value=str(selected_val), placeholder="fx Write formula or edit value...", label_visibility="collapsed")

# ---------------------------------------------------------
# TAB 1: Main Excel Sheet / Grid View
# ---------------------------------------------------------
if menu_tab == "🏠 Home / Data":
    st.markdown("##### 📄 Active Worksheet View")
    
    # Interactive Data Grid (Behaves like Excel Spreadsheet)
    edited_df = st.data_editor(
        st.session_state.df,
        num_rows="dynamic",
        use_container_width=True,
        height=480,
        key="excel_grid"
    )
    st.session_state.df = edited_df

# ---------------------------------------------------------
# TAB 2: Dashboard Builder (Popup Window Dialog)
# ---------------------------------------------------------
elif menu_tab == "📊 Dashboard Builder":
    st.subheader("📊 Dashboard & Chart Builder Dialog")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### Chart Controls")
        x_col = st.selectbox("Select Category (X-Axis)", st.session_state.df.columns, index=4)
        y_col = st.selectbox("Select Values (Y-Axis)", st.session_state.df.select_dtypes(include=[np.number]).columns, index=1)
        chart_type = st.selectbox("Chart Style", ["Bar Chart", "Line Chart", "Pie Chart", "Histogram"])
    
    with col2:
        st.markdown("### Visualization Output")
        if chart_type == "Bar Chart":
            fig = px.bar(st.session_state.df, x=x_col, y=y_col, color=x_col, title=f"{y_col} by {x_col}")
        elif chart_type == "Line Chart":
            fig = px.line(st.session_state.df, x=x_col, y=y_col, title=f"{y_col} Trend")
        elif chart_type == "Pie Chart":
            fig = px.pie(st.session_state.df, names=x_col, values=y_col, title=f"Distribution of {y_col}")
        else:
            fig = px.histogram(st.session_state.df, x=x_col, y=y_col)
        
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# TAB 3: Ask ChatGPT / AI Analyst
# ---------------------------------------------------------
elif menu_tab == "🤖 Ask ChatGPT / AI":
    st.subheader("💬 Ask AI Data Analyst")
    query = st.text_input("डेटा से क्या पूछना चाहते हैं? (e.g., 'किस शहर में सबसे ज़्यादा सेल हुई?'):")
    
    if st.button("▶ Execute AI Analysis"):
        if api_key:
            model = genai.GenerativeModel('gemini-1.5-flash')
            context = f"Dataset Columns: {list(st.session_state.df.columns)}\nData Preview:\n{st.session_state.df.head(5).to_string()}"
            response = model.generate_content(f"{context}\n\nQuestion: {query}")
            st.success("💡 **AI Analysis Result:**")
            st.write(response.text)
        else:
            st.warning("⚠️ कृपया बाईं ओर (Sidebar) में अपनी Gemini API Key दर्ज करें।")

# ---------------------------------------------------------
# TAB 4: Power Query / Data Cleaning
# ---------------------------------------------------------
elif menu_tab == "🧹 Power Query":
    st.subheader("🧹 Power Query & Transformation Engine")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Remove Duplicates"):
            st.session_state.df = st.session_state.df.drop_duplicates()
            st.success("Duplicates Removed!")
    with c2:
        if st.button("Drop Missing Values (Nulls)"):
            st.session_state.df = st.session_state.df.dropna()
            st.success("Missing Values Removed!")
    with c3:
        if st.button("Reset Original Data"):
            st.rerun()

    st.dataframe(st.session_state.df, use_container_width=True)

# ---------------------------------------------------------
# Bottom Excel Sheet Tabs
# ---------------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
sheet_tab = st.radio("Worksheets", ["📁 Sheet1 (Sales Data)", "📊 Sheet2 (Summary View)", "➕ Add Sheet"], horizontal=True)

# ---------------------------------------------------------
# Excel Bottom Status Bar
# ---------------------------------------------------------
total_rows = len(st.session_state.df)
total_cols = len(st.session_state.df.columns)
num_cols = st.session_state.df.select_dtypes(include=[np.number]).columns

sum_val = st.session_state.df[num_cols[0]].sum() if len(num_cols) > 0 else 0
avg_val = st.session_state.df[num_cols[0]].mean() if len(num_cols) > 0 else 0

st.markdown(f"""
    <div class="excel-status-bar">
        <div>READY &nbsp;|&nbsp; Rows: {total_rows} &nbsp;|&nbsp; Columns: {total_cols}</div>
        <div>Average: {avg_val:,.2f} &nbsp;|&nbsp; Count: {total_rows} &nbsp;|&nbsp; Sum: {sum_val:,.2f}</div>
    </div>
""", unsafe_allow_html=True)
