import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Page Configuration
st.set_page_config(
    page_title="Autonomous Data Analytics Super-App",
    page_icon="⚡",
    layout="wide"
)

# Custom Professional Styling
st.markdown("""
    <style>
    .main-title {
        font-size: 32px;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 16px;
        color: #4B5563;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<p class="main-title">⚡ Autonomous Data Analytics Super-App</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">AI-Powered Data Cleaning, Analysis & Visualization Dashboard</p>', unsafe_allow_html=True)

# Sidebar for File Upload
st.sidebar.header("📁 Data Management")
uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel File", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Load Data
        if uploaded_file.name.endswith('.csv'):
            df_original = pd.read_csv(uploaded_file)
        else:
            df_original = pd.read_excel(uploaded_file)
        
        st.sidebar.success("File successfully uploaded!")
        
        df_cleaned = df_original.copy()
        
        # --- SMART AUTO-CLEANING ENGINE ---
        initial_rows = len(df_cleaned)
        df_cleaned = df_cleaned.drop_duplicates()
        duplicates_removed = initial_rows - len(df_cleaned)
        
        missing_before = df_cleaned.isnull().sum().sum()
        for col in df_cleaned.columns:
            if df_cleaned[col].dtype == 'object':
                df_cleaned[col] = df_cleaned[col].fillna('Unknown')
                df_cleaned[col] = df_cleaned[col].astype(str).str.strip()
            else:
                df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].median())
        
        df_cleaned.columns = [str(c).strip().lower().replace(' ', '_') for c in df_cleaned.columns]

        # --- TABS LAYOUT ---
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Before & After Preview", "🧹 Cleaning Report", "📈 Power BI Style Visuals", "📥 Export Cleaned Data"])
        
        with tab1:
            st.subheader("Comparison Dashboard")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🛑 Before Cleaning (Raw Data)")
                st.dataframe(df_original.head(10), use_container_width=True)
                st.info(f"Original Shape: {df_original.shape[0]} rows, {df_original.shape[1]} columns")
            with col2:
                st.markdown("### ✨ After Cleaning (AI Processed)")
                st.dataframe(df_cleaned.head(10), use_container_width=True)
                st.success(f"Cleaned Shape: {df_cleaned.shape[0]} rows, {df_cleaned.shape[1]} columns")

        with tab2:
            st.subheader("🔍 Automated Cleaning Metrics")
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric(label="Duplicate Rows Removed", value=duplicates_removed)
            with m2:
                st.metric(label="Missing Values Fixed", value=int(missing_before))
            with m3:
                st.metric(label="Columns Optimized", value=len(df_cleaned.columns))

        with tab3:
            st.subheader("📈 Power BI & AI Visual Analytics")
            st.write("Generate professional interactive charts instantly without writing formulas or code.")
            
            # Select columns for plotting
            numeric_cols = df_cleaned.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df_cleaned.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if numeric_cols and categorical_cols:
                c1, c2, c3 = st.columns(3)
                with c1:
                    chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart"])
                with c2:
                    x_axis = st.selectbox("Select X-Axis (Category)", categorical_cols)
                with c3:
                    y_axis = st.selectbox("Select Y-Axis (Metric)", numeric_cols)
                
                # Plotly Dynamic Chart Generation
                if chart_type == "Bar Chart":
                    fig = px.bar(df_cleaned, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}", template="plotly_white")
                elif chart_type == "Line Chart":
                    fig = px.line(df_cleaned, x=x_axis, y=y_axis, title=f"{y_axis} over {x_axis}", template="plotly_white")
                elif chart_type == "Scatter Plot":
                    fig = px.scatter(df_cleaned, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}", template="plotly_white")
                elif chart_type == "Pie Chart":
                    fig = px.pie(df_cleaned, names=x_axis, values=y_axis, title=f"Distribution of {y_axis} by {x_axis}", template="plotly_white")
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Your dataset needs at least one numeric and one categorical column to generate charts.")

        with tab4:
            st.subheader("💾 Download Your Cleaned File")
            csv_data = df_cleaned.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Cleaned CSV File",
                data=csv_data,
                file_name="cleaned_professional_data.csv",
                mime="text/csv",
            )

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")

else:
    st.info("👈 Please upload a CSV or Excel file from the sidebar to begin.")
