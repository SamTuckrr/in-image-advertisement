import streamlit as st
import os
import json
import tempfile
from google.cloud import vision
from PIL import Image
import piexif

# --- Set Streamlit Page Config ---
st.set_page_config(page_title="InImageAd - Logo Detection Platform", layout="centered")

# --- Secure Credential Handling ---
with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
    json.dump(dict(st.secrets["gcp_service_account"]), tmp)
    tmp.flush()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp.name

# --- Load Brand Links (optional, from JSON) ---
brand_links = {}
try:
    with open("brand_links_500.json", "r") as f:
        brand_links = json.load(f)
except Exception:
    st.warning("⚠️ Could not load brand_links_500.json. No brand hyperlinks will be shown.")

# --- Vision API Client ---
try:
    client = vision.ImageAnnotatorClient()
except Exception:
    st.error("❌ Failed to initialize Google Vision Client.")
    st.stop()

# --- UI Instructions ---
st.title("InImageAd - Logo Detection Platform")
st.markdown("Upload your images to detect logos and extract metadata.")

uploaded_files = st.file_uploader("Upload image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# --- Main Processing ---
if uploaded_files:
    for idx, uploaded_file in enumerate(uploaded_files, 1):
        st.markdown(f"### 📷 Image {idx}")
        st.image(uploaded_file, use_column_width=True)

        image_bytes = uploaded_file.read()
        image = vision.Image(content=image_bytes)

        # Logo Detection
        try:
            response = client.logo_detection(image=image)
            logos = response.logo_annotations
        except Exception as e:
            st.error(f"❌ Error during logo detection: {e}")
            continue

        st.markdown("#### 🏷️ Detected Logos:")
        if logos:
            for logo in logos:
                name = logo.description
                score = round(logo.score * 100, 2)
                link = brand_links.get(name)

                st.write(f"**{name}** — {score}% confidence")
                if link:
                    st.markdown(f"[Visit Brand Site]({link})")
                st.write("---")
        else:
            st.info("No logos detected.")

        # EXIF Metadata Extraction
        st.markdown("#### 📂 Metadata Info:")
        try:
            img = Image.open(uploaded_file)
            exif_data = piexif.load(img.info.get("exif", b""))
            user_metadata = {
                "FileName": uploaded_file.name,
                "DetectedLogos": [logo.description for logo in logos],
                "ConfidenceScores": [round(logo.score * 100, 2) for logo in logos],
                "EXIF": {
                    "Make": exif_data["0th"].get(piexif.ImageIFD.Make, b"").decode("utf-8", "ignore"),
                    "Model": exif_data["0th"].get(piexif.ImageIFD.Model, b"").decode("utf-8", "ignore"),
                }
            }

            json_filename = uploaded_file.name + ".json"
            with open(json_filename, "w") as jf:
                json.dump(user_metadata, jf, indent=2)
            st.success(f"Metadata saved to **{json_filename}**")
        except Exception:
            st.warning("⚠️ Could not read or save EXIF metadata.")

# --- Footer ---
st.caption("Powered by Google Cloud Vision & Streamlit • © 2025 InImageAd")


