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

# Initialize Google Cloud Vision client using credentials from environment
try:
    creds_info = json.loads(os.environ.get("GCP_SERVICE_ACCOUNT", "{}"))
    credentials = service_account.Credentials.from_service_account_info(creds_info)
    client = vision.ImageAnnotatorClient(credentials=credentials)
except Exception as e:
    st.error(f"Failed to load Google credentials: {e}")
    st.stop()

# Load brand link mapping
try:
    with open("brand_links.json", "r") as f:
        brand_links = json.load(f)
except Exception as e:
    st.warning(f"Could not load brand links: {e}")
    brand_links = {}

# File uploader
uploaded_files = st.file_uploader(
    "Upload image(s)", accept_multiple_files=True, type=["jpg", "jpeg", "png"]
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)

        image_bytes = uploaded_file.getvalue()
        vision_image = vision.Image(content=image_bytes)

        logos = []
        try:
            response = client.logo_detection(image=vision_image)
            logos = response.logo_annotations
        except Exception as e:
            st.error(f"Vision API error: {e}")

        if logos:
            st.subheader("🧠 Detected Logos:")
            for logo in logos:
                desc = logo.description.lower()
                confidence = round(logo.score * 100, 2)
                url = brand_links.get(desc)
                if url:
                    st.markdown(f"- [{logo.description}]({url}) ({confidence}%)")
                else:
                    st.markdown(f"- **{logo.description}** ({confidence}%)")
        else:
            st.info("No logos detected.")

        st.subheader("📸 Metadata:")
        exif_display = {}
        try:
            img = Image.open(io.BytesIO(image_bytes))
            exif_bytes = img.info.get("exif")
            exif_dict = piexif.load(exif_bytes) if exif_bytes else {}
            for ifd in exif_dict:
                if isinstance(exif_dict[ifd], dict):
                    for tag, value in exif_dict[ifd].items():
                        label = piexif.TAGS[ifd].get(tag, {"name": "Unknown"})["name"]
                        if isinstance(value, bytes):
                            try:
                                value = value.decode("utf-8", errors="ignore")
                            except Exception:
                                value = str(value)
                        exif_display[label] = value
                        st.markdown(f"**{label}**: {value}")
            if not exif_display:
                st.info("No EXIF metadata found.")
        except Exception as e:
            st.warning(f"Metadata read error: {e}")

        result = {
            "filename": uploaded_file.name,
            "detected_logos": [logo.description for logo in logos],
            "exif": exif_display,
        }

        json_filename = f"{os.path.splitext(uploaded_file.name)[0]}_results.json"
        try:
            with open(json_filename, "w") as f:
                json.dump(result, f, indent=2)
        except Exception as e:
            st.warning(f"Could not save results: {e}")
