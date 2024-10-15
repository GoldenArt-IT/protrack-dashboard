import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

# Sample DataFrame
data = {
    'ID': ['001', '002', '003'],
    'Name': ['John', 'Jane', 'Doe'],
    'Age': [28, 34, 23]
}

df = pd.DataFrame(data)

# Set up AgGrid options to make rows clickable
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection('single')  # Allow single row selection

grid_options = gb.build()

# Display the dataframe with AgGrid and assign a unique key
grid_response = AgGrid(df, gridOptions=grid_options, height=200, width='100%', key='unique_grid_key')

# Get the selected row data
selected_row = grid_response['selected_rows']

# First check if selected_row is not None
if selected_row is not None and len(selected_row) > 0:
    st.write("Details of the selected row:")
    st.write(selected_row)
else:
    st.write("No row selected yet.")
