import os
import json_repair

import streamlit as st

from lib import *

st.set_page_config(layout="wide")

###################################################
# Section - Constants
###################################################

# Supporting both images and PDFs
ALLOWED_IMAGE_TYPES = ["jpeg", "jpg", "png"]
ALLOWED_FILE_TYPES = ALLOWED_IMAGE_TYPES + ["pdf"]
MODEL = "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO"
JSON_FORMATTER = 'format.json'
INVOICE_PATH = './invoices'

st.title('Invoice Viewer')

# Create two columns
col1, col2 = st.columns(2)

###################################################
# Section - Select/ Upload File
###################################################

with col1:

    # Upload an image or PDF
    uploaded_file = st.file_uploader("Choose an image or PDF file...", type=ALLOWED_FILE_TYPES)

    # Select an image or PDF from the directory
    if uploaded_file is None:
        invoice_files = get_invoice_files(INVOICE_PATH, ALLOWED_FILE_TYPES)
        selected_file = st.selectbox('Or choose a pre-existing invoice file:', invoice_files, format_func=lambda x: os.path.basename(x))
    else:
        selected_file = None

    # Display the uploaded or selected file
    if uploaded_file is not None:
        file_type = 'image' if any(uploaded_file.name.endswith(ext) for ext in ALLOWED_IMAGE_TYPES) else 'pdf'
        ocr_extracted_text = extract_ocr_text(None, uploaded_file, file_type)
    elif selected_file:
        file_type = 'image' if any(selected_file.endswith(ext) for ext in ALLOWED_IMAGE_TYPES) else 'pdf'
        ocr_extracted_text = extract_ocr_text(selected_file, None, file_type)

###################################################
# Section - LLM Application
###################################################

# Note I have use huggingchat to use huggingface models, but this code could easily be replaced with OpenAI
    # OpenAI solutions could be to use directly image to text or text to text with text extraction being done before hand

with col2:
    json_structure = load_data(JSON_FORMATTER)

    # Generate the prompt using the cached function
    prompt = generate_prompt(ocr_extracted_text, json_structure)

    llm_extracted_text = query_llm(prompt, MODEL)

    json_text = json_repair.repair_json(llm_extracted_text, return_objects=True)

    ###################################################
    # Section - JSONify
    ###################################################

    # Load and display the editable DataFrame
    data = load_data(JSON_FORMATTER)

    df = create_dataframe(json_text)
    for col in df.columns:
        df[col] = df[col].astype(str)

    edited_df = st.data_editor(df, key="data_editor", use_container_width=True, height=800)

# Creating side by side buttons for JSON creation and download
col_left, col_right = st.columns(2)

with col_left:
    # Button to manually refresh the JSON data
    if st.button('Create JSON'):
        data = update_json(data, df, edited_df)
        st.success('JSON data has been created.')
        st.json(data)

with col_right:
    # Download JSON option
    st.download_button(label="Download JSON", data=json.dumps(data, indent=4, sort_keys=True), file_name="data.json", mime="application/json")

