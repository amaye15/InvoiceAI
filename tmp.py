import streamlit as st
import json


# Load JSON data from a file
@st.cache_data
def load_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

data = load_data('format.json')  # Replace 'your_file_path.json' with the path to your JSON file

# Function to display and edit a single field
def display_field(key, field):
    with st.expander(f"{key.capitalize()} - Details"):
        # Check if each key exists before accessing
        value = st.text_input(f"{key} - Value", field.get("value", ""))
        confidence = st.text_input(f"{key} - Confidence", field.get("confidence", ""))
        state = st.text_input(f"{key} - State", field.get("state", ""))
        
        # Update the field values based on user input
        field["value"] = value
        field["confidence"] = confidence
        field["state"] = state

# Display and edit fields for each item in the JSON
for key, value in data.items():
    if isinstance(value, list):  # Handle nested lists
        for item in value:
            for subkey, subvalue in item.items():
                display_field(subkey, subvalue)
    else:
        display_field(key, value)

# Optionally, add a button to save changes
if st.button('Save Changes'):
    st.write(data)  # Replace this with actual save logic
