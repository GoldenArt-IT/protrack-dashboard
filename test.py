import streamlit as st
import pandas as pd

# Sample DataFrame
data = {
    'ID': ['001', '002', '003'],
    'Name': ['John', 'Jane', 'Doe'],
    'Age': [28, 34, 23]
}

df = pd.DataFrame(data)

# Function to display details of selected row
def display_details(selected_row):
    st.write(f"Details for selected row:")
    st.write(selected_row)

# Streamlit App Simulation
def streamlit_app_simulation():
    # Display the dataframe and buttons
    st.write("Click on a row to see details:")
    
    # Iterate over DataFrame and create a button for each row
    for index, row in df.iterrows():
        # Create a button for each row
        if st.button(f"Select Row {index + 1}"):
            # When a row is clicked, show the details
            display_details(row)

# Simulate the streamlit app
streamlit_app_simulation()