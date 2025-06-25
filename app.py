import streamlit as st
import os
import json
import uuid
import tempfile
import piexif
from PIL import Image
from google.cloud import vision

# --- Secure Credential Handling ---
with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
    json.dump(st.secrets["gcp_service_account"], tmp)
    tmp.flush()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp.name

# --- Load Brand Links Map (Optional) ---
BRAND_LINKS = {}
try:
    with open("brand_links_500.json", "r", encoding="utf-8") as f:
        BRAND_LINKS = json.load(f)
except:
    st.warning("Could not load brand_links_500.json. No brand hyperlinks will be shown.")

# --- Streamlit UI ---
st.set_page_config(page_title="InImageAd - Logo Detection Platform", layout="centered")
st.title("InImageAd - Logo Detection Platform")
st.markdown("Upload image(s) below to detect brand logos and generate metadata.")

uploaded_files = st.file_uploader(
    "Upload image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)

# --- Initialize Vision API ---
try:
    client = vision.ImageAnnotatorClient()
except Exception:
    st.error("❌ Failed to initialize Google Vision Client.")
    st.stop()

# --- Process Uploads ---
if uploaded_files:
    for idx, uploaded_file in enumerate(uploaded_files, 1):
        st.markdown(f"### 📷 Image {idx}")
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        image_bytes = uploaded_file.read()
        image = vision.Image(content=image_bytes)

        # --- Detect Logos ---
        try:
            response = client.logo_detection(image=image)
            logos = response.logo_annotations
        except Exception as ex:
            st.error(f"Logo detection failed: {ex}")
            continue

        st.subheader("Detected Logos:")
        metadata = {"detected_logos": []}

        if logos:
            for logo in logos:
                brand = logo.description
                score = round(logo.score * 100, 2)
                link = BRAND_LINKS.get(brand)
                metadata["detected_logos"].append({
                    "brand": brand,
                    "confidence": score,
                    "link": link
                })

                st.markdown(f"**{brand}** — {score}% confidence")
                if link:
                    st.markdown(f"[🔗 Visit Brand Site]({link})")
                else:
                    st.write("No link mapped")
                st.markdown("---")
        else:
            st.info("No logos detected.")

        # --- Extract EXIF Metadata ---
        exif_data = {}
        try:
            img = Image.open(uploaded_file)
            exif_bytes = img.info.get("exif")
            if exif_bytes:
                raw_exif = piexif.load(exif_bytes)
                for ifd in raw_exif:
                    if isinstance(raw_exif[ifd], dict):
                        for tag in raw_exif[ifd]:
                            key = piexif.TAGS[ifd].get(tag, {}).get("name", tag)
                            val = raw_exif[ifd][tag]
                            if isinstance(val, bytes):
                                val = val.decode(errors="ignore")
                            exif_data[f"{ifd}.{key}"] = val
            metadata["exif"] = exif_data
        except Exception as e:
            metadata["exif_error"] = str(e)

        # --- Save Metadata JSON ---
        output_filename = f"{uuid.uuid4()}.jpeg.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        st.success(f"✅ Metadata saved to `{output_filename}`")

st.caption("Powered by Google Cloud Vision & Streamlit | © 2025 InImageAd")

