import streamlit as st
import os
import json
import tempfile
from google.cloud import vision
from PIL import Image
import piexif
import uuid
import datetime

# --- Set Page Config ---
st.set_page_config(page_title="InImageAd - Logo Detection", layout="centered")

# --- Title and Sidebar ---
st.title("InImageAd - Logo Detection Platform")
st.sidebar.header("Instructions")
st.sidebar.markdown("""
1. Upload image(s) (jpg, jpeg, png).
2. We'll detect brand logos, generate metadata, and link to known brand sites.
3. Metadata is saved as a downloadable `.json` file.
""")

# --- Set up Google Cloud Vision credentials securely ---
with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json") as tmp:
    json.dump(st.secrets["gcp_service_account"].to_dict(), tmp)
    tmp.flush()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp.name

# --- Try loading brand links JSON (optional external file) ---
brand_links = {}
try:
    with open("brand_links_500.json", "r") as f:
        brand_links = json.load(f)
except Exception:
    st.warning("Could not load brand_links_500.json. No brand hyperlinks will be shown.")

# --- Upload Section ---
uploaded_files = st.file_uploader("Upload image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# --- Init Google Cloud Vision client ---
try:
    client = vision.ImageAnnotatorClient()
except Exception as e:
    st.error("⚠️ Failed to initialize Google Vision Client.")
    st.stop()

# --- Process uploaded images ---
if uploaded_files:
    for img_file in uploaded_files:
        st.image(img_file, caption="Uploaded Image", use_column_width=True)

        image_content = img_file.read()
        image = vision.Image(content=image_content)

        # Logo Detection
        try:
            response = client.logo_detection(image=image)
            logos = response.logo_annotations
        except Exception as e:
            st.error(f"Logo detection failed: {e}")
            continue

        # Display Results
        st.subheader("Detected Logos:")
        logo_results = []
        if logos:
            for logo in logos:
                name = logo.description
                score = round(logo.score * 100, 2)
                st.markdown(f"**{name}** — {score}% confidence")
                if name in brand_links:
                    st.markdown(f"[Visit Brand Site]({brand_links[name]})")
                else:
                    st.write("No link mapped")
                st.markdown("---")
                logo_results.append({"brand": name, "confidence": score})
        else:
            st.write("No logos detected.")

        # --- Metadata ---
        st.subheader("📦 Metadata")
        meta = {
            "id": str(uuid.uuid4()),
            "filename": img_file.name,
            "timestamp": datetime.datetime.now().isoformat(),
            "logo_detections": logo_results
        }

        # --- EXIF Read ---
        try:
            img_pil = Image.open(img_file)
            exif_data = piexif.load(img_pil.info["exif"])
            meta["exif"] = {k: str(v) for k, v in exif_data.get("0th", {}).items()}
        except Exception:
            meta["exif"] = "Not available"

        # --- Save metadata to downloadable .json ---
        json_filename = img_file.name + ".json"
        with open(json_filename, "w") as jf:
            json.dump(meta, jf, indent=2)

        with open(json_filename, "rb") as jf:
            st.download_button(
                label="Download Metadata JSON",
                data=jf,
                file_name=json_filename,
                mime="application/json"
            )

st.caption("Powered by Google Cloud Vision & Streamlit | © 2025 InImageAd")
