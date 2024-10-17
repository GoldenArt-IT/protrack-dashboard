import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import matplotlib.pyplot as plt
from st_aggrid import AgGrid, GridOptionsBuilder
from datetime import timedelta, datetime, time as dtime

def main():
    # Set page to always wide
    st.set_page_config(layout="wide")

    st.title("PRODUCTION PLANNER DASHBOARD")

    # Read the Production Progress
    conn1 = st.connection("gsheets", type=GSheetsConnection)
    df = conn1.read(worksheet="PRODUCTION PROGRESS", ttl=300)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.dropna(how="all", axis=0)
    df = df.drop(columns=['IN', 'FR', 'FB', 'WD', 'SP', 'SR', 'SW', 'AS', 'PC'])

    # Read the Data BOM
    conn2 = st.connection("gsheets", type=GSheetsConnection)
    df_bom = conn2.read(worksheet="DATA BOM", ttl=300)
    df_bom = df_bom.loc[:, ~df_bom.columns.str.contains('^Unnamed')]
    df_bom = df_bom.dropna(how="all", axis=0)
    df_bom = df_bom.rename(columns={'CONFIRM MODEL NAME': 'MODEL'})

    # Read Staff Data
    conn3 = st.connection("gsheets", type=GSheetsConnection)
    df_staff = conn3.read(worksheet="STAFF DATA", ttl=300)
    df_staff = df_staff.dropna(how="all", axis=0)

    # Initialize session state to manage selections
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = 'All'
    if 'selected_pi' not in st.session_state:
        st.session_state.selected_pi = []

    # Filter for departments, decoy date and pi selector
    col1, col2, col3 = st.columns(3)

    with col1:
        unique_department = df_staff['DEPARTMENT'].dropna().unique()
        selected_department = st.selectbox("Choose department", unique_department, index=0)

    with col2:
        unique_decoy_date = df['DECOY DATE'].dropna().unique()
        decoy_date_options = ['All'] + list(unique_decoy_date)  # Add 'All' as the default option
        selected_date = st.selectbox("Choose Plan Date", decoy_date_options, index=0, key="selected_date")  # Use session state

    # Filter df based on selected Plan Date, show all if 'All' is selected
    if st.session_state.selected_date != 'All':
        df_filtered_by_date = df[df['DECOY DATE'] == st.session_state.selected_date]
    else:
        df_filtered_by_date = df  # Show all data when 'All' is selected

    with col3:
        unique_pi = df_filtered_by_date['PI NUMBER'].dropna().unique()
        selected_pi = st.multiselect("Select PI Number", unique_pi, key="selected_pi")

    # Further filter df based on selected PI numbers
    if st.session_state.selected_pi:
        df_filtered_by_date = df_filtered_by_date[df_filtered_by_date['PI NUMBER'].isin(st.session_state.selected_pi)]


    # Table Order vs BOM Time logic based on department selection
    if selected_department == 'FRAME':
        df_bom = df_bom[['MODEL', 'FRAME TIME A', 'FRAME TIME B', 'FRAME TIME C', 'FRAME TIME D']]
        df_bom['TOTAL BOM TIME'] = df_bom.iloc[:, -4:].sum(axis=1)
        st.dataframe(df_bom)
    
    if selected_department == 'SPONGE':
        df_bom = df_bom[['MODEL', 'SPONGE TIME A', 'SPONGE TIME B', 'SPONGE TIME C', 'SPONGE TIME D']]
        df_bom['TOTAL BOM TIME'] = df_bom.iloc[:, -4:].sum(axis=1)
        st.dataframe(df_bom)
    
    if selected_department == 'SPRAY':
        df_bom = df_bom[['MODEL', 'SPRAY TIME A', 'SPRAY TIME B', 'SPRAY TIME C', 'SPRAY TIME D']]
        df_bom['TOTAL BOM TIME'] = df_bom.iloc[:, -4:].sum(axis=1)
        st.dataframe(df_bom)

    if selected_department == 'SEWING':
        df_bom = df_bom[['MODEL', 'SEW TIME A', 'SEW TIME B', 'SEW TIME C', 'SEW TIME D']]
        df_bom['TOTAL BOM TIME'] = df_bom.iloc[:, -4:].sum(axis=1)
        st.dataframe(df_bom)

    if selected_department == 'ASSEMBLY':
        df_bom = df_bom[['MODEL', 'ASSEMBLY TIME A', 'ASSEMBLY TIME B', 'ASSEMBLY TIME C', 'ASSEMBLY TIME D']]
        df_bom['TOTAL BOM TIME'] = df_bom.iloc[:, -4:].sum(axis=1)
        st.dataframe(df_bom)

    if selected_department == 'PACKING':
        df_bom = df_bom[['MODEL', 'PACKING TIME A', 'PACKING TIME B', 'PACKING TIME C', 'PACKING TIME D']]
        df_bom['TOTAL BOM TIME'] = df_bom.iloc[:, -4:].sum(axis=1)
        st.dataframe(df_bom)

    if selected_department == 'INTERIOR':
        df_bom = df_bom[['MODEL', 'INT/WEL TIME A', 'INT/WEL TIME B', 'INT/WEL TIME C', 'INT/WEL TIME D']]
        df_bom['TOTAL BOM TIME'] = df_bom.iloc[:, -4:].sum(axis=1)
        st.dataframe(df_bom)

    elif selected_department == 'FABRIC':
        df_bom = df_bom[['MODEL', 'FAB TIME A', 'FAB TIME B', 'FAB TIME C', 'FAB TIME D']]
        numeric_columns = ['FAB TIME A', 'FAB TIME B', 'FAB TIME C', 'FAB TIME D']
        for col in numeric_columns:
            df_bom[col] = pd.to_numeric(df_bom[col], errors='coerce')
        df_bom['TOTAL BOM TIME'] = df_bom[['FAB TIME A', 'FAB TIME B', 'FAB TIME C', 'FAB TIME D']].sum(axis=1)
        st.dataframe(df_bom)

    # Combine filtered production progress data with BOM data
    df_combine_bom = pd.merge(df_filtered_by_date, df_bom[['MODEL', 'TOTAL BOM TIME']], on='MODEL', how='left')
    df_combine_bom[f'TOTAL BOM TIME {selected_department} PER MODEL'] = df_combine_bom['TOTAL BOM TIME']
    df_combine_bom[f'TOTAL BOM TIME {selected_department} x QTY'] = df_combine_bom['QTY'] * df_combine_bom['TOTAL BOM TIME']

    df_combine_bom = df_combine_bom.drop(columns=['TOTAL BOM TIME'])

    # Filter df_staff based on the selected department
    df_staff_filtered = df_staff[df_staff['DEPARTMENT'] == selected_department]

    # Add assigned staff
    st.write("Assign staff to each row:")
    assigned_staff = []
    for i, row in df_combine_bom.iterrows():
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.write(row['PI NUMBER'])
        with col2:
            st.write(row['MODEL'])
        with col3:
            st.write(row['QTY'])
        with col4:
            staff = st.multiselect(f"Assign staff for {row['PI NUMBER']}", df_staff_filtered['STAFF NAME'].unique(), key=f"staff_{i}")
            assigned_staff.append(staff)
        with col5:
            st.write(f"{row[f'TOTAL BOM TIME {selected_department} x QTY']}")

    # Add the selected staff to the DataFrame
    df_combine_bom['ASSIGNED'] = assigned_staff

    # Convert the 'ASSIGNED' column to a hashable type (tuple) if it's a list
    df_combine_bom['ASSIGNED'] = df_combine_bom['ASSIGNED'].apply(lambda x: x if isinstance(x, list) else [x])

    # Apply CSS to wrap text in columns
    st.markdown(
        """
        <style>
        .dataframe td {
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        </style>
        """, unsafe_allow_html=True
    )

    # Display the updated DataFrame with assigned staff
    st.dataframe(df_combine_bom)

    # Converts each element of the specified column(s) into a row 
    # example : [PI-2024, [TEAK, WHITE]] = [[PI-2024, TEAK], [PI-2024, WHITE]]
    df_combine_bom_EXPLODE = df_combine_bom.explode('ASSIGNED')

    # Group by 'ASSIGNED' to create the Staff Assignment table
    staff_assignment = df_combine_bom_EXPLODE.groupby('ASSIGNED').agg({
        'PI NUMBER': 'count',
        'QTY': 'sum',
        f'TOTAL BOM TIME {selected_department} x QTY' : 'sum'
    }).reset_index()

    # Display the staff assignment summary table
    st.write("Staff Assignment Summary:")

    staff_assignment['TOTAL WORKING (HOURS)'] = 8 * 60
    staff_assignment['REMAINING TIME'] = staff_assignment['TOTAL WORKING (HOURS)'] - staff_assignment[f'TOTAL BOM TIME {selected_department} x QTY']

    st.write(staff_assignment)

if __name__ == "__main__":
    main()
