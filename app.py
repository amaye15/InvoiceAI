import streamlit as st
import os
from PIL import Image
import base64

# Supporting both images and PDFs
ALLOWED_IMAGE_TYPES = ["jpeg", "jpg", "png"]
ALLOWED_FILE_TYPES = ALLOWED_IMAGE_TYPES + ["pdf"]

def get_invoice_files():
    invoices_dir = './invoices'
    return [os.path.join(invoices_dir, f) for f in os.listdir(invoices_dir) if any(f.endswith(ext) for ext in ALLOWED_FILE_TYPES)]

st.title('Invoice Viewer')

# Upload an image or PDF
uploaded_file = st.file_uploader("Choose an image or PDF file...", type=ALLOWED_FILE_TYPES)

# Select an image or PDF from the directory
if uploaded_file is None:
    invoice_files = get_invoice_files()
    selected_file = st.selectbox('Or choose a pre-existing invoice file:', invoice_files, placeholder = "Choose an option")
else:
    selected_file = None

# Display the uploaded or selected file
if uploaded_file is not None:
    # Check file type and display accordingly
    if any(uploaded_file.name.endswith(ext) for ext in ALLOWED_IMAGE_TYPES):
        # Display image
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
    elif uploaded_file.name.endswith('pdf'):
        # Display PDF
        base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
        pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
        st.markdown(pdf_display, unsafe_allow_html=True)

elif selected_file:
    # Check file type and display accordingly
    if any(selected_file.endswith(ext) for ext in ALLOWED_IMAGE_TYPES):
        # Display image
        image = Image.open(selected_file)
        st.image(image, caption='Selected Image', use_column_width=True)
    elif selected_file.endswith('pdf'):
        # Display PDF
        with open(selected_file, "rb") as file:
            base64_pdf = base64.b64encode(file.read()).decode('utf-8')
        pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
        st.markdown(pdf_display, unsafe_allow_html=True)
