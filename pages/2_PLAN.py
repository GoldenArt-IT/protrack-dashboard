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
    df = conn1.read(worksheet="PRODUCTION PROGRESS", ttl=5)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.dropna(how="all", axis=0)
    df = df.drop(columns=['IN', 'FR', 'FB', 'WD',
                 'SP', 'SR', 'SW', 'AS', 'PC'])

    # Read the Data BOM
    conn2 = st.connection("gsheets", type=GSheetsConnection)
    df_bom = conn2.read(worksheet="DATA BOM", ttl=5)
    df_bom = df_bom.loc[:, ~df_bom.columns.str.contains('^Unnamed')]
    df_bom = df_bom.dropna(how="all", axis=0)

    # Read Staff Data
    conn3 = st.connection("gsheets", type=GSheetsConnection)
    df_staff = conn3.read(worksheet="STAFF DATA", ttl=5)
    df_staff = df_staff.dropna(how="all", axis=0)

    # Filter for departments, decoy date and pi selector
    col1, col2, col3 = st.columns(3)

    with col1:
        unique_department = df_staff['DEPARTMENT'].dropna().unique()
        selected_department = st.selectbox(
            "Choose department", unique_department, index=0)

    with col2:
        unique_decoy_date = df['DECOY DATE'].dropna().unique()
        selected_date = st.selectbox("Choose Plan Date", unique_decoy_date, index=0)

    with col3:
        unique_pi = df['PI NUMBER'].dropna().unique()
        selected_pi = st.multiselect("Select PI Number", unique_pi)


if __name__ == "__main__":
    main()
