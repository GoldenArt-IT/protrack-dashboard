import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import matplotlib.pyplot as plt
from st_aggrid import AgGrid, GridOptionsBuilder
from datetime import timedelta, datetime, time as dtime
import os
from datetime import datetime
import time


def main():
    # Set page to always wide
    st.set_page_config(layout="wide")

    st.title("PRODUCTION PLANNER DASHBOARD")

    # Read the Production Progress
    conn1 = st.connection("gsheets", type=GSheetsConnection)
    df = conn1.read(worksheet="PRODUCTION PROGRESS", ttl=5000)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.dropna(how="all", axis=0)
    df = df.drop(columns=['IN', 'FR', 'FB', 'WD',
                 'SP', 'SR', 'SW', 'AS', 'PC'])

    # Read the Data BOM
    conn2 = st.connection("gsheets", type=GSheetsConnection)
    df_bom = conn2.read(worksheet="DATA BOM", ttl=5000)
    df_bom = df_bom.loc[:, ~df_bom.columns.str.contains('^Unnamed')]
    df_bom = df_bom.dropna(how="all", axis=0)
    df_bom = df_bom.rename(columns={'CONFIRM MODEL NAME': 'MODEL'})
    # st.dataframe(df_bom)

    # Read Staff Data
    conn3 = st.connection("gsheets", type=GSheetsConnection)
    df_staff = conn3.read(worksheet="STAFF DATA", ttl=5000)
    df_staff = df_staff.dropna(how="all", axis=0)

    # Function to handle DataFrame display logic
    def toggle_dataframe(df, button_name):
        if 'show_df' not in st.session_state:
            st.session_state['show_df'] = False

        if st.button(button_name):
            # Toggle visibility
            st.session_state['show_df'] = not st.session_state['show_df']

        if st.session_state['show_df']:
            st.dataframe(df)

    # Initialize session state to manage selections
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = 'All'
    if 'selected_pi' not in st.session_state:
        st.session_state.selected_pi = []

    # Filter for departments, decoy date and pi selector
    col1, col2, col3 = st.columns(3)

    with col1:
        unique_department = df_staff['DEPARTMENT'].dropna().unique()
        selected_department = st.selectbox(
            "Choose department", unique_department, index=0)

    with col2:
        unique_decoy_date = df['DECOY DATE'].dropna().unique()
        # Add 'All' as the default option
        decoy_date_options = ['All'] + list(unique_decoy_date)
        selected_date = st.selectbox(
            "Choose Plan Date", decoy_date_options, index=1, key="selected_date")  # Use session state

    # Filter df based on selected Plan Date, show all if 'All' is selected
    if st.session_state.selected_date != 'All':
        df_filtered_by_date = df[df['DECOY DATE']
                                 == st.session_state.selected_date]
    else:
        df_filtered_by_date = df  # Show all data when 'All' is selected

    with col3:
        unique_pi = df_filtered_by_date['PI NUMBER'].dropna().unique()
        selected_pi = st.multiselect(
            "Select PI Number", unique_pi, key="selected_pi")

    # Further filter df based on selected PI numbers
    if st.session_state.selected_pi:
        df_filtered_by_date = df_filtered_by_date[df_filtered_by_date['PI NUMBER'].isin(
            st.session_state.selected_pi)]

    # Table Order vs BOM Time logic based on department selection
    if selected_department == 'FRAME':
        df_bom = df_bom[['MODEL', 'PART FRAME A', 'PART FRAME B', 'PART FRAME C',
                         'PART FRAME D', 'FRAME TIME A', 'FRAME TIME B', 'FRAME TIME C', 'FRAME TIME D']]
        df_bom['TOTAL BOM TIME'] = df_bom.iloc[:, -4:].sum(axis=1)

    if selected_department == 'SPONGE':
        df_bom = df_bom[['MODEL', 'PART SPONGE A', 'PART SPONGE B', 'PART SPONGE C',
                         'PART SPONGE D', 'SPONGE TIME A', 'SPONGE TIME B', 'SPONGE TIME C', 'SPONGE TIME D']]
        df_bom['TOTAL BOM TIME'] = df_bom.iloc[:, -4:].sum(axis=1)

    if selected_department == 'SPRAY':
        df_bom = df_bom[['MODEL', 'PART SPRAY A', 'PART SPRAY B', 'PART SPRAY C',
                         'PART SPRAY D', 'SPRAY TIME A', 'SPRAY TIME A.1', 'SPRAY TIME A.2', 'SPRAY TIME A.3']]
        df_bom['TOTAL BOM TIME'] = df_bom.iloc[:, -4:].sum(axis=1)

    if selected_department == 'SEWING':
        df_bom = df_bom[['MODEL', 'PART SEW A', 'PART SEW B', 'PART SEW C',
                         'PART SEW D',  'SEW TIME A', 'SEW TIME B', 'SEW TIME C', 'SEW TIME D']]
        df_bom['TOTAL BOM TIME'] = df_bom.iloc[:, -4:].sum(axis=1)

    if selected_department == 'ASSEMBLY':
        df_bom = df_bom[['MODEL', 'PART ASSEMBLY A', 'PART ASSEMBLY B', 'PART ASSEMBLY C',
                         'PART ASSEMBLY D', 'ASSEMBLY TIME A', 'ASSEMBLY TIME B', 'ASSEMBLY TIME C', 'ASSEMBLY TIME D']]
        df_bom['TOTAL BOM TIME'] = df_bom.iloc[:, -4:].sum(axis=1)

    if selected_department == 'PACKING':
        df_bom = df_bom[['MODEL', 'PART PACKING A', 'PART PACKING B', 'PART PACKING C',
                         'PART PACKING D', 'PACKING TIME A', 'PACKING TIME B', 'PACKING TIME C', 'PACKING TIME D']]
        df_bom['TOTAL BOM TIME'] = df_bom.iloc[:, -4:].sum(axis=1)

    if selected_department == 'INTERIOR':
        df_bom = df_bom[['MODEL', 'PART INT/WEL A', 'PART INT/WEL B', 'PART INT/WEL C',
                         'PART INT/WEL D', 'INT/WEL TIME A', 'INT/WEL TIME B', 'INT/WEL TIME C', 'INT/WEL TIME D']]
        df_bom['TOTAL BOM TIME'] = df_bom.iloc[:, -4:].sum(axis=1)

    elif selected_department == 'FABRIC':
        df_bom = df_bom[['MODEL', 'PART FAB A', 'PART FAB B', 'PART FAB C',
                         'PART FAB D', 'FAB TIME A', 'FAB TIME B', 'FAB TIME C', 'FAB TIME D']]
        numeric_columns = ['FAB TIME A',
                           'FAB TIME B', 'FAB TIME C', 'FAB TIME D']
        for col in numeric_columns:
            df_bom[col] = pd.to_numeric(df_bom[col], errors='coerce')
        df_bom['TOTAL BOM TIME'] = df_bom[['FAB TIME A',
                                           'FAB TIME B', 'FAB TIME C', 'FAB TIME D']].sum(axis=1)

    # Display BOM data based on department
    toggle_dataframe(df_bom, 'Show BOM Data')

    # Combine filtered production progress data with BOM data
    df_combine_bom = pd.merge(
        df_filtered_by_date, df_bom, on='MODEL', how='left')
    df_combine_bom[f'TOTAL BOM TIME {selected_department} PER MODEL'] = df_combine_bom['TOTAL BOM TIME']
    df_combine_bom[f'TOTAL BOM TIME {selected_department} x QTY'] = df_combine_bom['QTY'] * \
        df_combine_bom['TOTAL BOM TIME']

    df_combine_bom.iloc[:, -7] = df_combine_bom.iloc[:, -
                                                     7] * df_combine_bom['QTY']
    df_combine_bom.iloc[:, -6] = df_combine_bom.iloc[:, -
                                                     6] * df_combine_bom['QTY']
    df_combine_bom.iloc[:, -5] = df_combine_bom.iloc[:, -
                                                     5] * df_combine_bom['QTY']
    df_combine_bom.iloc[:, -4] = df_combine_bom.iloc[:, -
                                                     4] * df_combine_bom['QTY']

    df_combine_bom = df_combine_bom.drop(columns=['TOTAL BOM TIME'])
    toggle_dataframe(df_combine_bom, 'Show BOM time based on Plan')

    # Filter df_staff based on the selected department
    df_staff_filtered = df_staff[df_staff['DEPARTMENT'] == selected_department]

    if selected_date != "All":
        # Add assigned staff
        st.header(
            f"Assign staff - PLAN : {selected_date} - DEPARTMENT : {selected_department}")
        assigned_staff_a = []
        assigned_staff_b = []
        assigned_staff_c = []
        assigned_staff_d = []
        assigned_staff_all = []
        assigned_qc = []
        for i, row in df_combine_bom.iterrows():
            col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns(
                [2, 2, 1, 3, 3, 3, 3, 3, 2])
            with col1:
                st.write(row['PI NUMBER'])
            with col2:
                st.write(row['MODEL'])
                st.caption(f"{row['ORDER']} {row['TYPE']}")
            with col3:
                st.text(row['QTY'])
            with col4:
                staff_a = st.multiselect(
                    f"{row.iloc[8]} - {row.iloc[12]}", df_staff_filtered['STAFF NAME'].unique(), key=f"staff_{i}_a")
                assigned_staff_a.append(staff_a)
                if staff_a:
                    st.caption(
                        f"Selected staff for {row.iloc[8]} - {row.iloc[12]}: {', '.join(staff_a) if staff_a else 'None'}")
            with col5:
                staff_b = st.multiselect(
                    f"{row.iloc[9]} - {row.iloc[13]}", df_staff_filtered['STAFF NAME'].unique(), key=f"staff_{i}_b")
                assigned_staff_b.append(staff_b)
                if staff_b:
                    st.caption(
                        f"Selected staff for {row.iloc[9]} - {row.iloc[13]}: {', '.join(staff_b) if staff_b else 'None'}")
            with col6:
                staff_c = st.multiselect(
                    f"{row.iloc[10]} - {row.iloc[14]}", df_staff_filtered['STAFF NAME'].unique(), key=f"staff_{i}_c")
                assigned_staff_c.append(staff_c)
                if staff_c:
                    st.caption(
                        f"Selected staff for {row.iloc[10]} - {row.iloc[14]}: {', '.join(staff_c) if staff_c else 'None'}")
            with col7:
                staff_d = st.multiselect(
                    f"{row.iloc[11]} - {row.iloc[15]}", df_staff_filtered['STAFF NAME'].unique(), key=f"staff_{i}_d")
                assigned_staff_d.append(staff_d)
                if staff_d:
                    st.caption(
                        f"Selected staff for {row.iloc[11]} - {row.iloc[15]}: {', '.join(staff_d) if staff_d else 'None'}")
            with col8:
                staff_all = st.multiselect(
                    f"ALL PART - {row.iloc[-1]}", df_staff_filtered['STAFF NAME'].unique(), key=f"staff_{i}")
                assigned_staff_all.append(staff_all)
                if staff_all:
                    st.caption(
                        f"Selected staff for ALL PART - {row.iloc[-1]}: {', '.join(staff_all) if staff_all else 'None'}")
            with col9:
                qc = st.checkbox(f"QC - {row.iloc[0]}", key=f"qc_{i}")
                assigned_qc.append(qc)
                
            st.divider()

    # Add the selected staff to the DataFrame
    df_combine_bom['ASSIGNED PART A'] = assigned_staff_a
    df_combine_bom['ASSIGNED PART B'] = assigned_staff_b
    df_combine_bom['ASSIGNED PART C'] = assigned_staff_c
    df_combine_bom['ASSIGNED PART D'] = assigned_staff_d
    df_combine_bom['ASSIGNED'] = assigned_staff_all
    df_combine_bom['QC'] = assigned_qc

    # Function to save DataFrame to Excel
    def save_to_excel(df, title):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        filename = f'{title} for {selected_department} - {selected_date} - {timestamp}.xlsx'
        file_path = os.path.join(desktop_path, filename)
        df.to_excel(file_path, index=False)
        message_placeholder = st.empty()
        message_placeholder.success(f"File saved to: {file_path}")
        time.sleep(3)
        message_placeholder.empty()

    # Display the updated DataFrame with assigned staff
    st.header('Staff Assigned Table :')
    st.dataframe(df_combine_bom)
    if st.button('Save', key='save_button_1'):
        save_to_excel(df_combine_bom, 'Planned Assigned')


    # Convert the 'ASSIGNED' column to a hashable type (tuple) if it's a list
    df_combine_bom['ASSIGNED'] = df_combine_bom['ASSIGNED'].apply(
        lambda x: x if isinstance(x, list) else [x])
    df_combine_bom['ASSIGNED PART A'] = df_combine_bom['ASSIGNED PART A'].apply(
        lambda x: x if isinstance(x, list) else [x])
    df_combine_bom['ASSIGNED PART B'] = df_combine_bom['ASSIGNED PART B'].apply(
        lambda x: x if isinstance(x, list) else [x])
    df_combine_bom['ASSIGNED PART C'] = df_combine_bom['ASSIGNED PART C'].apply(
        lambda x: x if isinstance(x, list) else [x])
    df_combine_bom['ASSIGNED PART D'] = df_combine_bom['ASSIGNED PART D'].apply(
        lambda x: x if isinstance(x, list) else [x])

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

    # Converts each element of the specified column(s) into a row
    # example : [PI-2024, [TEAK, WHITE]] = [[PI-2024, TEAK], [PI-2024, WHITE]]
    df_combine_bom_EXPLODE = df_combine_bom.explode('ASSIGNED')

    # Group by 'ASSIGNED' to create the Staff Assignment table
    staff_assignment = df_combine_bom_EXPLODE.groupby('ASSIGNED').agg({
        'PI NUMBER': 'count',
        'QTY': 'sum',
        f'TOTAL BOM TIME {selected_department} x QTY': 'sum'
    }).reset_index()

    # Display the staff assignment summary table
    st.header("Staff Assigned Summary :")

    staff_assignment['TOTAL WORKING (HOURS)'] = 8 * 60
    staff_assignment['REMAINING TIME'] = staff_assignment['TOTAL WORKING (HOURS)'] - \
        staff_assignment[f'TOTAL BOM TIME {selected_department} x QTY']
    staff_assignment.rename(columns={
                            f'TOTAL BOM TIME {selected_department} x QTY': 'TOTAL TIME USED'}, inplace=True)

    # st.write(staff_assignment)

    def cal_staff_assigned(df, column, num):
        staff_assignment_part = df.groupby(column).agg({
            'PI NUMBER': 'count',
            'QTY': 'sum',
            f'{df.columns[num]}': 'sum'
        }).reset_index()

        staff_assignment_part['TOTAL WORKING (HOURS)'] = 7 * 60
        staff_assignment_part['REMAINING TIME'] = staff_assignment_part[
            'TOTAL WORKING (HOURS)'] - staff_assignment_part[f'{df.columns[num]}']
        staff_assignment_part.rename(
            columns={f'{staff_assignment_part.columns[3]}': 'TOTAL TIME USED'}, inplace=True)
        staff_assignment_part.rename(
            columns={f'{staff_assignment_part.columns[0]}': 'ASSIGNED'}, inplace=True)

        return staff_assignment_part

    cal_part_a = cal_staff_assigned(df_combine_bom.explode(
        'ASSIGNED PART A'), df_combine_bom.explode('ASSIGNED PART A').iloc[:, -6], -12)
    cal_part_b = cal_staff_assigned(df_combine_bom.explode(
        'ASSIGNED PART B'), df_combine_bom.explode('ASSIGNED PART B').iloc[:, -5], -11)
    cal_part_c = cal_staff_assigned(df_combine_bom.explode(
        'ASSIGNED PART C'), df_combine_bom.explode('ASSIGNED PART C').iloc[:, -4], -10)
    cal_part_d = cal_staff_assigned(df_combine_bom.explode(
        'ASSIGNED PART D'), df_combine_bom.explode('ASSIGNED PART D').iloc[:, -3], -9)

    staff_assignment = staff_assignment.append(cal_part_a)
    staff_assignment = staff_assignment.append(cal_part_b)
    staff_assignment = staff_assignment.append(cal_part_c)
    staff_assignment = staff_assignment.append(cal_part_d)

    staff_assignment = staff_assignment.groupby(['ASSIGNED']).agg({
        'PI NUMBER': 'sum',
        'QTY': 'sum',
        'TOTAL TIME USED': 'sum'
    }).reset_index()

    staff_assignment['TOTAL WORKING (HOURS)'] = 522
    staff_assignment['REMAINING TIME'] = staff_assignment[
        'TOTAL WORKING (HOURS)'] - staff_assignment['TOTAL TIME USED']

    st.table(staff_assignment)
    if st.button('Save', key='save_button_2'):
        save_to_excel(staff_assignment, 'Staff Assigned Summary')



if __name__ == "__main__":
    main()