import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import matplotlib.pyplot as plt
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from datetime import timedelta, datetime, time as dtime

def main():
    # Set page to always wide
    st.set_page_config(layout="wide")

    st.title("PRODUCTION DASHBOARD")

    # Read the Production Progress
    conn1 = st.connection("gsheets", type=GSheetsConnection)
    df = conn1.read(worksheet="PRODUCTION PROGRESS", ttl=300)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.dropna(how="all", axis=0)
    df = df.drop(columns=['DELIVERY PLAN DATE'])
    df = df.rename(columns={'DECOY DATE' : 'PLAN DATE'})

    # Read the Sewing Logs
    conn2 = st.connection("gsheets", type=GSheetsConnection)
    df_sewing = conn2.read(worksheet="SEWING LOGS", ttl=300)
    df_sewing = df_sewing.loc[:, ~df_sewing.columns.str.contains('^Unnamed')]
    df_sewing = df_sewing.dropna(how="all", axis=0)

    # Read the Data BOM
    conn3 = st.connection("gsheets", type=GSheetsConnection)
    df_bom = conn3.read(worksheet="DATA BOM", ttl=300)
    df_bom = df_bom.loc[:, ~df_bom.columns.str.contains('^Unnamed')]
    df_bom = df_bom.dropna(how="all", axis=0)

    # Set up AgGrid options to make rows clickable
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection('single')  # Allow single row selection

    grid_options = gb.build()

    # Display the dataframe with AgGrid
    grid_response = AgGrid(df, gridOptions=grid_options, height=300, width='100%', key='unique_grid_key', columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)

    # Get the selected row data
    selected_row = grid_response['selected_rows']

    # If a row is selected, show details
    if selected_row is not None and len(selected_row) > 0:
        st.write("Details of the selected row:")
        selected_row_df = pd.DataFrame(selected_row)
        selected_row_subset = selected_row_df[['IN', 'FR', 'FB', 'WD', 'SP', 'SR', 'SW', 'AS', 'PC']]

        column1, column2 = st.columns([1,3])

        with column1:
            st.write(f"PI NUMBER : {selected_row_df['PI NUMBER'][0]}")
            st.write(f"CUSTOMER : {selected_row_df['CUSTOMERS'][0]}")
            st.write(f"MODEL : {selected_row_df['MODEL'][0]}")
            st.write(f"QTY : {selected_row_df['QTY'][0]}")
            st.write("STATUS : ")
            st.dataframe(selected_row_subset)

        with column2:
            df_sewing_filtered = df_sewing[df_sewing['PI NUMBER'] == selected_row_df['PI NUMBER'][0]]
            st.dataframe(df_sewing_filtered)

            # Convert the 'TIMESTAMP' column to datetime
            df_sewing_filtered['TIMESTAMP'] = pd.to_datetime(df_sewing_filtered['TIMESTAMP'])

            # Extract start and end time
            start_time_sewing = df_sewing_filtered['TIMESTAMP'].iloc[0]
            end_time_sewing = df_sewing_filtered['TIMESTAMP'].iloc[-1]

            # Custom function to calculate working hours, excluding non-working hours and break times
            def calculate_working_hours_with_minutes(start, end):
                total_duration = timedelta()
                current_time = start

                while current_time < end:
                    work_start = current_time.replace(hour=8, minute=0, second=0)
                    work_end = current_time.replace(hour=18, minute=0, second=0)

                    # If the current time is outside working hours, move to the next day
                    if current_time.time() < dtime(8, 0) or current_time.time() > dtime(18, 0):
                        current_time += timedelta(days=1)
                        current_time = current_time.replace(hour=8, minute=0, second=0)
                        continue

                    # Calculate working time for the current day, excluding lunch break (12:30 PM - 1:30 PM)
                    if current_time < work_end:
                        day_duration = min(end, work_end) - current_time

                        # If during lunch break, subtract the break time
                        if current_time.time() < dtime(12, 30) < work_end.time():
                            day_duration -= timedelta(hours=1)

                        total_duration += day_duration

                    current_time += timedelta(days=1)
                    current_time = current_time.replace(hour=8, minute=0, second=0)

                return total_duration, total_duration.total_seconds() // 60  # Returning both duration and minutes

            # Calculate total working duration and minutes
            total_working_duration, duration_in_minutes = calculate_working_hours_with_minutes(start_time_sewing, end_time_sewing)

            # Calculate Bom time
            df_bom_sewing = df_bom[selected_row_df['MODEL'][0]==df_bom['CONFIRM MODEL NAME']]
            df_total_sum_time_sewing = df_bom_sewing['SEW TIME A'].fillna(0) + df_bom_sewing['SEW TIME B'].fillna(0) + df_bom_sewing['SEW TIME C'].fillna(0) + df_bom_sewing['SEW TIME D'].fillna(0)
          #   st.write(df_bom_sewing)
          #   st.write(df_total_sum_time_sewing)
            
            # Condense the information into a single row
            df_sewing_single_row_with_minutes = pd.DataFrame({
                'DEPARTMENT': 'SEWING',
                'PI NUMBER': [df_sewing_filtered['PI NUMBER'].iloc[0]],
                'MODEL': selected_row_df['MODEL'][0],
                'START TIME': [start_time_sewing],
                'END TIME': [end_time_sewing],
                'WORK STATUS': [df_sewing_filtered['WORK STATUS'].iloc[-1]],
                'ASSIGNED': [df_sewing_filtered['ASSIGN'].iloc[-1]],
                'DURATION': [total_working_duration],
                'DURATION (MINUTES)': [duration_in_minutes]
            })

            # Custom function to convert timedelta into a more readable format
            def format_timedelta(td): 
                days = td.days
                hours, remainder = divmod(td.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                return f"{days} day{'s' if days != 1 else ''}, {hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}, and {seconds} second{'s' if seconds != 1 else ''}"

            df_sewing_single_row_with_minutes['DURATION'] = df_sewing_single_row_with_minutes['DURATION'].apply(format_timedelta)
            df_sewing_single_row_with_minutes['BOM TIME (MINUTES)'] = df_total_sum_time_sewing.iloc[0] * selected_row_df['QTY'].iloc[0]
            df_sewing_single_row_with_minutes['DIFF (MINUTES)'] = df_sewing_single_row_with_minutes['BOM TIME (MINUTES)'] - df_sewing_single_row_with_minutes['DURATION (MINUTES)']

            df_sewing_single_row_with_minutes = df_sewing_single_row_with_minutes.drop(columns='DURATION')

          #   selected_row_df['QTY'][0].dtype

            st.dataframe(df_sewing_single_row_with_minutes)

            

    else:
        st.write("No row selected yet.")


if __name__ == "__main__":
    main()
