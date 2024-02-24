import streamlit as st
import os
from PIL import Image

def get_invoice_images():
    invoices_dir = './invoices'
    return [os.path.join(invoices_dir, f) for f in os.listdir(invoices_dir) if f.endswith('.jpeg')]

if __name__ == "__main__":

    st.title('Invoice Image Viewer')

    # Upload an image
    uploaded_image = st.file_uploader("Choose an image...", type="jpeg")

    # Select an image from the directory
    if uploaded_image is None:  # Show the selectbox only if no image is uploaded
        invoice_images = get_invoice_images()
        selected_image = st.selectbox('Or choose a pre-existing invoice image:', invoice_images)

    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption='Uploaded Image', use_column_width=True)
    elif selected_image:
        image = Image.open(selected_image)
        st.image(image, caption='Selected Image', use_column_width=True)


