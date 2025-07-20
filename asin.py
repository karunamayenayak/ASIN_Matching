import streamlit as st
import pandas as pd

st.title("CSV Column Updater with ASIN Matching")

# File uploader
main_file = st.file_uploader("Upload your main CSV file", type="csv")

# Detect and reload if a new file is uploaded
if main_file:
    if 'last_uploaded_filename' not in st.session_state or st.session_state.last_uploaded_filename != main_file.name:
        st.session_state.main_df = pd.read_csv(main_file)
        st.session_state.last_uploaded_filename = main_file.name
        st.success(f"New file '{main_file.name}' uploaded successfully!")

# Proceed only if DataFrame is loaded
if 'main_df' in st.session_state:
    main_df = st.session_state.main_df

    st.write("Main File Preview:")
    st.write(main_df.head())

    # Validate required columns
    required_cols = ['asin', 'marketplace', 'correctedLabel', 'asinLabel']
    if not all(col in main_df.columns for col in required_cols):
        st.error("The CSV must contain 'asin', 'marketplace', 'correctedLabel', and 'asinLabel' columns.")
    else:
        # User inputs
        asin_input = st.text_area("Enter ASIN IDs (separated by new lines)")
        country_id = st.text_input("Enter Marketplace ID")
        update_text = st.text_input("Enter text to update in 'correctedLabel'")

        if st.button("Update Column"):
            if asin_input and country_id and update_text:
                asin_list = [x.strip() for x in asin_input.split('\n') if x.strip()]
                condition = (main_df['asin'].isin(asin_list)) & (main_df['marketplace'].astype(str) == country_id)

                st.session_state.main_df.loc[condition, 'correctedLabel'] = update_text
                st.success(f"Updated {condition.sum()} row(s).")

                st.write("Updated Preview:")
                st.write(st.session_state.main_df.head())
            else:
                st.error("Please enter all the required fields.")

        # Button to fill remaining empty correctedLabel with asinLabel values
        if st.button("Fill remaining with asinLabel"):
            fill_condition = st.session_state.main_df['correctedLabel'].isna() | (st.session_state.main_df['correctedLabel'].astype(str).str.strip() == "")
            st.session_state.main_df.loc[fill_condition, 'correctedLabel'] = st.session_state.main_df.loc[fill_condition, 'asinLabel']
            st.success(f"Filled {fill_condition.sum()} remaining rows in 'correctedLabel' from 'asinLabel'.")

            st.write("Final Preview:")
            st.write(st.session_state.main_df.head())

        # Prepare download with same file name
        csv = st.session_state.main_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Full Updated CSV",
            data=csv,
            file_name=st.session_state.last_uploaded_filename,
            mime='text/csv'
        )
