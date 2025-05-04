import streamlit as st

import pandas as pd
import numpy as np

import os
import uuid
from pathlib import Path

from PIL import Image
from io import BytesIO
import base64


if "uploaded_images" not in st.session_state:
    st.session_state.uploaded_images = []

# st.session_state.test_selector = "Home phone"


# option = st.selectbox(
#     "How would you like to be contacted?",
#     ("Email", "Home phone", "Mobile phone"),
#     index=None,
#     key="test_selector"
# )

# st.write("You selected:", option)

# st.write(st.session_state)


def image_to_base64(img):
    if img:
        # Öffne das Bild mit PIL
        pil_image = Image.open(img)
        with BytesIO() as buffer:
            pil_image.save(buffer, "JPEG")
            raw_base64 = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{raw_base64}"


# Chat input
prompt = st.chat_input("Sag was und lade ein Bild hoch", accept_file="multiple", file_type=["jpg", "jpeg", "png"])



if prompt and prompt["files"]:
    #print(prompt["files"], " Laenge: ", len(prompt["files"]), " session state: ", st.session_state.uploaded_images)

    for image in prompt["files"]:
        st.session_state.uploaded_images.append(image)
        #print(image)
    
    #st.write(st.session_state)
    #print(len(st.session_state.uploaded_images))

    df = pd.DataFrame([
        {
            "name": image.name,
            "apps": image_to_base64(image)
        }
            for image in st.session_state.uploaded_images
    ])
    st.dataframe(
        df,
        column_config={
            "apps": st.column_config.ImageColumn(
                "Preview Image", help="Bild-Vorschau"
            )
        },
        use_container_width=True,
        hide_index=True,
        selection_mode="multi-row",
        row_height=100
    )






