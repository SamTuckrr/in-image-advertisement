import streamlit as st
import os
import json
import tempfile
import piexif
from PIL import Image
from google.cloud import vision
from google.oauth2 import service_account

# --- Authenticate with Google Cloud using Streamlit secrets ---
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = vision.ImageAnnotatorClient(credentials=creds)

# --- Inline brand links (100+ global + automotive) ---
BRAND_LINKS = {
    "Apple": "https://www.apple.com", "Nike": "https://www.nike.com", "Amazon": "https://www.amazon.com",
    "Google": "https://www.google.com", "Coca-Cola": "https://www.coca-cola.com", "Pepsi": "https://www.pepsi.com",
    "Microsoft": "https://www.microsoft.com", "Adidas": "https://www.adidas.com", "McDonald's": "https://www.mcdonalds.com",
    "Facebook": "https://www.facebook.com", "Samsung": "https://www.samsung.com", "YouTube": "https://www.youtube.com",
    "Netflix": "https://www.netflix.com", "Starbucks": "https://www.starbucks.com", "Tesla": "https://www.tesla.com",
    "Uber": "https://www.uber.com", "Visa": "https://www.visa.com", "MasterCard": "https://www.mastercard.com",
    "BMW": "https://www.bmw.com", "Mercedes-Benz": "https://www.mercedes-benz.com", "Audi": "https://www.audi.com",
    "Toyota": "https://www.toyota.com", "Volkswagen": "https://www.vw.com", "Ford": "https://www.ford.com",
    "Honda": "https://www.honda.com", "Lexus": "https://www.lexus.com", "Chevrolet": "https://www.chevrolet.com",
    "Nissan": "https://www.nissan.com", "Hyundai": "https://www.hyundai.com", "Porsche": "https://www.porsche.com",
    "Kia": "https://www.kia.com", "Land Rover": "https://www.landrover.com", "Jeep": "https://www.jeep.com"
}

# --- Streamlit App Layout ---
st.set_page_config(page_title="InImageAd", layout="centered")
st.title("InImageAd - Logo Detection Prototype")
st.write("Upload an image. We’ll detect logos and link you to the brand site if available.")

uploaded_files = st.file_uploader(
    "Upload image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)
if uploaded_file:
    st.image(uploaded_file, use_column_width=True)
    image_bytes = uploaded_file.read()

    # --- Logo Detection ---
    try:
        image = vision.Image(content=image_bytes)
        response = client.logo_detection(image=image)
        logos = response.logo_annotations

        st.subheader("Detected Logos")
        if logos:
            for logo in logos:
                brand = logo.description
                score = round(logo.score * 100, 2)
                st.write(f"**{brand}** — {score}% confidence")
                link = BRAND_LINKS.get(brand)
                if link:
                    st.markdown(f"[Visit Brand Site]({link})")
        else:
            st.info("No logos found.")
    except Exception as e:
        st.error(f"Error during logo detection: {e}")

    # --- EXIF Metadata (optional) ---
    try:
        tmp_path = tempfile.NamedTemporaryFile(delete=False).name
        with open(tmp_path, "wb") as f:
            f.write(image_bytes)

        img = Image.open(tmp_path)
        exif_data = piexif.load(img.info.get("exif", b""))
        st.subheader("Image Metadata")
        st.json(exif_data.get("0th", {}))
    except Exception:
        st.info("No EXIF metadata available.")

