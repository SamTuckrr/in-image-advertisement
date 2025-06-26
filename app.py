import streamlit as st
from google.cloud import vision
from google.oauth2 import service_account
from PIL import Image
import io
import os
import json
import piexif

# Page configuration
st.set_page_config(page_title="InImageAd - Logo Detection", layout="wide")
st.title("🖼️ InImageAd - Logo Detection Platform")
st.markdown("Upload one or more images. The system will scan for logos and metadata.")

# GCP credentials
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = vision.ImageAnnotatorClient(credentials=creds)

# File uploader
uploaded_files = st.file_uploader("Upload image(s)", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)

        # Read image bytes
        image_bytes = uploaded_file.read()

        # Wrap bytes in Google Vision API Image object
        vision_image = vision.Image(content=image_bytes)

        try:
            # Logo detection
            response = client.logo_detection(image=vision_image)
            logos = response.logo_annotations

            if logos:
                st.subheader("🧠 Detected Logos:")
                for logo in logos:
                    st.markdown(f"- **{logo.description}** (Confidence: {round(logo.score * 100, 2)}%)")
            else:
                st.info("No logos detected.")

            # Metadata extraction using piexif
            st.subheader("📸 Metadata:")
            try:
                img = Image.open(io.BytesIO(image_bytes))
                exif_data = piexif.load(img.info.get('exif', b''))
                if exif_data:
                    for ifd in exif_data:
                        if isinstance(exif_data[ifd], dict):
                            for tag in exif_data[ifd]:
                                label = piexif.TAGS[ifd].get(tag, {'name': 'Unknown'})['name']
                                value = exif_data[ifd][tag]
                                st.markdown(f"**{label}**: {value}")
                else:
                    st.info("No EXIF metadata found.")
            except Exception as e:
                st.warning(f"Metadata read error: {e}")

            # Save results to JSON
            result = {
                "filename": uploaded_file.name,
                "detected_logos": [logo.description for logo in logos],
                "metadata": "See metadata section above"
            }

            json_filename = f"{os.path.splitext(uploaded_file.name)[0]}_results.json"
            with open(json_filename, "w") as f:
                json.dump(result, f, indent=2)

        except Exception as e:
            st.error(f"Vision API error: {e}")
