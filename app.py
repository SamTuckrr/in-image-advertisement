import streamlit as st
import os
import tempfile
import json
import piexif
from PIL import Image
from google.cloud import vision
from google.oauth2 import service_account

# Secure Google Vision credentials
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = vision.ImageAnnotatorClient(credentials=creds)

# Brand hyperlinks (top 100+ global brands & cars)
BRAND_LINKS = {
    "Nike": "https://www.nike.com", "Adidas": "https://www.adidas.com", "Apple": "https://www.apple.com",
    "Samsung": "https://www.samsung.com", "Microsoft": "https://www.microsoft.com", "Amazon": "https://www.amazon.com",
    "Google": "https://www.google.com", "Facebook": "https://www.facebook.com", "Coca-Cola": "https://www.coca-cola.com",
    "Pepsi": "https://www.pepsi.com", "McDonald's": "https://www.mcdonalds.com", "Starbucks": "https://www.starbucks.com",
    "Toyota": "https://www.toyota.com", "BMW": "https://www.bmw.com", "Mercedes-Benz": "https://www.mercedes-benz.com",
    "Audi": "https://www.audi.com", "Volkswagen": "https://www.vw.com", "Ford": "https://www.ford.com",
    "Honda": "https://www.honda.com", "Hyundai": "https://www.hyundai.com", "Nissan": "https://www.nissan-global.com",
    "Chevrolet": "https://www.chevrolet.com", "Kia": "https://www.kia.com", "Lexus": "https://www.lexus.com",
    "Jeep": "https://www.jeep.com", "Land Rover": "https://www.landrover.com", "Porsche": "https://www.porsche.com",
    "Jaguar": "https://www.jaguar.com", "Mazda": "https://www.mazda.com", "Ferrari": "https://www.ferrari.com",
    "Lamborghini": "https://www.lamborghini.com", "Bugatti": "https://www.bugatti.com", "Rolls-Royce": "https://www.rolls-roycemotorcars.com",
    "Bentley": "https://www.bentleymotors.com", "Tesla": "https://www.tesla.com", "Shell": "https://www.shell.com",
    "BP": "https://www.bp.com", "Visa": "https://www.visa.com", "MasterCard": "https://www.mastercard.com",
    "Sony": "https://www.sony.com", "Panasonic": "https://www.panasonic.com", "LG": "https://www.lg.com",
    "Nestlé": "https://www.nestle.com", "Unilever": "https://www.unilever.com", "Procter & Gamble": "https://us.pg.com",
    "Heineken": "https://www.theheinekencompany.com", "Red Bull": "https://www.redbull.com", "Budweiser": "https://www.budweiser.com",
    "Netflix": "https://www.netflix.com", "Disney": "https://www.disney.com", "YouTube": "https://www.youtube.com",
    "Twitter": "https://www.twitter.com", "Instagram": "https://www.instagram.com", "LinkedIn": "https://www.linkedin.com",
    "HP": "https://www.hp.com", "Dell": "https://www.dell.com", "Lenovo": "https://www.lenovo.com",
    "Intel": "https://www.intel.com", "AMD": "https://www.amd.com", "NVIDIA": "https://www.nvidia.com",
    "Maxell": "https://www.maxell.eu.com", "Bank of America": "https://www.bankofamerica.com"
}

# Streamlit UI
st.set_page_config(page_title="InImageAd - Logo Detection", layout="centered")
st.title("InImageAd - Logo Detection Platform")
uploaded_files = st.file_uploader("Upload image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Main processing loop
if uploaded_files:
    for uploaded_file in uploaded_files:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        image_bytes = uploaded_file.read()
        vision_image = vision.Image(content=image_bytes)

        # Logo detection
        try:
            response = client.logo_detection(image=vision_image)
            logos = response.logo_annotations
        except Exception as e:
            st.error(f"Logo detection failed: {e}")
            continue

        st.markdown("### Detected Logos")
        if logos:
            for logo in logos:
                brand = logo.description
                score = round(logo.score * 100, 2)
                st.write(f"**{brand}** — {score}% confidence")
                st.markdown(f"[Visit Brand Site]({BRAND_LINKS.get(brand, '#')})" if brand in BRAND_LINKS else "No link mapped")
                st.write("---")
        else:
            st.info("No logos detected.")

        # EXIF metadata extraction
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name
            exif_dict = piexif.load(tmp_path)
            metadata = {str(tag): str(value) for tag, value in exif_dict.get("Exif", {}).items()}
        except Exception:
            metadata = {"warning": "No EXIF metadata available."}

        st.markdown("### Image Metadata")
        st.json(metadata)

        # Optional: Save metadata JSON
        filename = uploaded_file.name + ".json"
        with open(filename, "w") as f:
            json.dump({
                "filename": uploaded_file.name,
                "logos": [l.description for l in logos],
                "confidence": [round(l.score * 100, 2) for l in logos],
                "metadata": metadata
            }, f)
            st.success(f"Metadata saved to {filename}")

st.caption("Powered by Google Cloud Vision & Streamlit | © 2025 InImageAd")
