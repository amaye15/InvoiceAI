import streamlit as st
import json

# Set the page to wide mode
st.set_page_config(layout="wide")

# Load JSON data from a file
@st.cache
def load_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Replace 'your_file_path.json' with the path to your JSON file
data = load_data('format.json')

# Function to display and edit a single field within a column
def display_field(column, key, field):
    if 'value' in field:
        value = column.text_input(f"{key} Value", field["value"], key=f"{key}_value")
        field["value"] = value
    if 'confidence' in field:
        confidence = column.text_input(f"{key} Confidence", field["confidence"], key=f"{key}_confidence")
        field["confidence"] = confidence
    if 'state' in field:
        state = column.text_input(f"{key} State", field["state"], key=f"{key}_state")
        field["state"] = state

# Create a form for the editable fields
with st.form("my_form"):
    # Create two columns
    col1, col2 = st.columns(2)

    # Initialize a counter to alternate between columns
    col_counter = 0

    for key, value in data.items():
        if isinstance(value, list):  # Handle nested lists
            for item in value:
                for subkey, subvalue in item.items():
                    if col_counter % 2 == 0:
                        display_field(col1, subkey, subvalue)
                    else:
                        display_field(col2, subkey, subvalue)
                    col_counter += 1
        else:
            if col_counter % 2 == 0:
                display_field(col1, key, value)
            else:
                display_field(col2, key, value)
            col_counter += 1
    
    # Submit button for the form, placed outside the columns so it spans the entire form
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write("Changes saved!")
        # Here, you would typically save the updated `data` to a file or database.
        # For demonstration, we'll just display the updated data.
        #st.json(data)
        st.data_editor(data)
