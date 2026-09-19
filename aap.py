import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
import duckdb
import io

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="All-in-One Data Analytics Suite",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp header {
        background-color: transparent;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Navigation & Setup
# ---------------------------------------------------------
st.sidebar.title("📊 AI Analytics Suite")
st.sidebar.markdown("---")

api_key = st.sidebar.text_input("🔑 Google Gemini API Key", type="password", help="अपनी Gemini API Key दर्ज करें।")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

tool_choice = st.sidebar.radio(
    "🛠️ चुनें टूल (Select Tool):",
    [
        "📂 Excel / CSV Manager",
        "🧹 Power Query (Data Clean)",
        "🗄️ SQL Engine",
        "📊 Power BI / Tableau (Viz)",
        "🤖 Ask AI Analyst"
    ]
)

st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("📁 फ़ाइल अपलोड करें (CSV / Excel)", type=["csv", "xlsx"])

# Load Data Helper
@st.cache_data
def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

df = None
if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
        st.sidebar.success(f"✅ फ़ाइल सफलतापूर्वक लोड हुई! ({df.shape[0]} Rows, {df.shape[1]} Cols)")
    except Exception as e:
        st.sidebar.error(f"फ़ाइल लोड करने में त्रुटि: {e}")

# ---------------------------------------------------------
# 1. EXCEL / CSV MANAGER
# ---------------------------------------------------------
if tool_choice == "📂 Excel / CSV Manager":
    st.title("📂 Excel & CSV Manager")
    st.write("यहाँ अपने डेटा का अवलोकन करें, फ़िल्टर करें और सारांश प्राप्त करें।")

    if df is not None:
        tab1, tab2, tab3 = st.tabs(["📋 Data Preview", "🔢 Summary Stats", "📌 Pivot Table"])

        with tab1:
            st.subheader("डेटा की झलक (Data Preview)")
            st.dataframe(df.head(100), use_container_width=True)

        with tab2:
            st.subheader("संख्यात्मक सांख्यिकी (Summary Statistics)")
            st.dataframe(df.describe().T, use_container_width=True)

        with tab3:
            st.subheader("पिवट टेबल (Pivot Table Creator)")
            col1, col2, col3 = st.columns(3)
            with col1:
                index_col = st.selectbox("Row (Index)", options=df.columns)
            with col2:
                values_col = st.selectbox("Values", options=df.select_dtypes(include=[np.number]).columns)
            with col3:
                agg_func = st.selectbox("Aggregation", ["sum", "mean", "count", "min", "max"])

            if st.button("Pivot Table बनाएं"):
                pivot = pd.pivot_table(df, values=values_col, index=index_col, aggfunc=agg_func)
                st.dataframe(pivot, use_container_width=True)
    else:
        st.info("💡 कृपया बाईं ओर (Sidebar) से एक CSV या Excel फ़ाइल अपलोड करें।")

# ---------------------------------------------------------
# 2. POWER QUERY (DATA CLEANING)
# ---------------------------------------------------------
elif tool_choice == "🧹 Power Query (Data Clean)":
    st.title("🧹 Power Query & Data Cleaning Engine")
    st.write("डेटा की सफ़ाई और ट्रांसफ़ॉर्मेशन एक क्लिक में करें।")

    if df is not None:
        working_df = df.copy()
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("⚙️ Cleaning Tools")
            if st.checkbox("डुपलीकेट हटाएं (Remove Duplicates)"):
                before = len(working_df)
                working_df = working_df.drop_duplicates()
                st.success(f"हटाए गए डुपलीकेट पंक्तियाँ: {before - len(working_df)}")

            if st.checkbox("Null Values हटाएं (Drop Missing Values)"):
                working_df = working_df.dropna()
                st.success("सफलतापूर्वक नल वैल्यूज़ हटा दी गईं।")

            if st.checkbox("Null Values भरें (Fill Missing Values)"):
                fill_val = st.text_input("वैल्यू दर्ज करें (e.g. 0 या N/A)", "0")
                working_df = working_df.fillna(fill_val)
                st.success("मिसिंग वैल्यूज भर दी गईं।")

        with col2:
            st.subheader("📊 डेटा क्वालिटी रिपोर्ट")
            missing_data = pd.DataFrame({
                'Column': working_df.columns,
                'Missing Count': working_df.isnull().sum(),
                'Data Type': working_df.dtypes.astype(str)
            })
            st.dataframe(missing_data, use_container_width=True)

        st.markdown("---")
        st.subheader("क्लीन किया हुआ डेटा देखें और डाउनलोड करें")
        st.dataframe(working_df.head(50), use_container_width=True)

        csv_buffer = working_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Cleaned CSV डाउनलोड करें",
            data=csv_buffer,
            file_name="cleaned_data.csv",
            mime="text/csv"
        )
    else:
        st.info("💡 डेटा क्लीनिंग शुरू करने के लिए कृपया फ़ाइल अपलोड करें।")

# ---------------------------------------------------------
# 3. SQL ENGINE
# ---------------------------------------------------------
elif tool_choice == "🗄️ SQL Engine":
    st.title("🗄️ SQL Query Engine (Powered by DuckDB)")
    st.write("टेबल का नाम **`dataset`** मानकर अपनी SQL क्वैरी चलाएं।")

    if df is not None:
        con = duckdb.connect(database=':memory:')
        con.register('dataset', df)

        default_query = "SELECT * FROM dataset LIMIT 10;"
        user_query = st.text_area("SQL Query लिखें:", value=default_query, height=120)

        if st.button("▶️ Run Query"):
            try:
                result = con.execute(user_query).df()
                st.success(f"क्वोरी सफल रही! ({len(result)} परिणाम मिले)")
                st.dataframe(result, use_container_width=True)
            except Exception as e:
                st.error(f"SQL Error: {e}")
    else:
        st.info("💡 SQL का उपयोग करने के लिए पहले फ़ाइल अपलोड करें।")

# ---------------------------------------------------------
# 4. POWER BI / TABLEAU (VISUALIZATION)
# ---------------------------------------------------------
elif tool_choice == "📊 Power BI / Tableau (Viz)":
    st.title("📊 Power BI & Tableau Style Dashboard Builder")
    st.write("इंटरएक्टिव और सुंदर विज़ुअलाइज़ेशन जनरेट करें।")

    if df is not None:
        st.subheader("🎯 KPIs Summary")
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if num_cols:
            kpi_cols = st.columns(min(len(num_cols), 4))
            for i, c in enumerate(num_cols[:4]):
                kpi_cols[i].metric(label=f"Total {c}", value=f"{df[c].sum():,.2f}")

        st.markdown("---")
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("🎨 Chart Controls")
            chart_type = st.selectbox("Chart Type", ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart", "Histogram"])
            x_axis = st.selectbox("X-Axis (Categorical/Date)", options=df.columns)
            y_axis = st.selectbox("Y-Axis (Numeric)", options=df.columns)
            color_by = st.selectbox("Color / Group By (Optional)", options=[None] + list(df.columns))

        with col2:
            st.subheader("📈 Interactive Visualization")
            if chart_type == "Bar Chart":
                fig = px.bar(df, x=x_axis, y=y_axis, color=color_by, title=f"{y_axis} vs {x_axis}")
            elif chart_type == "Line Chart":
                fig = px.line(df, x=x_axis, y=y_axis, color=color_by, title=f"{y_axis} over {x_axis}")
            elif chart_type == "Scatter Plot":
                fig = px.scatter(df, x=x_axis, y=y_axis, color=color_by, title=f"{y_axis} vs {x_axis}")
            elif chart_type == "Pie Chart":
                fig = px.pie(df, names=x_axis, values=y_axis, title=f"Distribution of {y_axis} by {x_axis}")
            elif chart_type == "Histogram":
                fig = px.histogram(df, x=x_axis, color=color_by, title=f"Histogram of {x_axis}")

            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("💡 डैशबोर्ड और चार्ट्स बनाने के लिए फ़ाइल अपलोड करें।")

# ---------------------------------------------------------
# 5. ASK AI ANALYST
# ---------------------------------------------------------
elif tool_choice == "🤖 Ask AI Analyst":
    st.title("🤖 Ask AI Analyst (Natural Language Search)")
    st.write("अपने डेटा से हिंदी या इंग्लिश में सीधे सवाल पूछें।")

    if not api_key:
        st.warning("⚠️ कृपया बाईं ओर (Sidebar) में अपनी Gemini API Key दर्ज करें।")

    if df is not None:
        user_question = st.text_input("अपना सवाल पूछें (e.g. 'मुझे इस डेटा की टॉप 3 मुख्य इनसाइट्स बताओ'):")

        if st.button("🤖 AI से जवाब पूछें"):
            if not api_key:
                st.error("API Key उपलब्ध नहीं है।")
            else:
                with st.spinner("AI डेटा का विश्लेषण कर रहा है..."):
                    context = f"""
                    Dataset Shape: {df.shape}
                    Columns and Types: {df.dtypes.to_dict()}
                    First 5 rows:
                    {df.head(5).to_string()}
                    """
                    prompt = f"""
                    You are an expert Data Analyst AI agent. Answer the user's question accurately based on the provided dataset summary.
                    Dataset Context:
                    {context}

                    User Question: {user_question}
                    """
                    try:
                        response = model.generate_content(prompt)
                        st.subheader("💡 AI का उत्तर:")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"Gemini API Error: {e}")
    else:
        st.info("💡 AI से सवाल पूछने के लिए डेटाफ़ाइल अपलोड करें।")
