import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import google.generativeai as genai

# ---------------------------------------------------------
# Page Configuration & Styling (Excel Ribbon Theme)
# ---------------------------------------------------------
st.set_page_config(
    page_title="XLBooster AI Suite",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for Excel Layout & Modern Ribbon UI
st.markdown("""
    <style>
    .stApp {
        background-color: #f3f2f1;
    }
    .ribbon-bar {
        background-color: #ffffff;
        padding: 10px 15px;
        border-bottom: 2px solid #e1dfdd;
        margin-bottom: 15px;
        border-radius: 6px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 4px;
        height: 42px;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# Session State for Sample Data and Modal Popups
if 'df' not in st.session_state:
    data = {
        "Order ID": [f"IN24010{i:03d}" for i in range(1, 21)],
        "Order Date": ["01-Jan-2024"] * 10 + ["02-Jan-2024"] * 10,
        "Customer ID": [f"CUST{1000+i}" for i in range(20)],
        "Customer Name": ["Aditya Jadhav", "Rajesh Kapoor", "Tanvi Kumar", "Myra Gupta", "Rutuja Kulkarni", 
                         "Aadhya Kadam", "Myra Kadam", "Karan Rathod", "Deepak Yadav", "Mansi Shinde",
                         "Shruti Tiwari", "Prachi Pillai", "Kabir Sharma", "Meera Pawar", "Ishaan Deshmukh",
                         "Reyansh Deshmukh", "Ayaan Kulkarni", "Swati Deshmukh", "Siddharth Mishra", "Nisha Bhatia"],
        "City": ["Ranchi", "Ranchi", "Kerala", "Uttar Pradesh", "Kerala", "Jharkhand", "Maharashtra", "Gujarat", "Bengaluru", "Kolkata",
                 "Bhopal", "Coimbatore", "Kochi", "Kolkata", "Kolkata", "Jaipur", "Ranchi", "Jharkhand", "Coimbatore", "Jaipur"],
        "Category": ["Sports & Fitness", "Home & Kitchen", "Mobiles & Accessories", "Books & Stationery", "Fashion",
                     "Mobiles & Accessories", "Home & Kitchen", "Fashion", "Sports & Fitness", "Fashion",
                     "Home & Kitchen", "Electronics", "Fashion", "Electronics", "Sports & Fitness", "Home & Kitchen",
                     "Electronics", "Home & Kitchen", "Mobiles & Accessories", "Home & Kitchen"],
        "Product": ["Fitness Band", "Cookware Set", "Tempered Glass", "Kids Story Book", "Women Kurti",
                    "Smart Watch", "Mixer Grinder", "Jeans", "Cricket Bat", "Handbag",
                    "Air Fryer", "LED TV", "Handbag", "Wireless Mouse", "Yoga Mat", "Pressure Cooker",
                    "Keyboard", "Mixer Grinder", "Power Bank", "Cookware Set"],
        "Quantity": [3, 1, 1, 1, 3, 1, 1, 1, 1, 5, 2, 1, 1, 3, 1, 1, 1, 1, 1, 1],
        "Unit Price": [5099, 1499, 493, 204, 2799, 11599, 6999, 1999, 1099, 4399, 3899, 53399, 4099, 1899, 1899, 1899, 1200, 6999, 1499, 2499]
    }
    st.session_state.df = pd.DataFrame(data)

# ---------------------------------------------------------
# Sidebar - API Key Configuration
# ---------------------------------------------------------
st.sidebar.title("🔑 Configuration")
api_key = st.sidebar.text_input("Google Gemini API Key", type="password", help="अपडेटेड Gemini API Key डालें।")

if api_key:
    genai.configure(api_key=api_key)

uploaded_file = st.sidebar.file_uploader("Upload Excel/CSV Data", type=["csv", "xlsx"])
if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        st.session_state.df = pd.read_csv(uploaded_file)
    else:
        st.session_state.df = pd.read_excel(uploaded_file)
    st.sidebar.success("डेटा लोड हो गया!")

# ---------------------------------------------------------
# Ribbon Toolbar Header (Inspired by XLBooster Screen)
# ---------------------------------------------------------
st.markdown("<h3 style='margin-bottom:0px;'>📗 XLBooster AI Add-in Suite</h3>", unsafe_allow_html=True)

with st.container():
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        btn_dashboard = st.button("📊 Dashboard Builder")
    with col2:
        btn_ask_ai = st.button("💬 Ask AI / Chat")
    with col3:
        btn_clean = st.button("🧹 Data Cleaner")
    with col4:
        btn_formula = st.button("⚡ AI Formulas")
    with col5:
        btn_stats = st.button("📈 Data Summary")
    with col6:
        btn_export = st.button("📥 Export CSV")

st.markdown("---")

# ---------------------------------------------------------
# Modal Dialogs / Tools Action Handling
# ---------------------------------------------------------

# 1. Dashboard Builder Dialog (Same as Popup in Screenshot)
if btn_dashboard:
    @st.dialog("Dashboard Builder")
    def show_dashboard_dialog():
        st.write("डैशबोर्ड बनाने के लिए फ़ील्ड्स और चार्ट्स चुनें:")
        x_axis = st.selectbox("X-Axis Category Column", st.session_state.df.columns, index=4)
        y_axis = st.selectbox("Y-Axis Numerical Column", st.session_state.df.select_dtypes(include=[np.number]).columns, index=1)
        chart_type = st.selectbox("Chart Type", ["Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot"])
        
        if st.button("OK / Generate Dashboard", type="primary"):
            st.session_state.active_chart = (chart_type, x_axis, y_axis)
            st.rerun()

    show_dashboard_dialog()

# 2. Ask AI Dialog
if btn_ask_ai:
    @st.dialog("Ask AI Analyst")
    def show_ai_dialog():
        query = st.text_input("डेटा से संबंधित सवाल लिखें:")
        if st.button("Submit Query"):
            if api_key:
                model = genai.GenerativeModel('gemini-1.5-flash')
                context = f"Data Summary:\n{st.session_state.df.head(5).to_string()}"
                response = model.generate_content(f"{context}\n\nQuestion: {query}")
                st.success(response.text)
            else:
                st.warning("कृपया Sidebar में Gemini API Key दर्ज करें।")

    show_ai_dialog()

# Render Chart if Generated
if 'active_chart' in st.session_state:
    chart_type, x_axis, y_axis = st.session_state.active_chart
    st.subheader(f"📌 Generated {chart_type}: {y_axis} by {x_axis}")
    
    if chart_type == "Bar Chart":
        fig = px.bar(st.session_state.df, x=x_axis, y=y_axis, color=x_axis)
    elif chart_type == "Line Chart":
        fig = px.line(st.session_state.df, x=x_axis, y=y_axis)
    elif chart_type == "Pie Chart":
        fig = px.pie(st.session_state.df, names=x_axis, values=y_axis)
    else:
        fig = px.scatter(st.session_state.df, x=x_axis, y=y_axis)
        
    st.plotly_chart(fig, use_container_width=True)
    if st.button("Close Chart View"):
        del st.session_state.active_chart
        st.rerun()

# ---------------------------------------------------------
# Interactive Data Grid (Excel Like Table Sheet)
# ---------------------------------------------------------
st.subheader("📑 Active Worksheet: Data Preview")
edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True,
    height=450
)

# Update state if edited directly in Grid
st.session_state.df = edited_df
