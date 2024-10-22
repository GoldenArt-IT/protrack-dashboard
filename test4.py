import streamlit as st
import pandas as pd

# Function to handle DataFrame display logic
def toggle_dataframe(df, button_name):
    if 'show_df' not in st.session_state:
        st.session_state['show_df'] = False

    if st.button(button_name):
        st.session_state['show_df'] = not st.session_state['show_df']  # Toggle visibility

    if st.session_state['show_df']:
        st.dataframe(df)

# Sample DataFrame
data = {
    'Name': ['John', 'Jane', 'Doe'],
    'Age': [28, 24, 35],
    'City': ['New York', 'San Francisco', 'Los Angeles']
}
df = pd.DataFrame(data)

# Call the function to display the DataFrame
toggle_dataframe(df, 'test')
