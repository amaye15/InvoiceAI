import os
import re
import json
import pytesseract

from PIL import Image
from hugchat import hugchat
from hugchat.login import Login

import pandas as pd
import streamlit as st

from pdf2image import convert_from_path, convert_from_bytes

def get_invoice_files(invoices_dir: str, allowed_file_types: list):
    return [os.path.join(invoices_dir, f) for f in os.listdir(invoices_dir) if any(f.endswith(ext) for ext in allowed_file_types)]

def load_data(file_path: str):
    with open(file_path, 'r') as file:
        return json.load(file)
    
@st.cache_data(show_spinner = "OCR Text Extraction")
def extract_ocr_text(file_path: str, file_content = None, file_type: str ='image'):
    ocr_text = ""
    if file_type == 'image':
        image = Image.open(file_path if file_path else file_content)
        st.image(image, caption='Image', use_column_width=True)
        ocr_text += "\n" + pytesseract.image_to_string(image)
    elif file_type == 'pdf':
        pages = convert_from_path(file_path) if file_path else convert_from_bytes(file_content)
        for page in pages:
            st.image(page, caption='Uploaded Image', use_column_width=True)
            ocr_text += "\n" + pytesseract.image_to_string(page)
    return ocr_text
    

@st.cache_data(show_spinner = "Generating Prompt")
def generate_prompt(ocr_extracted_text: str, json_structure: dict):
    prompt = f"""Task: Text to JSON format

Output: 

1. Output
2. Assign a Value
3. Assign a Confidence 
4. Assign a State: Extracted or Not Extracted
5. Assign NA to unknown information

JSON Template: 
            
{json.dumps(json_structure, indent=4, sort_keys=True)}

Text:

{ocr_extracted_text}
"""
    return prompt

@st.cache_data(show_spinner = "LLM JSON Generation")
def query_llm(prompt: str, model: str, email: str = "EMAIL", password: str = "PASSWORD"):
    
    sign = Login(st.secrets[email], st.secrets[password])
    cookies = sign.login(save_cookies=False)
    chatbot = hugchat.ChatBot(cookies=cookies.get_dict(),) 
    llm_list = {llm.name:idx for idx, llm in enumerate(chatbot.get_available_llm_models())}
    chatbot.switch_llm(llm_list[model])

    llm_extracted_text = []
    start_idx = 0
    end_idx = 0
    for idx, response in enumerate(chatbot.query(prompt,use_cache=True, truncate=10000, max_new_tokens=10000, return_full_text=True, stream=True)):
        try:
            llm_extracted_text.append(response["token"])
            if ("{" in list(response["token"])) & (start_idx == 0):
                start_idx = idx
            if "}" in list(response["token"]):
                end_idx = idx
        except:
            pass

    llm_extracted_text = "".join(llm_extracted_text[start_idx:end_idx + 1])
    print("Not regex")
    print(llm_extracted_text)
    return llm_extracted_text

@st.cache_data(show_spinner=True)
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

@st.cache_data(show_spinner=True)
def update_json(data, df, edited_df):
    for key, val in data.items():
        if key == "articles":
            for key2, val2 in enumerate(val):
                for key3, val3 in val2.items():
                    for key4, val4 in val3.items():
                        try:
                            data[key][key2][key3][key4] = edited_df.loc[df["Field"] == key3, key4.capitalize()].to_list()[0]
                        except:
                            pass
        else:
            for key2, val2 in val.items():
                try:
                    data[key][key2] = edited_df.loc[df["Field"] == key, key2.capitalize()].to_list()[0]
                except:
                    pass
    return data