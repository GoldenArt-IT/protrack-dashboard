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

# Set up AgGrid with row selection
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection(selection_mode="single", use_checkbox=True)
grid_options = gb.build()

# Display the DataFrame
st.write("Click on a row to see details:")
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    enable_enterprise_modules=False,
    update_mode='MODEL_CHANGED',
)

# Display details of the selected row
selected_rows = grid_response['selected_rows']
if selected_rows:
    st.write("Details for the selected row:")
    st.write(selected_rows[0])
