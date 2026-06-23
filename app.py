import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="KSP Crime Analytics Dashboard", layout="wide")

st.title("KSP Crime Analytics Dashboard")

uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        st.subheader("Data Preview")
        st.dataframe(df)

        # Checking for required columns
        required_columns = ['Crime Type', 'District']
        if all(col in df.columns for col in required_columns):
            # Filtering
            crime_types = sorted(df['Crime Type'].unique().tolist())
            selected_crime = st.selectbox("Filter by crime type", ["All"] + crime_types)

            if selected_crime != "All":
                filtered_df = df[df['Crime Type'] == selected_crime]
            else:
                filtered_df = df

            st.subheader(f"Filtered Data: {selected_crime}")
            st.dataframe(filtered_df)

            # Visualization
            st.subheader("Crimes by District")
            district_counts = filtered_df['District'].value_counts().reset_index()
            district_counts.columns = ['District', 'Crime Count']

            fig = px.bar(
                district_counts,
                x='District',
                y='Crime Count',
                title=f"Distribution of {selected_crime} Crimes by District" if selected_crime != "All" else "Distribution of All Crimes by District",
                labels={'Crime Count': 'Number of Crimes', 'District': 'District Name'},
                color='Crime Count',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            missing = [col for col in required_columns if col not in df.columns]
            st.error(f"The uploaded CSV is missing required columns: {', '.join(missing)}")
            st.info("Please ensure your CSV has 'Crime Type' and 'District' columns.")

    except Exception as e:
        st.error(f"Error processing the file: {e}")
else:
    st.info("Waiting for CSV upload...")
