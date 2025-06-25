import streamlit as st
import os
import json
import tempfile
import piexif
from PIL import Image
from google.cloud import vision
from google.oauth2 import service_account

# --- Google Cloud Credentials ---
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = vision.ImageAnnotatorClient(credentials=creds)

# --- Streamlit UI ---
st.set_page_config(page_title="InImageAd - Logo Detection", layout="centered")
st.title("InImageAd - Logo Detection Platform")
st.caption("Upload one or more images. The system will scan for logos and metadata.")

uploaded_files = st.file_uploader("Upload image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# --- Process uploaded images ---
if uploaded_files:
    for idx, uploaded_file in enumerate(uploaded_files, 1):
        st.subheader(f"Image {idx}")
        st.image(uploaded_file, use_column_width=True)

        # --- Logo Detection ---
        image_bytes = uploaded_file.read()
        image = vision.Image(content=image_bytes)
        try:
            response = client.logo_detection(image=image)
            logos = response.logo_annotations
        except Exception as e:
            st.error(f"Logo detection failed: {e}")
            continue

        st.write("#### Detected Logos:")
        if logos:
            for logo in logos:
                brand = logo.description
                score = round(logo.score * 100, 2)
                st.markdown(f"- **{brand}** — {score}% confidence")
        else:
            st.info("No logos detected.")

        # --- EXIF Metadata Extraction ---
        exif_data = {}
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
                tmp_img.write(image_bytes)
                tmp_path = tmp_img.name

            img = Image.open(tmp_path)
            exif_raw = piexif.load(img.info.get("exif", b""))
            for ifd in exif_raw:
                for tag in exif_raw[ifd]:
                    label = piexif.TAGS[ifd][tag]["name"]
                    value = exif_raw[ifd][tag]
                    exif_data[label] = str(value)

        except Exception as e:
            exif_data["error"] = f"EXIF extract failed: {e}"

        # --- Save Results to JSON ---
        metadata = {
            "filename": uploaded_file.name,
            "detected_logos": [logo.description for logo in logos],
            "confidence_scores": [round(logo.score * 100, 2) for logo in logos],
            "exif": exif_data,
        }

        json_name = uploaded_file.name + ".json"
        with open(json_name, "w") as f:
            json.dump(metadata, f, indent=2)

        st.success(f"Metadata saved to **{json_name}**")
