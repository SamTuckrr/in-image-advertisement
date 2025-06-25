import streamlit as st
import json
import os
from google.cloud import vision
from google.oauth2 import service_account
from PIL import Image
from PIL.ExifTags import TAGS

# --- Secure Credentials Handling ---
credentials = service_account.Credentials.from_service_account_info(
    json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])
)

client = vision.ImageAnnotatorClient(credentials=credentials)

# --- Helper: Extract EXIF ---
def extract_exif(image_file):
    image = Image.open(image_file)
    exif_data = image._getexif()
    exif_info = {}

    if exif_data:
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            exif_info[tag] = value
    return exif_info

# --- Streamlit App UI ---
st.set_page_config(page_title="InImageAd - Logo Detection", layout="centered")
st.title("InImageAd - Logo Detection Platform (v3 with EXIF)")

uploaded_files = st.file_uploader(
    "Upload image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)

# --- Brand Links ---
BRAND_LINKS = {
    "Audi": "https://www.audi.co.uk/",
    "Nike": "https://www.nike.com/gb",
    "McDonald's": "https://www.mcdonalds.com/gb/en-gb.html",
    "Apple": "https://www.apple.com/uk/",
    "Maxell": "https://www.maxell.eu.com/",
    "Bank of America": "https://www.bankofamerica.com/"
}

# --- Main Processing ---
if uploaded_files:
    for idx, uploaded_file in enumerate(uploaded_files, 1):
        st.write(f"### Image {idx}")
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        image_bytes = uploaded_file.read()
        image = vision.Image(content=image_bytes)

        # Detect logos
        try:
            response = client.logo_detection(image=image)
            logos = response.logo_annotations
        except Exception as ex:
            st.error(f"Logo detection failed: {ex}")
            continue

        # Extract EXIF
        uploaded_file.seek(0)
        exif_info = extract_exif(uploaded_file)

        gps = exif_info.get("GPSInfo", None)
        timestamp = exif_info.get("DateTime", None)
        device = exif_info.get("Model", None)

        st.write("#### Detected Logos:")
        logo_results = []
        if logos:
            for logo in logos:
                brand = logo.description
                score = round(logo.score * 100, 2)
                hyperlink = BRAND_LINKS.get(brand, None)

                st.markdown(f"**{brand}** — {score}% confidence")
                if hyperlink:
                    st.markdown(f"[Visit Brand Site]({hyperlink})")
                else:
                    st.write("No link mapped")
                st.write("---")

                logo_results.append({
                    "brand": brand,
                    "score": score,
                    "hyperlink": hyperlink if hyperlink else "No link"
                })
        else:
            st.info("No logos detected.")

        # --- Save metadata + logos to JSON ---
        output = {
            "image_name": uploaded_file.name,
            "logos": logo_results,
            "exif": {
                "gps": str(gps),
                "timestamp": str(timestamp),
                "device": str(device)
            }
        }

        json_filename = f"{uploaded_file.name}.json"
        with open(json_filename, "w") as f:
            json.dump(output, f, indent=4)

        st.success(f"Metadata saved to {json_filename}")

# --- Footer ---
st.caption("Powered by Google Cloud Vision & Streamlit | © 2025 InImageAd")
