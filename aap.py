        # Load User File with robust error handling
        try:
            if uploaded_file.name.endswith('.csv'):
                try:
                    df_original = pd.read_csv(uploaded_file, encoding='utf-8')
                except UnicodeDecodeError:
                    df_original = pd.read_csv(uploaded_file, encoding='latin1')
            else:
                df_original = pd.read_excel(uploaded_file)
            
            st.sidebar.success("File successfully uploaded!")
        except Exception as file_error:
            st.error(f"File read error: {file_error}. Please check if the file format is correct.")
            st.stop()
            
