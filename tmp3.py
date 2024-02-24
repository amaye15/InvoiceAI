import streamlit as st
import pandas as pd
import json

# Load JSON data from a file
@st.cache
def load_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    # Flatten the JSON structure into a DataFrame
    flat_data = []
    for key, value in data.items():
        if key == 'articles':  # Assuming 'articles' contains a list of article dicts
            for article in value:
                for field, details in article.items():
                    if isinstance(details, dict) and 'value' in details:
                        flat_data.append({
                            'Field': field,
                            'Value': details.get('value', ''),
                            'Confidence': details.get('confidence', ''),
                            'State': details.get('state', '')
                        })
        elif key == 'picture_quality':  # Handle picture_quality as a special case
            flat_data.append({
                'Field': key,
                'Value': value.get('value', ''),
                'Confidence': '',  # Empty since it's not applicable
                'State': ''  # Empty since it's not applicable
            })
        else:
            if isinstance(value, dict) and 'value' in value:
                flat_data.append({
                    'Field': key,
                    'Value': value.get('value', ''),
                    'Confidence': value.get('confidence', ''),
                    'State': value.get('state', '')
                })
    return pd.DataFrame(flat_data)

# Replace 'your_file_path.json' with the path to your JSON file
df = load_data('format.json')

# Use st.data_editor to display and edit the data
edited_df = st.data_editor(df, use_container_width=True)

# Display the edited data
if edited_df is not None:
    st.write("Edited Data:", edited_df)


