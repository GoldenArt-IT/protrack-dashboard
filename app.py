import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import matplotlib.pyplot as plt
import time
from st_aggrid import AgGrid, GridOptionsBuilder

def main():

     # Set page to always wide
     st.set_page_config(layout="wide")

     st.title("PRODUCTION DASHBOARD")
     
     # st.write("Production Progress")
     conn1 = st.connection("gsheets", type=GSheetsConnection)
     df = conn1.read(worksheet="PRODUCTION PROGRESS", ttl=5)
     # df = df.dropna(how="all", axis=1)
     df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
     df = df.dropna(how="all", axis=0)
     # st.dataframe(df)

     # st.write("Sewing Production Progress")
     conn2 = st.connection("gsheets", type=GSheetsConnection)
     df_sewing = conn2.read(worksheet="SEWING LOGS", ttl=5)
     # df = df.dropna(how="all", axis=1)
     df_sewing = df_sewing.loc[:, ~df_sewing.columns.str.contains('^Unnamed')]
     df_sewing = df_sewing.dropna(how="all", axis=0)
     # st.dataframe(df_sewing)

     # Set up AgGrid options to make rows clickable
     gb = GridOptionsBuilder.from_dataframe(df)
     gb.configure_selection('single')  # Allow single row selection

     grid_options = gb.build()

     # Display the dataframe with AgGrid and assign a unique key
     grid_response = AgGrid(df, gridOptions=grid_options, height=300, width='100%', key='unique_grid_key')

     # Get the selected row data
     selected_row = grid_response['selected_rows']

     # First check if selected_row is not None
     if selected_row is not None and len(selected_row) > 0:
          st.write("Details of the selected row:")
          # st.write(selected_row)
          selected_row_df = pd.DataFrame(selected_row)
          selected_row_subset = selected_row_df[['IN', 'FR', 'FB', 'WD', 'SP', 'SR', 'SW', 'AS', 'PC']]

          column1, column2 = st.columns(2)
          
          with column1:
               st.write(f"PI NUMBER : {selected_row['PI NUMBER'][0]}")
               st.write(f"CUSTOMER : {selected_row['CUSTOMERS'][0]}")
               st.write(f"MODEL : {selected_row['MODEL'][0]}")
               st.write(f"QTY : {selected_row['QTY'][0]}")
               st.write("STATUS : ")
               st.dataframe(selected_row_subset)


          with column2:
               df_sewing = df_sewing[df_sewing['PI NUMBER'] == selected_row['PI NUMBER'][0]]
               st.dataframe(df_sewing)

               # Convert the 'TIMESTAMP' column to datetime
               df_sewing['TIMESTAMP'] = pd.to_datetime(df_sewing['TIMESTAMP'])

               # Extract start time (first row) and end time (last row)
               start_time_sewing = df_sewing['TIMESTAMP'].iloc[0]
               end_time_sewing = df_sewing['TIMESTAMP'].iloc[-1]

               # Condense the information into a single row without the 'INVENTORY STATUS'
               df_sewing_single_row = pd.DataFrame({
               'PI NUMBER': [df_sewing['PI NUMBER'].iloc[0]],  # Assume PI Number is the same across rows
               'START TIME': [start_time_sewing],
               'END TIME': [end_time_sewing],
               'WORK STATUS': [df_sewing['WORK STATUS'].iloc[-1]],  # Status at the last row
               'ASSIGNED': [df_sewing['ASSIGN'].iloc[-1]] # Assigned person at the last row
               })

               # Custom function to convert timedelta into a more readable format
               def format_timedelta(td):
                    days = td.days
                    hours, remainder = divmod(td.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    return f"{days} day{'s' if days != 1 else ''}, {hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}, and {seconds} second{'s' if seconds != 1 else ''}"
               

               # # Apply the formatting function to the duration column
               
               df_sewing_single_row['DURATION'] = df_sewing_single_row['END TIME'] - df_sewing_single_row['START TIME']
               # st.write(df_sewing_single_row['DURATION'].apply(format_timedelta))
               df_sewing_single_row['DURATION'] = df_sewing_single_row['DURATION'].apply(format_timedelta)

               st.dataframe(df_sewing_single_row)


     else:
          st.write("No row selected yet.")
     

if __name__ == "__main__":
    main()

