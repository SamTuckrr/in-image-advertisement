import streamlit as st
import os
import json
import tempfile
from google.cloud import vision

# --- Load Brand Links from JSON ---
try:
    with open("brand_links_500.json", "r") as f:
        BRAND_LINKS = json.load(f)
except Exception:
    BRAND_LINKS = {}
    st.warning("Could not load brand_links_500.json. No brand hyperlinks will be shown.")

# --- Streamlit Config ---
st.set_page_config(page_title="InImageAd - Logo Detection", layout="centered")
st.title("InImageAd - Logo Detection Platform")
st.sidebar.header("Instructions")
st.sidebar.markdown("""
- Upload one or more images (JPG, JPEG, PNG)
- The app will detect brand logos
- Click any brand name to visit their website
""")

uploaded_files = st.file_uploader("Upload image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# --- Authenticate with Google Vision using temp file from Streamlit Secrets ---
with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json") as tmp:
    json.dump(st.secrets["gcp_service_account"], tmp)
    tmp_path = tmp.name
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_path

# --- Google Vision Client ---
try:
    client = vision.ImageAnnotatorClient()
except Exception as e:
    st.error("❌ Failed to initialize Google Vision Client. Check credentials.")
    st.stop()

# --- Main Processing Loop ---
if uploaded_files:
    for idx, uploaded_file in enumerate(uploaded_files, 1):
        st.write(f"### Image {idx}")
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        image_bytes = uploaded_file.read()
        image = vision.Image(content=image_bytes)

        try:
            response = client.logo_detection(image=image)
            logos = response.logo_annotations
        except Exception as ex:
            st.error(f"Logo detection failed: {ex}")
            continue

        st.write("#### Detected Logos:")
        if logos:
            for logo in logos:
                brand = logo.description
                score = round(logo.score * 100, 2)
                link = BRAND_LINKS.get(brand)

                st.markdown(f"**{brand}** — {score}% confidence")
                if link:
                    st.markdown(f"[Visit Brand Site]({link})")
                else:
                    st.write("No link available.")
                st.markdown("---")
        else:
            st.info("No logos detected.")

# --- Footer ---
st.caption("Powered by Google Cloud Vision & Streamlit | © 2025 InImageAd")
