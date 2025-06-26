import streamlit as st
import os
import json
import piexif
from PIL import Image
from google.cloud import vision
from google.oauth2 import service_account
from datetime import datetime

# --- Page config ---
st.set_page_config(page_title="InImageAd - Logo Detection", layout="wide")

st.title("🧠 InImageAd - Logo Detection Platform")
st.caption("Upload one or more images. The system will scan for logos and extract metadata.")

# --- Load brand link map ---
brand_links = {}
if os.path.exists("brand_links_500.json"):
    with open("brand_links_500.json", "r", encoding="utf-8") as f:
        brand_links = json.load(f)
else:
    st.warning("Brand link file not found. Brand hyperlinks will not be shown.")

# --- Setup Google Vision Client ---
try:
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = vision.ImageAnnotatorClient(credentials=creds)
except Exception as e:
    st.error("❌ Failed to initialize Google Vision Client.")
    st.stop()

# --- Upload files ---
uploaded_files = st.file_uploader("Upload image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    st.success(f"{len(uploaded_files)} image(s) uploaded. Processing...")

    for uploaded_file in uploaded_files:
        st.divider()
        st.image(uploaded_file, caption=uploaded_file.name, width=300)

        # Read bytes
        image_bytes = uploaded_file.read()

        # --- Logo Detection ---
        try:
            response = client.logo_detection(image=image_bytes)
            logos = response.logo_annotations
        except Exception as e:
            st.error(f"Vision API error: {e}")
            continue

        st.subheader("🧷 Detected Logos")
        results = []
        if logos:
            for logo in logos:
                name = logo.description
                score = round(logo.score * 100, 2)
                link = brand_links.get(name.lower(), None)

                if link:
                    st.markdown(f"**{name}** ({score}%) – [Visit site]({link})")
                else:
                    st.write(f"**{name}** ({score}%)")

                results.append({"name": name, "confidence": score, "link": link})
        else:
            st.write("No logos found.")

        # --- Metadata Extraction ---
        st.subheader("🗂 Image Metadata")
        try:
            with Image.open(uploaded_file) as img:
                exif_data = piexif.load(img.info.get("exif", b""))
                formatted = {tag: str(value) for tag_dict in exif_data.values() for tag, value in tag_dict.items()}
                if formatted:
                    st.json(formatted)
                else:
                    st.write("No metadata found.")
        except Exception as e:
            st.write("No metadata or EXIF extraction failed.")

        # --- Save results as JSON file ---
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = uploaded_file.name.replace(" ", "_").replace(".", "_")
        result_file = f"scan_{safe_name}_{timestamp}.json"

        scan_result = {
            "filename": uploaded_file.name,
            "detected_logos": results,
            "metadata": formatted if 'formatted' in locals() else {},
            "timestamp": timestamp
        }

        with open(result_file, "w", encoding="utf-8") as out:
            json.dump(scan_result, out, indent=2)

        st.success(f"Scan results saved to: {result_file}")
