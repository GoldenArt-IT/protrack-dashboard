import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from datetime import timedelta, datetime, time as dtime

def main():
    # Set page to always wide
    st.set_page_config(layout="wide")

    st.title("PRODUCTION PLANNER DASHBOARD")

    # Read the Production Progress
    conn1 = st.connection("gsheets", type=GSheetsConnection)
    df = conn1.read(worksheet="PRODUCTION PROGRESS", ttl=5)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.dropna(how="all", axis=0)
    df = df.drop(columns=['IN', 'FR', 'FB', 'WD', 'SP', 'SR', 'SW', 'AS', 'PC'])

    # Read the Data BOM
    conn2 = st.connection("gsheets", type=GSheetsConnection)
    df_bom = conn2.read(worksheet="DATA BOM", ttl=5)
    df_bom = df_bom.loc[:, ~df_bom.columns.str.contains('^Unnamed')]
    df_bom = df_bom.dropna(how="all", axis=0)
    df_bom = df_bom.rename(columns={'CONFIRM MODEL NAME': 'MODEL'})

    # Read Staff Data
    conn3 = st.connection("gsheets", type=GSheetsConnection)
    df_staff = conn3.read(worksheet="STAFF DATA", ttl=5)
    df_staff = df_staff.dropna(how="all", axis=0)

    # Filter for departments, decoy date, and PI selector
    col1, col2, col3 = st.columns(3)

    with col1:
        unique_department = df_staff['DEPARTMENT'].dropna().unique()
        selected_department = st.selectbox("Choose department", unique_department, index=0)

    with col2:
        unique_decoy_date = df['DECOY DATE'].dropna().unique()
        selected_date = st.selectbox("Choose Plan Date", unique_decoy_date, index=0)

    with col3:
        unique_pi = df['PI NUMBER'].dropna().unique()
        selected_pi = st.multiselect("Select PI Number", unique_pi)

    # Filter the BOM based on selected department
    department_map = {
        'FRAME': ['MODEL', 'FRAME TIME A', 'FRAME TIME B', 'FRAME TIME C', 'FRAME TIME D'],
        'FABRIC': ['MODEL', 'FAB TIME A', 'FAB TIME B', 'FAB TIME C', 'FAB TIME D'],
        'SPONGE': ['MODEL', 'SPONGE TIME A', 'SPONGE TIME B', 'SPONGE TIME C', 'SPONGE TIME D'],
        'SPRAY': ['MODEL', 'SPRAY TIME A', 'SPRAY TIME B', 'SPRAY TIME C', 'SPRAY TIME D'],
        'SEWING': ['MODEL', 'SEW TIME A', 'SEW TIME B', 'SEW TIME C', 'SEW TIME D'],
        'ASSEMBLY': ['MODEL', 'ASSEMBLY TIME A', 'ASSEMBLY TIME B', 'ASSEMBLY TIME C', 'ASSEMBLY TIME D'],
        'PACKING': ['MODEL', 'PACKING TIME A', 'PACKING TIME B', 'PACKING TIME C', 'PACKING TIME D'],
        'INTERIOR': ['MODEL', 'INT/WEL TIME A', 'INT/WEL TIME B', 'INT/WEL TIME C', 'INT/WEL TIME D']
    }

    if selected_department in department_map:
        time_columns = department_map[selected_department]
        df_bom = df_bom[time_columns]
        df_bom['TOTAL BOM TIME'] = df_bom.iloc[:, -4:].sum(axis=1)
        st.dataframe(df_bom)

    # Combine the BOM and Production Progress DataFrames
    df_combine_bom = pd.merge(df, df_bom[['MODEL', 'TOTAL BOM TIME']], on='MODEL', how='left')
    df_combine_bom[f'TOTAL BOM TIME {selected_department} PER MODEL'] = df_combine_bom['TOTAL BOM TIME']
    df_combine_bom[f'TOTAL BOM TIME {selected_department} x QTY'] = df_combine_bom['QTY'] * df_combine_bom['TOTAL BOM TIME']
    df_combine_bom = df_combine_bom.drop(columns=['TOTAL BOM TIME'])

    # Staff selector for each row
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
            staff = st.selectbox(f"Assign staff for {row['PI NUMBER']}", df_staff['STAFF NAME'].unique(), key=f"staff_{i}")
            assigned_staff.append(staff)
        with col5:
            st.write(f"{row[f'TOTAL BOM TIME {selected_department} x QTY']}")

    # Add the selected staff to the DataFrame
    df_combine_bom['ASSIGNED STAFF'] = assigned_staff

    # Display the final DataFrame
    st.write("Updated DataFrame with Assigned Staff:")
    st.dataframe(df_combine_bom)

if __name__ == "__main__":
    main()
