import streamlit as st
import pandas as pd
import json


# Set the page to wide mode
st.set_page_config(layout="wide")

# Load JSON data from a file
@st.cache(allow_output_mutation=True)
def load_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to create a DataFrame from the JSON data
def create_dataframe(data):
    flat_data = []
    for key, value in data.items():
        if key == 'articles':
            for article in value:
                for field, details in article.items():
                    flat_data.append({
                        'Field': field,
                        'Value': details.get('value', ''),
                        'Confidence': details.get('confidence', ''),
                        'State': details.get('state', '')
                    })
        else:
            if key == 'picture_quality':  # Special handling for picture_quality
                flat_data.append({'Field': key, 'Value': value.get('value', ''), 'Confidence': '', 'State': ''})
            elif isinstance(value, dict) and 'value' in value:
                flat_data.append({
                    'Field': key,
                    'Value': value.get('value', ''),
                    'Confidence': value.get('confidence', ''),
                    'State': value.get('state', '')
                })
    return pd.DataFrame(flat_data)

def update_json(data, edited_df):
    for key, val in data.items():
        if key == "articles":
            for key2, val2 in enumerate(val):
                for key3, val3 in val2.items():
                    for key4, val4 in val3.items():
                        data[key][key2][key3][key4] = edited_df.loc[df["Field"] == key3, key4.capitalize()].to_list()[0]
        else:
            #print(val)
            for key2, val2 in val.items():
                data[key][key2] = edited_df.loc[df["Field"] == key, key2.capitalize()].to_list()[0]
                #for key3, val3 in val2.items():
                    #data[key][key2][key3] = edited_df.loc[df["Field"] == key2, key3.capitalize()].to_list()[0]


# Path to your JSON file
file_path = 'format.json'

# Load and display the editable DataFrame
data = load_data(file_path)
df = create_dataframe(data)
edited_df = st.data_editor(df, key="data_editor", use_container_width=True)

# Button to manually refresh the JSON data
if st.button('Refresh JSON'):
    update_json(data, edited_df)
    st.success('JSON data has been updated.')

# Optionally display the updated JSON data
st.write("Updated JSON Data:")
st.json(data)
